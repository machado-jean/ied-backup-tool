# IED Backup Manager v1.2.0

## Novidades

- Adicionado suporte a ABB PCM600 com arquivo principal `.pcmp`.
- O `.pcmp` e tratado como pacote ZIP para localizar
  `ProjectDataServer%versions.ini`.
- A versao do backup ABB e montada a partir de:
  - `ProductName`
  - `ProductVersion`
- O tipo `ABB PCM600 (.pcmp)` aparece na GUI e pode participar dos pacotes
  `IED-PACK` quando combinado com outros tipos na mesma subestacao.

## Exemplo de saida

Para:

```text
ProductName=PCM600_210
ProductVersion=2.10
```

O backup individual fica:

```text
PCM600-210-V2.10_SE-DDD_20260619-1230_COLABORADOR-EXEMPLO_TAF.zip
```

## Validacao

- `ruff check .`
- `pytest`
