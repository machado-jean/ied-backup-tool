# IED Backup Manager - Current State

Last updated: 2026-07-12

## Current Version

Current application version: `1.16.0`

Latest generated executable:

```text
releases/v1.16.0/IED_Backup_Manager.exe
```

The `v1.16.0` executable has been generated locally.

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
- `v1.10.3`: update notice opens direct latest executable download and the
  release asset uses underscore naming.
- `v1.10.4`: update notice text clarifies that clicking downloads the new
  version.
- `v1.10.5`: public repository sensitivity review and copyright indicator
  contrast fix.
- `v1.11.0`: structural refactor of GUI and core modules without intended
  behavior changes.
- `v1.12.0`: operational quarantine for suspicious/partial files after rare
  copy, publication, or archive failures.
- `v1.13.0`: controlled HIS cleanup with configurable retention days and
  protected latest backup per technical key and stage.
- `v1.14.0`: public visual documentation, sanitized example files,
  contribution guidance, issue/PR templates, and roadmap cleanup with new IED
  types as the next milestone.
- `v1.15.0`: GE Multilin / EnerVista UR support for SE-level environments,
  preserving GE IED subfolders and adding GE-specific metadata.
- `v1.16.0`: public documentation of IED identification/version rules,
  including special cases for INGETEAM and GE Multilin.

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
pytest: 116 passed
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

- Release script generates and copies `IED_Backup_Manager.exe` instead of a
  versioned executable filename.
- Version remains visible in the window title and splash screen through
  `APP_VERSION`.
- Release folders remain versioned as `releases/vX.Y.Z/`.
- GitHub can expose a stable latest-download URL:
  `https://github.com/machado-jean/ied-backup-tool/releases/latest/download/IED_Backup_Manager.exe`.

## Current v1.10.2 Scope

- Adds `LICENSE` with the `IED Backup Manager Non-Commercial License`.
- Adds license notes to README, executable-use documentation, and public help.
- Adds a clickable `©` indicator in the bottom-right corner of the GUI.
- Clicking `©` shows a compact authorship/license note and repository link.

## Current v1.10.3 Scope

- The release script generates `IED_Backup_Manager.exe`.
- The update notice opens the direct latest download URL:
  `https://github.com/machado-jean/ied-backup-tool/releases/latest/download/IED_Backup_Manager.exe`.
- The tooltip explains that clicking the update notice downloads the new
  version.

## Current v1.10.5 Scope

- Public repository scan reviewed versionable files outside ignored local
  backup folders, `.venv`, `.git`, and generated binary assets.
- Test fixtures were sanitized to use `COLABORADOR-EXEMPLO` instead of a real
  first name.
- `.gitignore` still protects `IED-DES/`, `IED-ATU/`, `IED-HIS/`, `.venv/`,
  `.vscode/`, `config.json`, build outputs, and `.spec` files.
- The bottom-right copyright indicator now uses a flat `QPushButton` with the
  active theme text color instead of rich-text link coloring.

## Current v1.11.0 Scope

- Extracted startup instructions into `src/gui/startup_instructions.py`.
- Extracted GUI language/runtime helpers into `src/gui/language_button.py` and
  `src/gui/runtime.py`.
- Extracted preview-table rendering and source-file display formatting into
  `src/gui/preview_table.py`.
- Extracted execution-summary text formatting into `src/gui/summary_text.py`.
- Extracted confirmation/conflict message builders into
  `src/gui/backup_confirmation.py`.
- Added `src/gui/backup_application_service.py` as a Qt-independent layer
  between `MainWindow` and core planning.
- Extracted backup status constants and data models into
  `src/core/backup_models.py`.
- Added `BackupStatus` as a string enum while preserving legacy status constants.
- Extracted backup planning into `src/core/backup_planner.py`.
- Extracted backup plan execution and history archiving into
  `src/core/backup_executor.py`.
- Extracted ATU duplicate planning/execution into
  `src/core/backup_duplicates.py`.
- Extracted backup metadata text generation into `src/core/backup_metadata.py`.
- Added focused tests for backup metadata, application service, and GUI
  presentation helpers.
- Progress dialog hides the progress bar's built-in percentage text and keeps
  only the explicit progress text above the bar.

## Current v1.12.0 Scope

- Adds `IED-QUARENTENA` beside the storage folders for suspicious or partial
  files left by rare copy/publication/archive failures.
- Moves partial temporary files to quarantine instead of silently deleting them
  when destination copy fails.
- Writes a `.txt` note beside each quarantined file with original path, reason,
  original error, timestamp, and manual-analysis guidance.
- Cleans matching quarantine entries automatically after a successful backup for
  the same technical key with equal or newer timestamp; removes the quarantine
  folder when it becomes empty.
- Keeps normal ATU/HIS transactional behavior unchanged.
- Updates README, executable usage docs, public help, and roadmap.

## Current v1.13.0 Scope

