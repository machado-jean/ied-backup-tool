# ADR 006 — Identidade atual baseada na família de software

- Estado: Aceita
- Data: 2026-11-08 (registro retrospectivo)
- Responsável: mantenedor do projeto
- Substitui: nenhuma
- Substituída por: nenhuma

## Contexto

Versões diferentes do mesmo software representam evolução do mesmo backup
atual, enquanto famílias diferentes podem representar alternativas que exigem
decisão operacional. Pacotes agrupados também não podem ser substituídos
silenciosamente por um backup individual.

## Decisão

A chave do backup atual é `SOFTWARE_FAMILY_PROJECT`. A identidade histórica é
`SOFTWARE_PROJECT_TIMESTAMP`; colaborador e etapa aparecem no nome, mas não
alteram essa identidade.

Mudança somente de versão dentro da mesma família atualiza `ATU` e arquiva a
anterior. A primeira ocorrência individual de outra família exige escolha
explícita entre manter ambas, substituir a existente ou cancelar; substituição
exige segunda confirmação. Um individual não substitui `IED-PACK`: o pacote
deve ser regenerado. Um novo `IED-PACK` arquiva somente as famílias individuais
que declara cobrir.

## Consequências

- números de versão são removidos da família, preservando o produto;
- CLI, worker e GUI não podem executar uma escolha não resolvida;
- planejamento precisa carregar a cobertura do pacote;
- alterações na identidade exigem regressões para `ATU`, `HIS`, duplicidades,
  limpeza, integridade e migração.

## Evidências

- `src/core/backup_planner.py`;
- `src/core/backup_models.py`;
- `src/core/storage.py`;
- `docs/LOGICA_IDENTIFICACAO_IEDS.md`;
- testes de service, storage e apresentação.
