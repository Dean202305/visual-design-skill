#!/usr/bin/env python3
"""Validate this portable skill without third-party Python packages."""
import argparse
import ast
import json
import re
from pathlib import Path
from urllib.parse import unquote

LINK = re.compile(r"\[[^\]\n]*\]\((<[^>]+>|[^\s)]+)(?:\s+[^)]*)?\)")
PRIVATE = {
    "machine_home_path": re.compile(r"/(?:Users|home)/[A-Za-z0-9._-]+/"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),
    "github_fine_grained_token": re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    "api_secret": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{24,}\b"),
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
}


def validate(root):
    errors, links, files = [], 0, 0
    entry = root / "SKILL.md"
    if not entry.is_file():
        return {"ok": False, "errors": ["Missing SKILL.md"]}
    body = entry.read_text(encoding="utf-8")
    frontmatter = re.match(r"\A---\n(.*?)\n---(?:\n|$)", body, re.S)
    if not frontmatter:
        errors.append("Missing YAML frontmatter")
    else:
        name = re.search(r"(?m)^name:\s*([a-z0-9-]+)\s*$", frontmatter[1])
        if not name or name[1] != root.name or len(name[1]) > 64:
            errors.append("Skill name must match its folder")
        if not re.search(r"(?m)^description:\s*\S.+$", frontmatter[1]):
            errors.append("Missing nonempty description")
    for expected in ["agents/openai.yaml", "assets/templates/design-brief.md", "assets/templates/competitive-review.md", "assets/templates/component-spec.md"]:
        if not (root / expected).is_file():
            errors.append("Missing required resource: " + expected)
    if list(root.rglob("SKILL.md")) != [entry]:
        errors.append("Unexpected nested skill entry")
    for path in sorted(root.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        files += 1
        relative = str(path.relative_to(root))
        if path.is_symlink():
            errors.append("Unexpected symlink: " + relative)
            continue
        if path.suffix not in {".md", ".py", ".yaml"}:
            errors.append("Unexpected publication file type: " + relative)
            continue
        text = path.read_text(encoding="utf-8")
        for label, pattern in PRIVATE.items():
            if pattern.search(text):
                errors.append(label + ": " + relative)
        if path.suffix == ".py":
            try:
                ast.parse(text, filename=relative)
            except SyntaxError as error:
                errors.append("Python syntax: " + relative + ": " + str(error.lineno))
        if path.suffix != ".md":
            continue
        prose = re.sub(r"```.*?```", "", text, flags=re.S)
        for match in LINK.finditer(prose):
            value = match[1].strip("<>")
            if value.startswith("#") or re.match(r"^[a-z][a-z0-9+.-]*:", value, re.I):
                continue
            value = unquote(value.split("#", 1)[0].split("?", 1)[0])
            if not value:
                continue
            links += 1
            target = (path.parent / value).resolve()
            if not target.is_relative_to(root):
                errors.append("Link escapes skill: " + relative + " -> " + value)
            elif not target.exists():
                errors.append("Broken link: " + relative + " -> " + value)
    return {"ok": not errors, "files": files, "local_links_checked": links, "errors": errors}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    result = validate(args.root.resolve())
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
