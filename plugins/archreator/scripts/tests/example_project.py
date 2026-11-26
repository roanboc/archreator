"""A small made-up business, before and after one change.

Corner Bikes repairs bicycles. Its owner asks for one thing: let customers
book a repair online, and text them when the bike is ready. This module holds
the shop's model before that request and after it, and builds both into a
repository so the tools have a real change to read.

Two readers use it. The tests of `build_preview.py` and `build_overview.py`
need a model with a base and a branch. The public site shows a newcomer what a
preview looks like, and what it shows has to be what the tool really writes -
so the site's example is generated from here, and a test holds the two
together.

**It is an illustration, not a worked model.** The worked models, of real
subjects, live in the sibling repository. This one is here because a tool that
draws a change cannot be tested, or shown, without a change to draw.

    python3 example_project.py --write <folder>   # regenerate the site's example
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PLUGIN = Path(__file__).resolve().parents[2]
SCAFFOLD = PLUGIN / "scaffold"
PREVIEW = PLUGIN / "scripts" / "build_preview.py"

STAMP = "An example · Corner Bikes is a made-up bicycle repair shop"
QUESTION = "Can a customer cancel a booking online, or only by phone?"
OPTIONS = ["Online, up to the day before", "Only by phone"]
ASSUMED = 2

FRONT = """\
# Architecture — Corner Bikes

What a neighbourhood bicycle repair shop knows about itself.
"""

MOTIVATION = """\
# Why the shop does what it does

**ArchiMate viewpoint:** Motivation.

**Status:** {status}

## Goals

```mermaid
flowchart LR
  d1["Customers phone to ask if their bike is ready [DRV1]"]
  g1["A repair is ready when we said it would be [G1]"]
  g2["Nobody waits on the phone [G2]"]
  g1 --> d1
  g2 --> d1
```

| ID | Goal | Because | Answers |
| -- | ---- | ------- | ------- |
| `G1` | **A repair is ready when we said it would be** | A late bike is a customer who cannot ride to work | `DRV1` |
| `G2` | **Nobody waits on the phone** | The person who answers is also the person at the till | `DRV1` |
{goals}
## What presses on the shop

| ID | Pressure | Seen as |
| -- | -------- | ------- |
| `DRV1` | **Customers phone to ask if their bike is ready** | Twenty calls on a busy day |
{drivers}
## Principles

| ID | Principle | Means |
| -- | --------- | ----- |
| `P1` | **A customer is asked for their details once** | The booking carries them to the workshop and to the pick-up |

## What the shop must be good at

| ID | Ability | Serves |
| -- | ------- | ------ |
| `CAP1` | **Repairing bikes** | `G1` |
| `CAP2` | **Taking bookings** | `G2`{cap2} |
| `CAP3` | **Keeping customers informed** | `G1`, `G2` |
"""

BUSINESS = """\
# Who does what

**ArchiMate viewpoint:** Business layer.

**Status:** {status}

## What the shop offers

```mermaid
flowchart LR
  r2["Front desk [ROLE2]"] --> s1["Repair booking [BSVC1]"]
  r1["Mechanic [ROLE1]"] --> s2["Repair [BSVC2]"]
```

| ID | Service | What the customer gets | Needs | Done by |
| -- | ------- | ---------------------- | ----- | ------- |
| `BSVC1` | **Repair booking** | {booking} | `CAP2` | `ROLE2` |
| `BSVC2` | **Repair** | The bike fixed by the day promised | `CAP1` | `ROLE1` |
| `BSVC3` | **Pick-up notice** | {notice} | `CAP3` | {notice_by} |

## Who works here

| ID | Role | Does |
| -- | ---- | ---- |
| `ROLE1` | **Mechanic** | Finds the fault, fixes it, says when it is done |
| `ROLE2` | **Front desk** | Takes bookings, takes payment, hands bikes back |
{rules}"""

RULES = """
## Rules the shop keeps

| ID | Rule | Applies to | Source |
| -- | ---- | ---------- | ------ |
| `RULE1` | **A text is sent only to a customer who agreed to it** | `BSVC3` | adopted — the request did not say whether every customer is texted, so only those who agreed are |
"""

INFORMATION = """\
# What the shop needs to know

**ArchiMate viewpoint:** Information structure.

**Status:** {status}

## Information

```mermaid
flowchart LR
  o1["Booking [DOBJ1]"] --> s1["Repair booking [BSVC1]"]
  o2["Customer [DOBJ2]"] --> s1
```

| ID | Information | Holds | Used by |
| -- | ----------- | ----- | ------- |
| `DOBJ1` | **Booking** | The bike, the fault and the day promised | `BSVC1`, `BSVC2` |
| `DOBJ2` | **Customer** | {customer} | `BSVC1`, `BSVC3` |
{objects}"""

REGISTER = """\
# What software does it

