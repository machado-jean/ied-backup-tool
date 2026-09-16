# Release Checklist

Use this checklist whenever the user asks to generate a new `.exe` or publish a
GitHub Release.

## 1. Decide Version

- Patch `vX.Y.Z+1`: bug fix, compatibility adjustment, UI polish, diagnostics,
  or documentation/release-process improvement.
- Minor `vX.Y+1.0`: new functional behavior or meaningful workflow capability.
- Major `vX+1.0.0`: breaking workflow or compatibility change.

## 2. Update Sources of Truth

Always update:

- `src/version.py`;
- current-version lines in `README.md` and `README.en.md`;
- `.agents/CURRENT_STATE.md`;
- `releases/vX.Y.Z/RELEASE_NOTES.md`.

When behavior or workflow changes, also review both languages of:

- `docs/USO_EXECUTAVEL.md` / `docs/EXECUTABLE_USAGE.en.md`;
- `docs/HELP.md` / `docs/HELP.en.md`;
- `docs/PLANO_MELHORIAS.md` / `docs/ROADMAP.en.md`;
- `CONTRIBUTING.md` / `CONTRIBUTING.en.md`;
- `.agents/PROJECT_CONTEXT.md`, `.agents/DECISIONS.md`, and this checklist.

Do not rewrite historical release notes from older versions.

Before packaging, confirm that release notes and public documentation use only
fictional generic examples such as `SE-AAA`, `SE-BBB`, or `SE-CCC`. Real cases
may guide implementation, but never reproduce operational identifiers supplied
during diagnosis.

## 3. Validate Before Build

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
```

Parse changed PowerShell scripts with
`System.Management.Automation.Language.Parser` before executing them.

## 4. Generate and Verify the Release

```powershell
.\scripts\release.ps1
```

The script must:

- run lint/tests unless `-SkipTests` follows equivalent validation in the same
  release task;
- sanitize `PATH` while PyInstaller runs;
- build the fixed filename `IED_Backup_Manager.exe` with `--onefile`;
- create/preserve `RELEASE_NOTES.md`;
- generate `SHA256SUMS.txt` and `PUBLISH_RELEASE.ps1`;
- execute `PUBLISH_RELEASE.ps1 -VerifyOnly`;
- remove `.spec`, `build/`, and `dist/` after successful packaging.

Expected local artifacts:

```text
releases/vX.Y.Z/IED_Backup_Manager.exe
releases/vX.Y.Z/RELEASE_NOTES.md
releases/vX.Y.Z/SHA256SUMS.txt
releases/vX.Y.Z/PUBLISH_RELEASE.ps1
```

`releases/` remains ignored by Git. Never force-add it.

## 5. Smoke Test

Open the packaged executable with isolated project/config and `LOCALAPPDATA`.
Confirm the main window opens, workers stop, closing returns code `0`, the log
records a normal event-loop exit, and Windows records no new application crash.
Remove only the explicitly created smoke-test directory afterward.

## 6. Final Local Checks

Confirm that all release assets exist, `-VerifyOnly` passes, `.spec`/`build`/
`dist` are absent, executable size is near the previous release, SHA256 matches,
and `releases/` remains ignored. Report paths, test count, size, hash, smoke-test
result, and whether publication occurred.

## 7. Commit, Push, and Publish

After user validation, commit tracked changes and push `master`. Do not create
or push the release tag manually; the generated publisher owns that step.

```powershell
.\releases\vX.Y.Z\PUBLISH_RELEASE.ps1 -VerifyOnly
.\releases\vX.Y.Z\PUBLISH_RELEASE.ps1
```

Publish only when explicitly requested. The publisher requires a clean
worktree, `HEAD == origin/master`, authenticated GitHub CLI, local lint/tests,
and successful `master` CI. It then pushes only the tag and waits for the tag CI
on the exact commit through `scripts/Check-ReleaseCi.ps1`. The GitHub Release
and its assets may be created only after that tag CI concludes successfully.
After all gates pass, the publisher must show a `CORRETO`/`INCORRETO` report and
ask `Publicar release com o release note e .exe?`. Only an affirmative response
may create the GitHub Release. When any gate fails or the user declines, leave
the release unpublished; the validated tag may remain for diagnosis or retry.
