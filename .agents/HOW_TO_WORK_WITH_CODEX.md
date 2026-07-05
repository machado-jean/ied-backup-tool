# How to Work With Codex on This Project

Use this guide to keep long-term collaboration efficient.

## At the Start of a New Conversation

Ask Codex:

```text
Leia .agents/PROJECT_CONTEXT.md, .agents/CURRENT_STATE.md e docs/PLANO_MELHORIAS.md antes de continuar.
```

If the task is a release, also ask:

```text
Leia .agents/RELEASE_CHECKLIST.md antes de gerar o executavel.
```

## Good Requests

For a new feature:

```text
Implemente a proxima etapa do roadmap, sem gerar o .exe ainda. Rode os testes e me diga como testar.
```

For a patch:

```text
Corrija este comportamento como patch, atualize testes e documentacao vigente se necessario.
```

For a release:

```text
Gere o .exe da versao X.Y.Z seguindo .agents/RELEASE_CHECKLIST.md.
```

For investigation only:

```text
Nao altere nada ainda. Apenas investigue e me diga a causa provavel.
```

## What Codex Should Usually Do

- Read the relevant files before changing code.
- Prefer existing architecture and tests.
- Update `README.md` whenever version, supported behavior, or public usage
  changes.
- Update `docs/USO_EXECUTAVEL.md` for user-facing workflow changes.
- Update `docs/PLANO_MELHORIAS.md` when roadmap items are completed or refined.
- Update `.agents/CURRENT_STATE.md` after important releases or direction
  changes.
- Update `.agents/CURRENT_STATE.md` on every release, and update the other
  `.agents` files whenever rules, workflow, roadmap, or release procedure
  changes.
- Run `ruff` and `pytest` after code changes.
- Clean caches after validation.

## What To Avoid

- Do not edit real backup folders unless explicitly requested:
  - source/design backup folder;
  - current-backup folder;
  - historical-backup folder.
- Do not generate `.exe` during feature development unless requested.
- Do not rewrite release notes from old versions unless explicitly requested;
  old release notes are historical records.
- Do not remove `.venv/` or `config.json` unless explicitly requested.

## Expected Final Answer After Implementation

Codex should report what changed, key files changed, tests run and result,
whether `.exe` was generated, how to test locally, and any known caveat.

## Expected Final Answer After Release

Codex should report executable path, release notes path, test result, final
executable size, temporary build folders cleaned, and next recommended Git
steps.
