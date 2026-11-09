# ADR 003 — Armazenamento ATU/HIS com publicação validada

- Estado: Aceita
- Data: 2026-11-08 (registro retrospectivo)
- Responsável: mantenedor do projeto
- Substitui: nenhuma
- Substituída por: nenhuma

## Contexto

O produto precisa identificar rapidamente o backup vigente e preservar versões
anteriores, sem perder a última cópia válida em falhas de compactação, cópia ou
movimentação.

## Decisão

Usar `ATU` para a cópia atual por identidade técnica e `HIS` para histórico. O
ZIP deve ser criado e validado antes de tocar no destino. A publicação usa
arquivo temporário no destino e movimentação controlada; conflitos de SHA não
são sobrescritos automaticamente. Falhas raras podem preservar material em
`IED-QUARENTENA`.

No Windows, a colocação final não usa `shutil.move` direto a partir do diretório
temporário. O arquivo final é recriado no destino para herdar as permissões de
`ATU`/`HIS`, evitando carregar ACLs inadequadas da origem.

## Consequências

- `ATU` e `HIS` precisam ser distintos, acessíveis e revalidados;
- identidade e ordenação precisam manter compatibilidade retroativa;
- substituição deve arquivar a versão anterior quando aplicável;
- limpeza de `HIS` é uma operação separada, com prévia e confirmação;
- alterações em nomes ou identidade exigem testes de migração e recuperação.

## Evidências

- `src/core/storage.py`;
- `src/core/zipper.py`;
- `src/core/integrity.py`;
- `src/core/history_cleanup.py`;
- `src/core/path_validation.py`;
- testes correspondentes e histórico de versões em `PLANO_MELHORIAS.md`.
