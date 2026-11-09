# ADR 001 — Python e PySide6 para a aplicação Windows

- Estado: Aceita
- Data: 2026-11-08 (registro retrospectivo)
- Responsável: mantenedor do projeto
- Substitui: nenhuma
- Substituída por: nenhuma

## Contexto

O produto é uma ferramenta desktop voltada a fluxos locais de backup de IED no
Windows. O repositório já possui domínio e CLI em Python, interface PySide6,
testes Pytest e distribuição pública como executável único.

## Decisão

Manter Python como linguagem principal, PySide6 como toolkit da GUI e
PyInstaller one-file/windowed como mecanismo atual de distribuição Windows.
A CLI e a GUI reutilizam o mesmo núcleo.

## Consequências

- regras de domínio continuam testáveis com Pytest;
- a GUI pode usar recursos nativos do Qt sem exigir navegador;
- builds devem ser validados no Windows;
- dependências Qt aumentam o tamanho do executável;
- troca de toolkit ou linguagem exige plano de migração e nova ADR.

## Evidências

- `requirements.txt`;
- `src/gui/app.py`;
- `src/main.py`;
- `scripts/release.ps1`;
- `.github/workflows/ci.yml`.
