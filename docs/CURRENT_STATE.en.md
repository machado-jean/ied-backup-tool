# Current state and restart point

[Português](ESTADO_ATUAL.md) | [English](CURRENT_STATE.en.md)

Updated: **12 November 2026**.

- current application version: **1.18.2**;
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

On 12 November 2026, Ruff passed, all **177 Pytest tests passed** on Python
3.13.17, relative Markdown links resolved, and `git diff --check` passed.
Pytest emitted a non-fatal Windows permission warning while inspecting its
temporary `pytest-current` cleanup link after the successful run; the process
still exited with code zero.

Backup timestamps now use the newest modification time among every related file
included in the ZIP. The real SEL scenario with an older `.rdb` and newer `.scd`
now plans a replacement using the `.scd` timestamp instead of reporting a SHA
conflict against the old temporal identity.

The `HIS Cleanup` retention selector now reserves minimum dimensions and draws
its increment and decrement buttons inside the field border, with consistent
contrast in light and dark themes. All 21 GUI presentation tests passed after
the adjustment.

The local **v1.18.2** release was generated and passed asset and hash
verification. Its isolated smoke test opened the main window, stopped workers
and the event loop with code zero, and left no orphan session marker. No
commit, tag, push, or GitHub Release was created at this stage.

Restart by checking the worktree, reading `AGENTS.md`, the roadmap and relevant
ADRs, then running Ruff and Pytest. Code signing remains paused; operational
reports, external `.sha256` files, and build-on-every-change remain outside the
active roadmap.

The Portuguese [`ESTADO_ATUAL.md`](ESTADO_ATUAL.md) is the canonical detailed
snapshot and should be updated at the end of material work.
