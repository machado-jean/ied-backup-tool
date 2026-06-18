# IED Backup Manager v1.0.1

Data: 18/06/2026

## Resumo

Versao de preparacao estrutural para suportar outros tipos de IED futuramente,
mantendo o comportamento atual do DIGSI 5.

## Alteracoes

- Criada a camada `src/core/project_types/`.
- DIGSI 5 passou a ser tratado como tipo registrado (`digsi5`).
- A logica geral de backup deixou de depender diretamente de `.dz5`.
- A GUI passou a montar os tipos de arquivo a partir do registro de tipos.
- A CLI passou a aceitar `--project-type`.
- Adicionado teste garantindo que a logica geral aceita um tipo de projeto
  alternativo.
- Documentacao atualizada para explicar o ponto de extensao para novos tipos,
  como SEL (`.rdb`).

## Compatibilidade

- O comportamento para DIGSI 5 (`.dz5`) permanece igual ao da versao anterior.
- O tipo padrao continua sendo `digsi5`.

## Arquivo

- `IED Backup Manager v1.0.1.exe`
