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
Whitespace within that text is collapsed into a hyphen. The underscore remains
the identifier delimiter and is not normalized as part of the project name.

Examples:

```text
SE-AAA_COMMENT_20260622_1350.dz5 -> SE-AAA
ETD-BBB_OTHER-COMMENT.rdb -> ETD-BBB
SE CCC_20260916_0800.dz5 -> SE-CCC
SE_CCC_20260916_0800.dz5 -> SE
```

Avoid underscores inside the project identifier.

## Generic Public Examples

Real operational cases may guide a fix, but public documentation, release notes,
screenshots, examples, tests, and user-facing text must use fictional generic
identifiers such as `SE-AAA`, `SE-BBB`, or `SE-CCC`. Do not repeat customer,
site, substation, project, equipment, collaborator, or path names supplied in a
real diagnosis.

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

## Crash Diagnostics Consent

An absent clean-exit marker means only that the previous session ended
unexpectedly; it is not sufficient by itself to classify a native crash.

On the next startup, ask before reading Windows Application events. If consent
is granted, query only event IDs 1000/1001 within ±2 minutes of the last
heartbeat and filter by executable name/path. Copy only sanitized diagnostic
fields into the local log. Do not access WER dumps, request UAC, or upload data.
Declining must perform no Windows event query and must dismiss that incident.

Use one transient `logs/sessions/<UUID>.json` marker per process instead of a
shared session file. Each marker records the application executable path, PID,
process-image path, process creation time, start time, and heartbeat. A marker
is active only when PID, process-image path, and creation time still match; this
prevents PID reuse and concurrent instances from producing false incidents.
Offer diagnostics only for a dead session whose application executable path
matches the current copy. Delete clean and handled markers immediately, expire
unresolved markers after 30 days, and retain at most 20 per executable path.
Keep one shared daily log, with session UUID and PID included in every line.

## Release Publication

Local release artifacts remain ignored by Git. `scripts/release.ps1` owns the
build plus generation of SHA256 and the per-release publisher. The generated
publisher owns tag/release creation after it verifies a clean synchronized
`master`, green CI, hashes, notes, and assets. Do not create tags manually in the
normal release flow.

The publisher must never create the GitHub Release before tag CI completes. Its
required order is: validate assets, rerun local lint/tests, require green
`master` CI for the exact commit, push the tag, require green tag CI for that
same commit, and only then run `gh release create --verify-tag`. A failed tag CI
may leave the diagnostic tag in place, but must not expose a release or assets.

After all pre-publication gates pass, the publisher must print a detailed report
with each completed check marked `CORRETO` or `INCORRETO` and ask
`Publicar release com o release note e .exe?`. Only an affirmative answer may
run `gh release create`; a refusal keeps the validated tag but creates no GitHub
Release and uploads no assets.

## Storage Movement

Do not use direct `shutil.move` for final backup placement into `ATU`/`HIS`.

Reason: on Windows, moving files from a temp folder can preserve problematic
source ACLs. Final files should be recreated in the destination folder so they
inherit destination permissions.
