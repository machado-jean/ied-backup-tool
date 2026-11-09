# Kit genérico de continuidade de projetos

Esta pasta é um modelo reutilizável para preparar projetos de software para
migração, retomada em outro computador e continuidade com pessoas ou agentes
que não possuem acesso às conversas anteriores.

Ela pode ser copiada para projetos públicos ou privados. Antes de preencher ou
versionar os modelos, remova dados pessoais, credenciais, segredos, arquivos de
clientes e qualquer conteúdo sem autorização para armazenamento no Git.

## Conteúdo

```text
project-continuity-kit/
├── README.md
├── AUDITORIA.md
├── CHECKLIST_TRANSFERENCIA.md
└── templates/
    ├── AGENTS.template.md
    ├── docs-README.template.md
    ├── ARQUITETURA.template.md
    ├── AMBIENTE_DESENVOLVIMENTO.template.md
    ├── CONTINUIDADE.template.md
    ├── ESTADO_ATUAL.template.md
    ├── ROADMAP.template.md
    ├── PROMPT_RETOMADA.template.md
    ├── decisions-README.template.md
    └── ADR.template.md
```

## Como usar em outro projeto

1. Copie a pasta `project-continuity-kit/` para o projeto que será auditado.
2. Leia `AUDITORIA.md` e execute primeiro apenas verificações de leitura.
3. Classifique Git, conversas e arquivos locais antes de criar documentos.
4. Copie somente os modelos necessários para os destinos abaixo.
5. Substitua todos os marcadores `<...>` por fatos verificados.
6. Remova seções não aplicáveis; não invente conteúdo para preencher o modelo.
7. Valide links, comandos, testes, build e restauração.
8. Faça commit e push somente após revisão e autorização.
9. Depois da adoção, remova `project-continuity-kit/` do projeto de destino
   antes do commit. Os documentos preenchidos passam a ser as únicas fontes de
   verdade daquele projeto.

Este repositório mantém a cópia canônica do kit. Nos demais projetos, copie a
pasta apenas como material temporário de preparação. Se houver uma necessidade
real de versionar o kit em outro lugar, mantenha-o em um repositório central
separado e use links; não preserve modelos ao lado dos documentos preenchidos.

## Destinos sugeridos

| Modelo | Destino no projeto |
| --- | --- |
| `AGENTS.template.md` | `AGENTS.md` |
| `docs-README.template.md` | `docs/README.md` |
| `ARQUITETURA.template.md` | `docs/ARQUITETURA.md` |
| `AMBIENTE_DESENVOLVIMENTO.template.md` | `docs/AMBIENTE_DESENVOLVIMENTO.md` |
| `CONTINUIDADE.template.md` | `docs/CONTINUIDADE.md` |
| `ESTADO_ATUAL.template.md` | `docs/ESTADO_ATUAL.md` |
| `ROADMAP.template.md` | `docs/ROADMAP.md` |
| `PROMPT_RETOMADA.template.md` | `docs/PROMPT_RETOMADA.md` |
| `decisions-README.template.md` | `docs/decisions/README.md` |
| `ADR.template.md` | `docs/decisions/NNN-titulo.md` |

## Conjunto mínimo

Para um projeto pequeno, normalmente bastam:

- `AGENTS.md`;
- README principal com instalação e execução;
- `docs/ESTADO_ATUAL.md`;
- `docs/PROMPT_RETOMADA.md`.

Adicione arquitetura, ambiente, continuidade, roadmap e ADRs quando a
complexidade ou o risco justificarem. Documentação em excesso também pode ficar
desatualizada; cada arquivo deve possuir uma responsabilidade clara.

## Evitar fontes duplicadas

- Um fato deve possuir uma fonte canônica.
- `AGENTS.md` aponta para documentos; não deve copiar manuais inteiros.
- Estado atual não substitui roadmap nem changelog.
- Roadmap registra intenção; testes e código comprovam comportamento.
- ADR registra a decisão e o motivo; arquitetura descreve o desenho vigente.
- Manual do usuário e documentação técnica podem abordar o mesmo recurso para
  públicos diferentes, mas devem linkar a regra canônica quando houver risco de
  divergência.
- Depois de preencher os modelos, apague a cópia temporária do kit no projeto
  de destino.

## Regras de segurança

- Repositório privado não é gerenciador de segredos.
- Não versione tokens, senhas, chaves privadas ou certificados privados.
- Não copie bancos, projetos reais ou arquivos de clientes sem necessidade e
  autorização explícitas.
- Prefira exemplos artificiais ou sanitizados.
- Use backup privado criptografado para dados operacionais.
- Se um segredo já foi commitado, revogue ou rotacione a credencial; apenas
  removê-lo do arquivo atual não resolve a exposição histórica.

## Marcadores usados nos modelos

Textos entre sinais de menor/maior, como `<NOME_DO_PROJETO>`, são placeholders.
Todos devem ser removidos ou substituídos antes do documento ser considerado
pronto.

Uma busca útil é:

```powershell
rg -n "<[^>]+>" AGENTS.md docs
```
