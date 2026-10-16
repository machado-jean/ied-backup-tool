<p align="center">
  <img src="assets/app_icon.png" alt="Ícone do IED Backup Manager" width="96">
</p>

<h1 align="center">IED Backup Manager</h1>

<p align="center">
  Backups de projetos de IED padronizados, rastreáveis e organizados entre
  <code>ATU</code> e <code>HIS</code>.
</p>

<p align="center">
  <a href="https://github.com/machado-jean/ied-backup-tool/actions/workflows/ci.yml"><img src="https://github.com/machado-jean/ied-backup-tool/actions/workflows/ci.yml/badge.svg?branch=master" alt="CI"></a>
  <a href="https://github.com/machado-jean/ied-backup-tool/releases/latest"><img src="https://img.shields.io/github/v/release/machado-jean/ied-backup-tool?display_name=tag&sort=semver" alt="Última versão"></a>
  <img src="https://img.shields.io/badge/Windows-10%20%7C%2011-0078D4?logo=windows" alt="Windows 10 e 11">
  <img src="https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white" alt="Python 3.13">
  <a href="LICENSE"><img src="https://img.shields.io/badge/licença-não%20comercial-blue" alt="Licença não comercial"></a>
</p>

<p align="center">
  <a href="README.md">Português</a> · <a href="README.en.md">English</a> ·
  <a href="https://github.com/machado-jean/ied-backup-tool/releases/latest">Baixar última versão</a>
</p>

Aplicação Windows para padronizar backups de projetos de IED, mantendo um backup
atual em `ATU`, histórico em `HIS` e nomes de arquivo consistentes para
rastreabilidade técnica. Versão atual: `1.18.0`.

- Manual do executável: [docs/USO_EXECUTAVEL.md](docs/USO_EXECUTAVEL.md)
- Ajuda operacional: [docs/HELP.md](docs/HELP.md)
- Lógica de identificação dos IEDs: [docs/LOGICA_IDENTIFICACAO_IEDS.md](docs/LOGICA_IDENTIFICACAO_IEDS.md)
- Plano de melhorias: [docs/PLANO_MELHORIAS.md](docs/PLANO_MELHORIAS.md)
- Arquivos públicos de exemplo: [docs/examples](docs/examples)
- Como contribuir: [CONTRIBUTING.md](CONTRIBUTING.md)

## Visão Geral

O IED Backup Manager processa os arquivos de trabalho que estão na pasta do
executável, identifica o projeto pelo trecho antes do primeiro sublinhado `"_"`,
convertendo espaços desse trecho em hífens,
gera um ZIP padronizado e aplica as regras de versionamento entre `ATU` e `HIS`.

O objetivo é reduzir backups manuais inconsistentes, evitar duplicidades
técnicas, preservar histórico e facilitar auditoria sem exigir que o usuário
renomeie manualmente os arquivos finais.

Quando houver backups antigos em `ATU`/`HIS` usando o formato anterior
`YYYYMMDD-HHMM`, o aplicativo identifica esses arquivos e pergunta se o usuário
deseja renomeá-los para o padrão atual.

## Interface

### Prévia antes de qualquer alteração

A tela principal identifica os arquivos, calcula o destino e resume quantos
backups serão criados, substituídos, arquivados ou ignorados. Nenhum arquivo é
movido durante a prévia.

![Tela principal com prévia](docs/images/pt-main-window-preview.png)

### Temas claro e escuro

O botão de tema alterna a aparência sem mudar a geometria da interface. Na
primeira execução, o aplicativo acompanha o Windows; depois de uma escolha
manual, a preferência é salva no `config.json`.

![Tela principal no tema claro](docs/images/pt-main-window-light.png)

### Configuração local

Nome, sobrenome e pastas `ATU`/`HIS` são configurados localmente. O arquivo
`config.json` fica ao lado do executável e não é enviado automaticamente.

![Tela de configurações](docs/images/pt-settings-window.png)

### Limpeza controlada do histórico

