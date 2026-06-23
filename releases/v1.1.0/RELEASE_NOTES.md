# IED Backup Manager v1.1.0

## Novidades

- Adicionado suporte a backups SEL com arquivo principal `.rdb`.
- Inclusao automatica de `.scd` ou `.selaprj` no ZIP quando existir arquivo
  Architect com o mesmo nome-base do `.rdb`.
- Deteccao automatica da versao QuickSet pelo trecho
  `Saved with Main Shell Version`.
- Deteccao automatica da versao AcSELerator Architect pelo `toolID` quando o
  arquivo Architect estiver presente.
- Campo de versao manual exibido na GUI quando a versao QuickSet nao puder ser
  detectada.
- Agrupamento por subestacao na GUI quando mais de um tipo de IED estiver
  selecionado, gerando pacote `IED-PACK` com todos os arquivos aplicaveis.
- Pacotes `IED-PACK` agora incluem `IED-PACK-MANIFEST.txt` com versoes
  detectadas e arquivos incluidos.
- Quando houver mais de um arquivo principal do mesmo tipo para a mesma
  subestacao, o pacote usa apenas o mais recente.
- CLI aceita `--project-type sel` e `--software-version` para arquivos antigos
  sem metadados de versao.

## Exemplos de saida

Backup SEL individual, quando apenas `SEL (.rdb)` estiver selecionado:

```text
SEL-QS7.5.3.10-AA2.4.2.34_ESD-PDO_20260623-0031_JEAN-CARLOS-MACHADO_TAF.zip
```

Pacote por subestacao, quando mais de um tipo de IED estiver selecionado:

```text
IED-PACK_SE-GVM_20260619-1230_JEAN-CARLOS-MACHADO_TAF.zip
```

O pacote `IED-PACK` inclui `IED-PACK-MANIFEST.txt` dentro do ZIP com as versoes
detectadas e os arquivos incluidos.

## Validacao

- `ruff check .`
- `pytest`
- Teste automatizado de pacote por subestacao com `.dz5`, `.rdb`, `.scd`,
  manifesto e selecao do arquivo principal mais recente por tipo.
- Smoke test com os arquivos reais `IED-DES/ESD-PDO.rdb` e `IED-DES/ESD-PDO.scd`.
