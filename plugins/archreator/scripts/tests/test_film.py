"""The film's words are written once, and everything else follows them.

`film/script.json` is what the narrator says. The timeline the picture is
drawn against, the captions under the film and the transcript on the public
page are all copies of it. Each exists because something has to read it
without the voice tool: a browser, a player, a person. These hold the copies
to the script, so a reworded line that was not voiced again fails here.

    uv run film/tools/voice.py && node film/tools/render.js
"""
import html
import json
import re
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
FILM = REPO / "film"
SITE = REPO / "site"
REMAKE = "make the film again: uv run film/tools/voice.py && node film/tools/render.js"


def lines() -> list[str]:
    script = json.loads((FILM / "script.json").read_text(encoding="utf-8"))
    return [line["text"] for scene in script["scenes"] for line in scene["lines"]]


class FilmTests(unittest.TestCase):
    def test_the_timeline_is_the_scripts_lines_in_order(self):
        text = (FILM / "timeline.js").read_text(encoding="utf-8")
        timeline = json.loads(text[text.index("{"):text.rindex("}") + 1])
        self.assertEqual([line["text"] for line in timeline["lines"]], lines(), REMAKE)
        starts = [line["start"] for line in timeline["lines"]]
        self.assertEqual(starts, sorted(starts))
        self.assertGreater(timeline["duration"], timeline["lines"][-1]["end"])

    def test_the_captions_are_the_same_words(self):
        vtt = (SITE / "assets" / "film" / "archreator.en.vtt").read_text(encoding="utf-8")
        cues = [block.splitlines()[2] for block in vtt.split("\n\n") if "-->" in block]
        self.assertEqual(cues, lines(), REMAKE)

    def test_the_page_offers_the_film_its_captions_and_its_words(self):
        page = (SITE / "index.html").read_text(encoding="utf-8")
        for name in ("archreator.mp4", "archreator.en.vtt", "poster.jpg"):
            self.assertIn(f"./assets/film/{name}", page)
            self.assertTrue((SITE / "assets" / "film" / name).is_file(), f"{name} is missing - {REMAKE}")
        read = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", page)))
        for line in lines():
            self.assertIn(line, read, "the transcript on the page has drifted from the script")

    def test_the_film_says_its_voice_is_synthetic(self):
        self.assertIn("synthetic voice", (SITE / "index.html").read_text(encoding="utf-8"))
        self.assertIn("synthetic voice", (FILM / "film.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
