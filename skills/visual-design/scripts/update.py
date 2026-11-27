#!/usr/bin/env python3
"""Check the official GitHub Release and replace an unmodified installation."""
import argparse
from contextlib import contextmanager
import hashlib
import io
import json
import os
from pathlib import Path, PureWindowsPath
import re
import stat
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile


NAME = "visual-design"
REPO = "Dean202305/visual-design-skill"
RELEASES = f"https://api.github.com/repos/{REPO}/releases"
MANIFEST = "release-manifest.json"
CHECK_INTERVAL = 6 * 60 * 60
MAX_DOWNLOAD = 16 * 1024 * 1024
MAX_UNPACKED = 64 * 1024 * 1024
VERSION = r"[0-9]{1,6}\.[0-9]{1,6}\.[0-9]{1,6}"


def version_key(version):
    if not isinstance(version, str) or not re.fullmatch(VERSION, version):
        raise ValueError("Invalid Visual Design version")
    return tuple(map(int, version.split(".")))


def identity(root):
    text = (root / "SKILL.md").read_text(encoding="utf-8")
    header = re.match(r"\A---\n(.*?)\n---(?:\n|$)", text, re.S)
    if not header or not re.search(r"(?m)^name:[ \t]*visual-design[ \t]*$", header[1]):
        raise ValueError("Selected directory is not a Visual Design installation")
    for prefix, profile in [("", "workbuddy"), ("  ", "portable")]:
        match = re.search(rf'(?m)^{prefix}version:[ \t]*["\']?({VERSION})["\']?[ \t]*$', header[1])
        if match:
            return match[1], profile
    raise ValueError("Installed Visual Design has no recognizable version")


def manifest_bytes(entries, version, profile):
    manifest = {
        "schema": 1,
        "version": version,
        "profile": profile,
        "files": file_digests(entries),
    }
    return (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")


def file_digests(entries):
    return {name: hashlib.sha256(content).hexdigest() for name, content in entries if name != MANIFEST}


def read_manifest(root, version, profile):
    manifest = json.loads((root / MANIFEST).read_bytes())
    if not isinstance(manifest, dict):
        raise ValueError("Invalid release manifest")
    identity_fields = manifest.get("schema"), manifest.get("version"), manifest.get("profile")
    if identity_fields != (1, version, profile):
        raise ValueError("Release manifest does not match the installed version and format")
    files = manifest.get("files")
    if not isinstance(files, dict) or not {"SKILL.md", "scripts/update.py"}.issubset(files):
        raise ValueError("Release manifest is incomplete")
    return files


def matches_tree(root, expected):
    files = {}
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if path.is_symlink():
            return False
        if "__pycache__" in relative.parts or path.name == ".DS_Store" or path.suffix == ".pyc":
            continue
        if path.is_dir() or relative.as_posix() == MANIFEST:
            continue
        if not path.is_file() or path.stat().st_size > MAX_UNPACKED:
            return False
        files[relative.as_posix()] = path
    if files.keys() != expected.keys():
        return False
    return all(hashlib.sha256(path.read_bytes()).hexdigest() == expected[name] for name, path in files.items())


class ReleaseRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        url = urllib.parse.urlsplit(newurl)
        if url.scheme != "https" or url.netloc not in {
            "api.github.com", "github.com", "release-assets.githubusercontent.com", "objects.githubusercontent.com",
        }:
            raise ValueError("Release redirect left GitHub HTTPS")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch(url, limit, accept="application/octet-stream"):
    request = urllib.request.Request(url, headers={"User-Agent": "visual-design-updater", "Accept": accept})
    opener = urllib.request.build_opener(ReleaseRedirect())
    try:
        with opener.open(request, timeout=5) as response:
            content = response.read(limit + 1)
    except urllib.error.HTTPError as error:
        raise ValueError(f"GitHub returned HTTP {error.code}") from error
    except (urllib.error.URLError, TimeoutError) as error:
        raise ValueError("GitHub is unreachable") from error
    if len(content) > limit:
        raise ValueError("GitHub response exceeded its expected size")
    return content


def get_release(version=None):
    endpoint = "latest" if version is None else f"tags/v{version}"
    release = json.loads(fetch(f"{RELEASES}/{endpoint}", 1024 * 1024, "application/vnd.github+json"))
    if not isinstance(release, dict) or release.get("draft") is not False or release.get("prerelease") is not False:
        raise ValueError("GitHub did not return a stable release")
    tag = release.get("tag_name", "")
    if not isinstance(tag, str) or not re.fullmatch(rf"v{VERSION}", tag) or (version and tag != f"v{version}"):
        raise ValueError("GitHub release tag does not match an official version")
    return release


def download(release, profile):
    tag = release["tag_name"]
    name = f"{NAME}-{profile}-{tag}.zip"
    url = f"https://github.com/{REPO}/releases/download/{tag}/{name}"
    assets = [asset for asset in release.get("assets", []) if isinstance(asset, dict) and asset.get("name") == name]
    if len(assets) != 1:
        raise ValueError("Expected release archive is unavailable")
    asset = assets[0]
    if asset.get("browser_download_url") != url or asset.get("state") != "uploaded":
        raise ValueError("Expected release archive is unavailable")
    size, digest = asset.get("size"), asset.get("digest")
    if type(size) is not int or not 0 < size <= MAX_DOWNLOAD:
        raise ValueError("GitHub release archive has an invalid size")
    if not isinstance(digest, str) or not re.fullmatch(r"sha256:[a-f0-9]{64}", digest):
        raise ValueError("GitHub release archive lacks a valid SHA-256 digest")
    archive = fetch(url, size)
    if len(archive) != size or "sha256:" + hashlib.sha256(archive).hexdigest() != digest:
        raise ValueError("Release archive failed its SHA-256 check")
    return archive


def archive_files(archive, profile):
    prefix = f"{NAME}/" if profile == "portable" else ""
    files, names, size = {}, set(), 0
    with zipfile.ZipFile(io.BytesIO(archive)) as bundle:
        for item in bundle.infolist():
            path = item.filename
            relative = path[len(prefix):]
            unsafe_part = any(
                part in {"", ".", ".."} or part.endswith((".", " ")) or PureWindowsPath(part).is_reserved()
                for part in relative.split("/")
            )
            if (not path.startswith(prefix) or item.orig_filename != path or unsafe_part
                    or re.search(r'[\\:<>"|?*\x00-\x1f]', relative) or relative.casefold() in names
                    or stat.S_IFMT(item.external_attr >> 16) not in {0, stat.S_IFREG}):
                raise ValueError("Unsafe path or unsupported entry in release archive")
            size += item.file_size
            if size > MAX_UNPACKED or len(files) >= 2000:
                raise ValueError("Release archive exceeds unpacking limits")
            names.add(relative.casefold())
            files[relative] = bundle.read(item)
    return files


def git_managed(root):
    if not any((parent / ".git").exists() for parent in (root, *root.parents)):
        return False
    try:
        result = subprocess.run(["git", "-C", str(root), "ls-files", "-z", "--", "."], capture_output=True, timeout=3)
    except (OSError, subprocess.TimeoutExpired):
        return True
    return result.returncode != 0 or bool(result.stdout)


def state_path(root):
    key = hashlib.sha256(os.fsencode(os.path.normcase(str(root)))).hexdigest()[:16]
    parent = root.parent.parent if root.parent.name == "skills" else root.parent
    return parent / ".visual-design-updates" / key


@contextmanager
def update_lock(directory):
    directory.mkdir(parents=True, exist_ok=True)
    with (directory / "lock").open("a+b") as lock:
        if os.name == "nt":
            import msvcrt

            lock.seek(0)
            try:
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            except OSError:
                yield False
                return
        else:
            import fcntl

            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                yield False
                return
        yield True


def stage_and_replace(root, directory, bundle, version, profile, expected, installed):
    with tempfile.TemporaryDirectory(prefix="stage-", dir=directory) as temporary:
        staged = Path(temporary) / NAME
        for relative, content in bundle.items():
            target = staged / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)
        if identity(staged) != (version, profile) or not matches_tree(staged, read_manifest(staged, version, profile)):
            raise ValueError("Downloaded skill does not match its release manifest")
        if identity(root) != (installed, profile) or not matches_tree(root, expected):
            return {"status": "local_changes", "version": installed, "latest": version}
        backup = directory / "backups" / f"v{installed}-{time.time_ns()}" / NAME
        backup.parent.mkdir(parents=True)
        root.rename(backup)
        try:
            staged.rename(root)
        except BaseException:
            backup.rename(root)
            raise
    return {"status": "updated", "version": version, "previous": installed, "backup": str(backup), "skill_dir": str(root)}


