# Auditoria de continuidade para outros projetos

[Português](AUDITORIA_CONTINUIDADE_PROJETOS.md) | [English](PROJECT_CONTINUITY_AUDIT.en.md)

## Objetivo

Este guia descreve como preparar qualquer projeto para ser retomado em outro
computador, por outra pessoa ou por outro agente de desenvolvimento, sem
depender do histórico de conversas nem de arquivos existentes somente na
máquina original.

O resultado esperado é um repositório que contenha o código, o contexto técnico
material e instruções suficientes para reconstruir o ambiente e continuar o
trabalho com segurança.

## Princípios

1. O repositório deve ser a fonte de verdade do desenvolvimento.
2. Conversas ajudam a reconstruir decisões, mas não devem ser a única memória.
3. Somente informações materiais devem virar documentação permanente.
4. Segredos e dados operacionais não pertencem ao Git.
5. Um repositório privado reduz exposição, mas não substitui gestão de segredos.
6. A transferência só está comprovada depois de um teste de restauração.
7. Commit, push, criação de repositório e uploads exigem autorização explícita.

## 1. Auditar o Git

Quando o projeto já usa Git, verificar:

```powershell
git status --short --branch
git remote -v
git log -10 --oneline --decorate
git branch --show-current
git tag --sort=-version:refname
```

Confirmar:

- branch principal e branches ainda relevantes;
- remoto correto;
- commits locais ainda não enviados;
- mudanças modificadas, staged ou não rastreadas;
- tags e releases;
- arquivos ignorados;
- submódulos, Git LFS ou dependências externas;
- diferença entre o estado local e o remoto.

Para investigar arquivos ignorados sem alterar nada:

```powershell
git status --ignored --short
git ls-files --others --ignored --exclude-standard
```

Não executar `git clean`, reset destrutivo ou exclusão antes de classificar e
preservar os arquivos necessários.

### Projeto sem Git

Se o projeto ainda não possui Git:

1. inventariar arquivos antes de inicializar o repositório;
2. separar código, documentação, artefatos, dados e segredos;
3. criar um `.gitignore` adequado;
4. verificar cuidadosamente o conteúdo que entrará no primeiro commit;
5. decidir se o remoto será público ou privado;
6. criar e publicar o repositório somente após autorização explícita.

## 2. Revisar as conversas relacionadas

Localizar as conversas associadas ao projeto e extrair somente informações que
possam afetar trabalho futuro:

- decisões do usuário;
- requisitos e limites de escopo;
- arquitetura escolhida e alternativas rejeitadas;
- regras de compatibilidade;
- correções cuja causa não seja óbvia pelo código;
- riscos de segurança, privacidade e recuperação;
- comandos confiáveis de build, teste e publicação;
- pendências, bloqueios e próximos passos;
- evidências de validação importantes;
- dependências ou arquivos existentes somente no computador original.

Não transformar a conversa inteira em documentação. Excluir:

- narração passo a passo sem valor futuro;
- saídas rotineiras de comandos;
- tentativas abandonadas que não influenciaram o resultado;
- especulação não confirmada;
- duplicação do código, testes ou documentação já canônica;
- tokens, senhas, chaves, dados pessoais e conteúdo operacional.

Para cada informação relevante, verificar primeiro se ela já está preservada
em código, teste, commit, issue, release ou documento. Criar documentação nova
somente quando ainda existir uma lacuna real.

## 3. Consolidar o contexto no repositório

Criar apenas os documentos necessários. Uma estrutura possível é:

```text
AGENTS.md
docs/
├── README.md
├── ARQUITETURA.md
├── AMBIENTE_DESENVOLVIMENTO.md
├── CONTINUIDADE.md
├── ESTADO_ATUAL.md
├── PLANO_MELHORIAS.md
├── PROMPT_RETOMADA.md
└── decisions/
    ├── README.md
    ├── template.md
    └── NNN-decisao.md
```

### Responsabilidade de cada documento

| Documento | Responsabilidade |
| --- | --- |
| `AGENTS.md` | Orientações permanentes, fontes de verdade, invariantes e comandos. |
| `docs/README.md` | Índice e finalidade da documentação. |
| Arquitetura | Componentes, dependências, fluxos e fronteiras. |
| Ambiente | Ferramentas, versões e reconstrução do computador. |
| Continuidade | Migração, backup, restauração e handoff. |
| Estado atual | Versão, validação, pendências e próximo ponto de retomada. |
| Roadmap | Entregas planejadas, marcos e itens descartados ou pausados. |
| Prompt de retomada | Instrução pronta para orientar um novo agente. |
| ADRs | Contexto, decisão, alternativas e consequências duráveis. |

