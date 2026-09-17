"""The PDF export tool: declared order, loud failure, diagram extraction and
the Chromium-launch environment quirks verification turned up.

`export_pdf.py` reads an audience config from an arbitrary project directory
handed to `resolve_files`/`count_mermaid`/`build_html` directly, so these
tests build small fixture trees of their own rather than needing a real
model. The scaffold only stands in for the module import, exactly as
`test_build_brief.py` uses it — the bootstrap needs *a* valid project on
`sys.argv` to find `model_graph.py`, not this test's actual fixture content.

`export_pdf.py` declares `markdown`, `pyyaml` and `playwright` as inline
script dependencies (PEP 723) for its own `uv run` invocation, which is not
the same environment `uv run --with pytest pytest ...` gives this suite. The
tests that need `markdown` or `playwright` skip when they are not importable,
so the documented bare test command stays green with no extra setup; run it
with `--with markdown --with playwright --with pyyaml` for full coverage.
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HAS_MARKDOWN = importlib.util.find_spec("markdown") is not None
HAS_PLAYWRIGHT = importlib.util.find_spec("playwright") is not None

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "export_pdf.py"
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scaffold" / "scripts"))
sys.path.insert(0, str(SCRIPT.parent))
sys.argv = [sys.argv[0], "--project", str(Path(__file__).resolve().parents[2] / "scaffold")]
spec = importlib.util.spec_from_file_location("export_pdf", SCRIPT)
export_pdf = importlib.util.module_from_spec(spec)
spec.loader.exec_module(export_pdf)


DIAGRAM = "```mermaid\nflowchart LR\n  a --> b\n```\n"


class ResolveFilesTests(unittest.TestCase):
    """Format-agnostic — carried over unchanged from the Word export's tests."""

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
        files = export_pdf.resolve_files(self.project, config, Path("audience.yml"))
        self.assertEqual(
            [f.relative_to(self.project).as_posix() for f in files],
            ["dir/one.md", "dir/two.md", "banana.md", "apple.md"],
        )

    def test_a_glob_matching_nothing_fails_loudly(self):
        config = {"files": ["missing/*.md"], "exclude": []}
        with self.assertRaises(SystemExit):
            export_pdf.resolve_files(self.project, config, Path("audience.yml"))

    def test_a_literal_path_that_does_not_exist_fails_loudly(self):
        config = {"files": ["nope.md"], "exclude": []}
        with self.assertRaises(SystemExit):
            export_pdf.resolve_files(self.project, config, Path("audience.yml"))

    def test_excluding_every_match_fails_loudly(self):
        config = {"files": ["apple.md"], "exclude": ["apple.md"]}
        with self.assertRaises(SystemExit):
            export_pdf.resolve_files(self.project, config, Path("audience.yml"))

    def test_a_file_named_by_two_entries_is_not_duplicated(self):
        config = {"files": ["dir/*.md", "dir/one.md"], "exclude": []}
        files = export_pdf.resolve_files(self.project, config, Path("audience.yml"))
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
            export_pdf.count_mermaid([self.project / "a.md", self.project / "b.md"]), 3
        )

    def test_a_non_mermaid_fence_is_not_counted(self):
        (self.project / "a.md").write_text("```python\nprint('mermaid')\n```\n", encoding="utf-8")
        self.assertEqual(export_pdf.count_mermaid([self.project / "a.md"]), 0)


class ExtractDiagramsTests(unittest.TestCase):
    """`extract_diagrams` and `count_mermaid` must always agree.

    `build_html` asserts this in `main()` — these tests are what would catch
    a regression in either regex before that assertion ever fires on real
    content.
    """

    def test_extraction_count_matches_the_precount(self):
        text = f"# Title\n\n{DIAGRAM}\ntext\n\n{DIAGRAM}"
        stripped, diagrams = export_pdf.extract_diagrams(text)
        self.assertEqual(len(diagrams), 2)
        self.assertNotIn("```mermaid", stripped)
        self.assertIn("\x00MERMAID_0\x00", stripped)
        self.assertIn("\x00MERMAID_1\x00", stripped)

    def test_diagram_source_is_preserved_verbatim(self):
        stripped, diagrams = export_pdf.extract_diagrams(DIAGRAM)
        self.assertEqual(diagrams[0], "flowchart LR\n  a --> b")


