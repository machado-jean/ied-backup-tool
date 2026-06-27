# IED Backup Manager v1.4.2

Data: 27/06/2026

## Resumo

Versao patch focada em seguranca operacional das pastas `ATU` e `HIS`.

## Alteracoes

- Valida `ATU` e `HIS` ao salvar configuracoes.
- Pergunta ao usuario se deseja criar `ATU` ou `HIS` quando alguma pasta nao
  existir.
- Bloqueia configuracoes em que `ATU` e `HIS` apontam para a mesma pasta.
- Mostra aviso quando `ATU` e `HIS` estao aninhadas, por exemplo `HIS` dentro
  de `ATU`.
- Revalida `ATU` e `HIS` antes de executar `Gerar backups`.
- Documentacao atualizada com o comportamento de validacao das pastas.

## Compatibilidade

- Mantem compatibilidade com `config.json` das versoes anteriores.
- Nao altera o padrao de nomes dos backups.
- Nao altera a estrutura dos ZIPs gerados.

## Arquivo

- IED Backup Manager v1.4.2.exe
