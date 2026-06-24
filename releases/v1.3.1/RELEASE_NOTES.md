# IED Backup Manager v1.3.1

## Correcoes

- DIGSI passa a informar familia e versao no prefixo do backup:
  - `dp5v100` -> `DIGSI5-V10.00`
  - `dp5v75` -> `DIGSI5-V7.50`
  - `dp5v98` -> `DIGSI5-V9.80`
  - `dp4v75` -> `DIGSI4-V7.50`
- SEL passa a seguir a nomenclatura completa da politica:
  `QUICKSET-V7.5.3.10-ARCHITECT-V2.4.2.34`.
- INGETEAM passa a usar `INGESYS-V{versao}` como prefixo do backup.

## Exemplos

```text
DIGSI5-V10.00_SE-GVM_20260529-1625_JEAN-CARLOS-MACHADO_TAF.zip
QUICKSET-V7.5.3.10-ARCHITECT-V2.4.2.34_ESD-PDO_20260623-0031_JEAN-CARLOS-MACHADO_TAF.zip
PCM600-V2.10_SE-ABB_20260619-1230_JEAN-CARLOS-MACHADO_TAF.zip
INGESYS-V5.5.4_SE-ING_20260619-1230_JEAN-CARLOS-MACHADO_TAF.zip
```

## Validacao

- `ruff check .`
- `pytest`
