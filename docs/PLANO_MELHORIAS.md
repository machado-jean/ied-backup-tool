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

Status: implementado em `v1.8.0`.

TODO:

- [x] Mostrar progresso real por arquivo durante compactacao e copia para
  `ATU`/`HIS`.
- [x] Mover o processamento para `QThread` ou worker dedicado.
- [x] Atualizar progresso por sinal.
- [x] Permitir cancelamento controlado antes de iniciar o proximo arquivo.
- [x] Se o cancelamento ocorrer durante a compactacao, descartar o ZIP em
  staging e nao copiar para `ATU`/`HIS`.

### Documentacao para Usuario Final

Status: implementado em `v1.9.0`.

- [x] Adicionar documento operacional `docs/HELP.md`.
- [x] Adicionar botao `Ajuda` / `Help` na tela principal.
- [x] Empacotar o documento de ajuda dentro do `.exe`.
- [x] Adicionar secao de limitacoes conhecidas.
- [x] Adicionar solucao de problemas para OneDrive, arquivo bloqueado e projeto
  identificado incorretamente.
- [x] Adicionar exemplo do arquivo de metadados interno do ZIP.
- [ ] Adicionar capturas reais da tela principal, configuracoes e previa quando
  houver material publico revisado.

### Preparacao Para Repositorio Publico

Objetivo: reduzir risco de exposicao antes de abrir o GitHub para acesso
publico.

Status: planejado para depois de `v1.9.2`.

- [x] Apontar o botao `Ajuda` / `Help` para o `HELP.md` publico no GitHub.
- [ ] Fazer varredura final de nomes reais, caminhos internos e amostras
  sensiveis.
- [ ] Confirmar que pastas locais com backups reais seguem ignoradas pelo Git.
- [ ] Revisar documentos publicos usando somente exemplos genericos.
- [ ] Registrar resultado da revisao em release note de patch.

### Verificacao de Atualizacoes

Objetivo: avisar o usuario quando existir uma versao nova publicada no GitHub,
sem baixar ou substituir o executavel automaticamente.

Status: implementado em `v1.10.0`.

- [x] Consultar a ultima versao publicada no GitHub Releases.
- [x] Comparar a versao publicada com `APP_VERSION`.
- [x] Mostrar aviso quando houver uma versao mais recente.
- [x] Permitir abrir o release no navegador ao clicar no aviso.
- [x] Nao exibir aviso quando o usuario ja estiver na versao mais recente.
- [x] Tratar falhas de internet ou bloqueio corporativo sem interromper o uso do
  aplicativo.

## Prioridade Baixa

### Refatoracao Estrutural

TODO:

- Separar `src/gui/main_window.py` em componentes menores.
- Separar `src/core/backup_service.py` em planejamento, execucao, agrupamento e
  resumo.
- Expandir testes de GUI com inicializacao em modo offscreen.
