# Contribuindo com o IED Backup Manager

Obrigado por considerar uma contribuicao. Este projeto aceita correcoes,
melhorias de documentacao, novos exemplos publicos e suporte a novos tipos de
IED, desde que os arquivos compartilhados nao contenham informacoes
confidenciais.

## Requisitos de Desenvolvimento

Ambiente recomendado:

- Windows 10 ou Windows 11;
- Python 3.12 ou superior;
- Git;
- PowerShell;
- acesso ao repositorio GitHub;
- ambiente virtual `.venv` local.

Criar o ambiente:

```powershell
git clone https://github.com/machado-jean/ied-backup-tool.git
cd ied-backup-tool
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Rodar a aplicacao em desenvolvimento:

```powershell
.\.venv\Scripts\python.exe -m src.gui.app
```

Rodar com os exemplos publicos:

```powershell
.\.venv\Scripts\python.exe -m src.gui.app --project-dir ".\docs\examples\sample-workspace"
```

Validar antes de abrir um pull request:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
```

## Como Reportar Erros

Antes de abrir uma issue:

1. Confirme se esta usando a versao mais recente publicada.
2. Tente reproduzir o erro com os arquivos de exemplo em `docs/examples`.
3. Verifique se `ATU` e `HIS` apontam para pastas diferentes e acessiveis.
4. Confirme se os arquivos de trabalho nao estao abertos em outro software.

Ao reportar, inclua:

- versao do IED Backup Manager;
- versao do Windows;
- tipo de IED selecionado;
- etapa selecionada;
- caminho geral da estrutura, sem dados confidenciais;
- passos para reproduzir;
- resultado esperado;
- resultado obtido;
- prints, se ajudarem;
- mensagem de erro completa, se houver.

Nao envie `config.json` real, caminhos internos de empresa, nomes reais de
colaboradores ou arquivos de backup com dados operacionais.

## Como Sugerir Melhorias

Ao sugerir uma melhoria, descreva:

- problema operacional que a melhoria resolve;
- fluxo atual;
- fluxo desejado;
- impacto esperado;
- se a mudanca afeta nomes de arquivos, `ATU`, `HIS`, metadados ou integridade.

Mudancas pequenas e bem delimitadas tendem a ser avaliadas mais rapidamente.

## Como Abrir Pull Requests

Fluxo recomendado:

1. Crie uma branch a partir da branch principal.
2. Mantenha a alteracao focada em um unico objetivo.
3. Atualize testes quando houver mudanca de comportamento.
4. Atualize documentacao quando houver mudanca visivel ao usuario.
5. Rode `ruff` e `pytest`.
6. Abra o pull request usando o template do repositorio.

Evite incluir:

- executaveis `.exe`;
- arquivos em `releases/`;
- `.spec`;
- `.venv/`;
- `config.json`;
- backups reais;
- arquivos com dados confidenciais;
- alteracoes de formatacao sem relacao com o objetivo do PR.

## Contribuicoes com Novos IEDs

Novos tipos de IED sao bem-vindos, mas precisam de amostras seguras para teste.

Voce pode contribuir com:

- arquivo limpo gerado por um novo projeto vazio no software do fabricante;
- backup demonstrativo sem dados de cliente, subestacao real, rede, IP,
  usuarios, caminhos internos ou nomes reais;
- arquivo sanitizado, quando a sanitizacao nao quebrar a estrutura necessaria
  para deteccao de versao;
- descricao textual do formato, caso o arquivo nao possa ser compartilhado.

Ao enviar arquivos de exemplo:

- use nomes genericos, como `SE-AAA`, `ETD-BBB`, `VAO-ZZZ`;
- use colaborador `COLABORADOR-EXEMPLO`;
- documente qual software gerou o arquivo;
- informe a versao esperada do software;
- indique qual extensao deve ser considerada arquivo principal;
- indique quais arquivos acompanhantes devem entrar no ZIP, se existirem.

Nao envie arquivos que contenham:

- nomes reais de subestacoes, clientes, projetos ou colaboradores;
- enderecos IP, credenciais, usuarios ou caminhos internos;
- dados eletricos, topologia, ajustes, logica, protecao ou comunicacao reais;
- backups operacionais de campo;
- qualquer material que voce nao tenha permissao para compartilhar publicamente.

Se houver duvida, nao envie o arquivo. Abra uma issue descrevendo o caso e
pergunte antes.

## Padroes de Codigo

- Prefira manter o padrao ja existente no repositorio.
- Regras comuns devem ficar em `src/core/`.
- Regras especificas de fabricante devem ficar em `src/core/project_types/`.
- Interface grafica deve ficar em `src/gui/`.
- Novos comportamentos precisam de testes focados.
- Evite alterar regras de `ATU`/`HIS` sem testes cobrindo o fluxo.

## Licenca

Ao contribuir, voce concorda que sua contribuicao sera disponibilizada sob a
licenca do projeto: **IED Backup Manager Non-Commercial License**.

Uso comercial, revenda, sublicenciamento, oferta como servico pago ou
incorporacao em produto/servico comercial nao sao permitidos sem autorizacao
previa por escrito do autor.
