"""What the public site shows as an example is what the tool really writes.

The landing page shows a newcomer one preview: a made-up bike shop adding
online booking. It is not a mock-up. `example_project.py` builds the shop and
runs `build_preview.py` on it, and the files under `site/demo/` are that run's
output, committed. These tests make the same run again and compare, so a
change to the tool that the site does not follow fails here.

    python3 plugins/archreator/scripts/tests/example_project.py --write site/demo
"""
import re
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
SITE = HERE.parents[3] / "site"
sys.path.insert(0, str(HERE))

import example_project as shop  # noqa: E402

REGENERATE = "regenerate with: python3 plugins/archreator/scripts/tests/example_project.py --write site/demo"


class SiteExampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory()
        root = Path(cls._tmp.name).resolve()
        cls.out = root / "out"
        repo = shop.build(root)
        cls.made = shop.preview(repo, "--name", "preview", "--to", str(cls.out))
        cls.whole = shop.overview(repo, "--name", "overview", "--to", str(cls.out))

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_the_example_page_and_picture_are_the_tools_own_output(self):
        self.assertEqual(self.made.returncode, 0, self.made.stdout + self.made.stderr)
        self.assertEqual(self.whole.returncode, 0, self.whole.stdout + self.whole.stderr)
        for name in ("preview.html", "preview.svg", "overview.html"):
            self.assertEqual(
                (SITE / "demo" / name).read_text(encoding="utf-8"),
                (self.out / name).read_text(encoding="utf-8"),
                f"site/demo/{name} is stale - {REGENERATE}",
            )

    def test_the_numbers_on_the_landing_page_are_the_examples(self):
        """The hero counts the change in four chips; the tool counts it too."""
        said = self.made.stdout.splitlines()[0]
        new, changed, gone = (int(n) for n in re.match(
            r"(\d+) new, (\d+) changed\. \d+ new connections, (\d+) taken away\.", said).groups())
        page = (SITE / "index.html").read_text(encoding="utf-8")
        self.assertIn(f'<li class="chip new">{new} new</li>', page)
        self.assertIn(f'<li class="chip changed">{changed} changed</li>', page)
        self.assertIn(f'<li class="chip gone">{gone} connection taken away</li>', page)
        self.assertIn('<li class="chip ask">1 question for you</li>', page)

    def test_the_example_says_it_is_an_example(self):
        page = (SITE / "demo" / "preview.html").read_text(encoding="utf-8")
        self.assertIn("made-up", page)


if __name__ == "__main__":
    unittest.main()
