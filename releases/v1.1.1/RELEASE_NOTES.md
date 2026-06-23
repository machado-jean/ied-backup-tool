# IED Backup Manager v1.1.1

## Ajustes

- Pacotes `IED-PACK` incluem `IED-PACK-MANIFEST.txt` com versoes detectadas e
  arquivos incluidos.
- Quando houver mais de um arquivo principal do mesmo tipo para a mesma
  subestacao, o pacote usa apenas o mais recente.
- Tipos de IED selecionados na GUI agora sao salvos em `config.json` e
  restaurados na proxima abertura.
- Quando nao houver preferencia salva, a GUI inicia sem tipo de IED selecionado.

## Exemplos de saida

Backup SEL individual:

```text
SEL-QS7.5.3.10-AA2.4.2.34_ESD-PDO_20260623-0031_JEAN-CARLOS-MACHADO_TAF.zip
```

Pacote por subestacao:

```text
IED-PACK_SE-GVM_20260619-1230_JEAN-CARLOS-MACHADO_TAF.zip
```

## Validacao

- `ruff check .`
- `pytest`
- GUI offscreen
