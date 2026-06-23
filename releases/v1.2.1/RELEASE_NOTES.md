# IED Backup Manager v1.2.1

## Ajuste

- Padronizada a nomenclatura de versoes nos backups SEL e ABB PCM600.
- PCM600 agora usa somente a versao do produto no prefixo do backup:
  `PCM600-V2.7`.
- SEL agora explicita o marcador `V` para QuickSet e Architect:
  `SEL-QS-V7.5.3.10-AA-V2.4.2.34`.

## Exemplos

Backup ABB PCM600:

```text
PCM600-V2.7_SE-ABB_20260619-1230_JEAN-CARLOS-MACHADO_TAF.zip
```

Backup SEL:

```text
SEL-QS-V7.5.3.10-AA-V2.4.2.34_ESD-PDO_20260623-0031_JEAN-CARLOS-MACHADO_TAF.zip
```

## Validacao

- `ruff check .`
- `pytest`
