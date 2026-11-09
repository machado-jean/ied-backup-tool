# Project continuity audit

[Português](AUDITORIA_CONTINUIDADE_PROJETOS.md) | [English](PROJECT_CONTINUITY_AUDIT.en.md)

This guide defines a reusable process for preparing any project to continue on
another computer, with another developer, or with another development agent.
The repository should preserve material technical context so previous chat
history is not required.

## Process

1. Audit Git branches, remotes, synchronisation, commits, tags, local changes,
   untracked files, ignored files, releases, Git LFS, and external dependencies.
2. Review related conversations and extract only decisions, requirements,
   constraints, root causes, pending work, and validation evidence that are not
   already preserved.
3. Consolidate material context into appropriate sources such as `AGENTS.md`,
   a documentation index, architecture, environment, continuity, current state,
   roadmap, resume prompt, and ADRs.
4. Classify local-only files as source, durable context, local configuration,
   operational data, secret, versioned artefact, large required file,
   reproducible environment, or temporary output.
5. Store public-safe material in a public repository, authorised confidential
   source/context in a private repository, versioned packages in Releases,
   genuinely versioned large files in Git LFS, operational data in encrypted
   private backup, and credentials in a secrets manager.
6. Review the complete change for credentials, personal paths, customer data,
   licensing, screenshots, large files, and `.gitignore` mistakes.
7. Run the relevant lint, tests, builds, Markdown-link checks, version checks,
   smoke tests, and `git diff --check`.
8. Prove recovery by cloning into a clean location and rebuilding exclusively
   from versioned instructions.

Private repositories are not secrets managers. Passwords, tokens, private keys,
production databases, and unnecessary personal or customer data should not be
committed merely because access is restricted.

## Completion criteria

The audit is complete when the required remote commits exist, local-only files
are classified and protected, secrets are outside Git, material chat knowledge
is stored in canonical sources, the current state and next step are clear, the
environment can be rebuilt, risk-proportionate validation has run, and recovery
has been demonstrated or its limitations are documented.

## Reusable prompt

```text
Prepare this project so development can continue on another computer without
depending on previous conversation history.

First perform a read-only audit:
- inspect Git state, remotes, commits, tags, local changes, untracked and
  ignored files when Git exists;
- review related conversations and extract only material knowledge not already
  preserved;
- classify local-only files and identify sensitive or third-party content;
- determine whether the environment, tests, build, and release can be
  reconstructed on a clean computer.

Before writing, report what is already preserved, what can still be lost, the
documents or adjustments you propose, appropriate storage for each category,
and decisions that require my input.

After approval, consolidate only material context. Do not copy complete chat
transcripts. Do not include secrets, operational data, personal paths, or
customer files. Do not commit, push, create a repository, publish, enable Git
LFS, or upload anything without my explicit authorisation.

Validate links, formatting, relevant tests, and git diff --check. Report exactly
what changed, what was verified, and what still requires private backup or an
external action.
```

The Portuguese guide
[`AUDITORIA_CONTINUIDADE_PROJETOS.md`](AUDITORIA_CONTINUIDADE_PROJETOS.md) is
the canonical detailed procedure, including storage decisions, security rules,
recovery testing, resume prompts, and maintenance frequency.
