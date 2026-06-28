# IED Backup Manager v1.3.0

## Novidade

- Adicionado suporte inicial a INGETEAM para arquivos `.efsPro` e `.ITPro2`.
- A versao INGETEAM passa a ser informada manualmente na GUI e salva em
  `config.json` em `software_versions.ingeteam`.
- O prefixo de backup INGETEAM segue o padrao `INGETEAM-Vx.y.z`.

## Interface

- O campo de versao INGETEAM aparece somente quando o tipo INGETEAM esta
  selecionado.
- O campo fica na mesma linha do checkbox INGETEAM, identificado por `v`, para
  evitar ambiguidade quando varios tipos de IED estao marcados.
- A janela inicia mais larga, usando aproximadamente 75% da largura disponivel
  da tela.

## Exemplos

Backup INGETEAM:

```text
INGETEAM-V5.5.4_SE-EEE_20260619-1230_COLABORADOR-EXEMPLO_TAF.zip
```

Pacote agrupado com INGETEAM e outros tipos selecionados:

```text
IED-PACK_SE-AAA_20260619-1230_COLABORADOR-EXEMPLO_TAF.zip
```

## Validacao

- `ruff check .`
- `pytest`
