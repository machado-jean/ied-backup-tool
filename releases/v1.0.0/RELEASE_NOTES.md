# IED Backup Manager v1.0.0

Data: 18/06/2026

## Resumo

Primeira versao funcional do executavel com interface grafica para gerar backups
padronizados de projetos DIGSI 5 (`.dz5`).

## Principais recursos

- Interface grafica para uso via executavel Windows.
- Configuracao por `config.json` ao lado do executavel.
- Selecao obrigatoria da etapa antes da geracao do backup.
- Suporte as etapas:
  `DEV`, `PRE-TAF`, `TAF`, `POS-TAF`, `PRE-TAC`, `TAC`, `POS-TAC`,
  `PRODUCAO`, `CUSTOM`.
- Previa do lote antes da execucao.
- Processamento de multiplos arquivos `.dz5`.
- Barra de progresso durante a geracao dos backups.
- Resumo final da execucao.
- Organizacao automatica entre `ATU` e `HIS`.
- Deteccao de duplicidades em `ATU`.
- Idioma portugues/ingles com preferencia salva no `config.json`.

## Arquivo

- `IED Backup Manager v1.0.0.exe`
