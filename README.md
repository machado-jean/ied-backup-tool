# IED Backup Manager

Aplicacao Windows para geracao padronizada de backups de projetos de protecao
eletrica, com suporte inicial a Siemens DIGSI 5 (`.dz5`), SEL QuickSet
(`.rdb` com Architect opcional), ABB PCM600 (`.pcmp`) e INGETEAM
(`.efsPro`/`.ITPro2`).

Status: base funcional em desenvolvimento.

## Escopo V1

- Detectar automaticamente arquivos de projeto suportados na pasta do projeto.
- Extrair o identificador do projeto pelo trecho antes do sufixo
  `_AAAAMMDD_HHMM`.
- Tratar o `.dz5` como ZIP para localizar a versao do DIGSI.
- Tratar o `.rdb` SEL como arquivo principal e incluir `.scd` ou `.selaprj`
  de mesmo nome-base quando existir.
- Tratar o `.pcmp` ABB PCM600 como pacote ZIP para localizar
  `ProjectDataServer%versions.ini` e extrair `ProductName`/`ProductVersion`.
- Processar arquivos INGETEAM `.efsPro` e `.ITPro2` usando a versao informada
  pelo usuario e salva em `config.json`.
- Agrupar arquivos por subestacao em um unico ZIP quando mais de um tipo de IED
  estiver selecionado na GUI.
- Incluir `IED-PACK-MANIFEST.txt` nos pacotes agrupados com versoes detectadas
  e arquivos incluídos.
- Usar a data/hora de ultima modificacao do arquivo principal na nomenclatura.
- Gerar ZIP no padrao:
  `SOFTWARE_PROJETO_DATAHORA_COLABORADOR_ETAPA.zip`
- Atualizar as pastas `ATU` e `HIS` mantendo apenas o backup mais recente em
  `ATU` para cada chave `SOFTWARE_PROJETO`.
- Comparar duplicidade tecnica por `SOFTWARE_PROJETO_DATAHORA`. `COLABORADOR`
  e `ETAPA` permanecem no nome do arquivo, mas nao fazem o sistema criar outra
  copia quando o conteudo tecnico ja existe.
- A etapa deve ser escolhida pelo usuario a cada execucao. Ela classifica o
  backup gerado, mas nao bloqueia retornos como `POS-TAC` para `DEV` em
  entregas futuras do mesmo projeto.

## Configuracao

Crie `config.json` ao lado do executavel:

```json
{
  "colaborador": "JEAN-CARLOS-MACHADO",
  "atu_path": "C:/Users/Jean/OneDrive/BKP/ATU",
  "his_path": "C:/Users/Jean/OneDrive/BKP/HIS"
}
```

## Uso temporario via CLI

```powershell
.\.venv\Scripts\python.exe -m src.main --project-dir "C:\caminho\do\projeto" --stage DEV
```

## GUI V1

```powershell
.\.venv\Scripts\python.exe -m src.gui.app
```

Versao atual do aplicativo: `1.4.0`.

Manual de uso do executavel: [docs/USO_EXECUTAVEL.md](docs/USO_EXECUTAVEL.md).

Para gerar o executavel versionado:

```powershell
.\scripts\release.ps1
```

Para avaliar a GUI usando uma pasta de amostras durante o desenvolvimento:

```powershell
.\.venv\Scripts\python.exe -m src.gui.app --project-dir ".\IED-DES"
```

A tela principal mostra a pasta atual, uma tabela de pre-visualizacao do lote,
contadores de resumo, selecao obrigatoria de etapa, idioma, tipos de arquivo
suportados e o modo `Processar apenas a partir do backup atual`. Use
`Configuracoes` para salvar colaborador, pasta `ATU` e pasta `HIS` em
`config.json`.

Ao abrir, a GUI exibe uma tela de instrucoes com orientacoes de pasta e nome dos
arquivos. O usuario pode marcar `Nao exibir novamente`; a preferencia fica salva
em `config.json`.

