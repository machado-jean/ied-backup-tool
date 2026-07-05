# IED Backup Manager - Project Context

Use this file as the first source of truth when resuming work in a new Codex
conversation.

## Objective

IED Backup Manager is a Windows application that standardizes IED project
backups. It keeps the current backup in `ATU`, historical backups in `HIS`, and
generates consistent ZIP names for technical traceability.

## Current Product Rules

- The executable normally stays in the folder that contains the working project
  files.
- The application/project identifier is the text before the first underscore
  `"_"`.
- Text after the first underscore is treated as user comment and is not part of
  the backup technical key.
- `ATU` contains the current backup for each technical key.
- `HIS` contains older backups and prevents duplicate technical identities.
- Technical key: `SOFTWARE_PROJECT`.
- Technical identity: `SOFTWARE_PROJECT_TIMESTAMP`.
- Collaborator and stage are part of the ZIP name, but not part of technical
  identity.

## Supported IED Types

- Siemens DIGSI: `.dz5`
- SEL QuickSet / Architect: `.rdb`, with optional `.scd` or `.selaprj`
- ABB PCM600: `.pcmp`, `.apcmp`
- INGETEAM INGESYS: `.efsPro`, `.ITPro2`

## Backup Metadata

Every generated ZIP contains `IEDS-BACKUP-INFO.txt`.

It includes backup name, project, software/version, timestamp, collaborator,
stage, detected versions, included files, source file modification time, source
file size, and source file SHA256.

The source-file SHA256 must not be added to the ZIP filename.

## Integrity Rules

Since `v1.6.0`, the app checks ZIPs with the same technical identity in `ATU`
and `HIS`.

If the existing ZIP has SHA256 metadata and the current source files produce
different SHA256 values, the preview shows `Conflito SHA` / `SHA conflict` and
blocks execution.

Old ZIPs without `IEDS-BACKUP-INFO.txt` or without SHA256 metadata remain
compatible and are not marked as conflicts.

## Architecture

- GUI entrypoint: `src/gui/app.py`
- Main GUI window: `src/gui/main_window.py`
- Core planning/execution rules: `src/core/backup_service.py`
- ATU/HIS storage rules: `src/core/storage.py`
- ZIP creation: `src/core/zipper.py`
- Integrity helpers: `src/core/integrity.py`
- Project type registry: `src/core/project_types/registry.py`
- Project-specific adapters: `src/core/project_types/`
- CLI entrypoint: `src/main.py`

## Local Workspace Folders

These are intentionally local/ignored and may contain real files:

- design/source backup folder;
- current-backup folder;
- historical-backup folder;
- local `config.json`.

Do not sanitize, delete, or rename local backup folders unless the user
explicitly asks for it. They may contain real operational files that should not
be committed.

## Commands

Run GUI in development:

```powershell
.\.venv\Scripts\python.exe -m src.gui.app
```

Run GUI against a specific local source folder:

```powershell
.\.venv\Scripts\python.exe -m src.gui.app --project-dir ".\SOURCE-FOLDER"
```

Run CLI dry-run:

```powershell
.\.venv\Scripts\python.exe -m src.main --project-dir ".\SOURCE-FOLDER" --process-all --dry-run --collaborator "COLABORADOR-EXEMPLO" --atu-path ".\ATU-FOLDER" --his-path ".\HIS-FOLDER"
```

Validate:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
```

Generate release executable:

```powershell
.\scripts\release.ps1
```

## Working Style

- Prefer small, versioned changes.
- Before generating an executable, update `src/version.py`, `README.md`,
  `.agents/CURRENT_STATE.md`, and `releases/vX.Y.Z/RELEASE_NOTES.md`.
- When the user asks to generate the `.exe`, generate it directly using
  `scripts/release.ps1` unless there is a clear blocker.
- After running tests or builds, remove generated caches/build folders when they
  are not needed: `.pytest_cache`, `.ruff_cache`, `__pycache__`, `build`, `dist`.