def update(root, mode="auto"):
    if mode == "auto" and os.environ.get("VISUAL_DESIGN_AUTO_UPDATE") == "0":
        return {"status": "disabled"}
    if root.is_symlink():
        return {"status": "unmanaged", "reason": "This installation is a symlink"}
    root = root.resolve(strict=True)
    installed, profile = identity(root)
    has_manifest = (root / MANIFEST).is_file()
    result = {"version": installed}
    if mode == "check":
        latest = get_release()["tag_name"][1:]
        return dict(result, status="available" if version_key(latest) > version_key(installed) else "current", latest=latest)
    if not has_manifest and mode == "auto":
        return dict(result, status="unmanaged")
    if git_managed(root):
        return dict(result, status="git_managed")
    directory = state_path(root)
    with update_lock(directory) as acquired:
        if not acquired:
            return dict(result, status="busy")
        marker = directory / "last-check"
        if mode == "auto" and marker.is_file() and 0 <= time.time() - marker.stat().st_mtime < CHECK_INTERVAL:
            return dict(result, status="cached")
        marker.touch()
        release = get_release()
        latest = release["tag_name"][1:]
        result["latest"] = latest
        if version_key(latest) <= version_key(installed):
            return dict(result, status="current")
        if has_manifest:
            expected = read_manifest(root, installed, profile)
        else:
            previous = archive_files(download(get_release(installed), profile), profile)
            expected = file_digests(previous.items())
        if not matches_tree(root, expected):
            return dict(result, status="local_changes")
        bundle = archive_files(download(release, profile), profile)
        return stage_and_replace(root, directory, bundle, latest, profile, expected, installed)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skill-dir", type=Path, default=Path(__file__).absolute().parents[1])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="Compare versions without writing files")
    mode.add_argument("--now", action="store_true", help="Check immediately and update an unchanged installation")
    args = parser.parse_args()
    try:
        result = update(args.skill_dir.expanduser(), "check" if args.check else "now" if args.now else "auto")
    except (OSError, ValueError, KeyError, TypeError, RuntimeError, zipfile.BadZipFile) as error:
        result = {"status": "unavailable", "reason": str(error)}
    print(json.dumps(result, ensure_ascii=True))
    if args.check or args.now:
        return 0 if result["status"] in {"updated", "current", "available"} else 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
