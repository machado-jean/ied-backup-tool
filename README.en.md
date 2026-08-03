# IED Backup Manager

[Português](README.md) | [English](README.en.md)

Windows application for standardizing IED project backups, keeping the current
backup in `ATU`, historical backups in `HIS`, and consistent ZIP names for
technical traceability.

Current version: `1.16.1`

- Executable usage guide: [docs/EXECUTABLE_USAGE.en.md](docs/EXECUTABLE_USAGE.en.md)
- Operational help: [docs/HELP.en.md](docs/HELP.en.md)
- IED identification logic: [docs/IED_IDENTIFICATION_LOGIC.en.md](docs/IED_IDENTIFICATION_LOGIC.en.md)
- Roadmap: [docs/ROADMAP.en.md](docs/ROADMAP.en.md)
- Public sample files: [docs/examples](docs/examples)
- How to contribute: [CONTRIBUTING.en.md](CONTRIBUTING.en.md)

## Overview

IED Backup Manager processes the working files in the executable folder,
identifies the project from the text before the first underscore `"_"`, creates a
standard ZIP, and applies the current/history storage rules between `ATU` and
`HIS`.

The goal is to reduce inconsistent manual backups, avoid technical duplicates,
preserve history, and make audits easier without requiring users to rename final
backup files manually.

## Main Features

- Windows GUI with batch preview before execution.
- Portuguese and English interface, saved in `config.json`.
- Public online help opened according to the selected UI language.
- GitHub update check with clickable update notice.
- Fixed executable name: `IED_Backup_Manager.exe`.
- Standard stages: `DEV`, `PRE-TAF`, `TAF`, `POS-TAF`, `PRE-TAC`, `TAC`,
  `POS-TAC`, and free description.
- Individual backups or grouped `IED-PACK` backups by project/substation.
- Metadata file `IEDS-BACKUP-INFO.txt` inside every generated ZIP.
- SHA256 source-file registration and integrity conflict detection.
- Validated `ATU`/`HIS` folders with assisted creation when missing.
- Operational quarantine folder `IED-QUARENTENA` for rare partial/suspicious
  files after copy or archive failures.
- Controlled `HIS` cleanup with retention, preview, and manual confirmation.
- Responsive execution with per-file progress and controlled cancellation.

## Supported Types

| Type | Input | Version used in backup |
| --- | --- | --- |
| Siemens DIGSI | `.dz5` | Internal `.dp4v###` or `.dp5v###` marker, for example `DIGSI5-V10.00`. |
| SEL QuickSet / Architect | `.rdb`, optional `.scd` or `.selaprj` | QuickSet and Architect versions when found. |
| ABB PCM600 | `.pcmp`, `.apcmp` | `ProjectDataServer%versions.ini` inside the package. |
| INGETEAM INGESYS | `.efsPro`, `.ITPro2` | Manually entered by the user and saved in `config.json`. |
| GE Multilin / EnerVista UR | folders with `.urs` or `.urk`; optional `.ENV` | Highest IED/application `GEMULTILIN` version found in `.urs/.urk`; `GE UR Setup` is kept as development metadata. |

## Naming Rule

The project, substation, bay, or equipment name is the text before the first
underscore `"_"`.

```text
SE-AAA_GENERIC-COMMENT_20260712_1030.dz5 -> Project: SE-AAA
ETD-BBB_OTHER-COMMENT.rdb                -> Project: ETD-BBB
VAO-ZZZ_GENERIC-COMMENT_20260712_1050.efsPro -> Project: VAO-ZZZ
```

Everything after the first underscore is treated as a user comment and is not
part of the technical backup key.

## Public Sample Files

The [docs/examples](docs/examples) folder contains artificial files for public
testing and documentation screenshots. The sample workspace intentionally does
not include `config.json`, so the first GUI run starts without previous settings
and requires the user to fill `Settings`.

Suggested GUI command:

```powershell
.\.venv\Scripts\python.exe -m src.gui.app --project-dir ".\docs\examples\sample-workspace"
```

Use `COLABORADOR-EXEMPLO` as collaborator and point `ATU`/`HIS` to
`docs\examples\sample-storage\ATU` and `docs\examples\sample-storage\HIS`.
For INGETEAM examples, use manual version `5.5.4`.

## Development

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m src.gui.app
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
```

Generate a local release executable only after validation:

```powershell
.\scripts\release.ps1
```

## Privacy

Do not publish real backup files, local `config.json`, internal company paths,
real collaborator names, IP addresses, credentials, or operational engineering
data. Public examples should use generic names such as `SE-AAA`, `ETD-BBB`,
`VAO-ZZZ`, and `COLABORADOR-EXEMPLO`.

## License

Copyright (c) 2026 Jean Carlos Machado.

This project is provided for free, non-commercial use under the **IED Backup
Manager Non-Commercial License**. Commercial use, resale, sublicensing, paid
service offering, or incorporation into commercial products requires prior
written authorization.
