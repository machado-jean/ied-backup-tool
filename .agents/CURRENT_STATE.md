# IED Backup Manager - Current State

Last updated: 2026-09-16

## Current Version

Current application version: `1.17.3` (release artifacts generated locally;
publication pending user commit and publisher execution)

Latest generated executable:

```text
releases/v1.17.3/IED_Backup_Manager.exe
```

The local release folder also contains `RELEASE_NOTES.md`, `SHA256SUMS.txt`, and
the generated `PUBLISH_RELEASE.ps1`. Generated release folders remain ignored by
Git and are published through GitHub Releases.

The `v1.17.3` executable, release notes, SHA256 file, and manual publisher were
generated and passed local verification. No tag or GitHub Release was created.

## Current v1.17.3 Scope

- Normalizes whitespace in the project identifier to hyphens, so the fictional
  example `SE CCC` becomes `SE-CCC`, while `_` remains the identifier delimiter.
- Keeps the `v1.17.0` readable ZIP naming policy:
  `SOFTWARE_PROJECT_YYYY-MM-DD_HHhMM_FIRST LAST_STAGE.zip`.
- Fixes Qt worker lifecycle for update checks, preview planning, and backup
  execution; workers and threads use controlled deferred deletion.
- Logs thread shutdown, `QApplication about to quit`, and the Qt event-loop exit
  code so a normal close is distinguishable from abrupt termination.
- Stores one UUID marker per running instance under
  `%LOCALAPPDATA%\IED Backup Manager\logs\sessions\`, with PID, process start
  time, executable path, and a 10-second heartbeat. Concurrent copies cannot
  overwrite one another.
- Removes clean/handled markers immediately, expires unresolved markers after
  30 days, and keeps at most 20 unresolved markers per executable path.
- On the next startup after an unclean same-path session whose process is no
  longer active, shows the originating path and asks for consent before reading
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
pytest: 154 passed
PowerShell syntax validation: passed
PUBLISH_RELEASE.ps1 -VerifyOnly: passed
latest packaged executable smoke test (v1.17.3): exit code 0, no remaining
session marker, and no Windows Application crash event 1000/1001
```

Latest generated executable:

```text
size: 47,546,714 bytes
SHA256: 0D6DFD250192931FD7CD6F906D0419DD61C29B61E1B73825401507D145B9FB2E
```

## Active Roadmap

Planned next minor milestone after `v1.17.3`:

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
