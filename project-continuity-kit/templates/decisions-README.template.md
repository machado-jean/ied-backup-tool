# Decisões arquiteturais

## Estados

- **Proposta:** requer decisão;
- **Aceita:** vigente;
- **Substituída:** outra ADR passou a ser vigente;
- **Rejeitada:** avaliada e não adotada.

ADRs aceitas preservam o contexto histórico. Quando uma decisão mudar, crie
outra ADR e marque a anterior como substituída.

## Catálogo

| ADR | Estado | Decisão |
| --- | --- | --- |
| `<NNN-TITULO.md>` | `<ESTADO>` | `<RESUMO>` |

## Quando criar uma ADR

Use ADR para decisões duráveis de arquitetura, formato, compatibilidade,
segurança, privacidade, persistência, recuperação, distribuição ou operação.
Não use ADR como diário de progresso ou registro de correções pequenas.
