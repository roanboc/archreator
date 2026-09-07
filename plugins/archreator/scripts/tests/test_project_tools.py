"""The reading tools run from the plugin and read a project.

These prove the thing no other check covers: that what `establish-project`
emits is a working project on its own, and that a tool run from the plugin
finds it, reads it, and refuses a directory that is not one.

The probe is built from the shipped scaffold rather than from a fixture, so a
change to the scaffold that breaks a new project fails here rather than in
somebody's first commit.
"""
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[2]
SCAFFOLD = PLUGIN / "scaffold"
MODEL = PLUGIN / "scripts" / "model.py"
BRIEF = PLUGIN / "scripts" / "build_brief.py"

BUSINESS = """\
# Business layer — Probe

_A probe, not a model._

ArchiMate Business layer.

**Status:** ◐ Draft catalogue — a probe, not yet validated.

## How to read this document

```mermaid
flowchart LR
  %% legend
  bsvc(["⚙ «Business Service» what the business offers [BSVC#]"]):::business
  classDef business fill:#fffbb5,stroke:#b8a200,color:#333
```

## Business services

| ID | Business service | Realized by |
| -- | ---------------- | ----------- |
| `BSVC1` | Answer an enquiry | `ACMP1` |
"""

APPLICATION = """\
# Application layer — Probe

_A probe, not a model._

ArchiMate Application layer.

**Status:** ◐ Draft catalogue — a probe, not yet validated.

## How to read this document

```mermaid
flowchart LR
  %% legend
  acmp["▭ «Application Component» a piece of software [ACMP#]"]:::application
  classDef application fill:#c2f0ff,stroke:#0288d1,color:#333
```

## Application components

| ID | Application component | Realizes |
| -- | --------------------- | -------- |
| `ACMP1` | Enquiry inbox | `BSVC1` |
"""


def run(*command, cwd=None):
    return subprocess.run(
        [sys.executable, *[str(c) for c in command]],
        capture_output=True, text=True, cwd=cwd,
    )


class ProjectToolTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.probe = Path(cls._tmp.name) / "probe"
        shutil.copytree(
            SCAFFOLD, cls.probe,
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        for layer, body in (("2_business", BUSINESS), ("4_application", APPLICATION)):
            folder = cls.probe / "architecture" / layer
            folder.mkdir(parents=True, exist_ok=True)
            (folder / "README.md").write_text(body, encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_the_scaffold_validates_itself_with_no_plugin(self):
        """A project checks itself with nothing but Python — no network, no plugin."""
        for validator in ("check_links.py", "check_model.py"):
            result = run(self.probe / "scripts" / validator, cwd=self.probe)
            self.assertEqual(result.returncode, 0, f"{validator}: {result.stdout}{result.stderr}")

    def test_the_scaffold_is_small(self):
        """The first commit is about the project, not about archreator.

        It was 44 files once. The number is asserted loosely because the point
        is the order of magnitude, not the exact count - but a change that
        doubles it should have to say so here.
        """
        files = [p for p in SCAFFOLD.rglob("*") if p.is_file() and "__pycache__" not in p.parts]
        self.assertLess(len(files), 15, f"the scaffold has grown: {sorted(str(f) for f in files)}")

    def test_coverage_reads_a_project_from_the_plugin(self):
        result = run(MODEL, "--project", self.probe, "coverage")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2 live element(s)", result.stdout)

    def test_health_counts_grants_against_promotions(self):
        """A granted gate is meant to move a status line; the report says
        whether one ever did. A dated row in the Approvals table is the grant,
        whatever language the heading above it is written in."""
        scope = self.probe / "architecture" / "scope"
        scope.mkdir(exist_ok=True)
        doc = scope / "1_probe.md"
        doc.write_text(
            "# Probe\n\n## Aprobaciones\n\n"
            "| Compuerta | Aprobó | Fecha | Qué se mostró |\n"
            "| --------- | ------ | ----- | ------------- |\n"
            "| Entendimiento | The owner | 2026-09-07 | The probe |\n",
            encoding="utf-8",
        )
        self.addCleanup(doc.unlink)
        result = run(MODEL, "--project", self.probe, "health")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("1 initiative(s), 2 live element(s)", result.stdout)
        self.assertIn("1 dated approval row(s)", result.stdout)
        self.assertIn("1 granted, 0 document(s) validated — the gap", result.stdout)
        self.assertIn("1 of 2 name what realizes them", result.stdout)

    def test_names_says_which_element_a_path_belongs_to(self):
        """A change inside a path an element names is inside the model; a change
        to a path nothing names is a new element in disguise."""
        folder = self.probe / "architecture" / "5_technology"
        folder.mkdir(exist_ok=True)
        doc = folder / "README.md"
        doc.write_text(
            "# Technology layer — Probe\n\n_A probe, not a model._\n\n"
            "ArchiMate Technology layer.\n\n"
            "**Status:** ◐ Draft catalogue — a probe, not yet validated.\n\n"
            "## How to read this document\n\n"
            "```mermaid\nflowchart LR\n  %% legend\n"
            '  art[/"⎔ «Artifact» a file the build reads [ART#]"/]:::technology\n'
            "  classDef technology fill:#c9e7b7,stroke:#558b2f,color:#333\n```\n\n"
            "## Artifacts\n\n"
            "| ID | Artifact | Realized by |\n| -- | -------- | ----------- |\n"
            "| `ART1` | The enquiry module | `src/probe/enquiry.py`, `src/probe/filters/` |\n",
            encoding="utf-8",
        )
        self.addCleanup(shutil.rmtree, folder)
        for path in ("src/probe/enquiry.py", "src/probe/filters/by_date.py", "src/probe/"):
            result = run(MODEL, "--project", self.probe, "names", path)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("ART1", result.stdout, path)
        result = run(MODEL, "--project", self.probe, "names", "src/other/report.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Nothing names", result.stdout)
        self.assertNotIn("ART1", result.stdout)

    def test_trace_walks_across_layers_with_no_database(self):
        result = run(MODEL, "--project", self.probe, "trace", "BSVC1")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("ACMP1", result.stdout)
        self.assertFalse(
            list(self.probe.rglob("*.db")),
            "a tool wrote a database; nothing is supposed to be cached",
        )

    def test_a_brief_is_written_to_the_ignored_work_area(self):
        result = run(BRIEF, "--project", self.probe, "--element", "BSVC1", "--stdout")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("disposable document", result.stdout)
        self.assertIn("ACMP1", result.stdout)

    def test_the_portal_config_lands_under_the_ignored_work_area(self):
        result = run(MODEL, "--project", self.probe, "portal")
        self.assertEqual(result.returncode, 0, result.stderr)
        config = self.probe / ".archreator" / "work" / "portal" / "mkdocs.yml"
        self.assertTrue(config.is_file())
        self.assertIn("mermaid", config.read_text(encoding="utf-8"))
        ignored = (self.probe / ".gitignore").read_text(encoding="utf-8")
        self.assertIn(".archreator/", ignored)

    def test_a_directory_that_is_not_a_project_is_refused(self):
        """Not half-read, and not a traceback: a sentence saying what to do."""
        with tempfile.TemporaryDirectory() as empty:
            for tool in (MODEL, BRIEF):
                result = run(tool, "--project", empty, "coverage")
                self.assertNotEqual(result.returncode, 0, f"{tool.name} accepted a non-project")
                self.assertIn("model_graph.py", result.stderr)

    def test_a_built_portal_does_not_fail_the_validators(self):
        """What lands under .archreator/ is a rendering, not repository content.

        Building the portal locally used to make check_links fail on the built
        site's own pages until the directory was deleted.
        """
        site = self.probe / ".archreator" / "work" / "portal" / "site"
        site.mkdir(parents=True, exist_ok=True)
        (site / "index.html").write_text(
            '<a href="missing.html">gone</a>', encoding="utf-8"
        )
        try:
            for validator in ("check_links.py", "check_model.py"):
                result = run(self.probe / "scripts" / validator, cwd=self.probe)
                self.assertEqual(
                    result.returncode, 0,
                    f"{validator} read the generated portal: {result.stdout}{result.stderr}",
                )
        finally:
            (site / "index.html").unlink()

    def test_help_answers_outside_a_project(self):
        """--help is a question about the tool, not about any project."""
        with tempfile.TemporaryDirectory() as empty:
            for tool in (MODEL, BRIEF):
                result = run(tool, "--help", cwd=empty)
                self.assertEqual(result.returncode, 0, f"{tool.name}: {result.stderr}")
                self.assertTrue(result.stdout.strip(), f"{tool.name} printed nothing")

    def test_a_tree_reaches_the_repository_root_scripts(self):
        """A repository of several trees keeps one scripts/ at its root.

        That is the worked-models layout: `--project <tree>` must find the
        shared parse by walking up, and the portal must render the tree the
        caller named, not the repository root.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "worked-models"
            (root / ".git").mkdir(parents=True)
            shutil.copytree(
                SCAFFOLD / "scripts", root / "scripts",
                ignore=shutil.ignore_patterns("__pycache__"),
            )
            tree = root / "product-x"
            (tree / "architecture" / "2_business").mkdir(parents=True)
            (tree / "architecture" / "README.md").write_text(
                "# Probe tree\n", encoding="utf-8"
            )
            (tree / "architecture" / "2_business" / "README.md").write_text(
                BUSINESS.replace("`ACMP1`", "—"), encoding="utf-8"
            )
            result = run(MODEL, "--project", tree, "coverage")
            self.assertEqual(result.returncode, 0, result.stderr)
            for wrong in (root / "product-y", root / "not-a-tree"):
                # A mistyped tree must be refused, not silently answered for
                # the whole repository by the root's scripts.
                (root / "not-a-tree").mkdir(exist_ok=True)
                refused = run(MODEL, "--project", wrong, "coverage")
                self.assertNotEqual(
                    refused.returncode, 0,
                    f"{wrong.name}: a non-project bound to the repository root",
                )
            portal = run(MODEL, "--project", tree, "portal")
            self.assertEqual(portal.returncode, 0, portal.stderr)
            config = tree / ".archreator" / "work" / "portal" / "mkdocs.yml"
            self.assertTrue(config.is_file(), "the portal config went somewhere else")
            self.assertIn(
                "product-x/architecture", config.read_text(encoding="utf-8"),
                "the portal is not rendering the tree the caller named",
            )


if __name__ == "__main__":
    unittest.main()


ORG_FRONT = "# Architecture — org probe\n\n**Federation ID:** `ORG`\n"
PRD_FRONT = "# Architecture — product probe\n\n**Federation ID:** `PRD_MTD`\n"

LEGEND = """\
## How to read this document

```mermaid
flowchart LR
  n["a probe legend"]
```

"""

ORG_MOTIVATION = """\
# Motivation — org probe

**Status:** ◐ Draft catalogue — a probe.

""" + LEGEND + """\
## Stakeholders

| ID | Stakeholder |
| -- | ----------- |
| `STK1` | The owner |
"""

PRD_BUSINESS = """\
# Business — product probe

**Status:** ◐ Draft catalogue — a probe.

""" + LEGEND + """\
## Services

| ID | Service | Serves |
| -- | ------- | ------ |
| `BSVC1` | Answering | `ORG.STK1` |
"""

PRD_FEDERATION = """\
# Federation

| ID | Model | Subject |
| -- | ----- | ------- |
| `ORG` | `org-probe` | The organization |
"""


SECTION_VIEW_FIRST = """\
## Delivery

```mermaid
flowchart LR
  d["a probe section view"]
```

| ID | Service |
| -- | ------- |
| `BSVC2` | Delivering |
"""

SECTION_VIEW_LAST = """\
## Delivery

| ID | Service |
| -- | ------- |
| `BSVC2` | Delivering |

```mermaid
flowchart LR
  d["a probe section view"]
```
"""

STEREOTYPED_VIEW = """\
## Delivery

```mermaid
flowchart LR
  d(["⬭ «Business Service» Delivering [BSVC2]"])
```

| ID | Service |
| -- | ------- |
| `BSVC2` | Delivering |
"""


class FederationTests(unittest.TestCase):
    """Cross-model references resolve by federation ID, and drift is named."""

    def _build(self, root):
        shutil.copytree(
            SCAFFOLD / "scripts", root / "scripts",
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        org = root / "org-probe" / "architecture"
        (org / "1_strategy").mkdir(parents=True)
        (org / "README.md").write_text(ORG_FRONT, encoding="utf-8")
        (org / "1_strategy" / "1_motivation.md").write_text(ORG_MOTIVATION, encoding="utf-8")
        prd = root / "prd-probe" / "architecture"
        (prd / "2_business").mkdir(parents=True)
        (prd / "README.md").write_text(PRD_FRONT, encoding="utf-8")
        (prd / "federation.md").write_text(PRD_FEDERATION, encoding="utf-8")
        (prd / "2_business" / "README.md").write_text(PRD_BUSINESS, encoding="utf-8")
        return root / "scripts" / "check_model.py", prd

    def test_a_document_without_a_view_or_with_its_view_last_fails(self):
        """Every element document opens with its legend; a picture stapled on last is not that."""
        with tempfile.TemporaryDirectory() as tmp:
            script, prd = self._build(Path(tmp))
            business = prd / "2_business" / "README.md"
            no_view = PRD_BUSINESS.replace(LEGEND, "")
            business.write_text(no_view, encoding="utf-8")
            result = run(script)
            self.assertNotEqual(result.returncode, 0, "a catalogue with no view passed")
            self.assertIn("carries no view", result.stdout + result.stderr)
            view_last = no_view + "\n" + LEGEND
            business.write_text(view_last, encoding="utf-8")
            result = run(script)
            self.assertNotEqual(result.returncode, 0, "a view after the tables passed")
            self.assertIn("after its first table", result.stdout + result.stderr)
            business.write_text(PRD_BUSINESS, encoding="utf-8")
            result = run(script)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_section_whose_own_diagram_follows_its_own_table_fails(self):
        """One diagram per section, and the section opens with it.

        The document-wide test alone is a gradient towards stacking every
        diagram at the top, which is what this catches.
        """
        with tempfile.TemporaryDirectory() as tmp:
            script, prd = self._build(Path(tmp))
            business = prd / "2_business" / "README.md"
            stacked = PRD_BUSINESS.replace(
                "## Services\n",
                "## Services\n",
            ) + SECTION_VIEW_LAST
            business.write_text(stacked, encoding="utf-8")
            result = run(script)
            self.assertNotEqual(result.returncode, 0, "a section's view after its table passed")
            self.assertIn("that section's first table", result.stdout + result.stderr)
            business.write_text(PRD_BUSINESS + SECTION_VIEW_FIRST, encoding="utf-8")
            result = run(script)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_stereotype_outside_a_legend_diagram_fails(self):
        """Glyph, shape and colour carry the type; a legend says so with `%% legend`."""
        with tempfile.TemporaryDirectory() as tmp:
            script, prd = self._build(Path(tmp))
            business = prd / "2_business" / "README.md"
            business.write_text(PRD_BUSINESS + STEREOTYPED_VIEW, encoding="utf-8")
            result = run(script)
            self.assertNotEqual(result.returncode, 0, "a stereotyped content node passed")
            self.assertIn("stereotype", result.stdout + result.stderr)
            marked = STEREOTYPED_VIEW.replace("flowchart LR\n", "flowchart LR\n  %% legend\n")
            business.write_text(PRD_BUSINESS + marked, encoding="utf-8")
            result = run(script)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_reference_by_federation_id_resolves_across_models(self):
        with tempfile.TemporaryDirectory() as tmp:
            check, _ = self._build(Path(tmp))
            result = run(check, cwd=tmp)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_federation_reference_to_a_missing_element_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            check, prd = self._build(Path(tmp))
            doc = prd / "2_business" / "README.md"
            doc.write_text(doc.read_text(encoding="utf-8").replace("ORG.STK1", "ORG.STK9"),
                           encoding="utf-8")
            result = run(check, cwd=tmp)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("names no element", result.stdout)

    def test_the_retired_double_colon_notation_is_named(self):
        with tempfile.TemporaryDirectory() as tmp:
            check, prd = self._build(Path(tmp))
            doc = prd / "2_business" / "README.md"
            doc.write_text(doc.read_text(encoding="utf-8") + "\nSee `org-probe::STK1`.\n",
                           encoding="utf-8")
            result = run(check, cwd=tmp)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("retired", result.stdout)

    def test_a_mapping_that_disagrees_with_the_declared_id_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            check, prd = self._build(Path(tmp))
            fed = prd / "federation.md"
            fed.write_text(fed.read_text(encoding="utf-8").replace("`ORG`", "`ORGX`"),
                           encoding="utf-8")
            doc = prd / "2_business" / "README.md"
            doc.write_text(doc.read_text(encoding="utf-8").replace("ORG.STK1", "ORGX.STK1"),
                           encoding="utf-8")
            result = run(check, cwd=tmp)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("declares the federation ID", result.stdout)

    def test_an_unmapped_qualifier_is_reported(self):
        with tempfile.TemporaryDirectory() as tmp:
            check, prd = self._build(Path(tmp))
            doc = prd / "2_business" / "README.md"
            doc.write_text(doc.read_text(encoding="utf-8").replace("ORG.STK1", "ZZZ.STK1"),
                           encoding="utf-8")
            result = run(check, cwd=tmp)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn("federation ID", result.stdout)
