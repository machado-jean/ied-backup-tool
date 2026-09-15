# IED Backup Manager - Current State

Last updated: 2026-09-15

## Current Version

Current application version: `1.17.2`

Latest generated executable:

```text
releases/v1.17.2/IED_Backup_Manager.exe
```

The local release folder also contains `RELEASE_NOTES.md`, `SHA256SUMS.txt`, and
the generated `PUBLISH_RELEASE.ps1`. Generated release folders remain ignored by
Git and are published through GitHub Releases.

## Current v1.17.2 Scope

- Keeps the `v1.17.0` readable ZIP naming policy:
  `SOFTWARE_PROJECT_YYYY-MM-DD_HHhMM_FIRST LAST_STAGE.zip`.
- Fixes Qt worker lifecycle for update checks, preview planning, and backup
  execution; workers and threads use controlled deferred deletion.
- Logs thread shutdown, `QApplication about to quit`, and the Qt event-loop exit
  code so a normal close is distinguishable from abrupt termination.
- Stores a per-user session marker and 10-second heartbeat under
  `%LOCALAPPDATA%\IED Backup Manager\logs\`.
- On the next startup after an unclean session, asks for consent before reading
  Windows Application events. Declining performs no event query.
- With consent, queries only event IDs 1000/1001 within ±2 minutes of the last
  heartbeat and filters by executable name/path. It stores only sanitized event
  fields in the local log; it does not access dumps, upload data, or request UAC.
- Keeps the update notice's direct executable download and adds a separate
  `O que há de novo?` / `What's new?` link to the specific GitHub release page.
- Adds a persistent light/dark theme toggle that follows the system until the
  user makes an explicit choice, while preserving identical interface geometry.
- Improves theme contrast, field borders, status colors, progress bars,
  tooltips, and the stage dropdown frame/padding.
- Uses current GitHub Actions releases compatible with Node.js 24.
- Keeps a Windows GitHub Actions workflow named `CI` for `master`, pull
  requests, and `v*` tags.
- `scripts/release.ps1` builds the executable and generates notes, SHA256, and a
  per-release publisher, then runs local `-VerifyOnly` validation.
- The publisher requires a clean, synchronized `master`, local lint/tests,
  green CI on `master`, and green tag CI for the exact commit. It then prints a
  `CORRETO`/`INCORRETO` report and asks for final confirmation before creating
  the GitHub Release and uploading assets.

## Validation Baseline

Latest known validation:

```text
ruff check .: passed
pytest: 148 passed
PowerShell syntax validation: passed
PUBLISH_RELEASE.ps1 -VerifyOnly: passed
packaged executable smoke test: exit code 0
```

Latest generated executable:

```text
size: 47,538,812 bytes
SHA256: 82D67F9CA78E261A967706E285383BCD876A5BF49305FF3F2589A34165F09A30
```

## Active Roadmap

Planned next minor milestone after `v1.17.2`:

```text
v1.18.0 - new IED types
```

Add new types only with clean/sanitized samples and reliable identification,
version, and included-file rules. Continue focused patch releases for concrete
stability, diagnostics, usability, and documentation issues.

Paused/out-of-scope items remain code signing, operational reports, external
per-backup `.sha256` files, and automatic executable replacement.

## Local Safety

- Never commit real backups, local `config.json`, `.venv`, `build`, `dist`, or
  generated `releases/` contents.
- Never send diagnostic logs automatically. Users decide whether to authorize
  the narrow Windows event query and whether to share the resulting local log.
- Keep HIS deletion manual and confirmed through the cleanup dialog.
- Follow `.agents/RELEASE_CHECKLIST.md` for every executable/release task.
