# IED Backup Manager v1.0.6

Data: 18/06/2026

## Resumo

Versao de ajuste das etapas de backup.

## Alteracoes

- Removidas as etapas `PRODUCAO` e `CUSTOM`.
- Adicionada a opcao `Descricao livre` no campo `Etapa`.
- Ao selecionar `Descricao livre`, a interface exibe um campo `Descricao`.
- A descricao pode ser preenchida manualmente ou deixada vazia.
- Textos livres sao normalizados para uso seguro no nome do arquivo.

## Compatibilidade

- Backups antigos com etapas removidas continuam sendo lidos normalmente.
- A comparacao tecnica continua ignorando colaborador e etapa.

## Arquivo

- `IED Backup Manager v1.0.6.exe`
