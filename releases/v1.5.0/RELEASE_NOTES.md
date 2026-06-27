# IED Backup Manager v1.5.0

Data: 27/06/2026

## Resumo

Versao menor que adiciona metadados internos em todos os ZIPs gerados pelo
aplicativo.

## Alteracoes

- Todo ZIP gerado passa a incluir `IEDS-BACKUP-INFO.txt`.
- Backups individuais DIGSI, SEL, PCM600 e INGETEAM agora tambem ficam
  autoexplicativos dentro do proprio ZIP.
- `IED-PACK` passa a usar o mesmo arquivo de metadados, mantendo a secao de
  versoes detectadas por tipo.
- O arquivo interno registra backup, projeto, software, data/hora, colaborador,
  etapa, versoes detectadas, arquivos incluidos, tamanho e data de modificacao.
- Documentacao atualizada para o novo arquivo de metadados.

## Compatibilidade

- Mantem compatibilidade com `config.json` das versoes anteriores.
- Nao altera o padrao de nomes dos ZIPs.
- O arquivo interno antigo `IEDS-VERSIONS.txt` e substituido por
  `IEDS-BACKUP-INFO.txt` nos novos backups.
- SHA256 ainda nao foi incluido; ele fica planejado para uma versao posterior.

## Arquivo

- IED Backup Manager v1.5.0.exe
