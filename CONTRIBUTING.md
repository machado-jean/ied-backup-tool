# Contribuindo com o IED Backup Manager

[Português](CONTRIBUTING.md) | [English](CONTRIBUTING.en.md)

Obrigado por considerar uma contribuição. Este projeto aceita correções,
melhorias de documentação, novos exemplos públicos e suporte a novos tipos de
IED, desde que os arquivos compartilhados não contenham informações
confidenciais.

## Requisitos de Desenvolvimento

Ambiente recomendado:

- Windows 10 ou Windows 11;
- Python 3.12 ou superior;
- Git;
- PowerShell;
- acesso ao repositório GitHub;
- ambiente virtual `.venv` local.

Criar o ambiente:

```powershell
git clone https://github.com/machado-jean/ied-backup-tool.git
cd ied-backup-tool
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Rodar a aplicação em desenvolvimento:

```powershell
.\.venv\Scripts\python.exe -m src.gui.app
```

Rodar com os exemplos públicos:

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

1. Confirme se está usando a versão mais recente publicada.
2. Tente reproduzir o erro com os arquivos de exemplo em `docs/examples`.
3. Verifique se `ATU` e `HIS` apontam para pastas diferentes e acessíveis.
4. Confirme se os arquivos de trabalho não estão abertos em outro software.

Ao reportar, inclua:

- versão do IED Backup Manager;
- versão do Windows;
- tipo de IED selecionado;
- etapa selecionada;
- caminho geral da estrutura, sem dados confidenciais;
- passos para reproduzir;
- resultado esperado;
- resultado obtido;
- prints, se ajudarem;
- mensagem de erro completa, se houver.

Não envie `config.json` real, caminhos internos de empresa, nomes reais de
colaboradores ou arquivos de backup com dados operacionais.

## Como Sugerir Melhorias

Ao sugerir uma melhoria, descreva:

- problema operacional que a melhoria resolve;
- fluxo atual;
- fluxo desejado;
- impacto esperado;
- se a mudança afeta nomes de arquivos, `ATU`, `HIS`, metadados ou integridade.

Mudancas pequenas e bem delimitadas tendem a ser avaliadas mais rapidamente.

## Como Abrir Pull Requests

Fluxo recomendado:

1. Crie uma branch a partir da branch principal.
2. Mantenha a alteração focada em um único objetivo.
3. Atualize testes quando houver mudança de comportamento.
4. Atualize documentação quando houver mudança visível ao usuário.
5. Rode `ruff` e `pytest`.
6. Abra o pull request usando o template do repositório.

Evite incluir:

- executáveis `.exe`;
- arquivos em `releases/`;
- `.spec`;
- `.venv/`;
- `config.json`;
- backups reais;
- arquivos com dados confidenciais;
- alteracoes de formatação sem relação com o objetivo do PR.

## Contribuicoes com Novos IEDs

Novos tipos de IED são bem-vindos, mas precisam de amostras seguras para teste.

Você pode contribuir com:

- arquivo limpo gerado por um novo projeto vazio no software do fabricante;
- backup demonstrativo sem dados de cliente, subestação real, rede, IP,
  usuários, caminhos internos ou nomes reais;
- arquivo sanitizado, quando a sanitização não quebrar a estrutura necessária
  para detecção de versão;
- descrição textual do formato, caso o arquivo não possa ser compartilhado.

Ao enviar arquivos de exemplo:

- use nomes genéricos, como `SE-AAA`, `ETD-BBB`, `VAO-ZZZ`;
- use colaborador `COLABORADOR-EXEMPLO`;
- documente qual software gerou o arquivo;
- informe a versão esperada do software;
- indique qual extensão deve ser considerada arquivo principal;
- indique quais arquivos acompanhantes devem entrar no ZIP, se existirem.

Não envie arquivos que contenham:

- nomes reais de subestações, clientes, projetos ou colaboradores;
- endereços IP, credenciais, usuários ou caminhos internos;
- dados elétricos, topologia, ajustes, lógica, proteção ou comunicação reais;
- backups operacionais de campo;
- qualquer material que você não tenha permissão para compartilhar publicamente.

Se houver dúvida, não envie o arquivo. Abra uma issue descrevendo o caso e
pergunte antes.

## Padroes de Codigo

- Prefira manter o padrão já existente no repositório.
- Regras comuns devem ficar em `src/core/`.
- Regras específicas de fabricante devem ficar em `src/core/project_types/`.
- Interface grafica deve ficar em `src/gui/`.
- Novos comportamentos precisam de testes focados.
- Evite alterar regras de `ATU`/`HIS` sem testes cobrindo o fluxo.

## Licença

Ao contribuir, você concorda que sua contribuição será disponibilizada sob a
licença do projeto: **IED Backup Manager Non-Commercial License**.

Uso comercial, revenda, sublicenciamento, oferta como serviço pago ou
incorporação em produto/serviço comercial não são permitidos sem autorização
prévia por escrito do autor.