Na GUI, a pasta processada e sempre a pasta atual do executavel/processo. A tela
pre-visualiza todos os arquivos suportados encontrados nessa pasta e o botao
`Gerar backups` executa o lote completo seguindo as regras `ATU/HIS`. Quando
mais de um tipo de IED estiver marcado, os arquivos encontrados sao avaliados
por subestacao/projeto. Se a subestacao tiver dois ou mais tipos encontrados, o
resultado e um pacote `IED-PACK`. Se apenas um tipo existir para aquela
subestacao, o backup mantem o nome individual daquele tipo. O pacote usa somente
o arquivo principal mais recente de cada tipo selecionado e inclui um manifesto
`.txt` com as versoes detectadas. Antes de executar, a GUI exibe uma confirmacao com a
quantidade de backups novos/substituidos. Apos a execucao, os botoes `Abrir ATU`
e `Abrir HIS` permitem acessar as pastas no Explorer.

Para processar todos os arquivos suportados de uma pasta em ordem cronologica:

```powershell
.\.venv\Scripts\python.exe -m src.main --project-dir ".\BKPs" --process-all --collaborator "JEAN-CARLOS-MACHADO" --atu-path ".\IED-ATU" --his-path ".\IED-HIS"
```

Para processar arquivos SEL via CLI, selecione o tipo `sel`. Quando a versao
nao for detectada automaticamente, informe `--software-version`:

```powershell
.\.venv\Scripts\python.exe -m src.main --project-dir ".\IED-DES" --project-type sel --process-all --software-version "7.5.2.3" --collaborator "JEAN-CARLOS-MACHADO" --atu-path ".\IED-ATU" --his-path ".\IED-HIS"
```

Para visualizar a acao prevista sem criar ZIP nem mover arquivos:

```powershell
.\.venv\Scripts\python.exe -m src.main --project-dir ".\IED-DES" --project-type sel --process-all --dry-run --collaborator "JEAN-CARLOS-MACHADO" --atu-path ".\IED-ATU" --his-path ".\IED-HIS"
```

Status possiveis:

- `stored`: novo backup salvo em `ATU`.
- `replaced_current`: backup anterior movido para `HIS` e novo backup salvo em `ATU`.
- `archived_history`: backup antigo salvo em `HIS` porque estava faltando no historico.
- `atu_duplicate`: duplicidade encontrada em `ATU`; a GUI mostra o arquivo
  problematico e pergunta se deve mover para `HIS`.
- `skipped_older`: arquivo ignorado porque ja existe backup mais recente em `ATU`.
- `already_current`: arquivo ja corresponde ao backup atual em `ATU`.

O idioma padrao da interface e das mensagens e portugues (`pt_BR`). O botao de
bandeira no canto superior alterna entre portugues e ingles (`en_US`) e salva a
preferencia em `config.json`.

Antes de compactar, o sistema valida se o arquivo de origem pode ser lido e
mostra mensagem amigavel caso esteja aberto, bloqueado ou indisponivel.

## Desenvolvimento

```powershell
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\python.exe -m ruff check src tests
```

## Tipos de IED

A regra geral de backup (`ATU/HIS`, nomenclatura, historico e duplicidade
tecnica) fica em `src/core/backup_service.py`.

As regras especificas de cada software/IED ficam em `src/core/project_types/`.
Atualmente existem os tipos `digsi5`, implementado em
`src/core/project_types/digsi.py`, `sel`, implementado em
`src/core/project_types/sel.py`, `pcm600`, implementado em
`src/core/project_types/pcm600.py`, e `ingeteam`, implementado em
`src/core/project_types/ingeteam.py`.

Para adicionar outro tipo, a ideia e criar um novo modulo nessa pasta
implementando:

- extensoes suportadas;
- identificador do projeto;
- software/versao usada no nome do backup.
- arquivos relacionados que devem entrar no ZIP, quando houver.

Depois, o novo tipo deve ser registrado em `src/core/project_types/registry.py`.

