# IED Backup Manager

Aplicacao Windows para padronizar backups de projetos de IED, mantendo um backup
atual em `ATU`, historico em `HIS` e nomes de arquivo consistentes para
rastreabilidade tecnica.

Versao atual: `1.15.1`

- Manual do executavel: [docs/USO_EXECUTAVEL.md](docs/USO_EXECUTAVEL.md)
- Ajuda operacional: [docs/HELP.md](docs/HELP.md)
- Logica de identificacao dos IEDs: [docs/LOGICA_IDENTIFICACAO_IEDS.md](docs/LOGICA_IDENTIFICACAO_IEDS.md)
- Plano de melhorias: [docs/PLANO_MELHORIAS.md](docs/PLANO_MELHORIAS.md)
- Arquivos publicos de exemplo: [docs/examples](docs/examples)
- Como contribuir: [CONTRIBUTING.md](CONTRIBUTING.md)

## Visao Geral

O IED Backup Manager processa os arquivos de trabalho que estao na pasta do
executavel, identifica o projeto pelo trecho antes do primeiro sublinhado `"_"`,
gera um ZIP padronizado e aplica as regras de versionamento entre `ATU` e `HIS`.

O objetivo e reduzir backups manuais inconsistentes, evitar duplicidades
tecnicas, preservar historico e facilitar auditoria sem exigir que o usuario
renomeie manualmente os arquivos finais.

## Interface

Tela principal com previa do lote, resumo, selecao de tipos de IED, etapa e
destino compacto:

![Tela principal com previa](docs/images/pt-main-window-preview.png)

Configuracao do colaborador e das pastas de armazenamento:

![Tela de configuracoes](docs/images/pt-settings-window.png)

Limpeza controlada da pasta `HIS`, sempre com previa e confirmacao manual:

![Limpeza HIS](docs/images/pt-history-cleanup.png)

Exemplo da interface em ingles:

![Main window preview](docs/images/en-main-window-preview.png)

## Principais Recursos

- Interface grafica para Windows com pre-visualizacao antes da execucao.
- Tela inicial de instrucoes com opcao `Nao exibir novamente`.
- Interface em portugues e ingles, com preferencia salva em `config.json`.
- Verificacao automatica de nova versao publicada no GitHub.
- Download direto do executavel mais recente pelo aviso de atualizacao.
- Executavel distribuido com nome fixo `IED_Backup_Manager.exe`.
- Etapas padrao: `DEV`, `PRE-TAF`, `TAF`, `POS-TAF`, `PRE-TAC`, `TAC`,
  `POS-TAC` e descricao livre.
- Processamento individual ou agrupado por subestacao/projeto.
- Pacote `IED-PACK` quando mais de um tipo de IED selecionado pertence ao mesmo
  projeto.
- Suporte a GE Multilin / EnerVista UR por pasta de SE, incluindo somente
  subpastas de IED com `.urs` ou `.urk`.
- Metadados `IEDS-BACKUP-INFO.txt` em todos os ZIPs.
- Registro de versoes detectadas, arquivos incluidos, tamanho, data de
  modificacao e SHA256 dos arquivos de origem.
- Alerta de integridade para mesma identidade tecnica com SHA256 divergente.
- Validacao das pastas `ATU` e `HIS`, com criacao assistida quando faltarem.
- Aviso para pastas sincronizadas, como OneDrive ou SharePoint.
- Atualizacao automatica de `ATU` e arquivamento do backup anterior em `HIS`.
- Escrita mais transacional, com ZIP validado antes de publicar o backup final.
- Quarentena operacional `IED-QUARENTENA` para falhas raras de copia ou
  movimentacao.
- Limpeza controlada de `HIS`, com retencao em dias, previa, confirmacao e
  preservacao do backup mais recente por etapa.
- Deteccao de duplicidades em `ATU`, com indicacao do arquivo problematico.
- Progresso real por arquivo durante compactacao e copia para `ATU`/`HIS`.
- Execucao em worker dedicado para manter a GUI responsiva.
- Cancelamento controlado antes de iniciar o proximo arquivo.
- Botao `Ajuda` / `Help` apontando para a documentacao operacional publica.
- Indicador `©` com autoria, licenca e link do repositorio.

## Tipos Suportados

| Tipo | Extensoes | Versao no backup |
| --- | --- | --- |
| Siemens DIGSI | `.dz5` | Detectada por marcador interno `.dp4v###` ou `.dp5v###`, gerando prefixos como `DIGSI5-V10.00`. |
| SEL QuickSet / Architect | `.rdb`, com `.scd` ou `.selaprj` opcional | QuickSet e Architect, quando encontrados, gerando prefixos como `QUICKSET-V7.5.3.10-ARCHITECT-V2.4.2.34`. |
| ABB PCM600 | `.pcmp`, `.apcmp` | Detectada em `ProjectDataServer%versions.ini`, gerando prefixos como `PCM600-V2.10`. |
| INGETEAM INGESYS | `.efsPro`, `.ITPro2` | Informada manualmente pelo usuario e salva em `config.json`, gerando prefixos como `INGESYS-V5.5.4`. |
| GE Multilin / EnerVista UR | pastas com `.urs` ou `.urk`; `.ENV` opcional | Usa a maior versao `GE UR Setup` encontrada em `.cid/.icd`, gerando prefixos como `GE-URSETUP-V8.61`; se nao houver SCL, usa a maior versao `GEMULTILIN` dos headers `.urs/.urk`. |