A limpeza de `HIS` apresenta retenção, candidatos, idade, tamanho e motivo. A
remoção só acontece após seleção explícita e confirmação do usuário.

![Limpeza HIS](docs/images/pt-history-cleanup.png)

### Primeira abertura e interface bilíngue

As instruções iniciais explicam a estrutura recomendada e as regras de nomes. A
interface pode ser alternada entre português e inglês a qualquer momento.

![Instruções de uso](docs/images/pt-startup-instructions.png)

![Main window preview](docs/images/en-main-window-preview.png)

## Fluxo em 5 passos

| Passo | Ação | Resultado |
| --- | --- | --- |
| 1 | Coloque o executável junto aos arquivos de trabalho | O projeto é detectado na pasta local. |
| 2 | Configure colaborador, `ATU`, `HIS` e tipos de IED | As preferências ficam no `config.json` local. |
| 3 | Escolha a etapa e confira a prévia | Destinos, versões e possíveis conflitos ficam visíveis. |
| 4 | Clique em `Gerar backups` | ZIPs validados são publicados em `ATU` e versões anteriores vão para `HIS`. |
| 5 | Use `Limpeza HIS` quando necessário | Candidatos antigos são removidos somente após confirmação. |

## Principais Recursos

- Interface gráfica para Windows com pré-visualização antes da execução.
- Tela inicial de instruções com opção `Não exibir novamente`.
- Interface em português e inglês, com preferência salva em `config.json`.
- Tema claro/escuro com botão rápido; na primeira utilização acompanha o sistema
  e, após a troca manual, salva a preferência em `config.json`.
- Verificação automática de nova versão publicada no GitHub.
- Download direto do executável mais recente pelo aviso de atualização.
- Link `O que há de novo?` para consultar as notas da versão disponível.
- Executável distribuído com nome fixo `IED_Backup_Manager.exe`.
- Etapas padrão: `DEV`, `PRE-TAF`, `TAF`, `POS-TAF`, `PRE-TAC`, `TAC`,
  `POS-TAC` e descrição livre.
- Processamento individual ou agrupado por subestação/projeto.
- Pacote `IED-PACK` quando mais de um tipo de IED selecionado pertence ao mesmo
  projeto.
- Suporte a GE Multilin / EnerVista UR por pasta de SE, incluindo somente
  subpastas de IED com `.urs` ou `.urk`.
- Metadados `IEDS-BACKUP-INFO.txt` em todos os ZIPs.
- Registro de versões detectadas, arquivos incluídos, tamanho, data de
  modificação e SHA256 dos arquivos de origem.
- Alerta de integridade para mesma identidade técnica com SHA256 divergente.
- Validação das pastas `ATU` e `HIS`, com criação assistida quando faltarem.
- Aviso para pastas sincronizadas, como OneDrive ou SharePoint.
- Atualização automática de `ATU` e arquivamento do backup anterior em `HIS`.
- Escrita mais transacional, com ZIP validado antes de publicar o backup final.
- Quarentena operacional `IED-QUARENTENA` para falhas raras de cópia ou
  movimentação.
- Limpeza controlada de `HIS`, com retenção em dias, prévia, confirmação e
  preservação do backup mais recente por etapa.
- Detecção de duplicidades em `ATU`, com indicação do arquivo problemático.
- Progresso real por arquivo durante compactação e cópia para `ATU`/`HIS`.
- Execução em worker dedicado para manter a GUI responsiva.
- Prévia do lote calculada em segundo plano para reduzir travamentos em pastas
  grandes.
- Log diário local para diagnóstico de inicialização, prévia, backup e falhas.
- Detecção de encerramento inesperado com marcador separado por sessão, validação
  de UUID, PID, horário e caminho do executável e coleta consentida de eventos do
  Windows, sem envio automático ou solicitação de UAC.
- Cancelamento controlado antes de iniciar o próximo arquivo.
- Botão `Ajuda` / `Help` apontando para a documentação operacional pública.
- Indicador `©` com autoria, licença e link do repositório.

