import contextlib
import copy
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('design_audit', ROOT / 'skills/visual-design/scripts/design_audit.py')
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


def snapshot():
    return {'schema_version': 1, 'captured_at': '2026-11-19T00:00:00Z',
            'viewport': {'width': 390, 'height': 844}, 'horizontal_overflow': 0,
            'document': {'ready_state': 'complete', 'fonts_status': 'loaded'},
            'text': [{'path': 'p', 'font_size': 12, 'sample': 'actual content'}],
            'images': [], 'coverage': {'text_nodes': 1, 'images': 0, 'iframes': 0, 'shadow_hosts': 0}}


class DesignAuditTests(unittest.TestCase):
    def test_broken_and_pending_images_are_different(self):
        data = snapshot()
        data['images'] = [{'path': 'img', 'status': 'broken'}, {'path': 'img', 'status': 'pending'}]
        result = AUDIT.check(data)
        self.assertEqual([x['kind'] for x in result['failures']], ['broken_image'])
        self.assertEqual([x['kind'] for x in result['review']], ['pending_image'])

    def test_no_failure_does_not_imply_visual_or_accessibility_pass(self):
        result = AUDIT.check(snapshot())
        self.assertEqual(result['status'], 'needs_review')
        self.assertFalse(result['failures'])
        self.assertIn('contrast_and_actual_font_glyphs', result['unverified'])
        self.assertIn('keyboard_touch_focus_and_business_states', result['unverified'])

    def test_overflow_and_small_text_are_project_review_not_automatic_failure(self):
        data = snapshot()
        data['horizontal_overflow'] = 20
        self.assertEqual([x['kind'] for x in AUDIT.check(data)['review']], ['horizontal_overflow'])
        result = AUDIT.check(data, 14)
        self.assertEqual(len(result['review']), 2)
        self.assertFalse(result['failures'])

    def test_loading_and_unsupported_content_remain_visible_gaps(self):
        data = snapshot()
        data['document'] = {'ready_state': 'interactive', 'fonts_status': 'loading'}
        data['text'] = []
        data['coverage']['iframes'] = 1
        data['coverage']['shadow_hosts'] = 1
        kinds = [x['kind'] for x in AUDIT.check(data)['review']]
        self.assertIn('document_not_complete', kinds)
        self.assertIn('fonts_not_settled', kinds)
        self.assertIn('no_supported_content', kinds)
        self.assertEqual(kinds.count('outside_collector_scope'), 2)

    def test_malformed_or_incomplete_evidence_is_rejected(self):
        cases = [None, {}, {'schema_version': True}]
        for key, value in [('viewport', {'width': 0, 'height': 20}), ('horizontal_overflow', float('nan')),
                           ('text', [{'font_size': True}]), ('images', [{'status': 'maybe'}]),
                           ('document', {}), ('coverage', {}), ('captured_at', '')]:
            data = snapshot()
            data[key] = value
            cases.append(data)
        for data in cases:
            with self.subTest(data=data), self.assertRaises(AUDIT.EvidenceError):
                AUDIT.check(data)

    def test_invalid_project_threshold_is_not_silently_used(self):
        for value in [0, -2, float('inf'), float('nan'), True]:
            with self.subTest(value=value), self.assertRaises(AUDIT.EvidenceError):
                AUDIT.check(snapshot(), value)

    def test_cli_status_missing_invalid_broken_and_measurable(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / 'evidence.json'
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(AUDIT.main(['check', str(path)]), 2)
                path.write_text('{', encoding='utf-8')
                self.assertEqual(AUDIT.main(['check', str(path)]), 2)
                data = snapshot()
                path.write_text(json.dumps(data), encoding='utf-8')
                self.assertEqual(AUDIT.main(['check', str(path)]), 0)
                data['images'] = [{'status': 'broken'}]
                path.write_text(json.dumps(data), encoding='utf-8')
                self.assertEqual(AUDIT.main(['check', str(path)]), 1)

    def test_analysis_does_not_change_source_evidence(self):
        data = snapshot()
        before = copy.deepcopy(data)
        AUDIT.check(data, 14)
        self.assertEqual(before, data)


if __name__ == '__main__':
    unittest.main()
