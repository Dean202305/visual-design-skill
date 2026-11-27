import importlib.util
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills/visual-design/scripts/design_memory.py"
SPEC = importlib.util.spec_from_file_location("design_memory", SCRIPT)
memory = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(memory)


class DesignMemoryTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.folder = Path(self.temporary.name) / "memory"

    def write_preference(self, identifier, scope, context, value):
        return memory.record(self.folder, {
            "id": identifier,
            "preferences": [{
                "scope": scope,
                "context": context,
                "key": "accent",
                "value": value,
                "evidence": "User confirmed the applicable scope.",
            }],
        })

    def read(self, project=None, medium=None, artifact=None):
        return memory.recall(self.folder, project, medium, artifact, 5)

    def test_recall_resolves_scope_and_preserves_unrelated_preferences(self):
        self.write_preference("common", "global", "", "ink")
        self.write_preference("slide", "medium", "slides", "navy")
        self.write_preference("project", "project", "Alpha", "gold")
        self.assertEqual(self.read("Alpha", "slides")["preferences"][0]["value"], "gold")
        self.assertEqual(self.read("Bravo", "slides")["preferences"][0]["value"], "navy")
        self.assertEqual(self.read("Bravo", "web")["preferences"][0]["value"], "ink")
        self.write_preference("project-retracted", "project", "Alpha", None)
        self.assertEqual(self.read("Alpha", "slides")["preferences"][0]["value"], "navy")

    def test_idempotent_record_has_no_effect_on_newer_choice(self):
        self.assertTrue(self.write_preference("one", "global", "", "ink")["recorded"])
        self.assertTrue(self.read()["enabled"])
        self.write_preference("two", "global", "", "navy")
        self.assertFalse(self.write_preference("one", "global", "", "ink")["recorded"])
        self.assertEqual(self.read()["preferences"][0]["value"], "navy")
        with self.assertRaises(ValueError):
            self.write_preference("one", "global", "", "gold")

    def test_recall_only_uses_latest_status_for_matching_artifact(self):
        revision = {
            "id": "navigation-02",
            "project": "Alpha",
            "artifact": "Navigation",
            "medium": "web",
            "feedback": "Use a left-hand panel.",
            "change": "Repositioned the panel.",
            "status": "applied",
        }
        memory.record(self.folder, {"id": "draft", "revision": revision})
        memory.record(self.folder, {"id": "confirmed", "revision": dict(revision, status="accepted")})
        rows = self.read("Alpha", "web", "Navigation")["recent_revisions"]
        self.assertEqual([(row["status"], row["event_id"]) for row in rows], [("accepted", "confirmed")])
        self.assertEqual(self.read("Bravo", "web")["recent_revisions"], [])
        history = list(memory.revisions(memory.events(self.folder), "Alpha", "web", None))
        self.assertEqual([row["status"] for row in history], ["accepted", "applied"])

    def test_ppt_refs_are_local_and_only_returned_for_slides(self):
        self.assertFalse(self.read(medium="slides")["enabled"])
        self.assertNotIn("ppt_references", self.read(medium="slides"))
        self.assertFalse(self.folder.exists())
        self.folder.mkdir()
        index = self.folder / memory.PPT_REFERENCES
        index.write_text("Private reference", encoding="utf-8")
        self.assertNotIn("ppt_references", self.read(medium="web"))
        self.assertEqual(self.read(medium="slides")["ppt_references"], str(index))


if __name__ == "__main__":
    unittest.main()
