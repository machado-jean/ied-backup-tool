# ADR 004 — Adaptadores registrados por tipo de IED

- Estado: Aceita
- Data: 2026-11-08 (registro retrospectivo)
- Responsável: mantenedor do projeto
- Substitui: nenhuma
- Substituída por: nenhuma

## Contexto

Fabricantes usam extensões, estruturas e fontes de versão diferentes. Colocar
todas as regras no fluxo principal aumenta acoplamento e risco de regressão ao
adicionar suporte.

## Decisão

Definir o contrato comum em `src/core/project_types/base.py`, implementar cada
família em módulo próprio e expor os tipos disponíveis pelo registry. Regras
comuns de nome, planejamento, ZIP, integridade e armazenamento permanecem fora
dos adaptadores.

## Consequências

- novos tipos precisam implementar o contrato, registrar-se e possuir testes;
- um adaptador decide detecção, versão e conjunto de arquivos, não a política
  geral de `ATU`/`HIS`;
- amostras públicas precisam ser artificiais ou sanitizadas;
- mudanças no contrato devem considerar todos os adaptadores existentes;
- regras específicas são documentadas em `LOGICA_IDENTIFICACAO_IEDS.md`.

## Evidências

- `src/core/project_types/`;
- `src/core/project_types/registry.py`;
- testes `test_*_project_type.py` e `test_project_types.py`.
