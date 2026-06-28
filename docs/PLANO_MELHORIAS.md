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

Status: registro de SHA256 implementado em `v1.5.2`; uso do SHA256 para alerta
de conflito fica planejado para versao posterior.

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

Escopo posterior opcional:

- Gerar arquivo externo `.sha256` ao lado do ZIP final.
- Alertar quando existir mesma identidade tecnica com SHA256 diferente.

## Prioridade Media

### Operacao Mais Transacional

Objetivo: reduzir estado parcial quando houver erro ao mover arquivos.

TODO:

- Criar ZIP em pasta temporaria.
- Validar leitura/tamanho antes de mover.
- Mover backup atual para `HIS` somente quando o novo ZIP estiver pronto.
- Considerar mecanismo de rollback ou quarentena em falhas de movimento.

### Execucao em Worker Thread

Objetivo: melhorar responsividade da GUI em backups grandes.

TODO:

- Mover o processamento para `QThread` ou worker dedicado.
- Atualizar progresso por sinal.
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
