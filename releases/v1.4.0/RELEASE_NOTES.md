# IED Backup Manager v1.4.0

## Novidade

- Adicionada tela inicial de instrucoes ao abrir a aplicacao.
- A tela explica onde deixar o executavel, a estrutura recomendada de pastas e a
  regra de identificacao pelo texto antes do primeiro sublinhado `"_"`.
- Incluida a opcao `Nao exibir novamente`, salva no `config.json` como
  `show_startup_instructions`.

## Interface

- A aplicacao continua seguindo o tema visual do Windows; nenhuma paleta clara
  ou escura fixa foi aplicada.
- A janela de instrucoes tambem permite alternar entre portugues e ingles.
- O botao de idioma usa icones SVG locais em vez de emoji.
- A bandeira do Brasil foi simplificada para evitar artefato visual em tamanho
  pequeno.
- O botao de idioma da tela principal foi movido para a direita de
  `Configuracoes`.
- O botao de idioma mantem o mesmo tamanho na tela principal e na janela de
  instrucoes.

## Validacao

- `ruff check .`
- `pytest`
