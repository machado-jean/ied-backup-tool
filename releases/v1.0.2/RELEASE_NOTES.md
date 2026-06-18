# IED Backup Manager v1.0.2

Data: 18/06/2026

## Resumo

Versao de acabamento visual e melhoria do processo de release.

## Alteracoes

- Adicionado icone proprio do aplicativo.
- O mesmo icone passou a ser usado no cabecalho da interface.
- O build do executavel passou a usar o icone `.ico`.
- Criado script `scripts/release.ps1` para padronizar geracao de releases.
- O script de release executa validacoes, gera assets, compila o executavel e
  copia o arquivo para `releases/vX.Y.Z/`.

## Compatibilidade

- O comportamento funcional de backup permanece igual ao da versao `v1.0.1`.
- O tipo padrao continua sendo `digsi5`.

## Arquivo

- `IED Backup Manager v1.0.2.exe`