## Regra de Nome dos Arquivos

O projeto/subestacao e identificado pelo texto antes do primeiro sublinhado
`"_"`.

Exemplos:

```text
SE-AAA_COMENTARIO-GENERICO_20260712_1030.dz5 -> Projeto: SE-AAA
ETD-BBB_OUTRO-COMENTARIO.rdb                 -> Projeto: ETD-BBB
VAO-ZZZ_COMENTARIO-GENERICO_20260712_1050.efsPro -> Projeto: VAO-ZZZ
```

Todo texto depois do primeiro sublinhado `"_"` e tratado como comentario do
usuario e nao entra na chave tecnica do backup.

Evite:

```text
SE_AAA_20260712_1030.dz5
CLIENTE_SE-AAA_20260712_1030.dz5
DEV_SE-AAA_20260712_1030.dz5
```

Nesses casos, o projeto pode ser identificado incorretamente.

## Nome dos Backups

O nome final segue o padrao:

```text
SOFTWARE_PROJETO_DATAHORA_COLABORADOR_ETAPA.zip
```

Exemplos:

```text
DIGSI5-V10.00_SE-AAA_20260712-1030_COLABORADOR-EXEMPLO_TAF.zip
QUICKSET-V7.5.3.10-ARCHITECT-V2.4.2.34_ETD-BBB_20260712-1035_COLABORADOR-EXEMPLO_TAF.zip
PCM600-V2.10_SE-DDD_20260712-1040_COLABORADOR-EXEMPLO_TAF.zip
INGESYS-V5.5.4_VAO-ZZZ_20260712-1050_COLABORADOR-EXEMPLO_TAF.zip
GE-URSETUP-V8.61_SE-AAA_20260712-1100_COLABORADOR-EXEMPLO_TAF.zip
IED-PACK_SE-AAA_20260712-1035_COLABORADOR-EXEMPLO_TAF.zip
```

## Configuracao

O `config.json` fica ao lado do executavel. A interface pode criar ou atualizar
esse arquivo pela tela `Configuracoes`.

Exemplo:

```json
{
  "colaborador": "COLABORADOR-EXEMPLO",
  "atu_path": "C:/Backups/Exemplo/ATU",
  "his_path": "C:/Backups/Exemplo/HIS",
  "language": "pt_BR",
  "project_types": ["digsi5", "sel", "pcm600", "ingeteam", "ge_multilin"],
  "software_versions": {
    "ingeteam": "5.5.4"
  },
  "show_startup_instructions": true,
  "history_cleanup": {
    "retention_days": 30
  }
}
```

## Fluxo de Uso

1. Coloque o executavel na pasta dos arquivos de trabalho.
2. Configure colaborador, `ATU`, `HIS`, idioma e tipos de IED.
3. Selecione a etapa.
4. Confira a `Previa do lote`.
5. Clique em `Gerar backups`.
6. Aguarde a conclusao ou cancele antes do proximo arquivo.
7. Quando necessario, use `Limpeza HIS` para revisar candidatos antes de apagar.

Na coluna `Destino`, a previa mostra um caminho compacto, como
`ATU\arquivo.zip` ou `HIS\arquivo.zip`. O caminho completo fica no tooltip da
celula.

## Estados de Processamento

- `stored`: novo backup salvo em `ATU`.
- `replaced_current`: backup anterior movido para `HIS` e novo backup salvo em
  `ATU`.
- `archived_history`: backup antigo salvo em `HIS` porque estava faltando no
  historico.
- `atu_duplicate`: duplicidade encontrada em `ATU`; a GUI mostra o arquivo
  problematico e pergunta se deve mover para `HIS`.
- `sha_conflict`: existe backup com a mesma identidade tecnica, mas SHA256
  diferente dos arquivos de origem; a execucao fica bloqueada ate verificacao.
- `skipped_older`: arquivo ignorado porque ja existe backup mais recente em
  `ATU`.
- `already_current`: arquivo ja corresponde ao backup atual em `ATU`.

## Exemplos Publicos

A pasta [docs/examples](docs/examples) contem arquivos artificiais para testes,
prints e demonstracoes publicas. Eles cobrem DIGSI, SEL, PCM600, INGETEAM e
GE Multilin, alem de uma estrutura `ATU`/`HIS` para demonstrar a tela
`Limpeza HIS`.

