# Ambiente de desenvolvimento

[Português](AMBIENTE_DESENVOLVIMENTO.md) | [English](DEVELOPMENT_ENVIRONMENT.en.md)

## Ambiente de referência

- Windows 10 ou Windows 11 x64;
- Python 3.13 no CI; o projeto declara compatibilidade de lint a partir do
  Python 3.12;
- PowerShell;
- Git;
- ambiente virtual `.venv` local;
- dependências fixadas em `requirements.txt`.

Não dependa de pacotes Python instalados globalmente.

## Preparar outro computador

```powershell
git clone https://github.com/machado-jean/ied-backup-tool.git
cd ied-backup-tool
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Confirme a instalação:

```powershell
.\.venv\Scripts\python.exe --version
.\.venv\Scripts\python.exe -m ruff --version
.\.venv\Scripts\python.exe -m pytest --version
```

## Executar

Interface gráfica:

```powershell
.\.venv\Scripts\python.exe -m src.gui.app
```

Interface com dados públicos de demonstração:

```powershell
.\.venv\Scripts\python.exe -m src.gui.app --project-dir ".\docs\examples\sample-workspace"
```

CLI somente leitura, fornecendo configuração ou overrides necessários:

```powershell
.\.venv\Scripts\python.exe -m src.main --help
.\.venv\Scripts\python.exe -m src.main --dry-run
```

O segundo comando exige `config.json` válido na pasta atual ou argumentos de
colaborador, `ATU` e `HIS`.

## Verificação

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
git diff --check
```

O CI executa Ruff e Pytest em `windows-latest` com Python 3.13 e
`QT_QPA_PLATFORM=offscreen`.

Para um teste de inicialização da GUI sem interação:

```powershell
$env:QT_QPA_PLATFORM = "offscreen"
.\.venv\Scripts\python.exe -m src.gui.app --smoke-test-exit-ms 1000
```

## Dados locais

O `config.json`, ambientes virtuais, builds, releases locais, logs e pastas
reais `ATU`/`HIS` não pertencem ao Git. Antes de testar escrita, use diretórios
temporários ou uma cópia controlada. Nunca use dados operacionais reais para
testes automatizados.

Logs da aplicação distribuída ficam sob `%LOCALAPPDATA%`, conforme descrito em
`docs/COLETA_DIAGNOSTICO.md`.

## Build e release

O build oficial local é gerado por:

```powershell
.\scripts\release.ps1
```

O script lê `APP_VERSION` de `src/version.py`, executa Ruff e Pytest, gera o
executável one-file/windowed com PyInstaller, prepara notas, hashes, ferramenta
de diagnóstico e um publicador dentro de `releases\vX.Y.Z`.

`-SkipTests` existe para situações excepcionais e não constitui evidência de
release validado. A publicação remota continua manual e exige as verificações
do publicador; detalhes estão em `CONTRIBUTING.md` e nos scripts de release.

## Atualização do ambiente

Ao alterar Python ou uma dependência:

1. atualize `requirements.txt` e configuração relacionada;
2. recrie ou sincronize a `.venv`;
3. execute Ruff e todos os testes;
4. valide a inicialização da GUI;
5. atualize este documento e o guia de contribuição;
6. para dependência distribuída, confira licença e impacto no executável.
