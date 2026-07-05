# IED Backup Manager v1.9.0

Data: 05/07/2026

## Resumo

Versao focada em documentacao publica/profissional e acesso de ajuda dentro da
aplicacao.

## Alteracoes

- Adicionado documento `docs/HELP.md` com fluxo de uso, estrutura de pastas,
  regras de nome, tipos suportados, exemplos de saida, metadados, limitacoes
  conhecidas, solucao de problemas e privacidade.
- Adicionado botao `Ajuda` / `Help` no cabecalho da tela principal.
- O documento de ajuda passa a ser empacotado no `.exe` pelo PyInstaller.
- Atualizada a documentacao principal para apontar para o novo documento de
  ajuda.
- Preparada a base para a futura v1.9.1 de verificacao final de dados sensiveis
  antes de eventual abertura publica do repositorio.

## Compatibilidade

- Nao altera as regras de backup, nomes finais, ATU/HIS, SHA256 ou tipos de IED.
- O `config.json` existente permanece compativel.

## Arquivo

- `IED Backup Manager v1.9.0.exe`
