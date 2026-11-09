# Documentation index

This is the maintenance and continuity entry point for IED Backup Manager. When
permanent documentation is created, moved, or removed, update the Portuguese
index [`README.md`](README.md) in the same change. Source code and tests remain
the source of truth for executable behaviour.

[Português](README.md) | [English](README.en.md)

## Development continuity

| Document | Purpose |
| --- | --- |
| [`AGENTS.md`](../AGENTS.md) | Permanent repository context, invariants, and working rules. |
| [`ARCHITECTURE.en.md`](ARCHITECTURE.en.md) | Components, dependencies, flows, and system boundaries. |
| [`DEVELOPMENT_ENVIRONMENT.en.md`](DEVELOPMENT_ENVIRONMENT.en.md) | Reproducible workstation setup and development commands. |
| [`CONTINUITY.en.md`](CONTINUITY.en.md) | Migration, backup, and project recovery. |
| [`DEVELOPMENT_RESUME_PROMPT.en.md`](DEVELOPMENT_RESUME_PROMPT.en.md) | Ready-to-use prompt for resuming work on another computer or agent. |
| [`project-continuity-kit/`](../project-continuity-kit/README.md) | Self-contained checklist and generic templates that can be copied to other projects. |
| [`CURRENT_STATE.en.md`](CURRENT_STATE.en.md) | Current version, validation, pending work, and restart point. |
| [`ROADMAP.en.md`](ROADMAP.en.md) | Active roadmap and implemented milestones. |
| [`RELEASE.md`](RELEASE.md) | Canonical build, verification, tag, and release-publication procedure. |
| [`decisions/README.md`](decisions/README.md) | Architecture decision record catalogue. |

The complete catalogue, including user, support, security, privacy, examples,
and root documents, is maintained in the Portuguese index because it already
links both language variants.

## Maintenance rule

- Link to canonical sources instead of duplicating facts.
- Never record secrets, real IED data, corporate paths, or personal content.
- Preserve historical ADRs; supersede them with a new decision.
- Treat `CURRENT_STATE.en.md` as a restart snapshot, not a full transcript.
- Keep Portuguese and English documents equivalent for public-facing changes.
