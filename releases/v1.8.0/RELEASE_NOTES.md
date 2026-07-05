# IED Backup Manager v1.8.0

Data: 05/07/2026

## Resumo

Versao minor focada em experiencia durante backups grandes: execucao em worker
dedicado, interface responsiva e cancelamento controlado.

## Alteracoes

- A geracao de backups agora roda em `QThread`, fora da thread principal da GUI.
- A janela principal permanece responsiva durante compactacao e copia de arquivos
  grandes.
- A janela de progresso continua exibindo o arquivo atual como `arquivo X/N`.
- O progresso passa a ser atualizado por sinais do worker.
- O botao `Cancelar` solicita cancelamento controlado.
- Se o cancelamento ocorrer durante a compactacao, o ZIP temporario e descartado
  e nao e copiado para `ATU`/`HIS`.
- Se a copia final para `ATU`/`HIS` ja tiver comecado, ela e finalizada antes de
  parar para preservar consistencia.
- A coluna `Acao` foi movida para a primeira posicao na previa do lote:
  `Acao | Arquivo | Projeto | Versao | Data/Hora | Destino`.
- Adicionados testes de regressao para cancelamento antes do primeiro arquivo e
  cancelamento durante compactacao.

## Compatibilidade

- Mantem compatibilidade com `config.json` existente.
- Mantem compatibilidade com o formato atual dos nomes de backup.
- Mantem compatibilidade com ZIPs gerados por versoes anteriores.
- Nao altera as regras de versionamento `ATU`/`HIS`.

## Arquivo

- `IED Backup Manager v1.8.0.exe`
