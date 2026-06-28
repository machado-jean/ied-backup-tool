# IED Backup Manager v1.5.1

Data: 27/06/2026

## Resumo

Versao patch para corrigir a abertura das pastas `ATU` e `HIS` quando alguma
delas foi apagada depois da configuracao.

## Alteracoes

- `Abrir ATU` e `Abrir HIS` nao recriam mais pastas silenciosamente.
- Quando a pasta nao existe, o usuario precisa confirmar antes da recriacao.
- Se o caminho apontar para um arquivo em vez de uma pasta, a abertura e
  bloqueada com mensagem.
- A documentacao foi atualizada com esse comportamento.

## Compatibilidade

- Mantem compatibilidade com `config.json` das versoes anteriores.
- Nao altera o padrao de nomes dos backups.
- Nao altera o conteudo dos ZIPs introduzido na `v1.5.0`.

## Arquivo

- IED Backup Manager v1.5.1.exe
