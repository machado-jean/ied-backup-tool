# IED Backup Manager v1.4.0

## Novidade

- Adicionada tela inicial de instrucoes ao abrir a aplicacao.
- A tela explica onde deixar o executavel, a estrutura recomendada de pastas e a
  regra de identificacao pelo texto antes do primeiro underline `_`.
- Incluida a opcao `Nao exibir novamente`, salva no `config.json` como
  `show_startup_instructions`.

## Interface

- A aplicacao continua seguindo o tema visual do Windows; nenhuma paleta clara
  ou escura fixa foi aplicada.

## Validacao

- `ruff check .`
- `pytest`
