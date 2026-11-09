# Decisões arquiteturais

Este diretório registra decisões duráveis do IED Backup Manager no formato ADR
(Architecture Decision Record). ADRs explicam o contexto e as consequências de
uma escolha; não substituem código, testes, roadmap ou manual do usuário.

## Estados

- **Proposta:** ainda requer decisão do mantenedor;
- **Aceita:** decisão vigente;
- **Substituída:** outra ADR passou a ser vigente;
- **Rejeitada:** avaliada e não adotada.

Depois de aceita, uma ADR não deve ser reescrita apenas porque a arquitetura
mudou. Crie outra ADR e registre a substituição. Correções factuais pequenas,
links e erros de digitação podem ser ajustados sem alterar a decisão histórica.

## Catálogo

| ADR | Estado | Decisão |
| --- | --- | --- |
| [`001-python-pyside6-windows.md`](001-python-pyside6-windows.md) | Aceita | Aplicação Windows em Python com GUI PySide6 e executável PyInstaller. |
| [`002-preview-before-write.md`](002-preview-before-write.md) | Aceita | Separar planejamento somente leitura de execução confirmada. |
| [`003-atu-his-transactional-storage.md`](003-atu-his-transactional-storage.md) | Aceita | Manter atual em ATU, anteriores em HIS e publicar ZIP validado. |
| [`004-project-type-adapters.md`](004-project-type-adapters.md) | Aceita | Isolar regras de fabricantes em adaptadores registrados. |
| [`005-local-configuration-and-private-data.md`](005-local-configuration-and-private-data.md) | Aceita | Configuração e dados operacionais permanecem locais e fora do Git. |
| [`006-family-based-current-backup-identity.md`](006-family-based-current-backup-identity.md) | Aceita | Backup atual usa família de software e escolhas explícitas para ambiguidades. |
| [`007-consented-crash-diagnostics.md`](007-consented-crash-diagnostics.md) | Aceita | Diagnóstico de encerramento inesperado é concorrente, limitado e consentido. |
| [`008-native-tls-trust-for-update-checks.md`](008-native-tls-trust-for-update-checks.md) | Aceita | Consulta de atualização usa confiança TLS nativa sem reduzir validação. |
| [`009-gated-release-publication.md`](009-gated-release-publication.md) | Aceita | Publicador controla tag e release somente após gates e confirmação. |

## Quando criar uma ADR

Crie uma ADR para mudança durável em arquitetura, formato de ZIP/metadados,
identidade técnica, compatibilidade, armazenamento, recuperação, privacidade,
segurança ou distribuição. Não crie ADR para correção pequena, refatoração sem
efeito arquitetural ou simples progresso de implementação.

Use [`template.md`](template.md), escolha o próximo número e atualize este
catálogo e `docs/README.md`.
