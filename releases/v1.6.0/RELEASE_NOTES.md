# IED Backup Manager v1.6.0

Data: 04/07/2026

## Resumo

Versao minor com validacao avancada de integridade por SHA256.

## Alteracoes

- Adicionado status `Conflito SHA` na previa do lote.
- O programa agora compara os SHA256 dos arquivos de origem com backups
  existentes que tenham a mesma identidade tecnica.
- A execucao fica bloqueada quando houver mesma identidade tecnica com SHA256
  diferente.
- A verificacao considera backups existentes em `ATU` e tambem em `HIS`.
- Backups antigos sem `IEDS-BACKUP-INFO.txt` ou sem SHA256 continuam
  compativeis e nao sao marcados como conflito.
- Ajustado o movimento final dos ZIPs para recriar o arquivo dentro da pasta
  destino e herdar as permissoes de `ATU`/`HIS`.
- Adicionados testes de regressao para conflito SHA e para evitar preservacao
  indevida de permissoes do arquivo temporario.

## Compatibilidade

- Mantem compatibilidade com `config.json` existente.
- Mantem compatibilidade com ZIPs antigos sem metadados SHA256.
- Nao altera o formato dos nomes de backup.

## Arquivo

- `IED Backup Manager v1.6.0.exe`
