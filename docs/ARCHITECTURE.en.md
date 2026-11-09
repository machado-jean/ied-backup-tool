# IED Backup Manager architecture

[Português](ARQUITETURA.md) | [English](ARCHITECTURE.en.md)

## Goal

The architecture separates presentation, coordination, and backup rules so
integrity-critical decisions can be tested without the Qt window.

```text
PySide6 GUI                 CLI (`src/main.py`)
       \                         /
          application and planning services
                       |
              `src/core/` domain
                       |
 project adapters + ZIP + filesystem + local configuration
```

The UI is not the source of truth for naming, identity, versioning, or file
movement. Those rules belong to the core and project-type adapters.

## Main boundaries

- `src/config/`: local `config.json` loading, validation, and persistence;
- `src/core/`: planning, execution, metadata, integrity, storage, cleanup,
  logging, internationalisation, and update checks;
- `src/core/project_types/`: manufacturer/family-specific detection, version,
  and inclusion rules;
- `src/gui/`: PySide6 presentation, workers, dialogs, and UI coordination;
- `src/main.py`: command-line entry point;
- `tests/`: behavioural regression suite.

`backup_planner.py` and `backup_service.py` build read-only plans;
`backup_executor.py`, `zipper.py`, and `storage.py` execute validated plans.
`backup_application_service.py` keeps preview validation and planning usable
without Qt widgets. Long-running preview, backup, and update operations use
dedicated workers.

## Backup flow

```text
configuration and selection
        ↓
project/version detection
        ↓
read-only plan and preview
        ↓
explicit confirmation
        ↓
temporary ZIP creation and validation
        ↓
publish current backup to ATU
        ↓
archive the previous version in HIS when required
        ↓
summary, log, and temporary cleanup
```

`ATU` holds the current backup per technical identity and `HIS` keeps previous
versions. `IEDS-BACKUP-INFO.txt` records source metadata and SHA256 hashes.
Integrity conflicts must not be silently overwritten. History cleanup requires
a preview, selection, and confirmation.

## Dependency rule

The GUI and CLI may depend on configuration and core services. The core must
not depend on Qt widgets. Project adapters implement the common core contract;
shared rules must not be copied into each adapter.

See [`ARQUITETURA.md`](ARQUITETURA.md) for the canonical detailed description,
including identity, storage, recovery, and evolution rules.
