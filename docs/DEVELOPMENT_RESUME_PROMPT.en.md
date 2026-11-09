# Development resume prompt

[Português](PROMPT_RETOMADA.md) | [English](DEVELOPMENT_RESUME_PROMPT.en.md)

Use this prompt after cloning the repository and opening it in Codex or another
development agent. The repository is the source of truth; previous conversation
history is not required.

```text
I want to resume development of IED Backup Manager on this computer.

Before changing any file, perform a read-only discovery pass of the repository.

1. Read in full:
   - AGENTS.md
   - docs/README.en.md
   - docs/CURRENT_STATE.en.md
   - docs/ARCHITECTURE.en.md
   - docs/DEVELOPMENT_ENVIRONMENT.en.md
   - docs/ROADMAP.en.md
   - docs/decisions/README.md
   - the relevant ADRs
   - CONTRIBUTING.en.md

2. Check:
   - the current branch and Git status;
   - the current version in src/version.py;
   - the structure of src/ and tests/;
   - the actual installation, execution, and verification commands;
   - the active roadmap, pending work, and documented restart point;
   - whether any documentation is contradictory or outdated.

3. Check whether the Python environment is ready. If .venv does not exist,
   report the required commands before installing anything.

4. Do not modify code, documentation, configuration, Git state, or external
   services during this discovery step.

When finished, report:
- your understanding of the product;
- the architecture and invariants that must be preserved;
- the current development state;
- the next documented priority;
- blockers or information that still requires my input;
- a small, verifiable plan for the next step.

Do not depend on previous conversation history. Use the repository as the
source of truth.
```

After approving the initial analysis, use the following prompt to start work:

```text
The analysis is correct. Let us work on the next documented priority.

Before implementing:
- define the exact scope;
- identify the files likely to be affected;
- define tests and acceptance criteria;
- identify decisions that require my confirmation.

Do not work outside this scope and do not commit, push, tag, or publish without
my explicit authorisation.
```

See [`DEVELOPMENT_ENVIRONMENT.en.md`](DEVELOPMENT_ENVIRONMENT.en.md) for the
workstation setup procedure.
