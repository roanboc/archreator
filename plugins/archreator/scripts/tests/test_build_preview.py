"""A preview shows what a change claims, to somebody who never read the model.

The shop in `example_project.py` is the probe: a model with a base and a
branch, built on the shipped scaffold. These hold the three things a preview
owes its reader - it names what changed and only that, it says it in the
subject's words with none of the model's notation, and what it writes opens
anywhere with nothing fetched.
"""
import re
import subprocess
import sys
import tempfile
import unittest
import xml.dom.minidom
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(PLUGIN / "scripts"))

import example_project as shop  # noqa: E402
import plain_view as pv  # noqa: E402

# Every identifier the shop's model defines, and every glyph the notation
# draws with. None of either may reach a reader.
IDENTIFIER = re.compile(r"\b(?:G|DRV|P|CAP|ROLE|BSVC|RULE|DOBJ|ACMP)\d+\b")
NOTATION = PLUGIN / "skills" / "architecture-document-style" / "references" / "archimate-on-mermaid.md"


def out_of(repo: Path, name: str = "preview") -> dict[str, str]:
    folder = repo / ".archreator" / "work" / "previews"
    return {path.suffix: path.read_text(encoding="utf-8") for path in folder.glob(f"{name}.*")}


class PreviewOfAChangeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.repo = shop.build(Path(cls._tmp.name).resolve())
        cls.made = shop.preview(cls.repo, "--name", "preview")
        cls.out = out_of(cls.repo)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_the_example_is_a_project_the_validators_accept(self):
        """What the site shows a newcomer is a model the method itself passes."""
        for validator in ("check_links.py", "check_model.py", "check_prose.py"):
            result = subprocess.run([sys.executable, str(self.repo / "scripts" / validator)],
                                    cwd=self.repo, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, f"{validator}: {result.stdout}{result.stderr}")

    def test_it_writes_a_page_a_picture_and_markdown(self):
        self.assertEqual(self.made.returncode, 0, self.made.stdout + self.made.stderr)
        self.assertEqual(set(self.out), {".md", ".svg", ".html"})
        self.assertIn("6 new, 3 changed. 6 new connections, 1 taken away.", self.made.stdout)

    def test_it_names_what_changed_and_how(self):
        text = self.out[".md"]
        self.assertIn("## Book a repair online", text)
        self.assertIn("Customers can book a repair online at any hour", text)
        self.assertIn("- **The booking page** (software)", text)
        self.assertIn("“A phone call from the front desk when the bike is ready” → "
                      "“A text message when the bike is ready”", text)
        # a relationship the change took away is drawn, and said to be gone
        self.assertRegex(text, r'-\.->\|"done by \(removed\)"\|')
        # what did not change is context, never listed as a change
        self.assertNotIn("- **The workshop diary**", text)

    def test_the_call_and_the_question_are_set_apart(self):
        for text in (self.out[".md"], self.out[".html"]):
            self.assertIn("Calls taken for you", text)
            self.assertIn("the request did not say whether every customer is texted", text)
            self.assertIn("Can a customer cancel a booking online, or only by phone?", text)
            self.assertIn("what was assumed", text)
        # the provenance cell itself is not offered as a fact about the shop
        self.assertNotIn("adopted", self.out[".md"])

    def test_no_identifier_and_no_glyph_reaches_the_reader(self):
        for kind, text in self.out.items():
            self.assertIsNone(IDENTIFIER.search(text), f"{kind} carries an identifier")
            self.assertFalse(set(text) & set(pv.GLYPHS), f"{kind} carries a notation glyph")

    def test_the_page_opens_anywhere_with_nothing_fetched(self):
        page = self.out[".html"]
        self.assertIsNone(re.search(r'(?:src|href)\s*=\s*["\']?(?:https?:)?//', page), "the page loads something")
        self.assertNotIn("<link", page)
        self.assertIn("<title>Book a repair online</title>", page)
        # both grounds are designed: a device set dark, and a viewer who chose
        self.assertIn('@media (prefers-color-scheme: dark)', page)
        self.assertIn(':root[data-theme="dark"]', page)
        xml.dom.minidom.parseString(self.out[".svg"])

    def test_the_picture_says_new_in_words_not_only_in_colour(self):
        picture = self.out[".svg"]
        self.assertIn(">NEW<", picture)
        self.assertIn(">CHANGED<", picture)
        self.assertIn('aria-label="new, The booking page, software"', picture)

    def test_the_markdown_can_go_straight_into_a_conversation(self):
        printed = shop.preview(self.repo, "--stdout")
        self.assertEqual(printed.returncode, 0, printed.stderr)
        self.assertIn("```mermaid", printed.stdout)
        self.assertIn("flowchart LR", printed.stdout)

    def test_narrowing_to_one_question_leaves_the_rest_out(self):
        narrowed = shop.preview(self.repo, "--name", "why", "--about", "why")
        self.assertEqual(narrowed.returncode, 0, narrowed.stderr)
        text = out_of(self.repo, "why")[".md"]
        self.assertIn("A customer can book without calling (new)", text)
        self.assertNotIn("The booking page (new)", text)


