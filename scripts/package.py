#!/usr/bin/env python3
"""Build reproducible portable and WorkBuddy ZIPs from the same design workflow."""
import argparse
import hashlib
import json
import tempfile
import zipfile
from pathlib import Path
from skill_tools import ROOT, NAME, check_skill, skill_files, version, workbuddy_entry


def build(output, profiles=('portable', 'workbuddy')):
    check_skill()
    output = Path(output)
    if output.resolve().is_relative_to((ROOT / 'skills').resolve()):
        raise ValueError('Output must be outside the canonical skill tree')
    output.mkdir(parents=True, exist_ok=True)
    artifacts = []
    for profile in profiles:
        if profile not in {'portable', 'workbuddy'}:
            raise ValueError('Unknown profile')
        entries = []
        for relative, content in skill_files():
            if profile == 'workbuddy':
                if relative.parts[0] == 'agents':
                    continue
                if relative.as_posix() == 'SKILL.md':
                    content = workbuddy_entry(content.decode('utf-8')).encode('utf-8')
            entries.append((relative.as_posix(), content))
        with tempfile.TemporaryDirectory(prefix='visual-design-package-check-') as temporary:
            staged = Path(temporary) / NAME
            for relative, content in entries:
                target = staged / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            check_skill(staged, profile)
        name = f'{NAME}-{profile}-v{version()}.zip'
        archive = output / name
        with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as bundle:
            for relative, content in entries:
                member = relative if profile == 'workbuddy' else NAME + '/' + relative
                info = zipfile.ZipInfo(member, date_time=(1980, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.create_system = 3
                info.external_attr = 0o100644 << 16
                bundle.writestr(info, content)
        artifacts.append(archive)
    checksums = ''.join(hashlib.sha256(path.read_bytes()).hexdigest() + '  ' + path.name + '\n' for path in artifacts)
    (output / 'SHA256SUMS').write_text(checksums, encoding='utf-8')
    return artifacts


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, default=ROOT / 'dist')
    parser.add_argument('--profile', choices=['all', 'portable', 'workbuddy'], default='all')
    args = parser.parse_args()
    profiles = ('portable', 'workbuddy') if args.profile == 'all' else (args.profile,)
    try:
        artifacts = build(args.output, profiles)
    except (OSError, ValueError) as error:
        parser.exit(1, 'Packaging failed: ' + str(error) + '\n')
    print(json.dumps({'version': version(), 'artifacts': [str(path) for path in artifacts]}, ensure_ascii=False, indent=2))
    return 0


if __name__ == '__main__':
    main()
