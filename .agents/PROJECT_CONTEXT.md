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
- When multiple IED types are selected, `IED-PACK` is created only for projects
  that actually have more than one selected type present. If only one real type
  exists for the project, process all files of that type unless the user checked
  `Processar apenas a partir do backup atual`.

## Supported IED Types

- Siemens DIGSI: `.dz5`
- SEL QuickSet / Architect: `.rdb`, with optional `.scd` or `.selaprj`
- ABB PCM600: `.pcmp`, `.apcmp`
- INGETEAM INGESYS: `.efsPro`, `.ITPro2`
- GE Multilin / EnerVista UR: direct child folders containing `.urs` or `.urk`;
  optional top-level `.ENV`
  - ZIP names use the highest IED/application `GEMULTILIN` version found in
    `.urs/.urk` headers.
  - `GE UR Setup` versions from `.cid/.icd` are metadata only.

## Backup Metadata

Every generated ZIP contains `IEDS-BACKUP-INFO.txt`.

It includes backup name, project, software/version, timestamp, collaborator,
stage, detected versions, included files, source file modification time, source
file size, and source file SHA256.

The source-file SHA256 must not be added to the ZIP filename.

For GE Multilin backups, `IEDS-BACKUP-INFO.txt` also includes a GE IED summary
with the environment folder, optional `.ENV` versions, included IED folders,
the GE UR Setup version used to develop each IED when available, and the
IED/application version from `.urs`/`.urk` headers.

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
- Startup instructions dialog: `src/gui/startup_instructions.py`
- GUI application service: `src/gui/backup_application_service.py`
- GUI confirmation text builders: `src/gui/backup_confirmation.py`
- GUI HIS cleanup dialog: `src/gui/history_cleanup_window.py`
- GUI preview-table rendering: `src/gui/preview_table.py`
- GUI summary text formatting: `src/gui/summary_text.py`
- User help documents: `docs/HELP.md` and `docs/HELP.en.md`
- IED identification logic documents: `docs/LOGICA_IDENTIFICACAO_IEDS.md` and
  `docs/IED_IDENTIFICATION_LOGIC.en.md`
- Public help URLs:
  `https://github.com/machado-jean/ied-backup-tool/blob/master/docs/HELP.md`
  and
  `https://github.com/machado-jean/ied-backup-tool/blob/master/docs/HELP.en.md`
- Public latest-release API:
  `https://api.github.com/repos/machado-jean/ied-backup-tool/releases/latest`
- Public latest-release page:
  `https://github.com/machado-jean/ied-backup-tool/releases/latest`
- Public latest executable download:
  `https://github.com/machado-jean/ied-backup-tool/releases/latest/download/IED_Backup_Manager.exe`
- License file: `LICENSE`
- Core planning/execution rules: `src/core/backup_service.py`
- HIS cleanup rules: `src/core/history_cleanup.py`
- Backup data models/status constants: `src/core/backup_models.py`
- Backup planning helpers: `src/core/backup_planner.py`
- Backup execution helpers: `src/core/backup_executor.py`
- Backup metadata builder: `src/core/backup_metadata.py`
- ATU duplicate handling: `src/core/backup_duplicates.py`
- ATU/HIS storage rules: `src/core/storage.py`
- ZIP creation: `src/core/zipper.py`
- Integrity helpers: `src/core/integrity.py`
- Project type registry: `src/core/project_types/registry.py`
- Project-specific adapters: `src/core/project_types/`
- GE Multilin adapter: `src/core/project_types/ge_multilin.py`
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
- Distributed executable filename is fixed: `IED_Backup_Manager.exe`.
- Keep versioning in the release folder, release notes, Git tag, window title,
  and splash screen, not in the executable filename.
- `releases/` is a local ignored artifact folder and must not be committed.
  Publish executables and release notes through GitHub Releases instead.
- When the user asks to generate the `.exe`, generate it directly using
  `scripts/release.ps1` unless there is a clear blocker.
- Every release should update `.agents/CURRENT_STATE.md`,
  `.agents/PROJECT_CONTEXT.md`, and relevant docs/release notes.
- Public-facing examples should use generic names such as `SE-AAA`, `ETD-BBB`,
  `VAO-ZZZ`, and `COLABORADOR-EXEMPLO`.
- Public documentation should be maintained as separate Portuguese and English
  Markdown files with language switch links at the top. The GUI help button
  should open `HELP.md` for `pt_BR` and `HELP.en.md` for `en_US`.
- The project is public/source-available under the `IED Backup Manager
  Non-Commercial License`, not OSI open source. Commercial use requires prior
  written permission from Jean Carlos Machado.
- The active next roadmap milestone after `v1.16.1` is improvement guided by
  real usage feedback. Operational reports and external `.sha256` files are
  intentionally outside the active roadmap for now.
- After running tests or builds, remove generated caches/build folders when they
  are not needed: `.pytest_cache`, `.ruff_cache`, `__pycache__`, `build`, `dist`.

## Storage Safety Rules

- Stage ZIP creation outside the final `ATU`/`HIS` name.
- Validate ZIP readability before publishing it to the final destination.
- Do not silently overwrite an unexpected destination ZIP.
- When replacing the current ATU backup, publish the validated new ZIP first and
  remove it again if the previous current backup cannot be archived in `HIS`.
- Move suspicious or partial files from rare copy/publication/archive failures
  to `IED-QUARENTENA` with a `.txt` recovery note, including the original
  exception text, instead of deleting them silently.
- After a successful backup, clean quarantine entries for the same technical key
  when the quarantined original timestamp is equal to or older than the
  successful backup; remove `IED-QUARENTENA` only when it becomes empty.
- Controlled HIS cleanup uses a configurable retention period in days, default
  `30`, and always preserves the newest backup for each `SOFTWARE + PROJECT +
  STAGE`.
- HIS cleanup deletion is manual only through the `Limpeza HIS` dialog. After a
  successful backup, the app may report candidates in the final summary, but it
  must not delete HIS files automatically.
- HIS cleanup ignores ZIP files that do not match the standard backup naming
  pattern.

## Progress Rules

- Long file operations should accept optional progress callbacks.
- GUI progress should show the current item as `file X/N`.
- ZIP creation and final destination copies should report byte progress, not only
  completed-item counts.
- GUI backup execution should run in a worker thread, not in the GUI thread.
- Cancellation during ZIP staging should stop before publishing to `ATU`/`HIS`.
- Cancellation should not interrupt a final destination copy midway.

## Update Check Rules

- Check GitHub Releases in a worker thread after startup.
- Show update status only when a newer version exists.
- Use a red clickable notice in the bottom-left corner of the main window.
- Keep network errors silent; update checks must never block backup workflows.
- Do not auto-download or replace the executable.
