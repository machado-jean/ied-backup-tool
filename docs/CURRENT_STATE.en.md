# Current state and restart point

[Português](ESTADO_ATUAL.md) | [English](CURRENT_STATE.en.md)

Updated: **8 November 2026**.

- current application version: **1.18.1**;
- primary branch: `master`;
- platform: Windows 10/11;
- development and CI runtime: Python 3.13;
- GUI: PySide6;
- distribution: one-file `IED_Backup_Manager.exe` built with PyInstaller.

The product currently includes read-only previews, individual/batch/grouped
backups, DIGSI/SEL/PCM600/INGESYS/GE adapters, ZIP metadata and SHA256,
integrity checks, quarantine, ATU/HIS storage, controlled history cleanup,
background workers, bilingual UI, themes, diagnostics, update checks, Windows
CI, and a gated release process.

The active roadmap identifies **v1.19.0 — new IED types** as the next known
milestone. Work must not begin until a clean/sanitised sample or reliable format
description can prove detection, versioning, included files, technical
identity, metadata, and ATU/HIS compatibility.

On 8 November 2026, Ruff passed, all **176 Pytest tests passed** on Python
3.13.16, relative Markdown links resolved, and `git diff --check` passed.
Pytest emitted a non-fatal Windows permission warning while inspecting its
temporary `pytest-current` cleanup link after the successful run; the process
still exited with code zero.

Restart by checking the worktree, reading `AGENTS.md`, the roadmap and relevant
ADRs, then running Ruff and Pytest. Code signing remains paused; operational
reports, external `.sha256` files, and build-on-every-change remain outside the
active roadmap.

The Portuguese [`ESTADO_ATUAL.md`](ESTADO_ATUAL.md) is the canonical detailed
snapshot and should be updated at the end of material work.
