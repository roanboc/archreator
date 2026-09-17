"""The Word export tool: declared order, loud failure, and the diagram count.

`export_word.py` reads an audience config from an arbitrary project directory
handed to `resolve_files`/`count_mermaid`/`build_document` directly, so these
tests build small fixture trees of their own rather than needing a real
model. The scaffold only stands in for the module import, exactly as
`test_build_brief.py` uses it — the bootstrap needs *a* valid project on
`sys.argv` to find `model_graph.py`, not this test's actual fixture content.

`export_word.py` declares `python-docx` as an inline script dependency
(PEP 723) for its own `uv run` invocation, which is not the same environment
`uv run --with pytest pytest ...` gives this suite. The tests that build an
actual document skip when `docx` is not importable, so the documented bare
test command stays green with no extra setup; run it with
`--with python-docx --with pyyaml` for full coverage of this file.
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

HAS_DOCX = importlib.util.find_spec("docx") is not None

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "export_word.py"
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scaffold" / "scripts"))
sys.path.insert(0, str(SCRIPT.parent))
sys.argv = [sys.argv[0], "--project", str(Path(__file__).resolve().parents[2] / "scaffold")]
spec = importlib.util.spec_from_file_location("export_word", SCRIPT)
export_word = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export_word)


DIAGRAM = "```mermaid\nflowchart LR\n  a --> b\n```\n"


class ResolveFilesTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.project = Path(self._tmp.name)
        (self.project / "dir").mkdir()
        for name, body in (
            ("apple.md", "# Apple\n"),
            ("banana.md", "# Banana\n"),
            ("dir/two.md", "# Two\n"),
            ("dir/one.md", "# One\n"),
        ):
            (self.project / name).write_text(body, encoding="utf-8")

    def test_declared_order_survives_glob_expansion(self):
        config = {"files": ["dir/*.md", "banana.md", "apple.md"], "exclude": []}
        files = export_word.resolve_files(self.project, config, Path("audience.yml"))
        self.assertEqual(
            [f.relative_to(self.project).as_posix() for f in files],
            ["dir/one.md", "dir/two.md", "banana.md", "apple.md"],
        )

    def test_a_glob_matching_nothing_fails_loudly(self):
        config = {"files": ["missing/*.md"], "exclude": []}
        with self.assertRaises(SystemExit):
            export_word.resolve_files(self.project, config, Path("audience.yml"))

    def test_a_literal_path_that_does_not_exist_fails_loudly(self):
        config = {"files": ["nope.md"], "exclude": []}
        with self.assertRaises(SystemExit):
            export_word.resolve_files(self.project, config, Path("audience.yml"))

    def test_excluding_every_match_fails_loudly(self):
        config = {"files": ["apple.md"], "exclude": ["apple.md"]}
        with self.assertRaises(SystemExit):
            export_word.resolve_files(self.project, config, Path("audience.yml"))

    def test_a_file_named_by_two_entries_is_not_duplicated(self):
        config = {"files": ["dir/*.md", "dir/one.md"], "exclude": []}
        files = export_word.resolve_files(self.project, config, Path("audience.yml"))
        self.assertEqual(
            [f.relative_to(self.project).as_posix() for f in files],
            ["dir/one.md", "dir/two.md"],
        )


class DiagramCountTests(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.project = Path(self._tmp.name)

    def test_mermaid_fences_are_counted_once_each(self):
        (self.project / "a.md").write_text(DIAGRAM + "\ntext\n\n" + DIAGRAM, encoding="utf-8")
        (self.project / "b.md").write_text(DIAGRAM, encoding="utf-8")
        self.assertEqual(
            export_word.count_mermaid([self.project / "a.md", self.project / "b.md"]), 3
        )

    def test_a_non_mermaid_fence_is_not_counted(self):
        (self.project / "a.md").write_text("```python\nprint('mermaid')\n```\n", encoding="utf-8")
        self.assertEqual(export_word.count_mermaid([self.project / "a.md"]), 0)

    @unittest.skipUnless(HAS_DOCX, "requires python-docx")
    def test_every_counted_diagram_reaches_the_document_without_mmdc(self):
        """The invariant `export_word.py` refuses to ship a mismatch on.

        No `mmdc` on `PATH` in this environment is the common case a project
        runs in, so every diagram falls back to a labeled source block —
        which must still mean nothing is dropped: the embedded count has to
        equal what was counted going in.
        """
        (self.project / "a.md").write_text(
            f"# A\n\n{DIAGRAM}\ntext\n\n{DIAGRAM}", encoding="utf-8"
        )
        (self.project / "b.md").write_text(f"# B\n\n{DIAGRAM}", encoding="utf-8")
        files = [self.project / "a.md", self.project / "b.md"]
        expected = export_word.count_mermaid(files)
        config = {"title": "Probe"}
        _doc, state = export_word.build_document(self.project, config, files)
        self.assertEqual(state["diagrams_embedded"], expected)
        self.assertEqual(expected, 3)


class TrackChangesPlacementTests(unittest.TestCase):
    @unittest.skipUnless(HAS_DOCX, "requires python-docx")
    def test_track_revisions_is_inserted_in_schema_order(self):
        """`w:trackRevisions` lands where CT_Settings' fixed sequence puts it.

        Inserted at a fixed index instead, it would sit before elements a
        freshly created `Document()` already carries earlier in the sequence
        (`w:zoom`, `w:proofState`) — schema-invalid, and the kind of thing
        that makes Word offer to repair the file.
        """
        from docx import Document
        from docx.oxml.ns import qn

        doc = Document()
        export_word.enable_track_changes(doc)
        tags = [child.tag for child in doc.settings.element]
        self.assertIn(qn("w:trackRevisions"), tags)
        # Whatever precedes it here must all be earlier in the real sequence.
        order = [qn(t) for t in export_word._SETTINGS_ORDER]
        before = tags[: tags.index(qn("w:trackRevisions"))]
        positions = [order.index(t) for t in before if t in order]
        self.assertEqual(positions, sorted(positions))


if __name__ == "__main__":
    unittest.main()
