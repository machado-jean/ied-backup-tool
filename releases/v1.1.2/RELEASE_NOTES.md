# IED Backup Manager v1.1.2

## Ajuste

- Quando mais de um tipo de IED estiver selecionado, `IED-PACK` agora so e usado
  quando a mesma subestacao tiver dois ou mais tipos realmente encontrados.
- Se apenas um tipo for encontrado para a subestacao, o backup mantem o nome
  individual daquele tipo.

## Exemplos

SEL encontrado sozinho, mesmo com `DIGSI 5` e `SEL` selecionados:

```text
SEL-QS7.5.3.10_SE-AAA_20260619-1230_COLABORADOR-EXEMPLO_TAF.zip
```

DIGSI + SEL encontrados para a mesma subestacao:

```text
IED-PACK_SE-AAA_20260619-1230_COLABORADOR-EXEMPLO_TAF.zip
```

## Validacao

- `ruff check .`
- `pytest`