## Tipos Suportados

| Tipo | Extensões | Versão no backup |
| --- | --- | --- |
| Siemens DIGSI | `.dz5` | Detectada por marcador interno `.dp4v###` ou `.dp5v###`, gerando prefixos como `DIGSI5-V10.00`. |
| SEL QuickSet / Architect | `.rdb`, com `.scd` ou `.selaprj` opcional | QuickSet e Architect, quando encontrados, gerando prefixos como `QUICKSET-V7.5.3.10-ARCHITECT-V2.4.2.34`. |
| ABB PCM600 | `.pcmp`, `.apcmp` | Detectada em `ProjectDataServer%versions.ini`, gerando prefixos como `PCM600-V2.10`. |
| INGETEAM INGESYS | `.efsPro`, `.ITPro2` | Informada manualmente pelo usuário e salva em `config.json`, gerando prefixos como `INGESYS-V5.5.4`. |
| GE Multilin / EnerVista UR | pastas com `.urs` ou `.urk`; `.ENV` opcional | Usa a maior versão entre headers `GEMULTILIN`/`GEVERNOVA` em `.urs/.urk` e `UR Setup` em `.cid/.icd`, gerando prefixos como `GE-MULTILIN-V8.71`. |

## Regra de Nome dos Arquivos

O projeto/subestação é identificado pelo texto antes do primeiro sublinhado
`"_"`.

Exemplos:

```text
SE-AAA_COMENTARIO-GENERICO_20260712_1030.dz5 -> Projeto: SE-AAA
ETD-BBB_OUTRO-COMENTARIO.rdb                 -> Projeto: ETD-BBB
VAO-ZZZ_COMENTARIO-GENERICO_20260712_1050.efsPro -> Projeto: VAO-ZZZ
```

Todo texto depois do primeiro sublinhado `"_"` é tratado como comentário do
usuário e não entra na chave técnica do backup.
Se um identificador fictício vier como `SE CCC`, ele será normalizado para
`SE-CCC`.

Evite:

```text
SE_AAA_20260712_1030.dz5
CLIENTE_SE-AAA_20260712_1030.dz5
DEV_SE-AAA_20260712_1030.dz5
```

Nesses casos, o projeto pode ser identificado incorretamente.

## Versão do Software e Backup Atual

A versão completa continua no nome e na identidade histórica do ZIP, mas não
cria outro espaço de backup atual. Uma versão mais nova da mesma família, como
`DIGSI5-V10.00` depois de `DIGSI5-V9.00`, substitui o backup anterior da mesma
SE em `ATU` e move o anterior para `HIS`.

Quando a mesma SE já possui um backup individual de outra família, a aplicação
não presume se o trabalho é complementar ou um novo desenvolvimento. Antes da
execução, ela apresenta as opções `Manter os dois`, `Substituir existente` e
`Cancelar`, explicando o efeito de cada uma. Um `IED-PACK` substitui
automaticamente somente os backups individuais das famílias incluídas nele.

![Decisão entre famílias de software](docs/images/pt-software-choice.png)

## Nome dos Backups

O nome final segue o padrão:

```text
SOFTWARE_PROJETO_YYYY-MM-DD_HHhMM_NOME SOBRENOME_ETAPA.zip
```

Exemplos:

```text
DIGSI5-V10.00_SE-AAA_2026-07-12_10h30_NOME SOBRENOME_TAF.zip
QUICKSET-V7.5.3.10-ARCHITECT-V2.4.2.34_ETD-BBB_2026-07-12_10h35_NOME SOBRENOME_TAF.zip
PCM600-V2.10_SE-DDD_2026-07-12_10h40_NOME SOBRENOME_TAF.zip
INGESYS-V5.5.4_VAO-ZZZ_2026-07-12_10h50_NOME SOBRENOME_TAF.zip
GE-MULTILIN-V8.71_SE-AAA_2026-07-12_11h00_NOME SOBRENOME_TAF.zip
IED-PACK_SE-AAA_2026-07-12_10h35_NOME SOBRENOME_TAF.zip
```

