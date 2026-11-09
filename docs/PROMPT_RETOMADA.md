# Prompt para retomar o desenvolvimento

[Português](PROMPT_RETOMADA.md) | [English](DEVELOPMENT_RESUME_PROMPT.en.md)

Use este prompt depois de clonar o repositório e abrir sua pasta no Codex ou em
outro agente de desenvolvimento. O repositório deve ser tratado como fonte de
verdade; não é necessário recuperar conversas anteriores.

```text
Quero retomar o desenvolvimento do IED Backup Manager neste computador.

Antes de alterar qualquer arquivo, faça uma descoberta somente leitura do
repositório.

1. Leia integralmente:
   - AGENTS.md
   - docs/README.md
   - docs/ESTADO_ATUAL.md
   - docs/ARQUITETURA.md
   - docs/AMBIENTE_DESENVOLVIMENTO.md
   - docs/PLANO_MELHORIAS.md
   - docs/decisions/README.md
   - as ADRs relevantes
   - CONTRIBUTING.md

2. Confira:
   - branch e estado do Git;
   - versão atual em src/version.py;
   - estrutura de src/ e tests/;
   - comandos reais de instalação, execução e verificação;
   - roadmap ativo, pendências e próximo ponto de retomada;
   - se há contradições ou documentação desatualizada.

3. Verifique se o ambiente Python está preparado. Se a .venv não existir,
   informe os comandos necessários antes de instalar qualquer coisa.

4. Não modifique código, documentação, configuração, Git ou serviços externos
   nesta etapa.

Ao terminar, apresente:
- sua compreensão do produto;
- arquitetura e invariantes que devem ser preservadas;
- estado atual do desenvolvimento;
- próxima prioridade documentada;
- possíveis bloqueios ou informações que ainda dependem de mim;
- plano pequeno e verificável para a próxima etapa.

Não dependa do histórico de conversas anteriores. Use o repositório como fonte
de verdade.
```

## Prompt para iniciar a próxima etapa

Depois de revisar e aprovar a análise inicial, use:

```text
A análise está correta. Vamos trabalhar na próxima prioridade documentada.

Antes de implementar:
- delimite exatamente o escopo;
- indique os arquivos provavelmente afetados;
- defina testes e critérios de aceitação;
- informe decisões que precisam da minha confirmação.

Não comece trabalho fora desse escopo e não faça commit, push, tag ou publicação
sem minha autorização explícita.
```

## Preparação mínima do computador

Antes de usar o prompt, clone o projeto e prepare o ambiente conforme
[`AMBIENTE_DESENVOLVIMENTO.md`](AMBIENTE_DESENVOLVIMENTO.md). O fluxo resumido
é:

```powershell
git clone https://github.com/machado-jean/ied-backup-tool.git
cd ied-backup-tool
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
```
