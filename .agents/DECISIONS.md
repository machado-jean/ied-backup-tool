# Technical Decisions

This file records decisions that should not need to be rediscovered from chat
history.

## Backup Identity

Technical key:

```text
SOFTWARE_PROJECT
```

Technical identity:

```text
SOFTWARE_PROJECT_TIMESTAMP
```

Collaborator and stage do not change technical identity.

## Project Name Policy

The project/substation/equipment identifier is always the text before the first
underscore `"_"`.

Examples:

```text
SE-AAA_COMMENT_20260622_1350.dz5 -> SE-AAA
ETD-BBB_OTHER-COMMENT.rdb -> ETD-BBB
```

Avoid underscores inside the project identifier.

## SHA256 Policy

SHA256 is calculated from source files, not from the final ZIP.

Source SHA is stable across collaborators/stages. ZIP SHA would change when
`IEDS-BACKUP-INFO.txt` changes.

## Integrity Conflict Policy

If a ZIP with the same technical identity has SHA256 metadata and the current
source files differ, block execution and show `Conflito SHA`.

Do not automatically overwrite, archive, or delete in this case.

Legacy ZIPs without SHA metadata remain compatible and do not trigger conflict.

## ZIP Metadata Filename

The internal metadata file is:

```text
IEDS-BACKUP-INFO.txt
```

Do not use `manifest` terminology in user-facing outputs for this file.

## IED-PACK

When multiple selected IED types belong to the same project, create an
`IED-PACK`.

If multiple types are selected but only one type exists for a project, use the
individual IED naming format, not `IED-PACK`.

For each selected type, include only the latest source file per project/type.

## ABB PCM600

Supported extensions: `.pcmp`, `.apcmp`.

Both are treated as ZIP-like packages. Version is read from:

```text
ProjectDataServer%versions.ini
```

Only `ProductVersion` is used in the backup prefix, for example
`PCM600-V2.10`.

## SEL

Main file: `.rdb`.

Optional related files: `.scd`, `.selaprj`.

Expected prefix examples:

```text
QUICKSET-V7.5.3.10
QUICKSET-V7.5.3.10-ARCHITECT-V2.4.2.34
```

## INGETEAM

Supported extensions: `.efsPro`, `.ITPro2`.

The version is manually entered by the user when INGETEAM is selected and is
saved in `config.json`.

Expected prefix example: `INGESYS-V5.5.4`.

## PyInstaller Build Mode

The app currently uses PyInstaller `--onefile`.

Tradeoff:

- easier distribution as one `.exe`;
- slower startup because the bundle is unpacked at launch.

The splash screen improves perceived startup but cannot remove the initial
PyInstaller unpacking delay.

## Storage Movement

Do not use direct `shutil.move` for final backup placement into `ATU`/`HIS`.

Reason: on Windows, moving files from a temp folder can preserve problematic
source ACLs. Final files should be recreated in the destination folder so they
inherit destination permissions.
