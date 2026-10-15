#!/usr/bin/env python3
"""Install the portable skill into a documented host directory; never overwrite."""
import argparse
import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from skill_tools import NAME, SKILL, check_skill


HOST_DIRS = {'codex': '.agents', 'claude-code': '.claude'}


def destination(agent, scope, project=None, dest=None, home=None):
    if dest is not None:
        if scope != 'directory':
            raise ValueError('--dest requires --scope directory')
        return Path(dest).expanduser().absolute()
    if agent == 'generic' or scope == 'directory':
        raise ValueError('Generic hosts require --scope directory --dest <full skill directory>')
    if agent not in HOST_DIRS:
        raise ValueError('Unknown agent')
    if scope == 'project':
        if project is None:
            raise ValueError('Project installation requires --project <project directory>')
        base = Path(project).expanduser().absolute()
        if not base.is_dir():
            raise ValueError('Project directory does not exist')
    else:
        base = Path(home) if home is not None else Path.home()
    return base / HOST_DIRS[agent] / 'skills' / NAME


def install(target, dry_run=False):
    check_skill()
    target = Path(target)
    if os.path.lexists(target):
        raise ValueError('Destination already exists; nothing was overwritten. Back up and move it before installing: ' + str(target))
    if target.resolve().is_relative_to(SKILL.resolve()):
        raise ValueError('Destination cannot be inside the source skill')
    result = {'skill': NAME, 'destination': str(target), 'dry_run': dry_run}
    if dry_run:
        return result
    target.parent.mkdir(parents=True, exist_ok=True)
    # Stage outside the scanned skills directory, then move the complete folder.
    with tempfile.TemporaryDirectory(prefix='.visual-design-stage-', dir=target.parent.parent) as temporary:
        staged = Path(temporary) / NAME
        shutil.copytree(SKILL, staged, ignore=shutil.ignore_patterns('__pycache__', '*.pyc', '.DS_Store'))
        check_skill(staged)
        if os.path.lexists(target):
            raise ValueError('Destination appeared during installation; nothing was overwritten')
        staged.rename(target)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--agent', choices=['codex', 'claude-code', 'generic'], required=True)
    parser.add_argument('--scope', choices=['project', 'user', 'directory'], default='project')
    parser.add_argument('--project', type=Path)
    parser.add_argument('--dest', type=Path, help='Complete destination skill directory, not its parent')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    try:
        if args.scope != 'project' and args.project is not None:
            raise ValueError('--project is only valid with --scope project')
        target = destination(args.agent, args.scope, args.project, args.dest)
        result = install(target, args.dry_run)
    except (OSError, ValueError) as error:
        parser.exit(1, 'Install failed: ' + str(error) + '\n')
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if not args.dry_run:
        print('Installed. Let the host reload its skills or start a new session.')
    return 0


if __name__ == '__main__':
    sys.exit(main())
