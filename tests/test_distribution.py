"""Meaningful distribution checks; all writes stay in temporary directories."""
import importlib.util
import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import install
import skill_tools

spec = importlib.util.spec_from_file_location('bundle_builder', ROOT / 'scripts/package.py')
package = importlib.util.module_from_spec(spec)
spec.loader.exec_module(package)


class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='visual-design-tests-')
        self.root = Path(self.temporary.name)
        self.project = self.root / '示例项目 with spaces'
        self.project.mkdir()

    def tearDown(self):
        self.temporary.cleanup()

    def test_project_installs_share_identical_workflow(self):
        expected = (skill_tools.SKILL / 'SKILL.md').read_bytes()
        for agent, directory in [('codex', '.agents'), ('claude-code', '.claude')]:
            target = install.destination(agent, 'project', project=self.project)
            self.assertEqual(target, self.project / directory / 'skills/visual-design')
            install.install(target)
            self.assertEqual((target / 'SKILL.md').read_bytes(), expected)
            self.assertTrue(skill_tools.check_skill(target)['ok'])

    def test_user_paths_are_documented_and_do_not_touch_actual_home(self):
        self.assertEqual(install.destination('codex', 'user', home=self.root), self.root / '.agents/skills/visual-design')
        self.assertEqual(install.destination('claude-code', 'user', home=self.root), self.root / '.claude/skills/visual-design')

    def test_generic_destination_is_explicit(self):
        with self.assertRaises(ValueError):
            install.destination('generic', 'user')
        target = install.destination('generic', 'directory', dest=self.root / 'custom/visual-design')
        install.install(target)
        self.assertTrue(skill_tools.check_skill(target)['ok'])

    def test_existing_installation_is_never_overwritten(self):
        target = self.root / 'existing'
        target.mkdir()
        marker = target / 'private-contents'
        marker.write_text('keep this installation')
        with self.assertRaises(ValueError):
            install.install(target)
        self.assertEqual(marker.read_text(), 'keep this installation')

    def test_existing_broken_symlink_is_preserved(self):
        target = self.root / 'existing-link'
        try:
            target.symlink_to(self.root / 'missing')
        except (OSError, NotImplementedError):
            self.skipTest('Symlink creation unavailable')
        with self.assertRaises(ValueError):
            install.install(target)
        self.assertTrue(target.is_symlink())

    def test_dry_run_does_not_create_directories(self):
        target = self.root / 'missing/skills/visual-design'
        self.assertTrue(install.install(target, dry_run=True)['dry_run'])
        self.assertFalse(target.parent.exists())

    def test_install_rejects_source_descendants(self):
        with self.assertRaises(ValueError):
            install.install(skill_tools.SKILL / 'never-create')
        self.assertFalse((skill_tools.SKILL / 'never-create').exists())

    def test_every_reference_and_asset_is_copied_unchanged(self):
        target = self.root / 'installed/visual-design'
        install.install(target)
        for relative, content in skill_tools.skill_files():
            self.assertEqual((target / relative).read_bytes(), content, str(relative))

    def test_packages_are_reproducible(self):
        first = package.build(self.root / 'first')
        second = package.build(self.root / 'second')
        self.assertEqual([p.read_bytes() for p in first], [p.read_bytes() for p in second])
        self.assertEqual((first[0].parent / 'SHA256SUMS').read_text(), (second[0].parent / 'SHA256SUMS').read_text())

    def test_portable_zip_has_one_skill_folder(self):
        archive = package.build(self.root / 'bundles', ('portable',))[0]
        with zipfile.ZipFile(archive) as bundle:
            self.assertIn('visual-design/SKILL.md', bundle.namelist())
            self.assertTrue(all(name.startswith('visual-design/') for name in bundle.namelist()))
            bundle.extractall(self.root / 'unpacked')
        self.assertTrue(skill_tools.check_skill(self.root / 'unpacked/visual-design')['ok'])

    def test_workbuddy_zip_has_root_entry_and_required_metadata(self):
        archive = package.build(self.root / 'bundles', ('workbuddy',))[0]
        with zipfile.ZipFile(archive) as bundle:
            self.assertIn('SKILL.md', bundle.namelist())
            self.assertFalse(any(name.startswith('agents/') for name in bundle.namelist()))
            generated = bundle.read('SKILL.md').decode('utf-8')
            frontmatter, body = skill_tools.split_entry(generated)
            for key in ['description_zh', 'description_en', 'version', 'author']:
                self.assertIn('\n' + key + ':', '\n' + frontmatter)
            original_body = skill_tools.split_entry((skill_tools.SKILL / 'SKILL.md').read_text(encoding='utf-8'))[1]
            self.assertEqual(body, original_body)
            target = self.root / 'workbuddy/visual-design'
            bundle.extractall(target)
        self.assertTrue(skill_tools.check_skill(target, 'workbuddy')['ok'])

    def test_workbuddy_extensions_are_not_in_standard_entry(self):
        source = (skill_tools.SKILL / 'SKILL.md').read_text(encoding='utf-8')
        frontmatter, _ = skill_tools.split_entry(source)
        self.assertNotIn('\ndescription_zh:', '\n' + frontmatter)
        self.assertTrue(skill_tools.check_skill()['ok'])

    def test_project_must_exist(self):
        with self.assertRaises(ValueError):
            install.destination('codex', 'project', project=self.root / 'missing')

    def test_cli_install_works_with_unicode_and_spaces(self):
        result = subprocess.run([sys.executable, str(ROOT / 'scripts/install.py'), '--agent', 'claude-code', '--project', str(self.project)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.project / '.claude/skills/visual-design/SKILL.md').is_file())


if __name__ == '__main__':
    unittest.main()
