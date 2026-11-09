# ADR 002 — Prévia somente leitura antes de escrever

- Estado: Aceita
- Data: 2026-11-08 (registro retrospectivo)
- Responsável: mantenedor do projeto
- Substitui: nenhuma
- Substituída por: nenhuma

## Contexto

O fluxo altera backups atuais e históricos. Decidir e escrever no mesmo passo
dificultaria a revisão do usuário, o teste dos resultados e o bloqueio seguro
de conflitos.

## Decisão

Separar planejamento de execução. A prévia detecta projetos, calcula nomes,
destinos, estados, duplicidades e conflitos sem mover ou publicar arquivos. A
execução somente ocorre após confirmação explícita e utiliza os planos
aprovados.

## Consequências

- o usuário vê substituições, arquivamentos e bloqueios antes da escrita;
- planners devem permanecer livres de efeitos colaterais;
- mudanças entre prévia e execução precisam ser revalidadas quando relevantes;
- GUI e CLI `--dry-run` podem compartilhar as regras de planejamento;
- novos estados de plano exigem teste de ausência ou presença correta de
  escrita.

## Evidências

- `src/core/backup_planner.py`;
- `src/core/backup_service.py`;
- `src/gui/backup_application_service.py`;
- `src/gui/preview_worker.py`;
- testes de service, storage, integridade e GUI.
