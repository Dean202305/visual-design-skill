"""Shared, standard-library-only helpers for installing and packaging one skill."""
import importlib.util
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills' / 'visual-design'
NAME = 'visual-design'


def version():
    value = (ROOT / 'VERSION').read_text(encoding='utf-8').strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+', value):
        raise ValueError('VERSION must be a semantic version such as 1.1.0')
    return value


def skill_script(name):
    spec = importlib.util.spec_from_file_location('visual_design_' + name, SKILL / 'scripts' / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def check_skill(path=SKILL, profile='portable'):
    path = Path(path).resolve()
    result = skill_script('validate').validate(path, profile)
    if not result['ok']:
        raise ValueError('; '.join(result['errors']))
    updater = skill_script('update')
    expected_version = version()
    if updater.identity(path) != (expected_version, profile):
        raise ValueError('SKILL.md version or format does not match the release')
    if (path / updater.MANIFEST).is_file():
        expected_files = updater.read_manifest(path, expected_version, profile)
        if not updater.matches_tree(path, expected_files):
            raise ValueError('Packaged files do not match the release manifest')
    return result


def release_manifest(entries, profile):
    updater = skill_script('update')
    return updater.MANIFEST, updater.manifest_bytes(entries, version(), profile)


def skill_files():
    for path in sorted(SKILL.rglob('*')):
        if '__pycache__' in path.parts or path.name == '.DS_Store':
            continue
        if path.is_symlink():
            raise ValueError('Skill bundles cannot contain symlinks')
        if path.is_file():
            yield path.relative_to(SKILL), path.read_bytes()


def split_entry(text):
    match = re.fullmatch(r'---\n(.*?)\n---\n+(.*)', text, re.S)
    if not match:
        raise ValueError('SKILL.md frontmatter is malformed')
    return match[1], match[2]


def workbuddy_entry(text):
    frontmatter, body = split_entry(text)
    description_line = re.search(r'(?m)^description:\s*(.+)$', frontmatter)
    description = json.loads(description_line[1])
    fields = {
        'display_name': '视觉设计工坊',
        'display_name_en': 'Visual Design Workshop',
        'description': description,
        'description_zh': '用途驱动的多平台视觉设计：竞品研究、组件选择、实现、预览与验收。',
        'description_en': 'Design UI/UX and visual artifacts through competitive research, component selection, implementation, previews and verification.',
        'version': version(),
        'author': 'Dean202305',
    }
    lines = ['name: ' + NAME] + [key + ': ' + json.dumps(value, ensure_ascii=False) for key, value in fields.items()]
    return '---\n' + '\n'.join(lines) + '\n---\n\n' + body
