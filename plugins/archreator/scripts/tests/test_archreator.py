from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
import io
import sys
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "archreator.py"
SPEC = importlib.util.spec_from_file_location("archreator_runtime", MODULE_PATH)
assert SPEC and SPEC.loader
archreator = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = archreator
SPEC.loader.exec_module(archreator)


ELEMENTS = """# Model

**Location:** Architecture → Test model.

| ID | Name | ArchiMate type | Description |
| --- | --- | --- | --- |
| BPROC1 | Take an order | Business Process | Accepts a customer's order. |
| ACMP1 | Order service | Application Component | Supports order handling. |
| DOBJ1 | Order | Data Object | Represents the order in the application. |

| From | Relationship | To | Meaning |
| --- | --- | --- | --- |
| **Take an order** [BPROC1] | Association | [Order service](https://example.test/service) [`ACMP1`] | Order handling uses the service. |
| Order service [ACMP1] | Access | Order [DOBJ1] | The service stores orders. |
"""


class RepositoryCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        (self.root / "architecture").mkdir()

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, relative: str, content: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path


class ModelTests(RepositoryCase):
    def test_parses_id_first_catalogue_name_and_type(self):
        self.write("architecture/model.md", ELEMENTS)
        model = archreator.load_model(self.root)

        self.assertEqual("Order service", model.elements["ACMP1"].name)
        self.assertEqual("Application Component", model.elements["ACMP1"].kind)
        self.assertNotIn("STALE_REFERENCE_NAME", {issue.code for issue in model.issues})

    def test_rejects_a_noncanonical_element_column_order(self):
        self.write(
            "architecture/model.md",
            """# Model

**Location:** Architecture → Test model.

| Name | ArchiMate type | Description | ID |
| --- | --- | --- | --- |
| Waste collection | Business Service | Schedules collection. | BSVC2 |
""",
        )
        model = archreator.load_model(self.root)

        self.assertNotIn("BSVC2", model.elements)
        self.assertIn("INVALID_ELEMENT_TABLE", {issue.code for issue in model.issues})

    def test_reads_source_fresh_after_an_edit(self):
        source = self.write("architecture/model.md", ELEMENTS)
        first = archreator.load_model(self.root)
        self.assertIn("DOBJ1", first.elements)

        source.write_text(ELEMENTS.replace("DOBJ1", "DOBJ2"), encoding="utf-8")
        second = archreator.load_model(self.root)
        self.assertNotIn("DOBJ1", second.elements)
        self.assertIn("DOBJ2", second.elements)
        self.assertEqual("DOBJ2", second.relationships[-1].target)

    def test_preserves_underscores_in_ids(self):
        self.write(
            "architecture/model.md",
            """# Model

**Location:** Architecture → Test model.

| ID | Name | ArchiMate type | Description |
| --- | --- | --- | --- |
| APP_CORE1 | Core service | Application Component | Provides shared behavior. |
""",
        )
        self.assertIn("APP_CORE1", archreator.load_model(self.root).elements)

    def test_nested_element_parent_declares_a_traversable_composition(self):
        self.write(
            "architecture/capabilities.md",
            """# Capabilities — Levels 1 and 2

**Location:** Architecture → Strategy → Capabilities.

| ID | Name | ArchiMate type | Description | Parent |
| --- | --- | --- | --- | --- |
| CAP1 | Commerce | Capability | Enables commercial outcomes. | — |
| CAP1.1 | Order fulfilment | Capability | Enables an accepted order to be fulfilled. | [Commerce](strategy.md#commerce-cap1) [CAP1] |
""",
        )
        self.write(
            "architecture/strategy.md",
            "# Strategy\n\n**Location:** Architecture → Strategy.\n\n## Commerce [CAP1]\n",
        )

        model = archreator.load_model(self.root)

        self.assertNotIn(
            "MISSING_PARENT_REFERENCE", {issue.code for issue in model.issues}
        )
        parent = archreator.trace(model, "CAP1.1", "reverse", 1)
        child = archreator.trace(model, "CAP1", "forward", 1)
        self.assertEqual(["CAP1"], [step.element.id for step in parent])
        self.assertEqual(["CAP1.1"], [step.element.id for step in child])
        self.assertEqual("Composition", child[0].relationship.kind)

    def test_nested_elements_require_a_matching_human_readable_parent(self):
        self.write(
            "architecture/capabilities.md",
            """# Capabilities — Level 2

**Location:** Architecture → Strategy → Capabilities → Level 2.

| ID | Name | ArchiMate type | Description |
| --- | --- | --- | --- |
| CAP1.1 | Order fulfilment | Capability | Enables an order to be fulfilled. |

| ID | Name | ArchiMate type | Description | Parent |
| --- | --- | --- | --- | --- |
| CAP2.1 | Payment assurance | Capability | Enables payment to be assured. | Commerce [CAP9] |
""",
        )

        codes = {issue.code for issue in archreator.load_model(self.root).issues}
        self.assertIn("MISSING_PARENT_REFERENCE", codes)
        self.assertIn("PARENT_ID_MISMATCH", codes)

    def test_every_non_root_canonical_file_needs_title_and_location(self):
        self.write("architecture/README.md", "# Architecture\n")
        self.write("architecture/orphan.md", "No title or orientation.\n")

        codes = {issue.code for issue in archreator.load_model(self.root).issues}
        self.assertIn("MISSING_TITLE", codes)
        self.assertIn("MISSING_LOCATION", codes)

    def test_traces_inbound_outbound_and_transitive_impact(self):
        self.write("architecture/model.md", ELEMENTS)
        model = archreator.load_model(self.root)

        forward = archreator.trace(model, "ACMP1", "forward", 1)
        reverse = archreator.trace(model, "ACMP1", "reverse", 1)
        both = archreator.trace(model, "ACMP1", "both", 1)
        transitive = archreator.trace(model, "BPROC1", "forward", 2)

        self.assertEqual(["DOBJ1"], [step.element.id for step in forward])
        self.assertEqual(["BPROC1"], [step.element.id for step in reverse])
        self.assertEqual({"BPROC1", "DOBJ1"}, {step.element.id for step in both})
        self.assertEqual(["ACMP1", "DOBJ1"], [step.element.id for step in transitive])
        self.assertEqual("Take an order", model.relationships[0].source_name)
        self.assertEqual("Order service", model.relationships[0].target_name)

    def test_bare_relationship_ids_are_not_document_references(self):
        self.write(
            "architecture/model.md",
            """# Model

**Location:** Architecture → Test model.

| ID | Name | ArchiMate type | Description |
| --- | --- | --- | --- |
| BPROC1 | Take an order | Business Process | Accepts an order. |
| ACMP1 | Order service | Application Component | Handles it. |

| From | Relationship | To | Meaning |
| --- | --- | --- | --- |
| BPROC1 | Association | ACMP1 | The process uses the service. |
""",
        )
        model = archreator.load_model(self.root)

        self.assertEqual((), model.relationships)
        self.assertIn("INVALID_RELATIONSHIP", {issue.code for issue in model.issues})

    def test_malformed_or_missing_trailing_endpoint_ids_fail(self):
        self.write(
            "architecture/model.md",
            """# Model

**Location:** Architecture → Test model.

| ID | Name | ArchiMate type | Description |
| --- | --- | --- | --- |
| ACMP1 | Order service | Application Component | Handles orders. |
| DOBJ1 | Order | Data Object | An order. |

| From | Relationship | To | Meaning |
| --- | --- | --- | --- |
| Order service | Access | Order [DOBJ1] | Missing source ID. |
| Order service [ACMP1 | Access | Order [DOBJ1] | Unclosed source ID. |
| Order service [ACMP1] extra | Access | Order [DOBJ1] | ID is not trailing. |
| [Order service](https://example.test/#ACMP1) | Access | Order [DOBJ1] | Link destination is not an ID. |
""",
        )
        model = archreator.load_model(self.root)

        self.assertEqual((), model.relationships)
        self.assertEqual(4, sum(issue.code == "INVALID_RELATIONSHIP" for issue in model.issues))

    def test_stale_decorated_name_is_reported_after_a_rename(self):
        self.write(
            "architecture/model.md",
            """# Model

**Location:** Architecture → Test model.

| ID | Name | ArchiMate type | Description |
| --- | --- | --- | --- |
| ACMP1 | Renamed order service | Application Component | Handles orders. |
| DOBJ1 | Order | Data Object | An order. |

| From | Relationship | To | Meaning |
| --- | --- | --- | --- |
| Order service [ACMP1] | Access | Order [DOBJ1] | The service stores orders. |
""",
        )
        model = archreator.load_model(self.root)

        stale = [issue for issue in model.issues if issue.code == "STALE_REFERENCE_NAME"]
        self.assertEqual(1, len(stale))
        self.assertIn("Order service", stale[0].message)
        self.assertIn("Renamed order service", stale[0].message)

    def test_cli_trace_renders_name_and_id_as_one_reference(self):
        self.write("architecture/model.md", ELEMENTS)
        output = io.StringIO()

        with redirect_stdout(output):
            result = archreator.main(
                ["--repo", str(self.root), "trace", "ACMP1", "--direction", "forward"]
            )

        rendered = output.getvalue()
        self.assertEqual(0, result)
        self.assertIn("trace from Order service [ACMP1]", rendered)
        self.assertIn("| Element | Source |", rendered)
        self.assertIn("| Order [DOBJ1] |", rendered)

    def test_reports_duplicate_and_unresolved_ids(self):
        self.write("architecture/a.md", ELEMENTS)
        self.write(
            "architecture/b.md",
            """# Duplicate model

**Location:** Architecture → Duplicate model.

| ID | Name | ArchiMate type | Description |
| --- | --- | --- | --- |
| ACMP1 | Duplicate service | Application Component | Duplicates the service. |

| From | To | Relationship |
| --- | --- | --- |
| Order service [ACMP1] | Missing service [MISSING9] | Serving |
""",
        )
        model = archreator.load_model(self.root)
        codes = [issue.code for issue in model.issues]
        self.assertIn("DUPLICATE_ID", codes)
        self.assertIn("UNRESOLVED_ID", codes)

    def test_checks_relative_paths_and_anchors(self):
        self.write(
            "architecture/target.md",
            "# Existing heading\n\n**Location:** Architecture → Existing heading.\n",
        )
        self.write(
            "architecture/model.md",
            "# Links\n\n**Location:** Architecture → Links.\n\n"
            "[valid](target.md#existing-heading) [missing](absent.md) [anchor](target.md#absent)\n",
        )
        issues = archreator.load_model(self.root).issues
        self.assertEqual({"BROKEN_LINK", "BROKEN_ANCHOR"}, {issue.code for issue in issues})


