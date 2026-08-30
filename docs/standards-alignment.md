# Standards alignment

_[Repository README](../README.md) · [The method](./method.md)_

ArChreator uses established architecture concepts where they improve shared
understanding and keeps its deliberate deviations visible.

| ArChreator concept | Established basis | Use in the method |
| --- | --- | --- |
| Strategy, Business, Application and Technology | ArchiMate layers and Motivation elements | Canonical element types and relationships remain secondary metadata |
| Information area | Data architecture and information ownership | Kept separate because meaning and ownership should be understood before software representation |
| Enterprise, Domain and Solution levels | Architecture partitioning and levels of detail | Each level owns facts once and refines exposed parent contracts |
| Plateau and Gap | ArchiMate Implementation and Migration elements | Used only when a real roadmap and transition exist |
| Mermaid views | No native Mermaid ArchiMate profile | Plain labels lead; type, relationship and source remain in canonical tables |
| Decision records | Architecture Decision Records | Created only when durable rationale will matter later |
| One source per fact | Single source of truth and living documentation | Repository, briefs and portal derive from the same Markdown |

The complete metadata and identifier convention is maintained in the
[`architecture-document-style` model structure](../plugins/archreator/skills/architecture-document-style/references/model-structure.md).
The matching [ArchiMate-on-Mermaid reference](../plugins/archreator/skills/architecture-document-style/references/archimate-on-mermaid.md)
defines the visual mapping once so diagrams stay recognizable without repeated
legends in every document. The [hierarchical-element rules](../plugins/archreator/skills/architecture-document-style/references/hierarchical-elements.md)
make level and parent context explicit for people even though the ID also
encodes it. The [process presentation profiles](../plugins/archreator/skills/process-and-capability-levels/references/process-presentation-patterns.md)
apply the same principle to process depth: stable meaning at each level with a
flexible page layout.