@unittest.skipUnless(HAS_MARKDOWN, "requires markdown")
class RenderSourceTests(unittest.TestCase):
    """A hand-rolled converter is exactly what broke fidelity in the Word
    version — these pin down that the real `markdown` library actually
    handles what that one didn't: links, in particular.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.project = Path(self._tmp.name)

    def test_a_markdown_link_becomes_a_real_anchor_tag(self):
        (self.project / "a.md").write_text(
            "_[← Back](../README.md) · [Scope](./scope/README.md)_\n", encoding="utf-8"
        )
        html_body, _ = export_pdf.render_source(self.project, self.project / "a.md", True)
        self.assertIn('<a href="../README.md">', html_body)
        self.assertIn('<a href="./scope/README.md">', html_body)
        self.assertNotIn("[← Back]", html_body)

    def test_a_link_inside_a_table_cell_still_renders(self):
        (self.project / "a.md").write_text(
            "| Layer | Doc |\n| --- | --- |\n| 0 | [Design](./0/README.md) |\n",
            encoding="utf-8",
        )
        html_body, _ = export_pdf.render_source(self.project, self.project / "a.md", True)
        self.assertIn("<table>", html_body)
        self.assertIn('<a href="./0/README.md">Design</a>', html_body)

    def test_diagram_becomes_a_live_pre_block_when_rendering_is_live(self):
        (self.project / "a.md").write_text(DIAGRAM, encoding="utf-8")
        html_body, count = export_pdf.render_source(self.project, self.project / "a.md", True)
        self.assertEqual(count, 1)
        self.assertIn('<pre class="mermaid">', html_body)

    def test_diagram_becomes_a_labeled_fallback_when_rendering_is_not_live(self):
        (self.project / "a.md").write_text(DIAGRAM, encoding="utf-8")
        html_body, count = export_pdf.render_source(self.project, self.project / "a.md", False)
        self.assertEqual(count, 1)
        self.assertIn('class="mermaid-fallback"', html_body)
        self.assertIn("flowchart LR", html_body)


class HeadingShiftTests(unittest.TestCase):
    """The bug this fixes: every source file's own `<h1>` landed at the same
    level regardless of where it sits in the folder tree, so a layer's
    README and its own documents came out as siblings in the PDF's bookmark
    panel instead of parent and child — reported directly against the real
    output. `heading_shift` reads the intended nesting from the path itself:
    a `README.md` sits at its folder's depth, anything else in that folder
    is one level deeper.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.project = Path(self._tmp.name)

    def _shift(self, relative: str) -> int:
        path = self.project / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# t\n", encoding="utf-8")
        return export_pdf.heading_shift(self.project, path)

    def test_the_front_door_is_not_shifted(self):
        self.assertEqual(self._shift("architecture/README.md"), 0)

    def test_a_layer_readme_nests_under_the_front_door(self):
        self.assertEqual(self._shift("architecture/0_layer/README.md"), 1)

    def test_a_layer_document_nests_under_that_layer_readme(self):
        self.assertEqual(self._shift("architecture/0_layer/1_topic.md"), 2)

    def test_a_subfolder_document_nests_one_level_deeper_still(self):
        self.assertEqual(self._shift("architecture/0_layer/detail/1_x.md"), 3)

    def test_readme_is_matched_case_insensitively(self):
        self.assertEqual(self._shift("architecture/0_layer/Readme.md"), 1)

    def test_shift_headings_moves_every_level_and_clamps_at_h6(self):
        html_in = "<h1>a</h1><h2 class='x'>b</h2></h1>"
        self.assertEqual(
            export_pdf.shift_headings(html_in, 2),
            "<h3>a</h3><h4 class='x'>b</h4></h3>",
        )
        self.assertEqual(export_pdf.shift_headings("<h5>a</h5>", 3), "<h6>a</h6>")

    def test_zero_shift_is_a_no_op(self):
        html_in = "<h1>a</h1>"
        self.assertEqual(export_pdf.shift_headings(html_in, 0), html_in)

    @unittest.skipUnless(HAS_MARKDOWN, "requires markdown")
    def test_render_source_applies_the_shift_for_a_nested_file(self):
        path = self.project / "architecture" / "0_layer" / "1_topic.md"
        path.parent.mkdir(parents=True)
        path.write_text("# Título\n\n## Sub\n", encoding="utf-8")
        html_body, _ = export_pdf.render_source(self.project, path, True)
        self.assertIn("<h3>Título</h3>", html_body)
        self.assertIn("<h4>Sub</h4>", html_body)


class FindChromiumTests(unittest.TestCase):
    """Verified against a real environment during implementation: the
    installed `playwright` pip package can expect a browser revision that
    differs from what is actually provisioned, and the full `chromium-*`
    build's `chrome_sandbox` helper can be present but not properly
    setuid-root in a container, which fails the launch outright regardless of
    `--no-sandbox`. `find_chromium` prefers `chromium_headless_shell-*`,
    which carries no such helper at all.
    """

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.browsers = Path(self._tmp.name)
        self._env_patch = mock.patch.dict(
            "os.environ", {"PLAYWRIGHT_BROWSERS_PATH": str(self.browsers)}
        )
        self._env_patch.start()
        self.addCleanup(self._env_patch.stop)

    def _make_executable(self, relative: str) -> Path:
        path = self.browsers / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("", encoding="utf-8")
        path.chmod(0o755)
        return path

    def test_prefers_headless_shell_over_the_full_build(self):
        self._make_executable("chromium-1194/chrome-linux/chrome")
        headless = self._make_executable(
            "chromium_headless_shell-1194/chrome-linux/headless_shell"
        )
        self.assertEqual(export_pdf.find_chromium(), str(headless))

    def test_falls_back_to_the_full_build_when_no_headless_shell_exists(self):
        chrome = self._make_executable("chromium-1194/chrome-linux/chrome")
        self.assertEqual(export_pdf.find_chromium(), str(chrome))

    def test_returns_none_when_nothing_is_found(self):
        self.assertIsNone(export_pdf.find_chromium())

    def test_returns_none_when_the_env_var_is_unset(self):
        self._env_patch.stop()
        import os

        os.environ.pop("PLAYWRIGHT_BROWSERS_PATH", None)
        self.assertIsNone(export_pdf.find_chromium())
        self._env_patch.start()  # keep addCleanup's stop() balanced


if __name__ == "__main__":
    unittest.main()
