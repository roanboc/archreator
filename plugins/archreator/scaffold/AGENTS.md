# ArChreator project

Read `architecture/README.md` before changing the modeled subject. Use the
ArChreator plugin to model context, assess a change, answer an architecture
question, or plan a roadmap.

- Keep current truth in `architecture/`; put temporary scopes and briefs under
  `.archreator/work/<run>/`.
- Ask a person only when evidence leaves a gap, inconsistency, unresolved
  choice, required authorization, or required acceptance.
- Define elements in ID-first catalogues (`ID | Name | …`). Everywhere else,
  reference them as `Name [ID]` so people never have to decode a bare ID.
- Make every canonical file self-locating with a title, direct navigation and
  one `Location` line. Give each populated hierarchy level its own file and
  name `Parent` as `Name [ID]` on every nested definition.
- When modeling processes or capabilities, apply the ArChreator level profiles:
  preserve their required meaning but choose the clearest presentation.
- Create a numbered layer folder only when this repository owns content in it.
  Record out-of-scope and externally owned layers once in
  `architecture/README.md`.
- Declare each relationship once and derive diagrams, impact views, and portal
  pages from that source.