class WorkTests(RepositoryCase):
    def test_creates_a_named_ignored_work_directory(self):
        first = archreator.ensure_work_directory(self.root, "impact-app1")
        second = archreator.ensure_work_directory(self.root, "decision-data1")

        self.assertEqual(self.root / ".archreator" / "work" / "impact-app1", first)
        self.assertTrue(first.is_dir())
        self.assertTrue(second.is_dir())
        ignore = (self.root / ".gitignore").read_text(encoding="utf-8")
        self.assertEqual(1, ignore.count("/.archreator/work/"))

    def test_rejects_a_path_as_a_run_name(self):
        with self.assertRaises(archreator.ArChreatorError):
            archreator.ensure_work_directory(self.root, "../outside")

    def test_pdf_refuses_model_source(self):
        source = self.write("architecture/model.md", ELEMENTS)
        with self.assertRaisesRegex(archreator.ArChreatorError, "must be inside"):
            archreator.export_pdf(self.root, source, kind="brief")

    def test_exports_one_work_scope_when_reportlab_is_available(self):
        try:
            import reportlab  # noqa: F401
        except ModuleNotFoundError:
            self.skipTest("ReportLab is optional")

        work = archreator.ensure_work_directory(self.root, "scope-checkout")
        source = work / "scope.md"
        source.write_text(
            """# Checkout change

This scope changes the checkout service only.

## Affected elements

| ID | Effect |
| --- | --- |
| ACMP1 | Update validation |

- Confirm the owner.
- Keep DOBJ1 unchanged.
""",
            encoding="utf-8",
        )
        output = archreator.export_pdf(self.root, source, kind="scope")

        self.assertEqual(source.with_suffix(".pdf"), output)
        self.assertGreater(output.stat().st_size, 1_000)
        self.assertEqual(b"%PDF", output.read_bytes()[:4])

    def test_builds_the_portal_only_when_requested(self):
        self.write(
            "architecture/README.md",
            "# Checkout architecture\n\nThe checkout service accepts customer orders.\n",
        )
        output = archreator.build_portal_output(self.root)

        self.assertEqual(self.root / ".archreator" / "work" / "portal" / "index.html", output)
        self.assertTrue(output.is_file())
        ignore = (self.root / ".gitignore").read_text(encoding="utf-8")
        self.assertIn("/.archreator/work/", ignore)


if __name__ == "__main__":
    unittest.main()
