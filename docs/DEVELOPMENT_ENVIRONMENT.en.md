# Development environment

[Português](AMBIENTE_DESENVOLVIMENTO.md) | [English](DEVELOPMENT_ENVIRONMENT.en.md)

## Reference environment

- Windows 10 or Windows 11 x64;
- Python 3.13 in CI; Ruff targets Python 3.12 or newer;
- PowerShell and Git;
- repository-local `.venv`;
- pinned dependencies from `requirements.txt`.

```powershell
git clone https://github.com/machado-jean/ied-backup-tool.git
cd ied-backup-tool
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m src.gui.app
```

Use the public sample workspace with:

```powershell
.\.venv\Scripts\python.exe -m src.gui.app --project-dir ".\docs\examples\sample-workspace"
```

The CI runs Ruff and Pytest on Windows with Python 3.13 and an offscreen Qt
platform. Local configuration, real ATU/HIS data, logs, builds, and release
folders are not versioned.

The release build command is `./scripts/release.ps1`. It reads the version from
`src/version.py`, validates the project, builds the PyInstaller executable, and
prepares release evidence and the manual publisher.

See [`AMBIENTE_DESENVOLVIMENTO.md`](AMBIENTE_DESENVOLVIMENTO.md) for the
canonical detailed setup, smoke test, data-safety, and dependency-update rules.
