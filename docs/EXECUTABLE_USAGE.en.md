# IED Backup Manager - Executable Usage

[Português](USO_EXECUTAVEL.md) | [English](EXECUTABLE_USAGE.en.md)

This guide explains how to use `IED_Backup_Manager.exe` to generate standardized
IED project backups.

For visual guidance, see [README.en.md](../README.en.md) and
[HELP.en.md](HELP.en.md). For project-type rules, see
[IED_IDENTIFICATION_LOGIC.en.md](IED_IDENTIFICATION_LOGIC.en.md).

## 1. Expected Folder Structure

The executable must be placed in the project folder that will be processed.

```text
Project folder/
|-- IED_Backup_Manager.exe
|-- config.json
|-- project working files
```

The app processes the folder where the executable is located. A legacy `BKPs`
folder is not required.

## 2. First Run

On first run, the startup instructions explain the recommended folder structure
and naming rules. You can switch languages in that window and mark `Do not show
again`.

Then configure:

- first name and last name;
- `ATU` folder;
- `HIS` folder;
- language;
- selected IED types.

The app validates that `ATU` and `HIS` exist, are different folders, and are not
unsafe nested paths.

## 3. Update Notice

At startup, the application checks the latest public GitHub release. If a newer
version exists, a clickable notice is shown in the lower-left corner.

The app does not replace itself automatically.

## 4. IED Types and Stage

Select at least one IED type before generating backups. The selected types are
saved in `config.json`.

Select the delivery stage. The stage is part of the generated ZIP name. Returning
to an earlier stage is allowed for long projects that need rework.

For GE Multilin / EnerVista UR, the app treats the selected folder as the
SE/application environment. Direct child folders containing `.urs` or `.urk` are
included as GE IED folders, with `.urs`, `.urk`, `.cid`, and `.icd` files. The
ZIP prefix uses the highest version found between `GEMULTILIN`/`GEVERNOVA`
headers in `.urs/.urk` and `GE Digital Energy UR Setup` / `Multilin UR Setup`
headers in `.cid/.icd`. Per-IED details remain available in
`IEDS-BACKUP-INFO.txt`.

## 5. Preview and Execution

Before generating backups, review the batch preview:

```text
Action | File | Project | Version | Date/Time | Destination
```

Click `Generate backups` only after the preview is correct. During execution,
the progress dialog shows the current file and byte progress.

In large folders, the preview is calculated in the background. While scanning is
in progress, the preview area shows `Processing files...` and `Generate backups`
remains disabled.

If cancellation is requested during ZIP staging, the staged ZIP is discarded and
is not copied to `ATU`/`HIS`.

## 6. Storage Behavior

- `ATU` keeps the newest current backup for each technical key.
- `HIS` keeps historical backups.
- Existing current backups are archived to `HIS` when replaced.
- Suspicious partial files from rare failures can be moved to `IED-QUARENTENA`.

## 7. HIS Cleanup

Use `HIS cleanup` to review cleanup candidates. Retention `0` disables automatic
post-backup candidate checks. Deletion always requires manual row selection and
confirmation.

## 8. Updating the Executable

The distributed executable keeps the stable name:

```text
IED_Backup_Manager.exe
```

Replace the old executable with the new one. Existing `config.json`, `ATU`, and
`HIS` folders can remain in place.

If the app closes by itself or freezes during startup, check the daily log under:

```text
%LOCALAPPDATA%\IED Backup Manager\logs\
```

Send the log from the day of the failure after removing sensitive information if
needed.
