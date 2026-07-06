# IED Backup Manager v1.10.5

Data: 05/07/2026

## Resumo

Patch de revisao publica do repositorio e ajuste visual do indicador de
copyright.

## Alteracoes

- Revisao de dados sensiveis em arquivos versionaveis, ignorando pastas locais
  de backup e ambiente virtual.
- Confirmado que `IED-DES/`, `IED-ATU/`, `IED-HIS/`, `.venv/`, `.vscode/` e
  `config.json` seguem ignorados pelo Git.
- O indicador `©` do canto inferior direito passa a usar um botao flat com a cor
  padrao do tema, melhorando contraste em modo escuro e claro.

## Compatibilidade

- Nao altera regras de backup, ATU/HIS, SHA256, tipos de IED ou `config.json`.
- Nao altera o link de download direto do executavel.

## Arquivo

- `IED_Backup_Manager.exe`