Executar a GUI com os exemplos:

```powershell
.\.venv\Scripts\python.exe -m src.gui.app --project-dir ".\docs\examples\sample-workspace"
```

Nas configuracoes, use:

```text
Colaborador: COLABORADOR-EXEMPLO
Pasta ATU: docs\examples\sample-storage\ATU
Pasta HIS: docs\examples\sample-storage\HIS
```

Para INGETEAM, use a versao manual `5.5.4`.

Os exemplos nao contem dados reais de engenharia e nao devem ser usados como
referencia tecnica dos formatos dos fabricantes.

## Download

O executavel publicado usa sempre o mesmo nome:

```text
IED_Backup_Manager.exe
```

Link fixo para baixar o ultimo executavel publicado:

```text
https://github.com/machado-jean/ied-backup-tool/releases/latest/download/IED_Backup_Manager.exe
```

## Desenvolvimento

Criar ambiente:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Executar a GUI em desenvolvimento:

```powershell
.\.venv\Scripts\python.exe -m src.gui.app
```

Executar via CLI:

```powershell
.\.venv\Scripts\python.exe -m src.main --project-dir ".\docs\examples\sample-workspace" --process-all --collaborator "COLABORADOR-EXEMPLO" --atu-path ".\docs\examples\sample-storage\ATU" --his-path ".\docs\examples\sample-storage\HIS"
```

Simular sem criar ZIP nem mover arquivos:

```powershell
.\.venv\Scripts\python.exe -m src.main --project-dir ".\docs\examples\sample-workspace" --project-type sel --process-all --dry-run --collaborator "COLABORADOR-EXEMPLO" --atu-path ".\docs\examples\sample-storage\ATU" --his-path ".\docs\examples\sample-storage\HIS"
```

Validar qualidade e testes:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
```

Gerar executavel:

```powershell
.\scripts\release.ps1
```

## Arquitetura

```text
src/core/
  backup_service.py      Regras principais de planejamento e execucao
  backup_planner.py      Previa e decisao ATU/HIS
  backup_executor.py     Execucao dos planos de backup
  storage.py             Regras de armazenamento, ATU/HIS e quarentena
  history_cleanup.py     Politica de limpeza controlada de HIS
  project_types/         Adaptadores por fabricante/software

src/gui/
  app.py                 Entrada da aplicacao grafica
  main_window.py         Janela principal
  settings_window.py     Configuracoes
  history_cleanup_window.py Limpeza HIS
  backup_worker.py       Execucao em worker Qt
```

Para adicionar outro tipo de IED, crie um novo adaptador em
`src/core/project_types/` com extensoes suportadas, identificador de projeto,
software/versao e arquivos relacionados. Depois registre o adaptador em
`src/core/project_types/registry.py`.

## Cuidados de Privacidade

Nao publique arquivos reais de backup, `config.json` local, caminhos internos de
empresa ou nomes reais de colaboradores. Para exemplos publicos, use nomes como
`SE-AAA`, `ETD-BBB`, `VAO-ZZZ` e `COLABORADOR-EXEMPLO`.

As pastas locais `IED-DES/`, `IED-ATU/`, `IED-HIS/`, `config.json`, `.venv/`,
`build/`, `dist/`, `.spec` e `releases/` ficam protegidas pelo `.gitignore`.

## Roadmap

Proximos marcos:

- Melhorar experiencia operacional conforme surgirem testes reais e feedback de
  usuarios.
- Adicionar novos tipos de IED apenas quando surgirem arquivos reais de teste,
  limpos ou sanitizados, com regras confiaveis de identificacao de versao.

Consulte [docs/PLANO_MELHORIAS.md](docs/PLANO_MELHORIAS.md) para detalhes.

## Contribuicoes

Contribuicoes sao bem-vindas para correcoes, documentacao, testes, exemplos
publicos e suporte a novos tipos de IED.

Antes de abrir uma issue ou pull request, leia
[CONTRIBUTING.md](CONTRIBUTING.md). O projeto possui templates para reportar
bugs, sugerir melhorias, propor novos tipos de IED e abrir pull requests.

Arquivos de exemplo so devem ser enviados quando forem artificiais, limpos ou
sanitizados. Nao envie backups com informacoes confidenciais, dados reais de
cliente/projeto/subestacao, IPs, usuarios, credenciais, caminhos internos,
ajustes ou logicas operacionais.

## Licenca

Este projeto e disponibilizado sob a **IED Backup Manager Non-Commercial
License**.

Uso gratuito, estudo, auditoria, modificacao e uso interno nao comercial sao
permitidos. Uso comercial, revenda, sublicenciamento, oferta como servico pago
ou incorporacao em produto/servico comercial nao sao permitidos sem autorizacao
previa por escrito do autor.

A atribuicao ao autor original, Jean Carlos Machado, deve ser preservada.

Leia o arquivo [LICENSE](LICENSE) para os termos completos.