**ArchiMate viewpoint:** Application usage.

**Status:** ◐ Draft catalogue.

## Components

```mermaid
flowchart LR
  a1["The workshop diary [ACMP1]"] --> s1["Repair booking [BSVC1]"]
```

| ID | Application component | Serves | Specification | Realized by |
| -- | --------------------- | ------ | ------------- | ----------- |
| `ACMP1` | **The workshop diary** | `BSVC1`, `BSVC2` | The owner's notes | A shared spreadsheet on the shop computer |
{components}"""

SCOPE = """\
# Project Scope — Book a repair online

_[← Model home](../README.md)_

**ArchiMate viewpoint:** Implementation & Migration.
**Delivered as:** the pull request for this change.

Customers can book a repair online at any hour and get a text message when the
bike is ready, so nobody has to phone the shop to ask.
"""

VALID = "● Validated, 2026-03-02 — confirmed by the owner."
DRAFT = "◐ Draft catalogue."

BASE = {
    "architecture/README.md": FRONT,
    "architecture/1_strategy/1_motivation.md": MOTIVATION.format(
        status=VALID, goals="", drivers="", cap2=""),
    "architecture/2_business/1_services.md": BUSINESS.format(
        status=VALID, booking="A slot in the workshop, booked by phone or at the counter",
        notice="A phone call from the front desk when the bike is ready", notice_by="`ROLE2`", rules=""),
    "architecture/3_information/1_information.md": INFORMATION.format(
        status=VALID, customer="Name and phone number", objects=""),
    "architecture/4_application/1_realization-register.md": REGISTER.format(components=""),
}

CHANGE = {
    "architecture/1_strategy/1_motivation.md": MOTIVATION.format(
        status=DRAFT,
        goals="| `G3` | **A customer can book without calling** | Half the people who want a slot try when the shop is shut | `DRV2` |\n",
        drivers="| `DRV2` | **People try to book when the shop is shut** | Missed calls every evening and every Sunday |\n",
        cap2=", `G3`"),
    "architecture/2_business/1_services.md": BUSINESS.format(
        status=DRAFT, booking="A slot in the workshop, booked online, by phone or at the counter",
        notice="A text message when the bike is ready", notice_by="—", rules=RULES),
    "architecture/3_information/1_information.md": INFORMATION.format(
        status=DRAFT, customer="Name, phone number, and whether they agreed to be texted",
        objects="| `DOBJ3` | **Free slots** | The times the workshop can still take a bike | `BSVC1` |\n"),
    "architecture/4_application/1_realization-register.md": REGISTER.format(components=(
        "| `ACMP2` | **The booking page** | `BSVC1` | Pending — future initiative | Pending — future initiative |\n"
        "| `ACMP3` | **The text sender** | `BSVC3` | Pending — future initiative | Pending — future initiative |\n")),
    "architecture/scope/1_book-a-repair-online.md": SCOPE,
}


def _git(repo: Path, *args: str) -> None:
    subprocess.run(
        ["git", "-C", str(repo), "-c", "user.name=example", "-c", "user.email=example@example.invalid",
         "-c", "commit.gpgsign=false", *args],
        check=True, capture_output=True,
    )


def _write(repo: Path, files: dict[str, str]) -> None:
    for name, text in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


def build(root: Path, *, change: bool = True, files: dict[str, str] | None = None) -> Path:
    """The shop as a repository: the base committed, the change on disk.

    Built on the shipped scaffold, so the project is the one a new adopter
    gets and the parser is the one they would run.
    """
    repo = root / "corner-bikes"
    shutil.copytree(SCAFFOLD, repo, ignore=shutil.ignore_patterns("__pycache__"))
    _write(repo, BASE if files is None else files)
    _git(repo, "init", "-q", "-b", "main")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "the shop as it is")
    if change:
        _git(repo, "checkout", "-q", "-b", "book-online")
        _write(repo, CHANGE)
    return repo


def preview(repo: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(PREVIEW), "--project", str(repo), "--base", "main", "--stamp", STAMP,
         "--question", QUESTION, "--option", OPTIONS[0], "--option", OPTIONS[1], "--default", str(ASSUMED), *extra],
        capture_output=True, text=True,
    )


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] != "--write":
        print(__doc__)
        return 2
    target = Path(sys.argv[2]).resolve()
    target.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        repo = build(Path(tmp))
        made = preview(repo, "--name", "preview", "--to", str(Path(tmp) / "out"))
        if made.returncode != 0:
            print(made.stdout + made.stderr)
            return 1
        for name in ("preview.html", "preview.svg"):
            shutil.copyfile(Path(tmp) / "out" / name, target / name)
    print(f"Wrote the example preview to {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
