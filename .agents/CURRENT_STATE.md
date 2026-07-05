# IED Backup Manager - Current State

Last updated: 2026-07-05

## Current Version

Current application version: `1.10.2`

The `v1.10.2` executable has been generated.

Latest generated executable:

```text
releases/v1.10.2/IED Backup Manager.exe
```

## Recently Completed

- `v1.5.3`: warning for `ATU`/`HIS` in common cloud-synced folders.
- `v1.5.4`: ABB PCM600 support expanded from `.pcmp` to `.pcmp` and `.apcmp`.
- `v1.5.5`: splash screen and startup ordering fix.
- `v1.6.0`: advanced SHA256 integrity check.
- `v1.7.0`: more transactional ATU/HIS movement and real per-file byte progress
  during ZIP creation and final copy.
- `v1.8.0`: worker-thread execution and controlled cancellation.
- `v1.9.0`: public/professional user documentation and in-app help access.
- `v1.9.1`: in-app help points to the public GitHub `HELP.md`.
- `v1.10.0`: automatic GitHub release check with clickable update notice.
- `v1.10.1`: fixed distributed executable name for simpler updates and latest
  download URLs.
- `v1.10.2`: non-commercial license file, public license documentation, and
  clickable copyright notice in the GUI.

## Current v1.6.0 Released Scope

- Reads SHA256 values from `IEDS-BACKUP-INFO.txt` in existing ZIPs.
- Detects same technical identity with different source-file SHA256 values.
- Shows `Conflito SHA` / `SHA conflict` in the batch preview.
- Blocks execution while an integrity conflict exists.
- Checks conflicts in both `ATU` and `HIS`.
- Keeps legacy ZIPs without SHA metadata compatible.
- Recreates final ZIP files inside destination folders to inherit `ATU`/`HIS`
  permissions instead of preserving temporary-file ACLs.

## Validation Baseline

Latest known validation:

```text
ruff check .: passed
pytest: 86 passed
```

## Local-Safety Notes

- Local source/current/history folders may contain real or sensitive files and
  must remain ignored by Git.
- Local `config.json` files are user-specific and should not be committed.
- Previously generated ZIPs created before the storage-permission fix may need
  manual deletion/recreation or ACL repair if Windows denies access to them.

## Current v1.7.0 Scope

- Validates staged ZIPs before touching `ATU`/`HIS`.
- Copies new ZIPs into a temporary file inside the destination folder and
  validates them before publishing the final name.
- Publishes the new ATU backup before archiving the previous current backup, and
  removes the new ATU backup if archiving the previous current backup fails.
- Creates missing history backups in a temporary staging folder before placing
  them in `HIS`.
- Rejects silent overwrite when a destination ZIP already exists unexpectedly.
- Shows `file X/N` while generating backups.
- Updates the progress bar by bytes during ZIP creation.
- Updates the progress bar by bytes while copying the final ZIP into `ATU`/`HIS`.
- Keeps duplicate correction progress tied to actual copy bytes when duplicate
  files are moved to `HIS`.

## Current v1.8.0 Scope

- Runs backup execution in a `QThread` worker instead of the GUI thread.
- Updates the progress dialog through Qt signals.
- Keeps the GUI event loop responsive while large files are being processed.
- Allows cancellation before the next backup file starts.
- If cancellation is requested while ZIP staging is running, the staged ZIP is
  discarded and the backup is not published to `ATU`/`HIS`.
- Does not interrupt a final destination copy midway, preserving transactional
  storage behavior.

## Current v1.9.0 Scope

- Adds `docs/HELP.md` with operational usage, folder structure, naming policy,
  supported IED types, output examples, ZIP metadata example, known limitations,
  troubleshooting, and privacy guidance.
- Adds an `Ajuda` / `Help` button to the main window.
- Bundles `docs/HELP.md` into the PyInstaller executable.
- Updates README, executable-use documentation, improvement roadmap, release
  notes, and agent context.

## Current v1.9.1 Scope

- Changes the main-window `Ajuda` / `Help` button to open the public GitHub
  document:
  `https://github.com/machado-jean/ied-backup-tool/blob/master/docs/HELP.md`.
- Removes `docs/HELP.md` from PyInstaller bundled data because the online
  document is now the single help target.
- Keeps the local `docs/HELP.md` in the repository as the public source
  document.

## Current v1.10.0 Scope

- On startup, a background Qt worker checks the latest public GitHub release.
- If a newer version exists, the main window shows a red clickable notice in
  the bottom-left corner.
- Clicking the notice opens the GitHub `/releases/latest` URL in the default
  browser.
- No message is shown when the installed version is current.
- Internet, proxy, corporate block, or GitHub errors are silent and do not block
  application startup or backup use.
- Automatic download/replacement remains out of scope.

## Current v1.10.1 Scope

- Release script generates and copies `IED Backup Manager.exe` instead of a
  versioned executable filename.
- Version remains visible in the window title and splash screen through
  `APP_VERSION`.
- Release folders remain versioned as `releases/vX.Y.Z/`.
- GitHub can expose a stable latest-download URL:
  `https://github.com/machado-jean/ied-backup-tool/releases/latest/download/IED%20Backup%20Manager.exe`.

## Current v1.10.2 Scope

- Adds `LICENSE` with the `IED Backup Manager Non-Commercial License`.
- Adds license notes to README, executable-use documentation, and public help.
- Adds a clickable `©` indicator in the bottom-right corner of the GUI.
- Clicking `©` shows a compact authorship/license note and repository link.

## Next Planned Work

Planned next improvement after `v1.10.2`:

```text
public-repository sensitivity review and repository polish
```

Likely scope:

- scan public docs/code for real names, real substations, internal paths, and
  sensitive samples;
- confirm ignored local folders are not staged;
- update release notes with the review result.
