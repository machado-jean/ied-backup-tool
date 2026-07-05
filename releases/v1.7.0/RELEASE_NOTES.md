# IED Backup Manager v1.7.0

Data: 05/07/2026

## Resumo

Versao minor que consolida as melhorias feitas depois da `v1.6.0`: operacao
mais transacional em `ATU`/`HIS` e progresso real por arquivo durante a geracao
dos backups.

## Alteracoes

- O novo ZIP agora e validado antes de ser publicado como backup final.
- A copia final e feita para um arquivo temporario dentro da pasta de destino e
  so depois e publicada com o nome definitivo.
- Ao substituir o backup atual em `ATU`, o novo ZIP e preparado e validado antes
  de arquivar o backup anterior em `HIS`.
- Se o arquivamento do backup anterior falhar, o novo ZIP publicado em `ATU` e
  removido para reduzir risco de estado parcial.
- Backups historicos faltantes passam a ser criados em staging antes de serem
  colocados em `HIS`.
- O sistema deixa de sobrescrever silenciosamente um ZIP inesperado que ja exista
  no destino.
- A janela de progresso agora mostra o arquivo atual como `arquivo X/N`.
- A barra de progresso passa a usar bytes processados durante a compactacao.
- A barra de progresso tambem usa bytes processados durante a copia final para
  `ATU`/`HIS`.
- Correcoes de duplicidade em `ATU` tambem reportam progresso real quando movem
  arquivos para `HIS`.
- Adicionados testes de regressao para validacao transacional e progresso por
  bytes.

## Compatibilidade

- Mantem compatibilidade com `config.json` existente.
- Mantem compatibilidade com o formato atual dos nomes de backup.
- Mantem compatibilidade com ZIPs gerados por versoes anteriores.
- Nao altera as regras de identificacao tecnica de projeto, etapa ou colaborador.

## Arquivo

- `IED Backup Manager v1.7.0.exe`
