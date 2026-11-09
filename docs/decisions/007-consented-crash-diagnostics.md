# ADR 007 — Diagnóstico de encerramento inesperado com consentimento

- Estado: Aceita
- Data: 2026-11-08 (registro retrospectivo)
- Responsável: mantenedor do projeto
- Substitui: nenhuma
- Substituída por: nenhuma

## Contexto

A ausência de encerramento limpo não prova, isoladamente, um crash nativo.
Instâncias simultâneas, reutilização de PID e cópias em caminhos diferentes
podem gerar falsos positivos. Eventos do Windows também podem conter dados que
não devem ser consultados ou enviados sem consentimento.

## Decisão

Cada processo usa um marcador transitório `logs/sessions/<UUID>.json` com
caminho do aplicativo, PID, imagem/criação do processo, início e heartbeat. Um
marcador só é ativo quando PID, imagem e criação ainda correspondem; alertas
consideram apenas sessões mortas do mesmo caminho do executável.

Na abertura seguinte, consultar eventos Application 1000/1001 somente após
consentimento, em janela estreita próxima ao heartbeat e filtrando pelo
executável. Copiar apenas campos sanitizados para o log local. Não acessar
dumps, solicitar UAC nem enviar dados automaticamente. Recusa não consulta os
eventos e encerra aquele incidente.

Marcadores limpos/tratados são removidos; pendências expiram após 30 dias e são
limitadas a 20 por caminho. O log diário identifica UUID e PID.

## Consequências

- diagnóstico é informativo, não classificação automática de causa;
- concorrência e reutilização de PID não devem produzir falsos alertas;
- suporte depende de ação explícita do usuário para coletar e compartilhar;
- mudanças em retenção, filtros ou upload exigem nova avaliação de privacidade.

## Evidências

- `src/core/app_logging.py`;
- `scripts/Collect-Diagnostics.ps1`;
- `docs/COLETA_DIAGNOSTICO.md`;
- testes de logging e lifecycle.