Não é obrigatório criar todos os arquivos. Projetos pequenos podem usar um
`AGENTS.md`, um README e um único documento de continuidade. Projetos maiores
podem exigir runbooks específicos para build, release, implantação, banco de
dados, recuperação ou suporte.

## 4. Classificar arquivos existentes somente no computador

Cada arquivo local deve pertencer a uma categoria:

| Categoria | Exemplos | Destino recomendado |
| --- | --- | --- |
| Fonte indispensável | código, scripts, migrations, documentação | Git |
| Contexto durável | decisões, arquitetura, procedimentos | Git |
| Configuração de exemplo | estrutura sem valores reais | Git |
| Configuração local | caminhos, preferências e nomes reais | backup privado ou recriação |
| Dados operacionais | bancos, projetos, backups e documentos reais | armazenamento privado autorizado |
| Segredos | tokens, chaves, certificados e senhas | gerenciador de segredos |
| Artefatos versionados | instaladores e pacotes publicados | GitHub Releases ou equivalente |
| Arquivos grandes necessários | modelos, datasets e binários fonte | Git LFS ou armazenamento de artefatos |
| Ambiente reproduzível | `.venv`, `node_modules`, caches | recriar; não versionar |
| Temporários | logs descartáveis, caches e builds intermediários | remover quando seguro |

Para itens relevantes, registrar:

- caminho ou categoria, sem expor dados sensíveis;
- tamanho aproximado;
- motivo para preservação;
- local de backup;
- procedimento de restauração;
- proprietário e restrições de acesso, quando aplicável.

## 5. Escolher onde guardar

### Repositório público

Usar somente para conteúdo que pode ser divulgado:

- código autorizado;
- documentação pública;
- fixtures artificiais ou sanitizadas;
- exemplos genéricos;
- arquivos sem credenciais ou dados de terceiros.

### Repositório privado

É adequado para código e documentação que não devem ser públicos, desde que o
usuário tenha autorização para armazená-los no serviço escolhido.

Um repositório privado não é local adequado para:

- senhas e tokens;
- chaves privadas;
- certificados com chave privada;
- bancos de produção desnecessários;
- dados pessoais ou operacionais sem necessidade e autorização;
- arquivos de clientes sujeitos a restrições contratuais.

### GitHub Releases ou armazenamento de artefatos

Usar para executáveis, instaladores, ZIPs e pacotes associados a versões.
Registrar versão, hash e procedimento de reconstrução sempre que possível.

### Git LFS

Usar apenas quando arquivos grandes precisam genuinamente de histórico junto ao
projeto. Antes de adotar, verificar limites, custos, retenção e recuperação.

### Backup privado criptografado

Usar para dados reais, configurações sensíveis, amostras autorizadas, bancos e
outros materiais que não pertencem ao Git. Aplicar a política 3-2-1 quando o
valor dos dados justificar:

- três cópias;
- dois tipos de armazenamento;
- uma cópia fora do computador principal.

### Gerenciador de segredos

Tokens, senhas e chaves devem ser recriados ou recuperados por um gerenciador
de segredos. A documentação deve explicar quais credenciais são necessárias,
mas nunca registrar seus valores.

## 6. Segurança antes do primeiro push

Antes de enviar um projeto novo ou uma grande consolidação:

- revisar o diff e a lista completa de arquivos;
- procurar tokens, senhas, chaves e credenciais;
- procurar caminhos de usuário, nomes reais e identificadores de clientes;
- revisar histórico, fixtures, screenshots e documentos;
- confirmar licenças de código, dependências e assets;
- verificar se arquivos grandes foram incluídos acidentalmente;
- confirmar `.gitignore` e regras de Git LFS;
- remover dados sensíveis antes do commit, não apenas depois do push.

Se um segredo já tiver sido commitado, removê-lo do arquivo não basta: revogar
ou rotacionar a credencial e avaliar a limpeza do histórico.

## 7. Validar documentação e projeto

Executar as verificações adequadas à tecnologia:

- lint e formatação;
- testes unitários e de integração;
- build reproduzível;
- verificação de links Markdown;
- consistência de versão;
- correspondência entre documentação e comportamento;
- `git diff --check`;
- smoke test da aplicação empacotada, quando houver.

Registrar somente comandos realmente executados, resultados observados e
limitações. Não declarar que um teste passou quando ele não foi executado.

## 8. Testar a restauração

A transferência somente está comprovada depois deste teste:

