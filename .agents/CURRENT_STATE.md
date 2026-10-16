# IED Backup Manager - Current State

Last updated: 2026-10-16

## Current Version

Current application version: `1.18.0`.

The user approved the family-based identity workflow and the updated printable
manual. Packaging is complete. The generated release remains local until the
tracked changes are committed and pushed and the user runs the generated
publisher manually.

Expected release assets:

```text
releases/v1.18.0/IED_Backup_Manager.exe
releases/v1.18.0/RELEASE_NOTES.md
releases/v1.18.0/SHA256SUMS.txt
releases/v1.18.0/PUBLISH_RELEASE.ps1
```

Generated release folders remain ignored by Git and are published through
GitHub Releases.

## Current v1.18.0 Scope

- Uses `SOFTWARE_FAMILY_PROJECT` as the current-backup key while preserving the
  complete software/version in historical identity.
- Treats a version change in the same software family as an update and archives
  the previous current backup automatically.
- Requires an explicit `keep both`, `replace existing`, or `cancel` choice when
  the same project first appears under another individual software family.
- Requires a second confirmation before replacing another software family.
- Prevents unresolved choices from executing through CLI, worker, or GUI
  fallback behavior.
- Prevents an individual backup from silently replacing an existing `IED-PACK`.
- Archives only covered individual families when generating a new `IED-PACK`.
- Adds the decision-needed preview state and bilingual dialog content.
- Updates public Markdown documentation, sanitized screenshots, the printable
  manual, roadmap, maintainer records, and documentation impact index.

## Validation Baseline

Latest release validation:

```text
ruff check .: passed
pytest: 171 passed
git diff --check: passed (line-ending normalization warnings only)
printable DOCX: rendered to 10 pages and visually verified
public examples/screenshots: reviewed for generic data
PowerShell syntax validation: passed
PUBLISH_RELEASE.ps1 -VerifyOnly: passed
packaged executable smoke test: exit code 0 and no remaining session marker
```

Latest generated executable:

```text
size: 47,553,113 bytes
SHA256: E66587A75EE0F0AC700358B234B7246DAFCEF344C2F72974FB1CABD958063FC4
```

The release tooling now aborts immediately when lint, tests, or PyInstaller
fails. Both the builder and generated publisher isolate Python/pytest temporary
files inside the project during validation and remove them afterward.

## Active Roadmap

The next planned minor milestone is:

```text
v1.19.0 - new IED types
```

Add new types only with clean/sanitized samples and reliable identification,
version, and included-file rules. Focused patch releases may continue for
concrete stability, diagnostics, usability, and documentation issues.

Paused/out-of-scope items remain code signing, operational reports, external
per-backup `.sha256` files, and automatic executable replacement.

## Local Safety

- Never commit real backups, local `config.json`, `.venv`, `build`, `dist`, or
  generated `releases/` contents.
- Never send diagnostic logs automatically. Users decide whether to authorize
  the narrow Windows event query and whether to share the resulting local log.
- Keep HIS deletion manual and confirmed through the cleanup dialog.
- Follow `.agents/RELEASE_CHECKLIST.md` for every executable/release task.
