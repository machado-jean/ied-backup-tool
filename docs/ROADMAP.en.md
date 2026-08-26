# Improvement Roadmap

[Português](PLANO_MELHORIAS.md) | [English](ROADMAP.en.md)

This document records implemented milestones, the active roadmap, and paused or
discarded decisions.

## Active Roadmap

| Estimated version | Milestone | Expected scope |
| --- | --- | --- |
| `v1.18.0` | New IED types | Add new vendors/software only when clean/sanitized samples and reliable identification, version, and included-file rules are available. |

## Implemented History

| Version | Milestone | Main deliveries |
| --- | --- | --- |
| `v1.0.0` | Initial functional version | Consolidated backup flow, standardized ZIP generation, and `ATU`/`HIS` organization. |
| `v1.5.0` | Metadata in every ZIP | `IEDS-BACKUP-INFO.txt` with backup, project, software, stage, included files, size, and dates. |
| `v1.6.0` | Advanced integrity | SHA256 comparison, `SHA conflict`, and execution blocking while conflicts exist. |
| `v1.8.0` | Worker thread and cancellation | Responsive GUI during large backups and controlled cancellation. |
| `v1.9.0` | Public help | Operational help, usage docs, troubleshooting, privacy guidance, and metadata examples. |
| `v1.10.0` | Update check | Public GitHub release check and clickable update notice. |
| `v1.11.0` | Structural refactor | Smaller GUI/core modules, planner, executor, metadata, duplicate handling, and tests. |
| `v1.12.0` | Operational quarantine | `IED-QUARENTENA` for rare partial/suspicious files after copy/archive failures. |
| `v1.13.0` | Controlled HIS cleanup | Retention policy, cleanup preview, and manual deletion confirmation. |
| `v1.14.0` | Public visual documentation | Screenshots, sanitized examples, contribution guidance, templates, and roadmap cleanup. |
| `v1.15.0` | GE Multilin / EnerVista UR | GE folder-based adapter, optional `.ENV`, IED subfolders, preserved paths, and GE metadata. |
| `v1.15.1` | Identification logic documentation | Public documentation for project-type detection, included files, automatic/manual versions, special INGETEAM and GE cases, and `IED-PACK`. |
| `v1.16.0` | Bilingual documentation and language-aware Help | Separate Portuguese/English public files, GitHub language switch links, and `Ajuda` / `Help` opening the document that matches the active UI language. |
| `v1.16.1` | GE ZIP version correction | GE prefixes now use the highest IED/application `GEMULTILIN` version from `.urs/.urk` headers; `GE UR Setup` from `.cid/.icd` remains development metadata only. |
| `v1.16.2` | GE Vernova / UR Setup compatibility | GE prefixes now accept `GEVERNOVA` headers in `.urs/.urk` and also compare `GE Digital Energy UR Setup` / `Multilin UR Setup` versions in `.cid/.icd`, using the highest detected version. |
| `v1.16.3` | Diagnostics and background preview | Preserves source modified time inside ZIPs, adds daily logs under `%LOCALAPPDATA%`, captures unhandled exceptions, and runs batch preview in a worker to reduce freezes in large folders. |
| `v1.17.0` | Naming policy and real-usage polish | New ZIP filename format with readable date/time and `FIRST LAST`, separate first/last name fields, assisted detection and renaming of old backups, translation review, and startup ordering fixed so instructions appear before legacy-rename prompts. |

## Paused or Discarded Items

| Item | Decision | Reason |
| --- | --- | --- |
| Operational reports | Paused/discarded for now | Could add noise to the main workflow and is not a current operational need. |
| External `.sha256` files | Paused/discarded for now | Internal source-file SHA256 metadata fits the current scope better. |
| Code signing | Paused | Can reduce SmartScreen warnings, but requires certificate cost, management, and distribution decisions. |
| Automatic packaging on every change | Outside normal flow | Executables should be generated only after validation and explicit release request. |

## New IED Type Criteria

To add a new vendor/software type, the project needs at least one of:

- a public, artificial, clean, or sanitized file;
- a backup generated from an empty vendor-software project;
- a reliable description of where to extract the version;
- clear main-extension and companion-file rules.