## Configuração

O `config.json` fica ao lado do executável. A interface pode criar ou atualizar
esse arquivo pela tela `Configurações`.

Exemplo:

```json
{
  "nome": "NOME",
  "sobrenome": "SOBRENOME",
  "colaborador": "NOME SOBRENOME",
  "atu_path": "C:/Backups/Exemplo/ATU",
  "his_path": "C:/Backups/Exemplo/HIS",
  "language": "pt_BR",
  "theme": "dark",
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

1. Coloque o executável na pasta dos arquivos de trabalho.
2. Configure nome, sobrenome, `ATU`, `HIS`, idioma e tipos de IED.
3. Selecione a etapa.
4. Confira a `Prévia do lote`.
5. Clique em `Gerar backups`.
6. Aguarde a conclusão ou cancele antes do próximo arquivo.
7. Quando necessário, use `Limpeza HIS` para revisar candidatos antes de apagar.

Na coluna `Destino`, a prévia mostra um caminho compacto, como
`ATU\arquivo.zip` ou `HIS\arquivo.zip`. O caminho completo fica no tooltip da
célula.

## Estados de Processamento

- `stored`: novo backup salvo em `ATU`.
- `replaced_current`: backup anterior movido para `HIS` e novo backup salvo em
  `ATU`.
- `archived_history`: backup antigo salvo em `HIS` porque estava faltando no
  histórico.
- `atu_duplicate`: duplicidade encontrada em `ATU`; a GUI mostra o arquivo
  problemático e pergunta se deve mover para `HIS`.
- `sha_conflict`: existe backup com a mesma identidade técnica, mas SHA256
  diferente dos arquivos de origem; a execução fica bloqueada até verificação.
- `skipped_older`: arquivo ignorado porque já existe backup mais recente em
  `ATU`.
- `already_current`: arquivo já corresponde ao backup atual em `ATU`.

## Exemplos Públicos

A pasta [docs/examples](docs/examples) contém arquivos artificiais para testes,
prints e demonstrações públicas. Eles cobrem DIGSI, SEL, PCM600, INGETEAM e
GE Multilin, além de uma estrutura `ATU`/`HIS` para demonstrar a tela
`Limpeza HIS`.

A pasta de exemplo não inclui `config.json` de propósito. Assim, na primeira
execução, a aplicação abre sem configuração prévia e o usuário precisa preencher
os dados em `Configurações`, simulando o uso inicial real.

Executar a GUI com os exemplos:

```powershell
.\.venv\Scripts\python.exe -m src.gui.app --project-dir ".\docs\examples\sample-workspace"
```

Nas configurações, use:

```text
Colaborador: NOME SOBRENOME
Pasta ATU: docs\examples\sample-storage\ATU
Pasta HIS: docs\examples\sample-storage\HIS
```

Para INGETEAM, use a versão manual `5.5.4`.

Os exemplos não contêm dados reais de engenharia e não devem ser usados como
referência técnica dos formatos dos fabricantes.

## Download

O executável publicado usa sempre o mesmo nome:

```text
IED_Backup_Manager.exe
```

Link fixo para baixar o último executável publicado:

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
.\.venv\Scripts\python.exe -m src.main --project-dir ".\docs\examples\sample-workspace" --process-all --collaborator "NOME SOBRENOME" --atu-path ".\docs\examples\sample-storage\ATU" --his-path ".\docs\examples\sample-storage\HIS"
```

Simular sem criar ZIP nem mover arquivos:

```powershell
.\.venv\Scripts\python.exe -m src.main --project-dir ".\docs\examples\sample-workspace" --project-type sel --process-all --dry-run --collaborator "NOME SOBRENOME" --atu-path ".\docs\examples\sample-storage\ATU" --his-path ".\docs\examples\sample-storage\HIS"
```

