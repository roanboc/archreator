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


LISTED_SKILL = REPO_ROOT / "plugins" / "archreator" / "skills" / "document-style" / "SKILL.md"
BY_NAME_SKILL = REPO_ROOT / "plugins" / "archreator" / "skills" / "record-decision" / "SKILL.md"


class ListingTests(unittest.TestCase):
    """Three skills are listed; the rest are invoked by name.

    A skill that drifts back into the listing is loaded into every session,
    and a listed description that grows spends the budget for all three - so
    both are failures, not style.
    """

    def setUp(self):
        self.listed = LISTED_SKILL.read_text(encoding="utf-8")
        self.by_name = BY_NAME_SKILL.read_text(encoding="utf-8")
        self.addCleanup(LISTED_SKILL.write_text, self.listed, encoding="utf-8")
        self.addCleanup(BY_NAME_SKILL.write_text, self.by_name, encoding="utf-8")

    def _fails_with(self, path, mutated, fragment):
        path.write_text(mutated, encoding="utf-8")
        result = run_check()
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, f"the mutation passed:\n{output}")
        self.assertIn(fragment, output)

    def test_a_listed_description_that_grows_fails(self):
        line = re.search(r"^description: .*$", self.listed, re.M).group(0)
        self._fails_with(
            LISTED_SKILL,
            self.listed.replace(line, line + " " + "again and " * 30, 1),
            "a listed description is at most",
        )

    def test_a_by_name_skill_without_the_key_fails(self):
        self.assertIn("disable-model-invocation: true\n", self.by_name)
        self._fails_with(
            BY_NAME_SKILL,
            self.by_name.replace("disable-model-invocation: true\n", "", 1),
            "must carry `disable-model-invocation: true`",
        )

    def test_a_listed_skill_carrying_the_key_fails(self):
        self._fails_with(
            LISTED_SKILL,
            self.listed.replace("\nmetadata:", "\ndisable-model-invocation: true\nmetadata:", 1),
            "must not carry `disable-model-invocation`",
        )

    def test_the_report_prints_what_the_listing_spends(self):
        result = subprocess.run(
            [sys.executable, str(CHECK_SKILLS), "--report"],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("listed descriptions:", result.stdout)
        self.assertIn("document-style", result.stdout)


if __name__ == "__main__":
    unittest.main()
