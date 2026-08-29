import importlib.util
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace


SCRIPT = Path(__file__).resolve().parents[2] / "scaffold" / "scripts" / "build_brief.py"
sys.path.insert(0, str(SCRIPT.parent))
spec = importlib.util.spec_from_file_location("build_brief", SCRIPT)
build_brief = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_brief)


def row(element, layer, element_type="Element"):
    return {
        "project": "model", "id": element, "layer_group": layer,
        "name": element, "type": element_type, "status": "validated",
        "retired": 0, "attrs": "{}", "doc": "architecture/model.md",
    }


class FocusSelectionTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.execute(
            "CREATE TABLE edges (project TEXT, src TEXT, dst_project TEXT, dst TEXT, "
            "rel TEXT, origin TEXT, pending INTEGER)"
        )
        for src, dst in [
            ("G1", "CAP1"), ("CAP1", "BSVC1"), ("BSVC1", "DOBJ1"),
            ("DOBJ1", "ACMP1"), ("ACMP1", "NODE1"), ("GAP1", "ACMP1"),
        ]:
            self.connection.execute(
                "INSERT INTO edges VALUES ('model', ?, '', ?, 'relates', 'table', 0)",
                (src, dst),
            )
        self.rows = [
            row("G1", "Motivation", "Goal"), row("CAP1", "Strategy", "Capability"),
            row("BSVC1", "Business", "Business Service"),
            row("DOBJ1", "Information", "Data Object"),
            row("ACMP1", "Application", "Application Component"),
            row("NODE1", "Technology", "Node"),
            row("GAP1", "Implementation & Migration", "Gap"),
            row("ACMP2", "Application", "Application Component"),
        ]

    def tearDown(self):
        self.connection.close()

    def ids_for(self, focus, anchor=None):
        kept, dropped = build_brief.apply_focus(self.connection, self.rows, focus, anchor)
        return {r["id"] for r in kept}, {d.split("::")[-1] for d in dropped}

    def test_business_keeps_primary_and_direct_support(self):
        kept, dropped = self.ids_for("business")
        self.assertEqual(kept, {"G1", "CAP1", "BSVC1", "DOBJ1"})
        self.assertIn("ACMP1", dropped)

    def test_information_keeps_direct_strategy_and_technology_context(self):
        kept, _ = self.ids_for("information")
        self.assertEqual(kept, {"CAP1", "BSVC1", "DOBJ1", "ACMP1", "ACMP2", "NODE1"})

    def test_solution_keeps_information_directly_connected_to_application(self):
        kept, _ = self.ids_for("solution")
        self.assertEqual(kept, {"DOBJ1", "ACMP1", "ACMP2", "NODE1"})

    def test_decision_keeps_directly_affected_solution_context(self):
        kept, _ = self.ids_for("decision")
        self.assertEqual(kept, {"G1", "CAP1", "BSVC1", "GAP1", "DOBJ1", "ACMP1"})

    def test_impact_and_legacy_calls_keep_the_full_scope(self):
        for focus in ("impact", None):
            kept, dropped = self.ids_for(focus)
            self.assertEqual(kept, {r["id"] for r in self.rows})
            self.assertEqual(dropped, set())

    def test_anchor_is_never_removed_and_can_pull_direct_support(self):
        kept, _ = self.ids_for("business", "NODE1")
        self.assertIn("NODE1", kept)
        self.assertIn("ACMP1", kept)


class BriefOutputTests(unittest.TestCase):
    def setUp(self):
        self.connection = sqlite3.connect(":memory:")
        self.connection.row_factory = sqlite3.Row
        self.connection.executescript(
            "CREATE TABLE nodes (project TEXT, id TEXT);"
            "CREATE TABLE edges (project TEXT, src TEXT, dst_project TEXT, dst TEXT, "
            "rel TEXT, origin TEXT, pending INTEGER);"
            "CREATE TABLE excerpts (project TEXT, element TEXT, heading TEXT, body TEXT, doc TEXT);"
        )
        self.connection.execute("INSERT INTO nodes VALUES ('model', 'BSVC1')")

    def tearDown(self):
        self.connection.close()

    def test_focus_metadata_and_exclusions_are_visible(self):
        args = SimpleNamespace(focus="business", depth=2, out=Path(tempfile.gettempdir()))
        body = build_brief.brief(
            self.connection, [row("BSVC1", "Business", "Business Service")],
            "`BSVC1` — Service, within 2 hop(s)", [], ["model::NODE1"], args,
        )
        self.assertIn("| **Focus** | Business and operations |", body)
        self.assertIn("| **Depth** | 2 relationship hop(s) |", body)
        self.assertIn("de-emphasized by **Business and operations**", body)

    def test_invalid_focus_is_rejected_by_the_cli(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--element", "BSVC1", "--focus", "everything"],
            capture_output=True, text=True,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("invalid choice", completed.stderr)


if __name__ == "__main__":
    unittest.main()
