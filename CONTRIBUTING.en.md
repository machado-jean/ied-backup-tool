# Contributing to IED Backup Manager

[Português](CONTRIBUTING.md) | [English](CONTRIBUTING.en.md)

Thank you for considering a contribution. This project accepts bug fixes,
documentation improvements, public examples, tests, and support for new IED
types, as long as shared files do not contain confidential information.

## Development Requirements

Recommended environment:

- Windows;
- Python 3.13;
- Git;
- access to the GitHub repository;
- local `.venv` virtual environment.

```powershell
git clone https://github.com/machado-jean/ied-backup-tool.git
cd ied-backup-tool
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Run the GUI:

```powershell
.\.venv\Scripts\python.exe -m src.gui.app
```

Validate before opening a pull request:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
```

## Reporting Bugs

Before opening an issue:

1. Confirm that you are using the latest published version.
2. Try reproducing the issue with the examples in `docs/examples`.
3. Confirm that `ATU` and `HIS` point to different accessible folders.
4. Confirm that source files are not open in another engineering tool.

Include:

- IED Backup Manager version;
- Windows version;
- selected IED type;
- expected behavior;
- actual behavior;
- general folder structure without confidential data;
- screenshots or full error messages when helpful.

Do not send real `config.json`, internal company paths, real collaborator names,
or backup files with operational data.

## Pull Requests

Recommended flow:

1. Create a branch from the main branch.
2. Keep the change focused on one objective.
3. Update tests when behavior changes.
4. Update documentation when the change is visible to users.
5. Run `ruff` and `pytest`.
6. Open the pull request using the repository template.

Avoid including `.venv/`, `releases/`, generated `.exe` files, real backups,
or unrelated formatting-only changes.

## New IED Types

New vendors and software types are welcome, but they need safe samples or clear
format information.

You may contribute:

- a clean file generated from an empty project in the vendor software;
- an artificial or sanitized sample;
- a textual description of the format when the file cannot be shared;
- version extraction rules and related-file rules.

Never send files containing real customer, project, substation, IP, credential,
protection, logic, topology, communication, or operational field data.

## License

By contributing, you agree that your contribution will be made available under
the project license: **IED Backup Manager Non-Commercial License**.
