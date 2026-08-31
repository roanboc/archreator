import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace


SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "build_brief.py"
# The tool imports the parse from the project it is pointed at; for a unit test
# of the focus rules there is no project, so the scaffold's copy stands in.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scaffold" / "scripts"))
sys.path.insert(0, str(SCRIPT.parent))
sys.argv = [sys.argv[0], "--project", str(Path(__file__).resolve().parents[2] / "scaffold")]
spec = importlib.util.spec_from_file_location("build_brief", SCRIPT)
build_brief = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build_brief)


def row(element, layer, element_type="Element"):
    return {
        "project": "model", "id": element, "layer_group": layer,
        "name": element, "type": element_type, "status": "validated",
        "retired": 0, "attrs": {}, "doc": "architecture/model.md",
    }


class FocusSelectionTests(unittest.TestCase):
    def setUp(self):
        # A Store built by hand rather than parsed: these test the focus rules,
        # not the parse.
        self.store = SimpleNamespace(edges=[
            {"s": f"model::{src}", "d": f"model::{dst}",
             "rel": "relates", "origin": "table", "pending": False}
            for src, dst in [
                ("G1", "CAP1"), ("CAP1", "BSVC1"), ("BSVC1", "DOBJ1"),
                ("DOBJ1", "ACMP1"), ("ACMP1", "NODE1"), ("GAP1", "ACMP1"),
            ]
        ])
        self.rows = [
            row("G1", "Motivation", "Goal"), row("CAP1", "Strategy", "Capability"),
            row("BSVC1", "Business", "Business Service"),
            row("DOBJ1", "Information", "Data Object"),
            row("ACMP1", "Application", "Application Component"),
            row("NODE1", "Technology", "Node"),
            row("GAP1", "Implementation & Migration", "Gap"),
            row("ACMP2", "Application", "Application Component"),
        ]

    def ids_for(self, focus, anchor=None):
        kept, dropped = build_brief.apply_focus(self.store, self.rows, focus, anchor)
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
        self.store = SimpleNamespace(
            nodes=[{"project": "model", "id": "BSVC1"}],
            edges=[],
            excerpts_for=lambda project, element: [],
        )

    def test_focus_metadata_and_exclusions_are_visible(self):
        args = SimpleNamespace(focus="business", depth=2)
        body = build_brief.brief(
            self.store, [row("BSVC1", "Business", "Business Service")],
            "`BSVC1` — Service, within 2 hop(s)", [], ["model::NODE1"], args,
        )
        self.assertIn("| **Focus** | Business and operations |", body)
        self.assertIn("| **Depth** | 2 relationship hop(s) |", body)
        self.assertIn("de-emphasized by **Business and operations**", body)

    def test_invalid_focus_is_rejected_by_the_cli(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--project",
             str(Path(__file__).resolve().parents[2] / "scaffold"),
             "--element", "BSVC1", "--focus", "everything"],
            capture_output=True, text=True,
        )
        self.assertEqual(completed.returncode, 2)
        self.assertIn("invalid choice", completed.stderr)


if __name__ == "__main__":
    unittest.main()
