# IED Backup Manager v1.5.2

Data: 27/06/2026

## Resumo

Versao patch que adiciona SHA256 dos arquivos de origem ao metadado interno dos
ZIPs.

## Alteracoes

- `IEDS-BACKUP-INFO.txt` agora registra `SHA256` para cada arquivo incluido.
- O calculo e feito em leitura por blocos para suportar arquivos maiores.
- O SHA256 nao altera o nome do ZIP.
- O SHA256 ainda nao bloqueia nem muda decisoes de backup; ele e apenas
  informativo nesta versao.
- Documentacao e testes atualizados.

## Compatibilidade

- Mantem compatibilidade com `config.json` das versoes anteriores.
- Nao altera o padrao de nomes dos backups.
- Mantem o arquivo interno `IEDS-BACKUP-INFO.txt` introduzido na `v1.5.0`.

## Arquivo

- IED Backup Manager v1.5.2.exe
