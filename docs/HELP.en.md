# IED Backup Manager - Help

[Português](HELP.md) | [English](HELP.en.md)

This document summarizes the operational use of IED Backup Manager with generic
public examples.

For detailed project-type rules, see
[IED_IDENTIFICATION_LOGIC.en.md](IED_IDENTIFICATION_LOGIC.en.md).

## Goal

IED Backup Manager standardizes IED project backups. It identifies working files
in the local folder, creates ZIPs with consistent names, keeps the current backup
in `ATU`, and archives previous backups in `HIS`.

## Recommended Structure

The executable must stay inside the folder that contains the substation,
application, bay, or equipment working files.

```text
Local folder/
+-- SE, ETD, bay, or equipment folder/
    +-- IED_Backup_Manager.exe
    +-- config.json
    +-- SE-AAA_GENERIC-COMMENT_20260622_1350.dz5
    +-- ETD-BBB_OTHER-COMMENT.rdb
    +-- ETD-BBB_OTHER-COMMENT.scd
    +-- VAO-ZZZ_GENERIC-COMMENT_20260619_1230.pcmp
    +-- GE-IED-A/
    |   +-- GE-IED-A.urs
    |   +-- GE-IED-A.cid
    +-- other working files
```

The app processes the folder where the executable is located. `ATU` and `HIS`
can be configured in another location.

## Naming Rules

- The SE, ETD, bay, or equipment name must come before the first underscore
  `"_"`.
- Use hyphen `"-"` inside the project name.
- Everything after the first underscore is treated as a user comment.
- Always check the `Project` column in the batch preview before generating
  backups.

Avoid names such as:

```text
SE_AAA_20260622_1350.dz5
CLIENT_SE-AAA_20260622_1350.dz5
DEV_SE-AAA_20260622_1350.dz5
```

## Supported Types

| Type | Input | Version used in ZIP |
| --- | --- | --- |
| Siemens DIGSI | `.dz5` | Detected from the package, producing `DIGSI4-Vx.xx` or `DIGSI5-Vx.xx`. |
| SEL QuickSet / Architect | `.rdb`, optional `.scd` or `.selaprj` | QuickSet and Architect when found. |
| ABB PCM600 | `.pcmp`, `.apcmp` | Internal `ProjectDataServer%versions.ini`. |
| INGETEAM INGESYS | `.efsPro`, `.ITPro2` | Manually entered and saved in `config.json`. |
| GE Multilin / EnerVista UR | folders with `.urs` or `.urk`; optional `.ENV` | Highest version found between `GEMULTILIN`/`GEVERNOVA` headers in `.urs/.urk` and `UR Setup` headers in `.cid/.icd`. |

## Basic Flow

1. Put the executable in the working-files folder.
2. Open the application.
3. Configure collaborator, `ATU`, `HIS`, language, and IED types.
4. Select the stage.
5. Check the batch preview.
6. Click `Generate backups`.
7. Wait for completion or cancel before the next file starts.
8. Use `HIS cleanup` when old historical backups should be reviewed.

## Batch Preview

The preview shows:

- `Action`: what will happen.
- `File`: identified main file.
- `Project`: technical project key.
- `Version`: detected software/version.
- `Date/Time`: timestamp used in the final ZIP name.
- `Destination`: compact destination such as `ATU\file.zip` or `HIS\file.zip`.

If `SHA conflict` appears, execution is blocked because a backup with the same
technical identity has different source-file content.

## Expected Outputs

```text
DIGSI5-V10.00_SE-AAA_20260622-1350_COLLABORATOR-EXAMPLE_TAF.zip
QUICKSET-V7.5.3.10-ARCHITECT-V2.4.2.34_ETD-BBB_20260612-0350_COLLABORATOR-EXAMPLE_TAF.zip
IED-PACK_ETD-BBB_20260612-0350_COLLABORATOR-EXAMPLE_TAF.zip
GE-MULTILIN-V8.71_SE-AAA_20260712-1100_COLLABORATOR-EXAMPLE_TAF.zip
```

## ZIP Metadata

Every generated ZIP includes `IEDS-BACKUP-INFO.txt` with backup name, project,
software, timestamp, collaborator, stage, included files, file sizes, and SHA256
hashes.

## HIS Cleanup

Use `HIS cleanup` to review old historical backups.

Default rule:

- retention is `30` days;
- retention `0` disables post-backup candidate checks;
- the newest backup for each `SOFTWARE + PROJECT + STAGE` is always preserved;
- deletion requires selecting rows and confirming manually.

## Known Limitations

- Large files can take time to compress and copy.
- OneDrive, SharePoint, or similar synced folders may delay or lock files.
- Files opened in engineering tools may be locked by Windows.
- The project is always identified by the text before the first underscore.
- Old ZIPs without `IEDS-BACKUP-INFO.txt` remain compatible, but do not provide
  SHA256 metadata for comparison.
- Rare copy/publication failures may move suspicious files to `IED-QUARENTENA`
  for manual review.

## Troubleshooting

### The executable takes time to open

The Windows `.exe` may take a few seconds to extract and prepare the application.
The splash screen indicates that loading is in progress.

### The app does not open in a synced folder

Try copying the executable to a local, non-synced folder. If it opens normally,
the likely cause is sync, pending cloud activity, or folder permissions.

### The project was identified incorrectly

Check the `Project` column. Rename the file so the SE, ETD, bay, or equipment
name comes before the first underscore `"_"`.

## Privacy

Do not publish real backups, local `config.json`, internal company paths, real
collaborator names, IP addresses, credentials, or operational engineering data.

## License

Copyright (c) 2026 Jean Carlos Machado.

IED Backup Manager is available for free, non-commercial use according to the
project license:

```text
https://github.com/machado-jean/ied-backup-tool
```
