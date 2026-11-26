"""A whole model on one page, for the people the business is made of.

The same probe as the preview's tests: the made-up shop, after its change.
These hold what the page owes a reader who will never open the repository -
every question the model answers is there, in the model's own words and none
of its notation, in one file that opens anywhere.
"""
import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0]))

import example_project as shop  # noqa: E402
import plain_view as pv  # noqa: E402

IDENTIFIER = re.compile(r"\b(?:G|DRV|P|CAP|ROLE|BSVC|RULE|DOBJ|ACMP)\d+\b")


class OverviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        cls.repo = shop.build(Path(cls._tmp.name).resolve())
        cls.made = shop.overview(cls.repo)
        path = cls.repo / ".archreator" / "work" / "overview" / "index.html"
        cls.page = path.read_text(encoding="utf-8") if path.is_file() else ""
        found = re.search(r'<script type="application/json" id="pv-data">(.*?)</script>', cls.page, re.S)
        cls.data = json.loads(found.group(1).replace("<\\/", "</")) if found else {}

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_it_writes_one_page_and_says_how_much_it_holds(self):
        self.assertEqual(self.made.returncode, 0, self.made.stdout + self.made.stderr)
        self.assertIn("21 elements on one page", self.made.stdout)
        self.assertIn("<title>Corner Bikes on one page</title>", self.page)

    def test_every_question_the_model_answers_has_a_tab(self):
        for heading in ("Why it exists", "What it must be good at", "Who does what",
                        "What it needs to know", "The software"):
            self.assertRegex(self.page, rf'role="tab" data-tab="q\d"[^>]*>{heading}<span class="n">\d+</span>')
        # nothing in the shop says where it runs, so no empty tab pretends otherwise
        self.assertNotIn("Where it runs<span", self.page)

    def test_every_element_is_there_in_its_own_words(self):
        names = {node["name"] for node in self.data["nodes"].values()}
        for name in ("Repair booking", "The booking page", "Nobody waits on the phone", "Front desk", "Free slots"):
            self.assertIn(name, names)
        booking = next(n for n in self.data["nodes"].values() if n["name"] == "Repair booking")
        self.assertIn(["What the customer gets", "A slot in the workshop, booked online, by phone or at the counter", "", False],
                      booking["detail"])
        self.assertTrue(any(link["word"] == "needs" and link["out"] for link in booking["links"]))

    def test_a_connection_can_be_followed_across_questions(self):
        nodes = self.data["nodes"]
        page = next(n for n in nodes.values() if n["name"] == "The booking page")
        target = nodes[page["links"][0]["to"]]
        self.assertEqual(target["name"], "Repair booking")
        self.assertNotEqual(page["tab"], target["tab"])

    def test_what_nobody_confirmed_says_so(self):
        nodes = {n["name"]: n for n in self.data["nodes"].values()}
        self.assertTrue(nodes["The booking page"]["draft"])
        self.assertIn("not confirmed by anybody yet", self.page)

    def test_no_identifier_and_no_glyph_reaches_the_reader(self):
        self.assertIsNone(IDENTIFIER.search(self.page))
        self.assertFalse(set(self.page) & set(pv.GLYPHS))

    def test_the_page_opens_anywhere_with_nothing_fetched(self):
        self.assertIsNone(re.search(r'(?:src|href)\s*=\s*["\']?(?:https?:)?//', self.page))
        self.assertNotIn("<link", self.page)

    def test_a_large_question_is_drawn_a_kind_at_a_time(self):
        many = "".join(f"| `G{n}` | **Goal number {n}** | It matters |\n" for n in range(1, 31))
        drivers = "".join(f"| `DRV{n}` | **Pressure number {n}** | `G{n}` |\n" for n in range(1, 4))
        doc = (
            "# Why\n\n**Status:** ◐ Draft catalogue.\n\n## Goals\n\n"
            "```mermaid\nflowchart LR\n  g[\"a goal [G1]\"]\n```\n\n"
            "| ID | Goal | Because |\n| -- | ---- | ------- |\n" + many +
            "\n## Pressures\n\n| ID | Pressure | Answered by |\n| -- | -------- | ----------- |\n" + drivers
        )
        with tempfile.TemporaryDirectory() as tmp:
            repo = shop.build(Path(tmp).resolve(), change=False,
                              files={"architecture/README.md": "# Architecture — Big\n",
                                     "architecture/1_strategy/1_motivation.md": doc})
            made = shop.overview(repo)
            self.assertEqual(made.returncode, 0, made.stdout + made.stderr)
            page = (repo / ".archreator" / "work" / "overview" / "index.html").read_text(encoding="utf-8")
            self.assertIn("<h2>goal</h2>", page)
            self.assertIn("<h2>pressure</h2>", page)

    def test_help_answers_outside_a_project(self):
        with tempfile.TemporaryDirectory() as empty:
            result = subprocess.run([sys.executable, str(shop.OVERVIEW), "--help"],
                                    capture_output=True, text=True, cwd=empty)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Show a whole model on one page", result.stdout)


if __name__ == "__main__":
    unittest.main()
