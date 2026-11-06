# IED Backup Manager - Current State

Last updated: 2026-11-06

## Current Version

Current application version: `1.18.1`.

The user approved the family-based identity workflow and the updated printable
manual. Packaging is complete. The generated release remains local until the
tracked changes are committed and pushed and the user runs the generated
publisher manually.

Expected release assets:

```text
releases/v1.18.1/IED_Backup_Manager.exe
releases/v1.18.1/IED_Backup_Manager_Diagnostics_Tool.zip
releases/v1.18.1/RELEASE_NOTES.md
releases/v1.18.1/SHA256SUMS.txt
releases/v1.18.1/PUBLISH_RELEASE.ps1
```

Generated release folders remain ignored by Git and are published through
GitHub Releases.

## Current v1.18.1 Patch Scope

- Update checks now use `truststore` and the native Windows certificate store,
  preserving certificate and hostname validation in packaged executables.
- The startup log identifies the native operating-system TLS trust source.
- A support collector can open an executable for 10 seconds and create a
  sanitized ZIP for the user to send directly to the maintainer, without UAC,
  Git, Python, automatic upload, backups, configuration, or credentials.
- Automatic system-theme selection now applies a complete matching palette on
  Windows 10 instead of mixing the native light palette with dark controls.
- The native title bar follows the selected theme through the Windows 11 DWM
  attribute with the compatible Windows 10 fallback.
- Internal typography uses Segoe UI 10 pt with stronger group titles and table
  headers for readable Windows 10/11 rendering at 96 DPI.
- Diagnostic JSON is written without a BOM for Windows PowerShell 5.1, while
  application config loading also tolerates UTF-8 BOM input.
- Diagnostic collector `1.1.0` validates CMD/PS1 compatibility, reports
  OK/FAIL states, records sanitized display/theme/timing data, and is packaged
  as a hash-verified GitHub Release asset.
- The packaged candidate passed smoke testing and local release verification.

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
pytest: 176 passed
git diff --check: passed (line-ending normalization warnings only)
public screenshots: regenerated and visually verified with generic data
PowerShell syntax validation: passed
PUBLISH_RELEASE.ps1 -VerifyOnly: passed
packaged executable smoke test: exit code 0 and no remaining session marker
collector 1.1.0: PowerShell 5.1 end-to-end and version mismatch tests passed
```

Latest generated executable:

```text
size: 48,015,372 bytes
SHA256: 141145FC794FF55AD00D527D44A6F04643ADC98C681AFF105674C20C2BD67386
diagnostic ZIP size: 9,367 bytes
diagnostic ZIP SHA256: E9939F9AAEBE0025973D6B700E73FEA812807CBC3C69C37570F8AD0908B5BB87
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
