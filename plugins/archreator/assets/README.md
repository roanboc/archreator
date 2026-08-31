# Assets

Templates a skill emits into a project **when that project has something to put
in them.** Nothing here ships on the first commit.

This is the half of the old scaffold that was arriving empty. A generated
project used to receive forty-four files and six and a half thousand lines
before anybody had said a word about the project itself — seven layer READMEs
with nothing in them, two workflows that did not run where they sat, a question
form for a comment box nobody had switched on. Emptiness is not structure, and
a folder is not a plan.

So the structure lives here, where an agent reads it, and a project's
`architecture/README.md` carries a status row per layer instead: `Local`,
`External`, `Out of scope`, or a named `Gap`. A missing layer becomes a stated
fact, which an empty README never was.

| Asset | Emitted by | When |
| ----- | ---------- | ---- |
| [`layers/1_strategy/`](./layers/1_strategy/README.md) | `discover-strategy` | The strategy layer is first filled |
| [`layers/2_business/`](./layers/2_business/README.md) · [`layers/3_information/`](./layers/3_information/README.md) | `align-change-through-layers`, `discover-current-landscape` | The layer first has an element to hold |
| [`layers/4_application/`](./layers/4_application/README.md) · [`layers/5_technology/`](./layers/5_technology/README.md) | `align-change-through-layers`, `discover-current-landscape` | The layer first has an element to hold |
| [`layers/0_business-design/`](./layers/0_business-design/README.md) | `discover-business-model` | The subject is an organization — Depth 2 and 3 |
| [`layers/6_transition/`](./layers/6_transition/README.md) | `plan-the-transition` | A target state is first described |
| [`layers/scope/`](./layers/scope/README.md) | `write-scope-document` | The first initiative is opened |
| [`layers/decisions/`](./layers/decisions/README.md) | `record-decision` | The first decision is recorded |
| [`layers/domains/`](./layers/domains/README.md) | `model-domains` | The model splits into business lines — Depth 3 |
| [`layers/reference/`](./layers/reference/README.md) | `discover-current-landscape`, `discover-business-model` | Source material is first filed |
| [`layers/federation.md`](./layers/federation.md) · [`layers/imports.md`](./layers/imports.md) | `model-domains` | This model first names another one |
| [`github/workflows/`](./github/workflows/README.md) | `establish-project` | The project is on GitHub and asks for CI |
| [`github/pull_request_template.md`](./github/pull_request_template.md) | `establish-project` | The project takes pull requests |
| [`CONTRIBUTING.md`](./CONTRIBUTING.md) | `establish-project` | The project will take contributions from more than its owner |

## Their links resolve where they land, not here

A template links the way the emitted copy needs to — `../README.md` means the
project's architecture front door. Resolving those here would be asking whether
they work in the one place they were never meant to, so `check_links.py` skips
this tree and the project's own copy of it checks the copy that matters.

What that would let rot instead is caught by `check_skills.py`: an asset no
skill emits, and a skill naming an asset that is not here, are both errors.