1. clonar o repositório em uma pasta limpa ou em outro computador;
2. seguir exclusivamente a documentação versionada;
3. instalar ferramentas e dependências;
4. executar lint, testes e build;
5. restaurar somente os dados privados necessários;
6. abrir ou executar o produto;
7. pedir a uma pessoa ou agente sem contexto anterior para explicar o projeto;
8. registrar lacunas encontradas e corrigi-las no repositório.

O teste deve responder:

- É possível reconstruir o ambiente?
- A versão e o estado atual estão claros?
- O próximo trabalho está delimitado?
- As decisões importantes possuem justificativa?
- Dados locais ausentes impedem desenvolvimento ou apenas uso operacional?
- Builds e releases podem ser reproduzidos?
- Há alguma dependência silenciosa da máquina antiga?

## 9. Critérios de conclusão

Uma auditoria pode ser considerada concluída quando:

- o Git está limpo ou todas as mudanças locais estão explicadas;
- o remoto contém todos os commits que precisam ser preservados;
- arquivos locais relevantes estão classificados e protegidos;
- segredos estão fora do Git;
- decisões materiais das conversas foram preservadas nas fontes corretas;
- o estado atual e o próximo passo são compreensíveis;
- o ambiente pode ser reconstruído;
- testes proporcionais ao risco foram executados;
- a restauração foi comprovada ou suas limitações estão documentadas;
- nenhuma ação externa pendente foi apresentada como concluída.

## Prompt reutilizável

Use o texto abaixo em qualquer projeto:

```text
Quero preparar este projeto para poder continuar o desenvolvimento em outro
computador sem depender do histórico desta conversa.

Faça primeiro uma auditoria somente leitura.

1. Se houver Git, verifique branch, remotos, sincronização, commits, tags,
   mudanças locais, arquivos não rastreados e ignorados.
2. Localize e revise as conversas relacionadas ao projeto. Extraia somente
   decisões, requisitos, restrições, causas de correções, pendências e próximos
   passos que ainda não estejam preservados no repositório.
3. Inventarie arquivos existentes somente neste computador e classifique-os
   como fonte, contexto, configuração local, dado operacional, segredo,
   artefato, arquivo grande reproduzível ou temporário.
4. Verifique código, testes, documentação, build, release e dependências para
   determinar se o projeto pode ser reconstruído em uma máquina limpa.
5. Identifique conteúdo sensível ou de terceiros que não possa ser enviado ao
   Git.

Antes de escrever, apresente:
- o estado atual do Git;
- o contexto relevante encontrado nas conversas;
- o que já está preservado;
- o que ainda pode ser perdido;
- os documentos ou ajustes que propõe criar;
- quais itens devem ficar em Git público, Git privado, Releases, Git LFS,
  backup criptografado ou gerenciador de segredos;
- riscos, dúvidas e decisões que dependem de mim.

Depois da minha aprovação, consolide somente o contexto material necessário.
Quando aplicável, crie ou atualize AGENTS.md, índice documental, arquitetura,
ambiente, continuidade, estado atual, roadmap, prompt de retomada e ADRs.

Não copie transcrições completas para o repositório. Não inclua segredos, dados
operacionais, caminhos pessoais ou arquivos de clientes. Não faça commit,
push, crie repositório, publique release, use Git LFS ou envie arquivos sem
minha autorização explícita.

Ao terminar, valide links, formatação, testes relevantes e git diff --check.
Relate exatamente o que foi alterado, o que foi validado e o que ainda depende
de backup ou ação externa.
```

## Prompt de retomada depois da transferência

Quando a auditoria e a transferência estiverem concluídas, adaptar e usar:

```text
Quero retomar o desenvolvimento deste projeto neste computador.

Antes de alterar qualquer arquivo, leia integralmente o AGENTS.md, o índice da
documentação, o estado atual, a arquitetura, o ambiente, o roadmap e as ADRs
relevantes. Confira o estado do Git, a versão, os testes e os comandos reais de
execução.

Não modifique nada nesta primeira etapa. Apresente sua compreensão do produto,
as invariantes, o estado atual, a próxima prioridade, os bloqueios e um plano
pequeno e verificável.

Não dependa de conversas anteriores. Use o repositório como fonte de verdade.
```

## Manutenção contínua

Repetir uma auditoria reduzida:

- antes de trocar de computador;
- antes de arquivar ou abandonar um projeto;
- antes de releases importantes;
- após decisões arquiteturais relevantes;
- quando muitas conversas acumularem conhecimento não documentado;
- quando o projeto passar a depender de novos dados ou serviços externos.

O objetivo não é produzir documentação em excesso. É garantir que nenhuma
decisão, dependência ou arquivo indispensável exista somente na memória de uma
pessoa, em uma conversa ou em um único computador.
