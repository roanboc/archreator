from __future__ import annotations

from contextlib import redirect_stdout
import importlib.util
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest


MODULE_PATH = Path(__file__).parents[1] / "check_method.py"
SPEC = importlib.util.spec_from_file_location("archreator_method_check", MODULE_PATH)
assert SPEC and SPEC.loader
check_method = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = check_method
SPEC.loader.exec_module(check_method)

REPOSITORY_ROOT = Path(__file__).resolve().parents[4]


def procedure_text(
    name: str = "model-context",
    process: str = "BPROC1.1",
    gates: str = "Context resolution",
    include_produces: bool = True,
) -> str:
    gate_marker = "" if gates == "none" else f"**❖ Gate — {gates}.** Stop when needed.\n\n"
    produces = "**→ Produces.** A result.\n" if include_produces else ""
    return f"""---
name: {name}
description: Procedure — run this for a test workflow.
metadata:
  archreator:
    kind: gated-procedure
    realizes_process: {process}
    gates: {gates}
---

# ⚙ Test procedure

## ⊕ When to use this

When the fixture needs it.

## ⊖ When not to

When it does not.

## ⌖ Where this sits

Realizes `{process}`.

## ⚓ Invariants

Keep the fixture small.

## ⚙ Steps

### 1. Do the work

**← Needs.** An input.

{gate_marker}{produces}
## ⇄ Hands off to

Nothing.

## ⚠ Anti-patterns

Skipping the result.

## ☑ Done when

The result exists.
"""


def template_text(name: str = "write-brief") -> str:
    return f"""---
name: {name}
description: Document — write one when the fixture needs an artifact.
metadata:
  archreator:
    kind: document-template
    gates: none
---

# ▤ Test template

## ⊕ When to use this
Use it.
## ⊖ When not to
Do not use it.
## ⌖ Where this sits
Supports a process.
## ▤ Template
The shape.
## ※ Rules
The rules.
## ⚠ Anti-patterns
The mistakes.
## ☑ Done when
The document is complete.
"""


def rulebook_text(name: str = "document-style") -> str:
    return f"""---
name: {name}
description: Rulebook — consult when the fixture needs a rule.
metadata:
  archreator:
    kind: rulebook
    gates: none
---

# ※ Test rules

## ⊕ When to use this
Use it.
## ⊖ When not to
Do not use it.
## ⌖ Where this sits
Supports work.
## ※ Rules
One rule.
## ⚠ Anti-patterns
One mistake.
"""


class TemporaryCase(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self):
        self.temporary.cleanup()

    def write(self, relative: str, content: str) -> Path:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path


class FrontmatterTests(unittest.TestCase):
    def test_parses_nested_string_mapping_without_yaml(self):
        mapping, body, body_line = check_method.parse_frontmatter(
            """---
name: model-context
description: "Procedure — run this: when needed."
metadata:
  archreator:
    kind: gated-procedure
    gates: none
---
# ⚙ Model context
"""
        )

        self.assertEqual("model-context", mapping["name"])
        self.assertEqual(
            "gated-procedure", mapping["metadata"]["archreator"]["kind"]
        )
        self.assertEqual("# ⚙ Model context", body)
        self.assertEqual(9, body_line)

    def test_rejects_yaml_sequences(self):
        with self.assertRaises(check_method.FrontmatterError):
            check_method.parse_frontmatter(
                """---
name: example
gates:
  - one
---
body
"""
            )


