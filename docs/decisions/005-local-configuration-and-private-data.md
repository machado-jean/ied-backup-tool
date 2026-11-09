# ADR 005 — Configuração local e dados operacionais fora do Git

- Estado: Aceita
- Data: 2026-11-08 (registro retrospectivo)
- Responsável: mantenedor do projeto
- Substitui: nenhuma
- Substituída por: nenhuma

## Contexto

O aplicativo processa projetos de infraestrutura elétrica que podem conter
identificadores, ajustes, topologia, caminhos internos e outros dados
confidenciais. A configuração também contém nome do colaborador e caminhos da
máquina.

## Decisão

Manter `config.json`, projetos reais, `ATU`, `HIS`, quarentena e logs fora do
Git. Não enviar automaticamente configuração, logs ou projetos. Exemplos
públicos devem ser artificiais/sanitizados. Diagnóstico exige ação e
consentimento explícitos e deve minimizar dados.

## Consequências

- o GitHub sozinho não é backup dos dados operacionais;
- migração de PC exige backup privado separado e revisão de caminhos;
- testes automatizados usam temporários e fixtures seguras;
- contribuições com novos IEDs dependem de material autorizado;
- qualquer futura telemetria, sincronização ou upload requer avaliação de
  privacidade, consentimento e nova ADR.

## Evidências

- `.gitignore`;
- `CONTRIBUTING.md`;
- `docs/HELP.md`;
- `docs/COLETA_DIAGNOSTICO.md`;
- `docs/examples/README.md`.
