# IED Backup Manager - Current State

Last updated: 2026-07-05

## Current Version

Current application version: `1.7.0`

The `v1.7.0` release combines all changes made after `v1.6.0`.

Latest generated executable:

```text
releases/v1.7.0/IED Backup Manager v1.7.0.exe
```

## Recently Completed

- `v1.5.3`: warning for `ATU`/`HIS` in common cloud-synced folders.
- `v1.5.4`: ABB PCM600 support expanded from `.pcmp` to `.pcmp` and `.apcmp`.
- `v1.5.5`: splash screen and startup ordering fix.
- `v1.6.0`: advanced SHA256 integrity check.
- `v1.7.0`: more transactional ATU/HIS movement and real per-file byte progress
  during ZIP creation and final copy.

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
pytest: 77 passed
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

## Next Planned Work

Planned next improvement after `v1.7.0`:

```text
Worker-thread execution and controlled cancellation
```

Likely scope:

- execute backup processing in a worker thread;
- keep the GUI responsive during large backups;
- prepare controlled cancellation before starting the next file.