- Adds `src/core/history_cleanup.py` with a testable HIS cleanup policy.
- Adds `Limpeza HIS` / `HIS cleanup` dialog in the main GUI.
- Saves cleanup preferences in `config.json` under `history_cleanup`.
- Default retention is `30` days.
- Retention `0` disables post-backup cleanup checks and suppresses cleanup
  notices in the final summary.
- Cleanup candidates are ZIPs in `HIS` older than the retention period.
- The newest backup for each `SOFTWARE + PROJETO + ETAPA` is always preserved,
  even when it is older than the retention period.
- The cleanup preview shows candidate count, total HIS size, candidate size,
  age, stage, project, timestamp, and reason.
- Manual cleanup requires row selection and explicit confirmation.
- The `Limpeza HIS` table uses a checkbox in the first column; deletion uses
  checked rows, not visual table selection.
- The app reports cleanup candidates in the final backup summary after a
  successful backup; it does not show a permanent main-window notice.
- No post-backup path deletes HIS automatically. Deletion is restricted to the
  `Limpeza HIS` dialog with explicit row selection and confirmation.
- `history_cleanup` now stores only `retention_days`; the removed automatic
  cleanup flag is no longer parsed or written.
- The final backup summary uses a custom compact dialog that hides zero-value
  counters and shows cleanup guidance as a separate highlighted note.
- Files outside the standard ZIP naming pattern are ignored by cleanup.
- Fixed grouped preview behavior: when multiple IED types are selected but only
  one real type exists for a project, the app now processes all files of that
  type unless `Processar apenas a partir do backup atual` is checked. `IED-PACK`
  still uses only the newest file per type when multiple real types exist.
- Tests now include config parsing and core cleanup rules.

## Current v1.14.0 Scope

- Updates the public README with current screenshots, download guidance,
  supported IED types, examples, development commands, architecture notes,
  privacy guidance, contribution links, roadmap, and license summary.
- Adds visual documentation to `docs/HELP.md`.
- Adds public sanitized images under `docs/images/`.
- Adds artificial public examples under `docs/examples/`.
- Adds `CONTRIBUTING.md` with install, reproduction, pull request, and safe
  sample-file contribution guidance.
- Adds GitHub issue and pull request templates for bugs, feature requests, new
  IED types, and pull requests.
- Reorganizes `docs/PLANO_MELHORIAS.md` with implemented history since
  `v1.0.0` and active roadmap focused on new IED types.
- Keeps release artifacts local under ignored `releases/`.

## Current v1.15.0 Scope

- Adds `src/core/project_types/ge_multilin.py`.
- Registers `ge_multilin` in the project type registry, CLI, and GUI checkbox
  list.
- Detects GE backups from direct child folders containing `.urs` or `.urk`.
- Includes the top-level `.ENV` file when present, but does not require it.
- Includes only `.urs`, `.urk`, `.cid`, and `.icd` inside selected GE IED
  folders.
- Excludes non-IED folders/files such as RDP, switches, GPS, `.cfg`, `.xml`,
  `.msf`, and extensionless switch configs unless future rules explicitly add
  them.
- Uses the highest `GE Digital Energy UR Setup` version found in `.cid/.icd`
  for the backup name, e.g. `GE-URSETUP-V8.61`.
- Falls back to the highest `GEMULTILIN` header version from `.urs/.urk` when
  no SCL setup version exists, e.g. `GE-MULTILIN-V8.40`.
- Preserves nested folder paths inside ZIPs when source files span subfolders.
- Adds a GE-specific section to `IEDS-BACKUP-INFO.txt` with environment,
  optional `.ENV` versions, included IED folders, development version, and
  IED/application version.
- Adds artificial GE examples under `docs/examples/ge-workspace/SE-AAA`.
- Adds `docs/LOGICA_IDENTIFICACAO_IEDS.md` explaining detection/version rules
  for DIGSI, SEL, PCM600, INGETEAM, GE Multilin, and `IED-PACK`.
- Updates README, HELP, executable-use docs, roadmap, and tests.

## Current v1.16.0 Scope

- Promotes `docs/LOGICA_IDENTIFICACAO_IEDS.md` as the public reference for IED
  identification logic.
- Documents which project types use automatic version detection and which can
  require manual input.
- Explains why INGETEAM uses a manually informed version due to ambiguous
  internal markers across imported/newer components.
- Explains the GE Multilin special case: SE/application folder as the project,
  `.ENV` optional, IED folders detected by `.urs`/`.urk`, allowed extensions,
  excluded non-IED equipment files, and version selection order.
- Links the logic document from README, HELP, executable-use docs, and agent
  context.

## Next Planned Work

Planned next improvement after `v1.16.0`:

```text
real-usage improvements
```

Likely scope:

- validate GE behavior with more real environments;
- refine user-facing labels, warnings, and documentation based on actual tests;
- add new IED types only when clean/sanitized samples and reliable version rules
  are available.

Roadmap reference:

- `docs/PLANO_MELHORIAS.md` now lists `v1.17.0` as the next estimated milestone
  for improvements guided by real use; code signing, operational reports, and
  external `.sha256` files remain outside the active roadmap.
