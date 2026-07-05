# IED Backup Manager - Current State

Last updated: 2026-07-04

## Current Version

Current application version: `1.6.0`

Latest generated executable:

```text
releases/v1.6.0/IED Backup Manager v1.6.0.exe
```

## Recently Completed

- `v1.5.3`: warning for `ATU`/`HIS` in common cloud-synced folders.
- `v1.5.4`: ABB PCM600 support expanded from `.pcmp` to `.pcmp` and `.apcmp`.
- `v1.5.5`: splash screen and startup ordering fix.
- `v1.6.0`: advanced SHA256 integrity check.

## Current v1.6.0 Scope

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
pytest: 73 passed
```

## Local-Safety Notes

- Local source/current/history folders may contain real or sensitive files and
  must remain ignored by Git.
- Local `config.json` files are user-specific and should not be committed.
- Previously generated ZIPs created before the storage-permission fix may need
  manual deletion/recreation or ACL repair if Windows denies access to them.

## Next Planned Work

Planned next minor release:

```text
v1.7.0 - More transactional ATU/HIS movement
```

Likely scope:

- validate the newly created ZIP before touching `ATU`;
- validate readable destination file after final placement;
- handle blocked destination files more clearly;
- consider rollback/quarantine when archiving current `ATU` to `HIS` fails.
