# IED Backup Manager - Current State

Last updated: 2026-09-14

## Current Version

Current application version: `1.17.1`

Latest generated executable:

```text
releases/v1.17.1/IED_Backup_Manager.exe
```

The local release folder also contains `RELEASE_NOTES.md`, `SHA256SUMS.txt`, and
the generated `PUBLISH_RELEASE.ps1`. Generated release folders remain ignored by
Git and are published through GitHub Releases.

## Current v1.17.1 Scope

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
- Adds a Windows GitHub Actions workflow named `CI` for `master`, pull requests,
  and `v*` tags.
- `scripts/release.ps1` builds the executable and generates notes, SHA256, and a
  per-release publisher, then runs local `-VerifyOnly` validation.
- The publisher requires a clean, synchronized `master` with green CI, creates
  the GitHub Release/tag, verifies uploaded assets, and waits for tag CI.

## Validation Baseline

Latest known validation:

```text
ruff check .: passed
pytest: 142 passed
PowerShell syntax validation: passed
PUBLISH_RELEASE.ps1 -VerifyOnly: passed
packaged executable smoke test: exit code 0
```

Latest generated executable before the final documentation-only rebuild was
approximately 47.5 MB. Always report the exact final size and SHA256 after the
last build.

## Active Roadmap

Planned next minor milestone after `v1.17.1`:

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
