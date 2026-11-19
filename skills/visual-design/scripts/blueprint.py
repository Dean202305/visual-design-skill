#!/usr/bin/env python3
"""List or import a pinned, licensed design blueprint offline; never overwrite."""
import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

CORE = Path(__file__).resolve().parents[1] / 'resources/design-core'


def catalog():
    data = json.loads((CORE / 'catalog.json').read_text(encoding='utf-8'))
    if data.get('schema') != 1:
        raise ValueError('Unsupported design core catalog')
    return data


def source_bytes(data, relative):
    path = CORE / relative
    if not path.resolve().is_relative_to(CORE.resolve()) or path.is_symlink():
        raise ValueError('Source must stay inside the design core')
    expected = data['files'][relative]
    content = path.read_bytes()
    if len(content) != expected['bytes'] or hashlib.sha256(content).hexdigest() != expected['sha256']:
        raise ValueError('Source integrity check failed: ' + relative)
    return content


def export(slug, project, dry_run=False):
    data = catalog()
    if slug not in data['blueprints']:
        raise ValueError('Unknown blueprint; use list to see available names')
    base = Path(project).expanduser().resolve()
    if not base.is_dir():
        raise ValueError('Project directory does not exist')
    target = base / 'design-references' / slug
    if not target.resolve().is_relative_to(base) or os.path.lexists(target):
        raise ValueError('Destination exists or leaves the project; nothing was overwritten')
    item = data['blueprints'][slug]
    design = source_bytes(data, item['path'])
    license_text = source_bytes(data, item['license_path'])
    source = data['sources']['awesome-design-md']
    origin = data['files'][item['path']]
    url = 'https://github.com/' + source['repository'] + '/blob/' + source['commit'] + '/' + origin['upstream_path']
    notice = ('# Blueprint source\n\nCommunity design analysis, not an official brand specification.\n\n'
              + '- Source: ' + url + '\n- License: MIT; see LICENSE.md.\n'
              + '- Original SHA256: ' + origin['sha256'] + '\n\n'
              + 'Keep the original as reference. Adapt selected rules into the project design system; '
              + 'brand assets and fonts require their own permissions.\n')
    if not dry_run:
        target.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='.blueprint-stage-', dir=target.parent) as temporary:
            staged = Path(temporary) / slug
            staged.mkdir()
            (staged / 'DESIGN.md').write_bytes(design)
            (staged / 'LICENSE.md').write_bytes(license_text)
            (staged / 'SOURCE.md').write_text(notice, encoding='utf-8')
            if os.path.lexists(target):
                raise ValueError('Destination appeared during import; nothing was overwritten')
            staged.rename(target)
    return {'blueprint': slug, 'destination': str(target), 'source': url, 'dry_run': dry_run}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('list')
    importer = commands.add_parser('import')
    importer.add_argument('name')
    importer.add_argument('--project', type=Path, required=True)
    importer.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        if args.command == 'list':
            result = {'blueprints': sorted(catalog()['blueprints'])}
        else:
            result = export(args.name, args.project, args.dry_run)
    except (OSError, ValueError, KeyError) as error:
        parser.exit(1, 'Blueprint operation failed: ' + str(error) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