class SkillContractTests(TemporaryCase):
    def validate(self, name: str, content: str):
        path = self.write(f"skills/{name}/SKILL.md", content)
        return check_method.validate_skill(path, check_method.DEFAULT_SECTION_CONTRACT)

    def test_accepts_all_three_skill_kinds(self):
        cases = (
            ("model-context", procedure_text()),
            ("write-brief", template_text()),
            ("document-style", rulebook_text()),
        )
        for name, content in cases:
            with self.subTest(name=name):
                record, issues = self.validate(name, content)
                self.assertIsNotNone(record)
                self.assertEqual([], issues)

    def test_procedure_requires_needs_and_produces_per_step(self):
        _, issues = self.validate(
            "model-context", procedure_text(include_produces=False)
        )
        self.assertIn("STEP_PRODUCES", {issue.code for issue in issues})

    def test_declared_gate_must_have_a_marker_and_none_is_allowed(self):
        missing = procedure_text().replace(
            "**❖ Gate — Context resolution.** Stop when needed.\n\n", ""
        )
        _, issues = self.validate("model-context", missing)
        self.assertIn("MISSING_GATE", {issue.code for issue in issues})

        _, no_gate_issues = self.validate(
            "model-context", procedure_text(gates="none")
        )
        self.assertNotIn(
            "MISSING_GATE", {issue.code for issue in no_gate_issues}
        )

    def test_folder_name_and_kind_markers_are_checked(self):
        content = procedure_text(name="different").replace(
            "description: Procedure —", "description: Document —"
        ).replace("# ⚙", "# ▤")
        _, issues = self.validate("model-context", content)
        codes = {issue.code for issue in issues}
        self.assertTrue({"SKILL_NAME", "DESCRIPTION_KIND", "H1_KIND"} <= codes)

    def test_contract_table_controls_required_sections(self):
        contract = check_method.section_contract_from_text(
            """| Glyph | Section | Holds | Procedure | Template | Rulebook |
| --- | --- | --- | --- | --- | --- |
| `⊕` | Activate | Conditions | required | required | required |
| `⚙` | Work | Steps | required | — | — |
"""
        )
        self.assertEqual(
            frozenset({"⊕ Activate", "⚙ Work"}),
            contract["gated-procedure"],
        )


class BindingTests(TemporaryCase):
    def record(
        self,
        name: str,
        processes: tuple[str, ...],
        body: str = "",
        headings: frozenset[str] = frozenset(),
    ):
        return check_method.SkillRecord(
            path=self.root / name / "SKILL.md",
            folder_name=name,
            declared_name=name,
            kind="gated-procedure",
            description="Procedure — test",
            process_ids=processes,
            gates=(),
            body=body,
            body_start_line=1,
            headings=headings,
        )

    def test_process_bindings_are_bidirectional(self):
        text = """| ID | Process | Realized by |
| --- | --- | --- |
| `BPROC1.1` | Model context | `model-context` |
"""
        rows, duplicates = check_method.process_rows_from_text(text)
        records = {"model-context": self.record("model-context", ("BPROC1.1",))}

        self.assertEqual([], duplicates)
        self.assertEqual(
            [],
            check_method.validate_process_bindings(
                records, rows, self.root / "process.md"
            ),
        )

        broken = {"model-context": self.record("model-context", ("BPROC9.9",))}
        codes = {
            issue.code
            for issue in check_method.validate_process_bindings(
                broken, rows, self.root / "process.md"
            )
        }
        self.assertTrue({"UNKNOWN_PROCESS", "SKILL_PROCESS_MISSING"} <= codes)

    def test_cross_skill_section_reference_resolves(self):
        target = self.record(
            "document-style", (), headings=frozenset({"rules", "anti-patterns"})
        )
        source = self.record(
            "model-context", (), body="Apply `document-style` § Rules."
        )
        records = {"document-style": target, "model-context": source}
        self.assertEqual([], check_method.validate_cross_references(records))

        broken = self.record(
            "model-context", (), body="Apply `document-style` § Missing heading."
        )
        codes = {
            issue.code
            for issue in check_method.validate_cross_references(
                {"document-style": target, "model-context": broken}
            )
        }
        self.assertIn("CROSS_HEADING", codes)


