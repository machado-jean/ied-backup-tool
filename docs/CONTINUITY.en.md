# Development continuity and recovery

[Português](CONTINUIDADE.md) | [English](CONTINUITY.en.md)

Conversation history is not the canonical project memory. Durable knowledge
must be stored in versioned source, tests, documentation, and ADRs.

Before a planned migration:

1. run Ruff, Pytest, and `git diff --check`;
2. update `CURRENT_STATE.en.md` and its Portuguese canonical counterpart;
3. commit and push important changes;
4. verify the GitHub commit and CI result;
5. privately back up real projects, `ATU`, `HIS`, quarantine data, and any
   required local configuration;
6. keep credentials and secrets outside the repository.

Restore on another Windows workstation with:

```powershell
git clone https://github.com/machado-jean/ied-backup-tool.git
cd ied-backup-tool
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
```

Read `AGENTS.md`, the documentation index, current-state snapshot,
architecture, and relevant ADRs before changing code. Recreate local settings,
validate the public sample workspace first, then use only an authorised copy of
real data.

Git intentionally excludes `config.json`, real IED projects, ATU/HIS content,
logs, virtual environments, local builds, credentials, and certificates. Back
up operational data privately using the organisation's recovery policy.

See [`CONTINUIDADE.md`](CONTINUIDADE.md) for the canonical detailed migration,
uncommitted-work recovery, handoff, and periodic verification procedure.
