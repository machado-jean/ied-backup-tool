# IED Backup Manager v1.10.0

Data: 05/07/2026

## Resumo

Versao que adiciona verificacao automatica de novas versoes publicadas no
GitHub.

## Alteracoes

- Ao abrir o aplicativo, a GUI consulta o ultimo release publico no GitHub.
- Quando houver versao mais nova, a tela principal mostra `Nova versão
  disponível` em vermelho no canto inferior esquerdo.
- O aviso e clicavel e abre a pagina `/releases/latest` dos releases no
  navegador.
- Quando o usuario ja esta na versao mais recente, nada e exibido.
- Falhas de internet, bloqueio corporativo ou indisponibilidade do GitHub sao
  tratadas de forma silenciosa e nao interrompem o uso do aplicativo.

## Compatibilidade

- Nao altera regras de backup, ATU/HIS, SHA256, tipos de IED ou `config.json`.
- Nao baixa nem substitui o executavel automaticamente.

## Arquivo

- `IED Backup Manager v1.10.0.exe`
