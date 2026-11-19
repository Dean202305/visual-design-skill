"""Offline import integrity and project-preservation checks for design blueprints."""
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('blueprint_importer', ROOT / 'skills/visual-design/scripts/blueprint.py')
blueprint = importlib.util.module_from_spec(spec)
spec.loader.exec_module(blueprint)


class BlueprintTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='blueprint-tests-')
        self.root = Path(self.temporary.name)
        self.project = self.root / '现有项目 with spaces'
        self.project.mkdir()
        (self.project / 'DESIGN.md').write_text('Keep the approved system')

    def tearDown(self):
        self.temporary.cleanup()

    def test_all_blueprints_and_licenses_match_pinned_checksums(self):
        data = blueprint.catalog()
        self.assertGreater(len(data['blueprints']), 1)
        for item in data['blueprints'].values():
            self.assertTrue(blueprint.source_bytes(data, item['path']))
            self.assertIn(b'MIT License', blueprint.source_bytes(data, item['license_path']))

    def test_import_preserves_reference_license_and_project_design(self):
        result = blueprint.export('linear.app', self.project)
        target = Path(result['destination'])
        data = blueprint.catalog()
        self.assertEqual((target / 'DESIGN.md').read_bytes(), blueprint.source_bytes(data, data['blueprints']['linear.app']['path']))
        self.assertIn('MIT License', (target / 'LICENSE.md').read_text())
        self.assertIn(data['sources']['awesome-design-md']['commit'], (target / 'SOURCE.md').read_text())
        self.assertEqual((self.project / 'DESIGN.md').read_text(), 'Keep the approved system')

    def test_existing_reference_is_never_overwritten(self):
        target = Path(blueprint.export('notion', self.project)['destination'])
        (target / 'DESIGN.md').write_text('Project customisation')
        with self.assertRaises(ValueError):
            blueprint.export('notion', self.project)
        self.assertEqual((target / 'DESIGN.md').read_text(), 'Project customisation')

    def test_unknown_name_and_path_traversal_do_not_write(self):
        for name in ('missing-brand', '../escape', '/absolute', '..'):
            with self.assertRaises(ValueError):
                blueprint.export(name, self.project)
        self.assertFalse((self.project / 'design-references').exists())

    def test_missing_project_does_not_get_created(self):
        with self.assertRaises(ValueError):
            blueprint.export('stripe', self.root / 'absent')
        self.assertFalse((self.root / 'absent').exists())

    def test_dry_run_checks_integrity_without_writing(self):
        self.assertTrue(blueprint.export('stripe', self.project, dry_run=True)['dry_run'])
        self.assertFalse((self.project / 'design-references').exists())

    def test_tampered_reference_is_rejected_before_project_write(self):
        core = self.root / 'altered-core'
        shutil.copytree(blueprint.CORE, core)
        data = blueprint.catalog()
        (core / data['blueprints']['stripe']['path']).write_text('tampered')
        with patch.object(blueprint, 'CORE', core), self.assertRaisesRegex(ValueError, 'integrity'):
            blueprint.export('stripe', self.project)
        self.assertFalse((self.project / 'design-references').exists())

    def test_symlink_destination_cannot_leave_project(self):
        outside = self.root / 'outside'
        outside.mkdir()
        try:
            (self.project / 'design-references').symlink_to(outside, target_is_directory=True)
        except (OSError, NotImplementedError):
            self.skipTest('Symlinks unavailable')
        with self.assertRaises(ValueError):
            blueprint.export('stripe', self.project)
        self.assertEqual(list(outside.iterdir()), [])

    def test_cli_lists_and_imports_into_unicode_project(self):
        script = ROOT / 'skills/visual-design/scripts/blueprint.py'
        result = subprocess.run([sys.executable, str(script), 'list'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('linear.app', json.loads(result.stdout)['blueprints'])
        result = subprocess.run([sys.executable, str(script), 'import', 'linear.app', '--project', str(self.project)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((Path(json.loads(result.stdout)['destination']) / 'SOURCE.md').is_file())


if __name__ == '__main__':
    unittest.main()
