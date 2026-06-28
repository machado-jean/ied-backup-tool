# IED Backup Manager v1.0.7

Data: 19/06/2026

## Resumo

Versao de ajuste da politica de identificacao do projeto/subestacao pelo nome
do arquivo de origem.

## Alteracoes

- O projeto passa a ser sempre o primeiro bloco antes do primeiro `_`.
- Textos intermediarios como etapa, revisao ou sequencial sao ignorados na
  identificacao do projeto.
- Exemplo: `SE-BBB_DEV_01_20260619_0013.dz5` gera projeto `SE-BBB`.
- Manual atualizado com exemplos e casos de renomeacao que violam a politica.
- Testes adicionados para proteger a regra.

## Compatibilidade

- Backups antigos continuam sendo lidos normalmente.
- Esta mudanca afeta a chave tecnica de novos backups quando arquivos de origem
  possuem textos intermediarios depois do projeto.

## Arquivo

- `IED Backup Manager v1.0.7.exe`
