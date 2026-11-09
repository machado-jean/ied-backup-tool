# Orientações permanentes do repositório

Este arquivo é a entrada de contexto para agentes de desenvolvimento. Ele não
substitui o código, os testes ou a documentação canônica. Antes de alterar o
projeto, leia este arquivo e os documentos indicados para o escopo da tarefa.

## Produto

O IED Backup Manager é uma aplicação Windows, em Python e PySide6, que cria
backups rastreáveis de projetos de IED. O fluxo mantém um backup atual em
`ATU`, versões anteriores em `HIS` e metadados `IEDS-BACKUP-INFO.txt` dentro de
cada ZIP. A aplicação possui interface gráfica e uma entrada CLI.

Versão, nome do aplicativo e identidade visual devem permanecer coerentes com
`src/version.py`, `README.md`, o fluxo de release e os artefatos publicados.

## Fontes de verdade

- comportamento executável: `src/` e testes em `tests/`;
- versão do aplicativo: `src/version.py`;
- arquitetura e fronteiras: `docs/ARQUITETURA.md`;
- ambiente e comandos: `docs/AMBIENTE_DESENVOLVIMENTO.md`;
- estado, pendências e retomada: `docs/ESTADO_ATUAL.md`;
- roadmap e histórico de marcos: `docs/PLANO_MELHORIAS.md`;
- decisões duráveis: `docs/decisions/`;
- operação do usuário: `docs/USO_EXECUTAVEL.md` e `docs/HELP.md`;
- regras por tipo de IED: `docs/LOGICA_IDENTIFICACAO_IEDS.md`;
- geração e publicação de release: `scripts/release.ps1`,
  `scripts/PUBLISH_RELEASE.Template.ps1` e `CONTRIBUTING.md`.

Consulte `docs/README.md` para o catálogo completo.

## Fronteiras do código

- `src/core/`: domínio, planejamento, integridade, armazenamento e regras
  independentes da interface;
- `src/core/project_types/`: comportamento específico de cada fabricante ou
  família de projeto;
- `src/config/`: leitura, validação e persistência da configuração local;
- `src/gui/`: apresentação PySide6, workers, diálogos e coordenação da UI;
- `src/main.py`: interface de linha de comando;
- `tests/`: regressões unitárias e de integração leve.

Evite colocar regras de negócio em widgets. A GUI deve montar solicitações,
mostrar prévias e delegar planejamento/execução aos serviços existentes.

## Invariantes operacionais

1. A prévia não deve mover, remover ou publicar arquivos.
2. `ATU` e `HIS` devem ser pastas distintas e validadas antes da execução.
3. Um ZIP deve ser criado e validado antes de substituir o backup atual.
4. Conflitos de mesma identidade técnica com SHA256 divergente não devem ser
   sobrescritos silenciosamente.
5. Cancelamento deve ocorrer em limites seguros, sem publicar arquivo parcial.
6. Falhas de movimentação não devem apagar a última cópia válida; quando
   aplicável, preservar material recuperável em `IED-QUARENTENA`.
7. Arquivos reais de IED, `config.json`, caminhos internos, credenciais e dados
   de clientes não podem entrar no repositório.
8. Exemplos públicos devem usar identificadores fictícios e dados sanitizados.

## Desenvolvimento

Ambiente recomendado: Windows 10/11, Python 3.13 e `.venv` local.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m src.gui.app
```

Para abrir a interface com o workspace público de demonstração:

```powershell
.\.venv\Scripts\python.exe -m src.gui.app --project-dir ".\docs\examples\sample-workspace"
```

## Regras para mudanças

- Faça primeiro uma descoberta somente leitura do código e dos testes do fluxo.
- Preserve mudanças locais não relacionadas.
- Mudança de comportamento exige teste focado e atualização da documentação
  afetada.
- Novo tipo de IED deve usar `src/core/project_types/`, ser registrado no
  registry e possuir amostra segura ou fixture suficiente para comprovar
  detecção, versão e arquivos incluídos.
- Mudanças em nomes, identidade técnica, `ATU`/`HIS`, ZIP ou metadados exigem
  regressões explícitas de compatibilidade e recuperação.
- Registre uma nova ADR quando uma escolha alterar de forma durável arquitetura,
  formato, compatibilidade, segurança, distribuição ou fronteiras do sistema.
- Não reescreva ADR aceita para esconder uma decisão antiga; marque-a como
  substituída e crie outra.

## Verificação e entrega

Antes de considerar uma alteração concluída:

1. execute `ruff check .`;
2. execute a bateria relevante de `pytest` e, quando possível, a bateria toda;
3. execute `git diff --check`;
4. confira se documentação e pares PT-BR/English afetados continuam coerentes;
5. relate os comandos realmente executados e limitações de validação.

Não faça commit, push, tag, publicação de release, upload de dados ou alteração
em serviços externos sem solicitação explícita do usuário.

## Continuidade

Ao encerrar uma etapa material, atualize apenas as fontes correspondentes:

- descoberta ou decisão durável: ADR ou documento arquitetural;
- progresso, pendência ou próximo passo: `docs/ESTADO_ATUAL.md`;
- entrega planejada ou marco concluído: `docs/PLANO_MELHORIAS.md`;
- mudança pública de uso: README, ajuda e manual aplicáveis.

Não use documentos como transcrição de conversa. Registre somente contexto que
possa mudar uma implementação futura, evitar redescoberta ou preservar uma
restrição, decisão, evidência ou pendência relevante.
