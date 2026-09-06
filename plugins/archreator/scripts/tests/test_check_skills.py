"""The corpus validator, on the checks that have no downstream counterpart.

`check_model.py` and `check_links.py` run in every project and are covered by
`test_project_tools.py`. What is covered here is what only this repository can
check: an asset template obeys the diagram rules it teaches, because once it is
emitted it stops being an asset and no validator downstream will ever look at
it again.
"""

import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
CHECK_SKILLS = REPO_ROOT / "plugins" / "archreator" / "scripts" / "check_skills.py"
PROBE_ASSET = (
    REPO_ROOT / "plugins" / "archreator" / "assets" / "layers" / "3_information" / "README.md"
)


def run_check(cwd=None):
    return subprocess.run(
        [sys.executable, str(CHECK_SKILLS)],
        capture_output=True,
        text=True,
        cwd=cwd or REPO_ROOT,
    )


class AssetDiagramTests(unittest.TestCase):
    """A template that draws a node wrongly draws it wrongly in every project.

    Each case mutates a real asset in place and restores it, so the check is
    exercised against the tree it actually guards rather than a fixture that
    could drift from it.
    """

    def setUp(self):
        self.original = PROBE_ASSET.read_text(encoding="utf-8")
        self.addCleanup(PROBE_ASSET.write_text, self.original, encoding="utf-8")

    def _fails_with(self, mutated, fragment):
        PROBE_ASSET.write_text(mutated, encoding="utf-8")
        result = run_check()
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, f"the mutation passed:\n{output}")
        self.assertIn(fragment, output)

    def test_the_corpus_is_clean(self):
        result = run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_a_stereotype_on_a_content_node_fails(self):
        """Glyph, shape and colour carry the type; the stereotype is the widest
        thing on the node and the least informative."""
        node = re.search(r'^\s+\w+\[.*\[DOBJ#\].*$', self.original, re.M)
        self.assertIsNotNone(node, "the probe asset no longer draws a DOBJ node")
        mutated = self.original.replace(
            node.group(0), '  obj["«Data Object» <Domain type>"]', 1
        )
        self._fails_with(mutated, "carries a «stereotype»")

    def test_a_plausible_real_identifier_in_a_template_fails(self):
        """`[DOBJ1]` in a template lands in a project as a reference to an
        element nobody defined."""
        self._fails_with(
            self.original.replace("[DOBJ#]", "[DOBJ1]", 1),
            "a plausible real identifier",
        )

    def test_a_section_whose_diagram_follows_its_table_fails(self):
        mutated = self.original + (
            "\n## Probe section\n\n"
            "| ID | Thing |\n| -- | ----- |\n| `X` | y |\n\n"
            "```mermaid\nflowchart LR\n  n[\"probe\"]\n```\n"
        )
        self._fails_with(mutated, "comes after that section's first table")

    def test_a_legend_may_keep_its_stereotypes(self):
        """The one diagram whose subject is the notation says so with a marker
        the validator reads, so the rule holds in any language."""
        mutated = self.original + (
            "\n## Probe legend\n\n"
            "```mermaid\nflowchart LR\n  %% legend\n"
            '  n["▦ «Data Object» what it is [DOBJ#]"]\n```\n'
        )
        PROBE_ASSET.write_text(mutated, encoding="utf-8")
        result = run_check()
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
