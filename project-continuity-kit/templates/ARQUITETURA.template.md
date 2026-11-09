# Arquitetura de `<NOME_DO_PROJETO>`

## Objetivo arquitetural

`<POR_QUE_A_ARQUITETURA_ESTA_ORGANIZADA_DESTA_FORMA>`

## Visão geral

```text
<DIAGRAMA_TEXTUAL_DAS_CAMADAS_E_FLUXOS>
```

## Componentes e responsabilidades

| Componente/caminho | Responsabilidade | Não deve fazer |
| --- | --- | --- |
| `<COMPONENTE>` | `<RESPONSABILIDADE>` | `<LIMITE>` |

## Fluxos principais

### `<NOME_DO_FLUXO>`

```text
<ENTRADA> -> <VALIDACAO> -> <PROCESSAMENTO> -> <SAIDA>
```

## Persistência e dados

- fonte de verdade: `<FONTE>`;
- formatos: `<FORMATOS>`;
- migrations/compatibilidade: `<POLITICA>`;
- backup e recuperação: `<POLITICA>`.

## Dependências permitidas

- `<CAMADA_A>` pode depender de `<CAMADA_B>`;
- `<CAMADA_B>` não pode depender de `<CAMADA_A>`;
- `<OUTRA_REGRA>`.

## Segurança, privacidade e confiabilidade

- `<REGRA>`;
- `<REGRA>`.

## Evolução

Mudanças duráveis em `<FRONTEIRAS_RELEVANTES>` exigem ADR e atualização deste
documento. O código e os testes continuam sendo a fonte de verdade do
comportamento executável.
