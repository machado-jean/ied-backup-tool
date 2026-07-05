# Release Checklist

Use this checklist whenever the user asks to generate a new `.exe`.

## 1. Decide Version

- Patch `vX.Y.Z+1`: bug fix, small compatibility extension, UI polish, docs
  update that affects release output.
- Minor `vX.Y+1.0`: new functional behavior or meaningful workflow capability.
- Major `vX+1.0.0`: breaking workflow or compatibility change.

## 2. Update Files

Update:

- `src/version.py`
- `README.md` current version line
- `.agents/CURRENT_STATE.md`
- `releases/vX.Y.Z/RELEASE_NOTES.md`

For user-visible behavior, also update when relevant:

- `docs/USO_EXECUTAVEL.md`
- `docs/PLANO_MELHORIAS.md`
- `.agents/PROJECT_CONTEXT.md`

## 3. Validate Before Build

Run:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
```

## 4. Generate Executable

Run:

```powershell
.\scripts\release.ps1
```

The script should run lint/tests, build with PyInstaller, copy the executable to
`releases/vX.Y.Z/`, and remove the generated `.spec`.

## 5. Clean Temporary Files

After build, remove temporary artifacts if they exist:

- `build/`
- `dist/`
- `.pytest_cache/`
- `.ruff_cache/`
- `__pycache__/`

Do not remove `.venv/`, `.vscode/`, local source/current/history backup
folders, `config.json`, or `releases/vX.Y.Z/`.

## 6. Final Checks

Confirm:

```text
releases/vX.Y.Z/IED Backup Manager.exe exists
releases/vX.Y.Z/RELEASE_NOTES.md exists
IED Backup Manager.spec does not exist
build/ and dist/ do not exist
```

Then report executable path, release notes path, validation result, final
executable size, and any local ignored files worth attention.

## 7. Git Closeout

Recommended after user validation:

```powershell
git status
git add .
git commit -m "Release vX.Y.Z"
git tag vX.Y.Z
git push
git push origin vX.Y.Z
```
