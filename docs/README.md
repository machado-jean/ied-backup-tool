# Índice da documentação

Este é o ponto de entrada para manutenção e continuidade do IED Backup Manager.
Ao criar, mover ou excluir documentação permanente, atualize este índice na
mesma alteração. O código e os testes continuam sendo a fonte de verdade para o
comportamento executável.

[Português](README.md) | [English](README.en.md)

## Continuidade e desenvolvimento

| Documento | Finalidade | Revisar quando |
| --- | --- | --- |
| [`AGENTS.md`](../AGENTS.md) | Contexto permanente, invariantes e forma de trabalhar no repositório. | Mudança de arquitetura, processo, segurança ou verificação. |
| [`ARQUITETURA.md`](ARQUITETURA.md) | Componentes, dependências, fluxos e fronteiras do sistema. | Mudança estrutural ou novo subsistema. |
| [`AMBIENTE_DESENVOLVIMENTO.md`](AMBIENTE_DESENVOLVIMENTO.md) | Preparação reproduzível do PC e comandos de desenvolvimento. | Mudança de Python, dependência, ferramenta ou comando. |
| [`CONTINUIDADE.md`](CONTINUIDADE.md) | Migração para outro computador, backup e recuperação do projeto. | Mudança em dados locais, Git, release ou restauração. |
| [`PROMPT_RETOMADA.md`](PROMPT_RETOMADA.md) | Prompt pronto para orientar a retomada em outro computador ou agente. | Mudança nas fontes de contexto, preparação ou processo de retomada. |
| [`project-continuity-kit/`](../project-continuity-kit/README.md) | Kit autocontido com checklist e modelos genéricos para copiar a outros projetos. | Mudança nos modelos ou no processo reutilizável. |
| [`ESTADO_ATUAL.md`](ESTADO_ATUAL.md) | Foto curta da versão vigente, validação, pendências e próximo ponto de retomada. | Ao concluir trabalho material ou mudar a próxima prioridade. |
| [`PLANO_MELHORIAS.md`](PLANO_MELHORIAS.md) | Roadmap ativo e histórico dos marcos implementados. | Nova entrega, adiamento ou mudança de prioridade. |
| [`RELEASE.md`](RELEASE.md) | Build, smoke test, gates, tag e publicação de releases. | Mudança em versão, CI, scripts, artefatos ou processo de publicação. |
| [`decisions/README.md`](decisions/README.md) | Catálogo de decisões arquiteturais (ADRs). | Nova decisão ou substituição de decisão existente. |
| [`decisions/template.md`](decisions/template.md) | Modelo para registrar uma decisão. | Mudança no formato exigido para ADRs. |

Os pares em inglês são `README.en.md`, `ARCHITECTURE.en.md`,
`DEVELOPMENT_ENVIRONMENT.en.md`, `CONTINUITY.en.md`,
`DEVELOPMENT_RESUME_PROMPT.en.md` e `CURRENT_STATE.en.md`.

## Uso e suporte

| Documento | Finalidade |
| --- | --- |
| [`USO_EXECUTAVEL.md`](USO_EXECUTAVEL.md) | Manual de uso do executável em português. |
| [`EXECUTABLE_USAGE.en.md`](EXECUTABLE_USAGE.en.md) | Manual equivalente em inglês. |
| [`HELP.md`](HELP.md) | Ajuda, limitações, privacidade e solução de problemas. |
| [`HELP.en.md`](HELP.en.md) | Ajuda equivalente em inglês. |
| [`COLETA_DIAGNOSTICO.md`](COLETA_DIAGNOSTICO.md) | Coleta segura e consentida de diagnóstico. |
| [`DIAGNOSTIC_COLLECTION.en.md`](DIAGNOSTIC_COLLECTION.en.md) | Diagnóstico equivalente em inglês. |

## Regras técnicas e exemplos

| Documento | Finalidade |
| --- | --- |
| [`LOGICA_IDENTIFICACAO_IEDS.md`](LOGICA_IDENTIFICACAO_IEDS.md) | Regras de detecção, versão e conteúdo por tipo de IED. |
| [`IED_IDENTIFICATION_LOGIC.en.md`](IED_IDENTIFICATION_LOGIC.en.md) | Regras equivalentes em inglês. |
| [`examples/README.md`](examples/README.md) | Limites e uso dos arquivos públicos de demonstração. |

## Documentos da raiz

| Documento | Finalidade |
| --- | --- |
| [`README.md`](../README.md) / [`README.en.md`](../README.en.md) | Apresentação pública, recursos e fluxo principal. |
| [`CONTRIBUTING.md`](../CONTRIBUTING.md) / [`CONTRIBUTING.en.md`](../CONTRIBUTING.en.md) | Ambiente, contribuição, testes e limites de dados. |
| [`LICENSE`](../LICENSE) | Termos não comerciais do projeto. |

## Regra de atualização

- Não copie fatos que já possuem uma fonte canônica; crie links.
- Não registre segredos, dados reais de IED, caminhos corporativos ou conteúdo
  pessoal.
- ADRs preservam o contexto histórico; uma decisão substituída não deve ser
  apagada.
- `ESTADO_ATUAL.md` é uma fotografia de retomada, não um diário completo.
- Para mudanças públicas, mantenha PT-BR e English equivalentes.