Validar qualidade e testes:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
```

Gerar executável:

```powershell
.\scripts\release.ps1
```

O comando também gera `SHA256SUMS.txt` e `PUBLISH_RELEASE.ps1` dentro da pasta
`releases\vX.Y.Z`. Antes de publicar, valide os artefatos:

```powershell
.\releases\vX.Y.Z\PUBLISH_RELEASE.ps1 -VerifyOnly
```

Depois de fazer commit e enviar `master`, publique manualmente com:

```powershell
.\releases\vX.Y.Z\PUBLISH_RELEASE.ps1
```

É necessário ter o GitHub CLI instalado e autenticado com `gh auth login`.
Antes de criar o GitHub Release, o publicador executa novamente lint e testes,
exige o CI verde de `master`, envia a tag, aguarda o CI dessa tag para o mesmo
commit e apresenta um relatório com cada verificação marcada como `CORRETO` ou
`INCORRETO`. Quando tudo estiver correto, pergunta
`Publicar release com o release note e .exe?`; somente uma resposta afirmativa
cria o GitHub Release e envia os assets. Se qualquer validação falhar, nenhum
GitHub Release é criado.

## Arquitetura

```text
src/core/
  backup_service.py      Regras principais de planejamento e execução
  backup_planner.py      Prévia e decisão ATU/HIS
  backup_executor.py     Execução dos planos de backup
  storage.py             Regras de armazenamento, ATU/HIS e quarentena
  history_cleanup.py     Politica de limpeza controlada de HIS
  project_types/         Adaptadores por fabricante/software

src/gui/
  app.py                 Entrada da aplicação grafica
  main_window.py         Janela principal
  settings_window.py     Configurações
  history_cleanup_window.py Limpeza HIS
  backup_worker.py       Execução em worker Qt
```

Para adicionar outro tipo de IED, crie um novo adaptador em
`src/core/project_types/` com extensões suportadas, identificador de projeto,
software/versão e arquivos relacionados. Depois registre o adaptador em
`src/core/project_types/registry.py`.

## Cuidados de Privacidade

Não publique arquivos reais de backup, `config.json` local, caminhos internos de
empresa ou nomes reais de colaboradores. Para exemplos públicos, use nomes como
`SE-AAA`, `ETD-BBB`, `VAO-ZZZ` e `NOME SOBRENOME`.

As pastas locais `IED-DES/`, `IED-ATU/`, `IED-HIS/`, `config.json`, `.venv/`,
`build/`, `dist/`, `.spec` e `releases/` ficam protegidas pelo `.gitignore`.

## Roadmap

Proximos marcos:

- Melhorar experiência operacional conforme surgirem testes reais e feedback de
  usuários.
- Adicionar novos tipos de IED apenas quando surgirem arquivos reais de teste,
  limpos ou sanitizados, com regras confiáveis de identificação de versão.

Consulte [docs/PLANO_MELHORIAS.md](docs/PLANO_MELHORIAS.md) para detalhes.

## Contribuicoes

Contribuições são bem-vindas para correções, documentação, testes, exemplos
públicos e suporte a novos tipos de IED.

Antes de abrir uma issue ou pull request, leia
[CONTRIBUTING.md](CONTRIBUTING.md). O projeto possui templates para reportar
bugs, sugerir melhorias, propor novos tipos de IED e abrir pull requests.

Arquivos de exemplo só devem ser enviados quando forem artificiais, limpos ou
sanitizados. Não envie backups com informações confidenciais, dados reais de
cliente/projeto/subestação, IPs, usuários, credenciais, caminhos internos,
ajustes ou lógicas operacionais.

## Licença

Este projeto é disponibilizado sob a **IED Backup Manager Non-Commercial
License**.

Uso gratuito, estudo, auditoria, modificação e uso interno não comercial são
permitidos. Uso comercial, revenda, sublicenciamento, oferta como serviço pago
ou incorporação em produto/serviço comercial não são permitidos sem autorização
prévia por escrito do autor.

A atribuição ao autor original, Jean Carlos Machado, deve ser preservada.

Leia o arquivo [LICENSE](LICENSE) para os termos completos.
