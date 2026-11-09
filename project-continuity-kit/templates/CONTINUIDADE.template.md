# Continuidade e recuperação

## O que o Git preserva

- `<CODIGO_E_DOCUMENTOS>`;
- `<TESTES_E_CONFIGURACOES_REPRODUZIVEIS>`;
- `<OUTROS_ITENS>`.

## O que exige backup separado

| Item | Motivo | Destino | Como restaurar |
| --- | --- | --- | --- |
| `<ITEM>` | `<MOTIVO>` | `<BACKUP>` | `<PROCEDIMENTO>` |

Nunca inclua valores de segredos neste documento.

## Preparar migração

1. validar lint, testes e build;
2. atualizar estado atual e decisões materiais;
3. revisar Git e arquivos locais;
4. enviar commits autorizados ao remoto;
5. confirmar backup privado;
6. registrar limitações e próximo passo.

## Restaurar em outro computador

```text
<COMANDOS_DE_CLONE_E_PREPARACAO>
```

Depois:

1. ler `AGENTS.md` e o índice documental;
2. restaurar somente configurações/dados necessários;
3. executar testes e build;
4. executar fluxo mínimo ou smoke test;
5. usar o prompt de retomada.

## Handoff mínimo

- versão, branch e commit;
- estado validado;
- mudança em andamento;
- testes executados;
- riscos e decisões abertas;
- próximo passo pequeno e verificável.

## Teste periódico de recuperação

Defina frequência, responsável e evidência: `<POLITICA_DE_TESTE>`.