class PreviewEdgeTests(unittest.TestCase):
    def test_a_branch_that_changes_nothing_says_so(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = shop.build(Path(tmp).resolve(), change=False)
            result = shop.preview(repo, "--name", "same")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Nothing added, changed or removed.", result.stdout)
            self.assertNotIn("```mermaid", out_of(repo, "same")[".md"])

    def test_a_model_with_no_base_is_shown_whole_as_new(self):
        """A discovery: the base holds a scaffold and nothing else."""
        with tempfile.TemporaryDirectory() as tmp:
            repo = shop.build(Path(tmp).resolve(), files={})
            shop._write(repo, shop.BASE)
            result = shop.preview(repo, "--name", "first")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertRegex(result.stdout, r"^\d+ new\.")
            self.assertNotIn("changed", result.stdout.splitlines()[0])

    def test_a_large_change_is_drawn_one_question_at_a_time(self):
        """Past one screen the preview splits, as the rulebook says it must."""
        many = "".join(f"| `G{n}` | **Goal number {n}** | It matters |\n" for n in range(1, 16))
        able = "".join(f"| `CAP{n}` | **Ability number {n}** | `G{n}` |\n" for n in range(1, 16))
        doc = (
            "# Why\n\n**Status:** ◐ Draft catalogue.\n\n## Goals\n\n"
            "```mermaid\nflowchart LR\n  g[\"a goal [G1]\"]\n```\n\n"
            "| ID | Goal | Because |\n| -- | ---- | ------- |\n" + many +
            "\n## Abilities\n\n| ID | Ability | Serves |\n| -- | ------- | ------ |\n" + able
        )
        with tempfile.TemporaryDirectory() as tmp:
            repo = shop.build(Path(tmp).resolve(), files={})
            shop._write(repo, {"architecture/1_strategy/1_motivation.md": doc})
            result = shop.preview(repo, "--name", "big")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            folder = repo / ".archreator" / "work" / "previews"
            self.assertTrue((folder / "big-1.svg").is_file() and (folder / "big-2.svg").is_file())
            text = (folder / "big.md").read_text(encoding="utf-8")
            self.assertIn("### Why it exists", text)
            self.assertIn("### What it must be good at", text)

    def test_help_answers_outside_a_project(self):
        with tempfile.TemporaryDirectory() as empty:
            result = subprocess.run([sys.executable, str(shop.PREVIEW), "--help"],
                                    capture_output=True, text=True, cwd=empty)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Show what a change claims", result.stdout)


class PlainViewTests(unittest.TestCase):
    def test_every_glyph_of_the_notation_is_dropped(self):
        """The notation is written once, in the reference; this copy is held to it."""
        table = NOTATION.read_text(encoding="utf-8")
        used = set(re.findall(r"`([^\x00-\x7f])`", table))
        self.assertTrue(used, "the notation reference lists no glyph")
        self.assertFalse(used - set(pv.GLYPHS), f"plain_view.GLYPHS is missing {sorted(used - set(pv.GLYPHS))}")

    def test_a_cell_is_reduced_to_its_words(self):
        names = {"BSVC1": "Repair booking"}
        self.assertEqual(pv.plain("[`BSVC1`] Repair booking, and **more**", names), "Repair booking, and more")
        self.assertEqual(pv.plain("served by `BSVC1`", names), "served by Repair booking")
        self.assertEqual(pv.plain("⚙ «Business Process» Take a booking"), "Take a booking")

    def test_long_names_wrap_and_then_stop(self):
        lines = pv.wrap("A very long name that goes on well past what one box could ever hold in three lines of text", 160, 13)
        self.assertEqual(len(lines), 3)
        self.assertTrue(lines[-1].endswith("…"))
        self.assertTrue(all(pv.text_width(line, 13) <= 170 for line in lines))

    def test_the_drawing_is_well_formed_and_as_wide_as_a_page(self):
        nodes = [
            {"key": "n1", "name": "A goal", "kind": "goal", "group": "Motivation", "status": "new"},
            {"key": "n2", "name": "A service", "kind": "service", "group": "Business", "status": "same"},
        ]
        edges = [{"a": "n2", "b": "n1", "word": "serves", "status": "new"}]
        picture = pv.svg(nodes, edges, title="A probe")
        xml.dom.minidom.parseString(picture)
        width = int(re.search(r'viewBox="0 0 (\d+)', picture).group(1))
        self.assertLessEqual(width, 900, "a drawing wider than a page scrolls sideways")
        self.assertIn(">serves<", picture)
        self.assertEqual(pv.svg([], [], title="nothing"), "")


if __name__ == "__main__":
    unittest.main()
