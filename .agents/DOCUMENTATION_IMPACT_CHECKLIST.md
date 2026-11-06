# Documentation Impact Checklist

Use this index for every behavior, interface, packaging, or release change.
Review every row and record why it is impacted or not impacted. Public examples
must remain fictional and generic.

## Previous v1.18.0 Change

Released change: family-based current-backup identity, explicit choice for
different individual software families, and coverage-aware `IED-PACK`
replacement.

| Document | Audience | Impact | Current action |
| --- | --- | --- | --- |
| `README.md` | Public PT-BR landing page | Yes | Updated storage and choice overview. |
| `README.en.md` | Public English landing page | Yes | Updated storage and choice overview. |
| `docs/USO_EXECUTAVEL.md` | Detailed PT-BR operation | Yes | Updated preview status, actions, confirmations, and package behavior. |
| `docs/EXECUTABLE_USAGE.en.md` | Detailed English operation | Yes | Updated storage, actions, confirmations, and package behavior. |
| `docs/HELP.md` | In-app PT-BR help | Yes | Updated operator guidance. |
| `docs/HELP.en.md` | In-app English help | Yes | Updated operator guidance. |
| `docs/LOGICA_IDENTIFICACAO_IEDS.md` | PT-BR technical identification | Yes | Updated current key, historical identity, families, and package coverage. |
| `docs/IED_IDENTIFICATION_LOGIC.en.md` | English technical identification | Yes | Updated current key, historical identity, families, and package coverage. |
| `docs/PLANO_MELHORIAS.md` | PT-BR roadmap | Yes | Reserved `v1.18.0` for this workflow and moved new IED types to `v1.19.0`. |
| `docs/ROADMAP.en.md` | English roadmap | Yes | Mirrored roadmap change. |
| `docs/IED Backup Manager.docx` | Printable PT-BR manual | Yes | Updated, metadata-scrubbed, rendered to 10 pages, and visually verified page by page. |
| `docs/images/*.png` | Public visual documentation | Yes | Regenerated all existing captures under `C:\IED-Backup-Manager-Demo` and added the decision dialog; visually verified. |
| `scripts/capture_documentation_screenshots.py` | Reproducible documentation tooling | Yes | Can prepare the sanitized demo and capture the new dialog. |
| `docs/examples/README.md` | Artificial sample instructions | No | Sample files and manual versions are unchanged. |
| `CONTRIBUTING.md` | PT-BR contributors | No | Contribution and validation workflow are unchanged. |
| `CONTRIBUTING.en.md` | English contributors | No | Contribution and validation workflow are unchanged. |
| `.agents/PROJECT_CONTEXT.md` | Maintainer context | Yes | Updated product and roadmap rules. |
| `.agents/DECISIONS.md` | Durable technical decisions | Yes | Replaced the current-key decision and recorded ambiguity handling. |
| `.agents/CURRENT_STATE.md` | Current development state | Yes | Recorded the approved `v1.18.0` release build and validation state. |
| `.agents/HOW_TO_WORK_WITH_CODEX.md` | Collaboration procedure | No | The working procedure is unchanged. |
| `.agents/RELEASE_CHECKLIST.md` | Release procedure | No | Packaging and publication gates are unchanged. |
| `.github/ISSUE_TEMPLATE/bug_report.md` | Public issue intake | No | Bug-report fields remain sufficient. |
| `.github/ISSUE_TEMPLATE/feature_request.md` | Public feature intake | No | Feature-request fields remain sufficient. |
| `.github/ISSUE_TEMPLATE/new_ied_type.md` | New-adapter intake | No | Adapter evidence requirements are unchanged. |
| `.github/pull_request_template.md` | Pull requests | No | Existing test and documentation checks remain sufficient. |

## Post-release Corrective Change Review

Change reviewed: native Windows TLS trust for update checks, Windows 10 theme
consistency, and a PowerShell 5.1-compatible sanitized diagnostic collector.

| Document | Impact | Current action |
| --- | --- | --- |
| `README.md` / `README.en.md` | Yes | Linked the support collection guide. |
| `docs/USO_EXECUTAVEL.md` / `docs/EXECUTABLE_USAGE.en.md` | Yes | Documented secure native certificate trust and troubleshooting. |
| `docs/HELP.md` / `docs/HELP.en.md` | Yes | Added missing-update-notice guidance. |
| `docs/COLETA_DIAGNOSTICO.md` / `docs/DIAGNOSTIC_COLLECTION.en.md` | Yes | Added the sanitized ZIP workflow for nontechnical users. |
| Roadmaps and identification logic | No | Product roadmap and backup identity behavior are unchanged. |
| Printable manual | No | The operational workflow and manual instructions are unchanged. |
| `docs/images/*.png` | Yes | Regenerated from a sanitized generic workspace and visually verified with the final typography and themes. |
| Release procedure | Yes | Publishes and hash-verifies the matched diagnostic-tool ZIP as a release asset. |
| Contributor procedures | No | Contribution requirements remain unchanged. |
| `.agents` maintainer records | Yes | Recorded the security decision and current development state. |

## v1.18.1 Release Review Completed

- Version references and maintainer state were updated to `v1.18.1`.
- Generic release notes were reviewed for operational identifiers.
- All seven public screenshots were regenerated from generic sample data and
  visually checked in both themes.
- The diagnostic-tool ZIP and executable are hash-verified release assets.
- Every corrective-change row above was reviewed for the final release diff.