class PackageTests(TemporaryCase):
    def test_catalogue_lists_exact_skill_directories_once(self):
        skills_root = self.root / "plugins" / "archreator" / "skills"
        links = []
        for name in sorted(check_method.EXPECTED_SKILLS):
            (skills_root / name).mkdir(parents=True, exist_ok=True)
            links.append(f"- [`{name}`](./{name}/SKILL.md)")
        self.write(
            "plugins/archreator/skills/README.md", "# Skills\n\n" + "\n".join(links)
        )
        self.assertEqual([], check_method.validate_catalogue(self.root))

        (skills_root / "extra-skill").mkdir()
        self.assertIn(
            "SKILL_DIRECTORIES",
            {issue.code for issue in check_method.validate_catalogue(self.root)},
        )

    def test_manifest_copies_and_marketplace_version_must_agree(self):
        manifest = {"name": "archreator", "version": "1.2.3", "skills": "./skills/"}
        encoded = json.dumps(manifest)
        self.write("plugins/archreator/plugin.json", encoded)
        self.write("plugins/archreator/.claude-plugin/plugin.json", encoded)
        self.write("plugins/archreator/.codex-plugin/plugin.json", encoded)
        marketplace = {
            "name": "archreator",
            "plugins": [{"name": "archreator", "version": "1.2.3"}],
        }
        market_path = self.write(
            ".claude-plugin/marketplace.json", json.dumps(marketplace)
        )
        self.assertEqual([], check_method.validate_manifests(self.root))

        marketplace["plugins"][0]["version"] = "9.9.9"
        market_path.write_text(json.dumps(marketplace), encoding="utf-8")
        self.assertIn(
            "MARKETPLACE_VERSION",
            {issue.code for issue in check_method.validate_manifests(self.root)},
        )

    def test_scaffold_is_minimal_and_uses_pointer_files(self):
        self.write("plugins/archreator/scaffold/.gitignore", "/.archreator/work/\n")
        self.write("plugins/archreator/scaffold/AGENTS.md", "# Project\n")
        self.write("plugins/archreator/scaffold/CLAUDE.md", "@AGENTS.md\n")
        self.write("plugins/archreator/scaffold/GEMINI.md", "@AGENTS.md\n")
        self.write("plugins/archreator/scaffold/architecture/README.md", "# Architecture\n")
        self.assertEqual([], check_method.validate_scaffold(self.root))

        (self.root / "plugins/archreator/scaffold/architecture/1_strategy").mkdir()
        codes = {issue.code for issue in check_method.validate_scaffold(self.root)}
        self.assertTrue({"SCAFFOLD_DIRECTORIES", "EMPTY_SCAFFOLD_AREA"} <= codes)

    def test_sqlite_and_old_scripts_are_rejected(self):
        self.write("plugins/archreator/scripts/new.py", "import sqlite3\n")
        self.write("plugins/archreator/scripts/model_graph.py", "# legacy\n")
        codes = {
            issue.code
            for issue in check_method.validate_forbidden_implementation(self.root)
        }
        self.assertTrue({"SQLITE", "OLD_SCRIPT"} <= codes)

    def test_runtime_enforces_work_portal_and_pdf_boundaries(self):
        self.assertEqual(
            [], check_method.validate_runtime_boundaries(REPOSITORY_ROOT)
        )

    def test_cli_returns_one_for_an_invalid_repository(self):
        output = io.StringIO()
        with redirect_stdout(output):
            result = check_method.main(["--repo", str(self.root)])
        self.assertEqual(1, result)
        self.assertIn("FAILED:", output.getvalue())


class RepositoryIntegrationTests(unittest.TestCase):
    def test_repository_satisfies_method_contract(self):
        issues = check_method.validate_repository(REPOSITORY_ROOT)
        self.assertEqual(
            [],
            issues,
            "\n".join(issue.display(REPOSITORY_ROOT) for issue in issues),
        )
        output = io.StringIO()
        with redirect_stdout(output):
            result = check_method.main(["--repo", str(REPOSITORY_ROOT)])
        self.assertEqual(0, result)
        self.assertIn("OK: 10 skills", output.getvalue())


if __name__ == "__main__":
    unittest.main()
