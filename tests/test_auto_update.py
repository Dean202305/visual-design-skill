"""Exercise the release updater against checked archives and temporary installs."""
import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from skill_tools import skill_script, version, workbuddy_entry

updater = skill_script('update')


def release_zip(number, profile, *, legacy=False):
    skill = ROOT / 'skills' / 'visual-design'
    entry = (skill / 'SKILL.md').read_text(encoding='utf-8')
    if profile == 'workbuddy':
        entry = workbuddy_entry(entry)
    files = {'SKILL.md': entry.replace(version(), number).encode('utf-8'), 'references/example.md': number.encode()}
    if not legacy:
        files['scripts/update.py'] = (skill / 'scripts' / 'update.py').read_bytes()
        files[updater.MANIFEST] = updater.manifest_bytes(files.items(), number, profile)
    archive = io.BytesIO()
    with zipfile.ZipFile(archive, 'w') as bundle:
        for name, content in files.items():
            member = f'visual-design/{name}' if profile == 'portable' else name
            bundle.writestr(member, content)
    return archive.getvalue()


class AutoUpdateTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix='visual-design-update-tests-')
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve() / 'host' / 'skills' / 'visual-design'
        self.responses = {}
        fetch_patch = patch.object(updater, 'fetch', side_effect=self.read_response)
        self.fetch = fetch_patch.start()
        self.addCleanup(fetch_patch.stop)

    def read_response(self, url, limit, accept=None):
        value = self.responses[url]
        self.assertLessEqual(len(value), limit)
        return value

    def publish(self, number, profile, content, latest=False):
        tag = f'v{number}'
        name = f'visual-design-{profile}-{tag}.zip'
        url = f'https://github.com/{updater.REPO}/releases/download/{tag}/{name}'
        asset = {'name': name, 'browser_download_url': url, 'state': 'uploaded', 'size': len(content),
                 'digest': 'sha256:' + hashlib.sha256(content).hexdigest()}
        endpoint = 'latest' if latest else f'tags/{tag}'
        release = {'tag_name': tag, 'draft': False, 'prerelease': False, 'assets': [asset]}
        self.responses[f'{updater.RELEASES}/{endpoint}'] = json.dumps(release).encode()
        self.responses[url] = content
        return url

    def install(self, content, profile='portable'):
        for relative, content in updater.archive_files(content, profile).items():
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(content)

    def test_legacy_connects_once_then_auto_updates_and_throttles(self):
        old, first, second = '1.7.0', version(), '2.1.0'
        archive = release_zip(old, 'portable', legacy=True)
        self.install(archive)
        self.publish(old, 'portable', archive)
        self.publish(first, 'portable', release_zip(first, 'portable'), latest=True)
        self.assertEqual(updater.update(self.root)['status'], 'unmanaged')
        self.fetch.assert_not_called()
        memory = self.root.parents[2] / '.visual-design' / 'memory' / 'preferences.json'
        memory.parent.mkdir(parents=True)
        memory.write_text('private preference', encoding='utf-8')

        result = updater.update(self.root, 'now')
        self.assertEqual(result['status'], 'updated')
        self.assertEqual(updater.identity(Path(result['backup'])), (old, 'portable'))
        self.assertEqual(updater.identity(self.root), (first, 'portable'))

        self.publish(second, 'portable', release_zip(second, 'portable'), latest=True)
        self.fetch.reset_mock()
        self.assertEqual(updater.update(self.root)['status'], 'cached')
        self.fetch.assert_not_called()
        (updater.state_path(self.root) / 'last-check').unlink()
        self.assertEqual(updater.update(self.root)['status'], 'updated')
        self.assertEqual(updater.identity(self.root), (second, 'portable'))
        self.assertEqual(memory.read_text(encoding='utf-8'), 'private preference')

    def test_workbuddy_keeps_its_installed_layout_and_metadata(self):
        profile = 'workbuddy'
        self.install(release_zip(version(), profile), profile)
        self.publish('2.1.0', profile, release_zip('2.1.0', profile), latest=True)
        self.assertEqual(updater.update(self.root)['status'], 'updated')
        self.assertEqual(updater.identity(self.root), ('2.1.0', profile))
        self.assertIn('description_zh:', (self.root / 'SKILL.md').read_text(encoding='utf-8'))
        self.assertFalse((self.root / 'agents').exists())

    def test_custom_file_prevents_replacement(self):
        self.install(release_zip(version(), 'portable'))
        custom = self.root / 'references' / 'example.md'
        custom.write_text('local edit', encoding='utf-8')
        asset = self.publish('2.1.0', 'portable', release_zip('2.1.0', 'portable'), latest=True)
        self.assertEqual(updater.update(self.root)['status'], 'local_changes')
        self.assertEqual(custom.read_text(encoding='utf-8'), 'local edit')
        self.assertNotIn(asset, [call.args[0] for call in self.fetch.call_args_list])

    def test_bad_download_leaves_original_intact(self):
        self.install(release_zip(version(), 'portable'))
        archive = release_zip('2.1.0', 'portable')
        asset = self.publish('2.1.0', 'portable', archive, latest=True)
        self.responses[asset] = b'X' + archive[1:]
        with self.assertRaisesRegex(ValueError, 'SHA-256'):
            updater.update(self.root)
        self.assertEqual(updater.identity(self.root), (version(), 'portable'))

    def test_traversal_remains_outside_filesystem(self):
        self.install(release_zip(version(), 'portable'))
        archive = io.BytesIO()
        with zipfile.ZipFile(archive, 'w') as bundle:
            bundle.writestr('visual-design/../escape', 'escape')
        self.publish('2.1.0', 'portable', archive.getvalue(), latest=True)
        with self.assertRaisesRegex(ValueError, 'Unsafe path'):
            updater.update(self.root)
        self.assertEqual(updater.identity(self.root), (version(), 'portable'))

    def test_rename_failure_restores_old_directory(self):
        self.install(release_zip(version(), 'portable'))
        self.publish('2.1.0', 'portable', release_zip('2.1.0', 'portable'), latest=True)
        rename = Path.rename

        def fail_new_directory(path, target):
            if path.parent.name.startswith('stage-'):
                raise PermissionError('staged replacement blocked')
            return rename(path, target)

        with patch.object(Path, 'rename', fail_new_directory), self.assertRaises(PermissionError):
            updater.update(self.root)
        self.assertEqual(updater.identity(self.root), (version(), 'portable'))

    def test_check_only_and_disabled_dont_create_state(self):
        self.install(release_zip(version(), 'portable'))
        self.publish('2.1.0', 'portable', release_zip('2.1.0', 'portable'), latest=True)
        with patch.dict(os.environ, {'VISUAL_DESIGN_AUTO_UPDATE': '0'}):
            self.assertEqual(updater.update(self.root)['status'], 'disabled')
            self.fetch.assert_not_called()
            self.assertEqual(updater.update(self.root, 'check')['status'], 'available')
        self.assertFalse(updater.state_path(self.root).exists())

    def test_concurrent_updater_skips_the_same_installation(self):
        self.install(release_zip(version(), 'portable'))
        with updater.update_lock(updater.state_path(self.root)) as acquired:
            self.assertTrue(acquired)
            self.assertEqual(updater.update(self.root)['status'], 'busy')
        self.fetch.assert_not_called()

    @unittest.skipUnless(shutil.which('git'), 'Git unavailable')
    def test_repository_managed_dist_is_not_replaced(self):
        self.install(release_zip(version(), 'portable'))
        repo = self.root.parents[2]
        subprocess.run(['git', 'init', '-q', str(repo)], check=True, capture_output=True)
        subprocess.run(['git', '-C', str(repo), 'add', str(self.root)], check=True, capture_output=True)
        self.assertEqual(updater.update(self.root)['status'], 'git_managed')
        self.fetch.assert_not_called()


if __name__ == '__main__':
    unittest.main()
