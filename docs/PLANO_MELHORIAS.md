# Plano de Melhorias Tecnicas

Este documento registra melhorias aprovadas ou candidatas para implementacao
futura. Ele serve como referencia pesquisavel para retomar decisoes tecnicas
sem depender apenas do historico de conversa.

## Roadmap por Marcos

Este roadmap parte da versao atual `v1.10.5`. As versoes sao estimativas
pragmaticas e podem mudar se surgir uma correcao urgente ou um novo tipo de IED
prioritario.

| Versao estimada | Marco | Entregas principais |
| --- | --- | --- |
| `v1.10.5` | Revisao publica do repositorio | Implementado: varredura final de dados sensiveis, caminhos internos, nomes reais e arquivos locais; confirmacao de `.gitignore`; ajuste de contraste do indicador `©`; release note registrando a revisao. |
| `v1.11.0` | Refatoracao estrutural | Separar `main_window.py` e `backup_service.py` em componentes menores; ampliar testes de GUI em modo offscreen; reduzir risco antes de novas telas. |
| `v1.12.0` | Recuperacao operacional | Quarentena explicita para falhas raras de movimentacao/copia, com orientacao ao usuario para analise manual. |
| `v1.13.0` | Limpeza controlada de historico | Ferramenta para localizar backups antigos por idade, quantidade ou tamanho, inicialmente em modo previa/confirmacao. |
| `v1.14.0` | Relatorios operacionais | Relatorio simples de execucao em `.txt` ou `.csv`, com resumo do lote, arquivos criados, ignorados, conflitos, hashes e mensagens relevantes. |
| `v1.15.0` | Documentacao visual publica | Capturas reais e sanitizadas da tela principal, configuracoes, previa e fluxo de execucao; atualizacao do README e `docs/HELP.md` com imagens limpas. |
| `v1.16.0` | Novos tipos de IED | Inclusao de novos fabricantes/formatos conforme surgirem arquivos reais de teste e regras de versao confiaveis, depois da documentacao base estar estavel. |
| `v1.17.0` | Integridade externa opcional | Avaliar se vale gerar arquivo `.sha256` ao lado do ZIP final para verificacao independente; manter fora do fluxo principal se nao houver uso real. |

Marcos removidos do roadmap ativo:

- Assinatura de codigo: abortada por enquanto. O alerta do SmartScreen pode ser
  documentado como limitacao conhecida enquanto nao houver decisao de custo e
  distribuicao com certificado.

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

Status: implementado em `v1.10.5`.

- [x] Apontar o botao `Ajuda` / `Help` para o `HELP.md` publico no GitHub.
- [x] Fazer varredura final de nomes reais, caminhos internos e amostras
  sensiveis.
- [x] Confirmar que pastas locais com backups reais seguem ignoradas pelo Git.
- [x] Revisar documentos publicos usando somente exemplos genericos.
- [x] Registrar resultado da revisao em release note de patch.

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

### Licenca e Autoria

Objetivo: deixar claro que o projeto e publico/source-available para uso
gratuito e nao comercial, preservando autoria e restringindo uso comercial sem
autorizacao previa.

Status: implementado em `v1.10.2`.

- [x] Criar arquivo `LICENSE` com a `IED Backup Manager Non-Commercial License`.
- [x] Adicionar secao de licenca no README.
- [x] Adicionar nota curta de licenca no `docs/HELP.md`.
- [x] Adicionar instrucao de licenca/autoria em `docs/USO_EXECUTAVEL.md`.
- [x] Adicionar indicador `©` no canto inferior direito da GUI.
- [x] Ao clicar em `©`, mostrar autoria, uso nao comercial e link do
  repositorio.

## Prioridade Baixa

### Refatoracao Estrutural

TODO:

- Separar `src/gui/main_window.py` em componentes menores.
- Separar `src/core/backup_service.py` em planejamento, execucao, agrupamento e
  resumo.
- Expandir testes de GUI com inicializacao em modo offscreen.
