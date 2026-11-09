# Orientações permanentes do repositório

> Modelo: substitua todos os placeholders `<...>` e remova instruções não
> aplicáveis antes de salvar este arquivo como `AGENTS.md` na raiz do projeto.

## Produto

`<NOME_DO_PROJETO>` é `<DESCRICAO_CURTA_DO_PRODUTO>`.

- objetivo: `<OBJETIVO>`;
- usuários: `<USUARIOS>`;
- plataformas: `<PLATAFORMAS>`;
- versão canônica: `<ARQUIVO_OU_FONTE_DA_VERSAO>`.

## Fontes de verdade

- comportamento executável: `<CAMINHOS_DE_CODIGO_E_TESTES>`;
- arquitetura: `<DOCUMENTO_DE_ARQUITETURA>`;
- ambiente e comandos: `<DOCUMENTO_DE_AMBIENTE>`;
- estado atual: `<DOCUMENTO_DE_ESTADO>`;
- roadmap: `<DOCUMENTO_DE_ROADMAP>`;
- decisões: `<DIRETORIO_DE_ADRS>`;
- build/release: `<DOCUMENTOS_OU_SCRIPTS>`.

## Estrutura

- `<CAMINHO>`: `<RESPONSABILIDADE>`;
- `<CAMINHO>`: `<RESPONSABILIDADE>`;
- `<CAMINHO>`: `<RESPONSABILIDADE>`.

## Invariantes

1. `<REGRA_QUE_NAO_PODE_SER_QUEBRADA>`.
2. `<REGRA_DE_COMPATIBILIDADE_OU_INTEGRIDADE>`.
3. `<REGRA_DE_SEGURANCA_OU_PRIVACIDADE>`.

## Desenvolvimento

Toolchain: `<SISTEMA_E_VERSOES>`.

```text
<COMANDO_DE_INSTALACAO>
<COMANDO_DE_EXECUCAO>
<COMANDO_DE_LINT>
<COMANDO_DE_TESTES>
<COMANDO_DE_BUILD>
```

## Regras para mudanças

- Faça descoberta somente leitura antes de alterar fluxos desconhecidos.
- Preserve mudanças locais não relacionadas.
- Mudanças de comportamento exigem testes e documentação proporcionais.
- Registre uma ADR quando houver decisão durável de arquitetura,
  compatibilidade, segurança, dados, distribuição ou operação.
- Não registre segredos, dados pessoais ou conteúdo de clientes.

## Verificação

Antes de concluir:

1. execute `<LINT>`;
2. execute `<TESTES>`;
3. execute `<BUILD_OU_SMOKE_TEST_SE_APLICAVEL>`;
4. execute `git diff --check`;
5. confira documentação e versões;
6. relate resultados observados e limitações.

Não faça commit, push, tag, publicação, implantação ou alteração externa sem
autorização explícita do responsável.

## Continuidade

- decisão durável: ADR ou arquitetura;
- progresso e próximo passo: estado atual;
- entrega planejada: roadmap;
- mudança pública: documentação do usuário;
- procedimento operacional: runbook correspondente.

Registre somente contexto material. Não use documentação como transcrição de
conversa ou diário de comandos.
