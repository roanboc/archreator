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
