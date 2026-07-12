# IED Type Identification Logic

[Português](LOGICA_IDENTIFICACAO_IEDS.md) | [English](IED_IDENTIFICATION_LOGIC.en.md)

This document explains how IED Backup Manager identifies each backup type,
selects files for the ZIP, and determines the software/version used in the final
backup name.

## General Rule

For most IED types, the project, SE, ETD, bay, or equipment is identified by the
text before the first underscore `"_"`.

```text
SE-AAA_GENERIC-COMMENT_20260622_1350.dz5 -> Project: SE-AAA
ETD-BBB_OTHER-COMMENT.rdb                -> Project: ETD-BBB
```

Everything after the first underscore is treated as a comment and is not part of
the technical backup key.

## Siemens DIGSI

- Main file: `.dz5`.
- Version is detected automatically from internal `.dp4v###` or `.dp5v###`
  markers.
- Examples: `.dp5v100` becomes `DIGSI5-V10.00`; `.dp5v75` becomes
  `DIGSI5-V7.50`.

Manual version: no.

## SEL QuickSet / Architect

- Main file: `.rdb`.
- Optional companion files with the same base name: `.scd` or `.selaprj`.
- QuickSet version is read from the `.rdb`.
- Architect version is read from `.scd` or `.selaprj` when present.

If an old SEL file does not contain the QuickSet version, the app may request a
manual version.

## ABB PCM600

- Main files: `.pcmp` or `.apcmp`.
- The package is inspected as a compressed file.
- Version is read from `ProjectDataServer%versions.ini`, using
  `ProductName` and `ProductVersion`.

Manual version: no.

## INGETEAM INGESYS

- Main files: `.efsPro` or `.ITPro2`.
- Version is not determined automatically.
- The user enters the INGETEAM/INGESYS software version in use.
- The value is saved in `config.json`.

This is intentional because these formats can contain imported/newer component
markers even when the project was worked on with an older software version.

Manual version: yes.

## GE Multilin / EnerVista UR

GE is a special case. The backup represents an SE/application environment with
IED subfolders, not a single root file.

Rules:

- the project is the SE/application folder name;
- a direct child folder is considered a GE IED folder when it contains `.urs` or
  `.urk`;
- top-level `.ENV` is included when present, but is not required;
- `.ENV` alone is not enough to characterize a valid GE backup;
- inside selected IED folders, only `.urs`, `.urk`, `.cid`, and `.icd` are
  included.

Version selection:

1. Use the highest `GE Digital Energy UR Setup` version found in `.cid/.icd`.
2. If no SCL setup version exists, use the highest `GEMULTILIN` version from
   `.urs/.urk`.

## IED-PACK

When multiple IED types are selected and more than one real type is found for
the same project, the app creates an `IED-PACK`.

Rules:

- if only one real type is found, the individual type name is used;
- if two or more real types are found for the same project, the backup uses
  `IED-PACK`;
- the ZIP includes `IEDS-BACKUP-INFO.txt` with detected software versions for
  each included type.

## When to Update This Document

Update this document whenever a new vendor/software is added, version detection
changes, a type starts requiring manual version input, or real cases change the
interpretation of a format.
