# Plano de Melhorias Tecnicas

Este documento registra melhorias aprovadas ou candidatas para implementacao
futura. Ele serve como referencia pesquisavel para retomar decisoes tecnicas
sem depender apenas do historico de conversa.

## Prioridade Alta

### Validacao de ATU e HIS

Objetivo: reduzir risco operacional antes de criar ou mover backups.

Status: implementado em `v1.4.2`.

- [x] Validar, na tela de configuracoes, se `ATU` e `HIS` existem.
- [x] Se alguma pasta nao existir, perguntar se o usuario deseja cria-la.
- [x] Validar novamente antes de `Gerar backups`, pois uma pasta pode ter sido
  apagada, desconectada ou ficar indisponivel depois da configuracao.
- [x] Bloquear execucao quando `ATU` e `HIS` apontarem para a mesma pasta.
- [x] Avisar quando uma pasta estiver dentro da outra, por exemplo `HIS` dentro de
  `ATU`.
- [x] Pedir confirmacao antes de recriar `ATU` ou `HIS` ao usar `Abrir ATU` ou
  `Abrir HIS`.
- [x] Avisar quando `ATU` ou `HIS` estiverem em pasta sincronizada, como
  OneDrive, SharePoint ou similar.

### Metadados em Todos os ZIPs

Objetivo: todo backup deve ser autoexplicativo e auditavel, inclusive backups
individuais DIGSI, SEL, PCM600 e INGETEAM.

Status: implementado em `v1.5.0`.

- [x] Criar um arquivo de informacoes dentro de todos os ZIPs.
- [x] Nome adotado: `IEDS-BACKUP-INFO.txt`.
- [x] Incluir versoes detectadas, arquivos incluidos, tamanho e data de
  modificacao.
- [x] Incluir SHA256 dos arquivos de origem em `v1.5.2`.

Conteudo minimo sugerido:

```text
IED Backup Manager - Backup Information

Backup: DIGSI5-V10.00_SE-XXX_20260622-1350_COLABORADOR_TAF.zip
Project: SE-XXX
Software: DIGSI5-V10.00
Timestamp: 20260622-1350
Collaborator: COLABORADOR
Stage: TAF

Included files:
- SE-XXX_COMENTARIO-GENERICO_20260622_1350.dz5
  Modified: 20260622-1350
  Size: 12345678 bytes
```

Para `IED-PACK`, manter tambem uma secao de versoes detectadas:

```text
Detected versions:
- DIGSI 5 (.dz5): DIGSI5-V10.00
- SEL (.rdb): QUICKSET-V7.5.3.10-ARCHITECT-V2.4.2.34
```

### SHA256 dos Arquivos de Origem

Objetivo: registrar a impressao digital dos arquivos incluidos no ZIP.

Status: registro de SHA256 implementado em `v1.5.2`; alerta de conflito por
SHA256 implementado em `v1.6.0`.

Vantagens:

- Detectar arquivos diferentes com mesma identidade tecnica.
- Ajudar auditoria futura.
- Permitir conferir se um arquivo de origem foi alterado depois.
- Melhorar investigacao quando alguem altera manualmente `ATU` ou `HIS`.

Escopo inicial recomendado:

- [x] Calcular SHA256 de cada arquivo de origem incluido no ZIP.
- [x] Registrar SHA256, tamanho e data de modificacao no arquivo interno de
  metadados.
- [x] Nao colocar SHA256 no nome do ZIP.

Escopo implementado em `v1.6.0`:

- [x] Alertar quando existir mesma identidade tecnica com SHA256 diferente.
- [x] Bloquear execucao enquanto houver conflito de integridade na previa.

Escopo posterior opcional:

- Gerar arquivo externo `.sha256` ao lado do ZIP final.

## Prioridade Media

### Operacao Mais Transacional

Objetivo: reduzir estado parcial quando houver erro ao mover arquivos.

Status: implementado em `v1.7.0`.

- [x] Criar ZIP em pasta temporaria.
- [x] Validar leitura/tamanho antes de mover.
- [x] Preparar e validar o novo ZIP dentro da pasta de destino antes de arquivar
  o backup atual.
- [x] Remover o novo ZIP de `ATU` se a movimentacao do backup atual para `HIS`
  falhar.
- [x] Criar backups historicos faltantes em staging antes de publica-los em
  `HIS`.

Escopo posterior opcional:

- Criar quarentena explicita para falhas raras em que um arquivo parcialmente
  movido precise de analise manual.

### Execucao em Worker Thread

Objetivo: melhorar responsividade da GUI em backups grandes.

Status: progresso real por arquivo implementado em `v1.7.0`.

TODO:

- [x] Mostrar progresso real por arquivo durante compactacao e copia para
  `ATU`/`HIS`.
- Mover o processamento para `QThread` ou worker dedicado.
- Atualizar progresso por sinal quando o worker dedicado for implementado.
- Permitir cancelamento controlado antes de iniciar o proximo arquivo.

### Documentacao para Usuario Final

TODO:

- Adicionar secao de limitacoes conhecidas.
- Adicionar solucao de problemas para OneDrive, arquivo bloqueado e projeto
  identificado incorretamente.
- Adicionar exemplo do arquivo de metadados interno do ZIP.
- Adicionar capturas da tela principal, configuracoes e previa.

## Prioridade Baixa

### Refatoracao Estrutural

TODO:

- Separar `src/gui/main_window.py` em componentes menores.
- Separar `src/core/backup_service.py` em planejamento, execucao, agrupamento e
  resumo.
- Expandir testes de GUI com inicializacao em modo offscreen.
