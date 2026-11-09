# Continuidade e recuperação do desenvolvimento

[Português](CONTINUIDADE.md) | [English](CONTINUITY.en.md)

## Objetivo

Este procedimento permite retomar o projeto se o computador atual falhar ou se
o desenvolvimento migrar para outra máquina. O histórico de conversas pode
ajudar, mas não é fonte canônica de projeto.

## O que precisa existir fora deste computador

### Repositório Git remoto

Antes de encerrar uma etapa, confirme que commits importantes estão no GitHub:

```powershell
git status --short --branch
git log -5 --oneline
git remote -v
```

Código, testes, documentação, tags e releases publicados são recuperáveis pelo
GitHub somente depois de commit e push. Mudanças locais não enviadas precisam
de cópia separada.

### Dados operacionais

O Git não preserva, por desenho:

- `config.json` real;
- projetos originais de IED;
- pastas `ATU`, `HIS` e `IED-QUARENTENA`;
- logs locais e pacotes de diagnóstico;
- `.venv`, `build`, `dist` e `releases` locais;
- credenciais, sessões do GitHub ou certificados.

`ATU`, `HIS` e os projetos de origem devem seguir a política de backup da
organização. Prefira ao menos três cópias, dois meios e uma cópia fora do PC.
Não envie conteúdo operacional para um repositório público.

O `config.json` pode ser copiado para armazenamento privado protegido, mas deve
ser revisto no novo computador porque contém caminhos locais e dados de
colaborador. Nunca o adicione ao Git.

## Preparar uma migração planejada

1. Execute Ruff, Pytest e `git diff --check`.
2. Atualize `docs/ESTADO_ATUAL.md` com versão, branch, validação, pendências e
   próximo passo concreto.
3. Atualize roadmap, ADRs ou arquitetura somente se houve mudança material.
4. Faça commit e push pela política normal do projeto.
5. Confirme que o commit aparece no GitHub e que o CI está aprovado.
6. Confirme que tags/releases importantes e seus hashes continuam acessíveis.
7. Faça backup privado de dados operacionais e, se necessário, do
   `config.json`.
8. Registre separadamente como recuperar credenciais; não coloque segredos nos
   documentos do repositório.

## Restaurar em outro computador

```powershell
git clone https://github.com/machado-jean/ied-backup-tool.git
cd ied-backup-tool
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
```

Depois:

1. leia `AGENTS.md`, `docs/README.md`, `docs/ESTADO_ATUAL.md`, arquitetura e
   ADRs relevantes;
2. restaure ou recrie `config.json` pela interface;
3. conecte `ATU` e `HIS` restaurados e confirme que são pastas distintas;
4. abra primeiro o workspace público de demonstração;
5. execute uma prévia com dados controlados e confirme que nenhuma escrita
   ocorre;
6. somente então valide com uma cópia de dados reais autorizados;
7. não gere release até reproduzir os gates locais.

## Recuperação de mudança sem commit

Se o disco ainda puder ser lido, preserve o diretório inteiro antes de tentar
reparos. Em seguida, capture:

```powershell
git status --short --branch
git diff
git diff --cached
git log -10 --oneline
```

Arquivos ignorados não aparecem normalmente no diff. Copie-os somente para
armazenamento privado e seguro. Não use operações destrutivas como reset ou
clean antes de confirmar que existe uma cópia recuperável.

## Handoff mínimo

Uma pessoa ou agente deve conseguir continuar apenas com o repositório. O
handoff em `ESTADO_ATUAL.md` deve informar:

- versão e branch vigentes;
- último estado validado;
- alteração em andamento, se houver;
- arquivos ou módulos mais relevantes;
- testes executados e resultados;
- riscos, limitações e decisões abertas;
- próximo passo pequeno e verificável.

Não inclua transcrição de conversa nem saída rotineira de comandos. Inclua o
motivo de decisões que possam ser interpretadas de forma diferente no futuro.

## Verificação periódica

Ao menos antes de cada release:

- teste um clone limpo;
- instale as dependências a partir do arquivo versionado;
- execute a bateria completa;
- confirme que a documentação de ambiente ainda é suficiente;
- verifique acesso aos releases e hashes;
- confirme que o backup privado de dados operacionais é restaurável.
