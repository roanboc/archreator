from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent))

from build_portal import PORTAL_MARKER, PortalError, build_portal  # noqa: E402


class PortalBuilderTests(unittest.TestCase):
    def make_project(self, root: Path) -> Path:
        project = root / "plain-initiative"
        (project / "architecture" / "4_application").mkdir(parents=True)
        (project / "docs").mkdir()
        (project / "README.md").write_text(
            "# Plain Initiative\n\nA small service for a real customer need.\n",
            encoding="utf-8",
        )
        (project / "architecture" / "README.md").write_text(
            """# Plain Initiative Architecture

| Layer | Status | Comment |
| --- | --- | --- |
| Business design | Outside scope | This solution does not model an operating model. |
| Strategy | Outside scope | Direction is already settled. |
| Business | Owned elsewhere | The parent company model defines the service. |
| Information | Blocked | The owner of customer information is unresolved. |
| Application | Documented | This repository owns the solution. |
""",
            encoding="utf-8",
        )
        (project / "architecture" / "4_application" / "README.md").write_text(
            """# Application

The checkout service accepts an order and confirms payment.

```mermaid
flowchart LR
  customer --> checkout
```

See the [business guide](../../docs/guide.md).
""",
            encoding="utf-8",
        )
        (project / "docs" / "guide.md").write_text(
            "# Business Guide\n\nThis explains the checkout service to business readers.\n",
            encoding="utf-8",
        )
        return project

    def test_builds_searchable_layered_portal_in_disposable_work_folder(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.make_project(Path(temporary))
            index = build_portal(project, "https://example.test/source")

            portal = project / ".archreator" / "work" / "portal"
            self.assertEqual(index, portal / "index.html")
            self.assertEqual(
                (project / ".archreator" / "work" / ".gitignore").read_text(encoding="utf-8"),
                "*\n!.gitignore\n",
            )
            self.assertTrue((portal / PORTAL_MARKER).is_file())
            self.assertTrue((portal / "architecture" / "4_application" / "index.html").is_file())
            self.assertTrue((portal / "docs" / "guide.html").is_file())

            landing = index.read_text(encoding="utf-8")
            self.assertIn("Plain Initiative Architecture", landing)
            self.assertIn("Out of scope", landing)
            self.assertIn("Externally owned", landing)
            self.assertIn("Blocked", landing)
            self.assertIn("No status or content is recorded in this model.", landing)
            self.assertIn("Architecture layers", landing)

            application = (portal / "architecture" / "4_application" / "index.html").read_text(encoding="utf-8")
            self.assertIn('<pre class="mermaid">', application)
            self.assertIn("../../docs/guide.html", application)
            self.assertIn("https://example.test/source/architecture/4_application/README.md", application)

            search = (portal / "assets" / "portal.js").read_text(encoding="utf-8")
            self.assertIn("checkout service", search)
            self.assertIn("docs/guide.html", search)

    def test_rebuilds_owned_portal_and_refuses_unowned_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.make_project(Path(temporary))
            build_portal(project)
            portal = project / ".archreator" / "work" / "portal"
            (portal / "stale.html").write_text("stale", encoding="utf-8")

            build_portal(project)
            self.assertFalse((portal / "stale.html").exists())

            (portal / PORTAL_MARKER).unlink()
            with self.assertRaisesRegex(PortalError, "does not contain the ArChreator portal marker"):
                build_portal(project)

    def test_requires_canonical_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(PortalError, "No canonical Markdown found"):
                build_portal(Path(temporary))

    def test_command_builds_an_isolated_project(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project = self.make_project(Path(temporary))
            result = subprocess.run(
                [sys.executable, "-B", str(Path(__file__).with_name("build_portal.py")), str(project)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Portal built:", result.stdout)
            self.assertTrue((project / ".archreator" / "work" / "portal" / "index.html").is_file())


if __name__ == "__main__":
    unittest.main()
