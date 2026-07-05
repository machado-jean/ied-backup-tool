# IED Backup Manager

Aplicacao Windows para padronizar backups de projetos de IED, mantendo um
backup atual em `ATU`, historico em `HIS` e nomes de arquivo consistentes para
rastreabilidade tecnica.

Versao atual: `1.8.0`

Manual do executavel: [docs/USO_EXECUTAVEL.md](docs/USO_EXECUTAVEL.md)

Backlog tecnico: [docs/PLANO_MELHORIAS.md](docs/PLANO_MELHORIAS.md)

## Visao Geral

O IED Backup Manager processa os arquivos de trabalho que estao na mesma pasta
do executavel, identifica o projeto pelo trecho antes do primeiro sublinhado
`"_"`, gera um ZIP padronizado e aplica as regras de versionamento entre `ATU`
e `HIS`.

O objetivo e reduzir backups manuais inconsistentes, evitar duplicidades
tecnicas e preservar historico sem exigir que o usuario renomeie manualmente os
arquivos finais.

## Recursos

- Interface grafica para Windows com pre-visualizacao do lote antes da execucao.
- Tela inicial de instrucoes com opcao `Nao exibir novamente`.
- Interface em portugues e ingles, com preferencia salva em `config.json`.
- Selecao obrigatoria de etapa: `DEV`, `PRE-TAF`, `TAF`, `POS-TAF`,
  `PRE-TAC`, `TAC`, `POS-TAC` ou descricao livre.
- Processamento individual ou agrupado por subestacao/projeto.
- Pacote `IED-PACK` quando mais de um tipo de IED selecionado pertence ao mesmo
  projeto.
- Metadados `IEDS-BACKUP-INFO.txt` em todos os ZIPs, com versoes detectadas,
  arquivos incluidos, tamanho, data de modificacao e SHA256.
- Alerta de integridade quando um backup existente tem a mesma identidade tecnica,
  mas SHA256 diferente dos arquivos de origem.
- Validacao das pastas `ATU` e `HIS`, com criacao assistida quando faltarem.
- Atualizacao automatica de `ATU` e arquivamento do backup anterior em `HIS`.
- Gravacao mais transacional: o novo ZIP e validado antes de substituir o backup
  atual, reduzindo risco de estado parcial em falhas de arquivo ou permissao.
- Deteccao de duplicidades em `ATU`, com aviso do arquivo problematico.
- Barra de progresso durante a geracao dos backups.
- Progresso real por arquivo durante compactacao e copia para `ATU`/`HIS`.
- Execucao em worker dedicado para manter a GUI responsiva em backups grandes.
- Cancelamento controlado antes de iniciar o proximo arquivo.
- Cancelamento durante compactacao impede a copia final para `ATU`/`HIS`.
- Validacao amigavel para arquivos bloqueados, ausentes ou indisponiveis.

## Tipos Suportados

| Tipo | Extensoes | Versao no backup |
| --- | --- | --- |
| Siemens DIGSI | `.dz5` | Detectada por marcador interno `.dp4v###` ou `.dp5v###`, gerando prefixos como `DIGSI5-V10.00`. |
| SEL QuickSet / Architect | `.rdb`, com `.scd` ou `.selaprj` opcional | QuickSet e Architect, quando encontrados, gerando prefixos como `QUICKSET-V7.5.3.10-ARCHITECT-V2.4.2.34`. |
| ABB PCM600 | `.pcmp`, `.apcmp` | Detectada em `ProjectDataServer%versions.ini`, gerando prefixos como `PCM600-V2.10`. |
| INGETEAM INGESYS | `.efsPro`, `.ITPro2` | Informada manualmente pelo usuario e salva em `config.json`, gerando prefixos como `INGESYS-V5.5.4`. |

## Nome dos Backups

O nome final segue o padrao:

```text
SOFTWARE_PROJETO_DATAHORA_COLABORADOR_ETAPA.zip
```

Exemplos:

```text
DIGSI5-V10.00_SE-XXX_20260622-1350_COLABORADOR-EXEMPLO_TAF.zip
QUICKSET-V7.5.3.10-ARCHITECT-V2.4.2.34_ETD-YYY_20260612-0350_COLABORADOR-EXEMPLO_TAF.zip
PCM600-V2.10_SE-DDD_20260619-1230_COLABORADOR-EXEMPLO_TAF.zip
INGESYS-V5.5.4_VAO-ZZZ_20260619-1230_COLABORADOR-EXEMPLO_TAF.zip
IED-PACK_ETD-YYY_20260612-0350_COLABORADOR-EXEMPLO_TAF.zip
```

Para identificar o projeto, o sistema usa somente o texto antes do primeiro
sublinhado `"_"`. Textos depois dele funcionam como comentario do usuario e nao
entram na chave tecnica do backup.

## Configuracao

O `config.json` fica ao lado do executavel:

```json
{
  "colaborador": "COLABORADOR-EXEMPLO",
  "atu_path": "C:/Backups/Exemplo/ATU",
  "his_path": "C:/Backups/Exemplo/HIS",
  "language": "pt_BR",
  "project_types": ["digsi5", "sel"],
  "software_versions": {
    "ingeteam": "5.5.4"
  },
  "show_startup_instructions": true
}
```

Na primeira abertura, a aplicacao pode criar ou atualizar esse arquivo pela tela
de configuracoes.

## Uso

Executar a GUI em desenvolvimento:

```powershell
.\.venv\Scripts\python.exe -m src.gui.app
```

Executar a GUI usando uma pasta de amostras:

```powershell
.\.venv\Scripts\python.exe -m src.gui.app --project-dir ".\IED-DES"
```

Gerar o executavel versionado:

```powershell
.\scripts\release.ps1
```

Executar via CLI:

```powershell
.\.venv\Scripts\python.exe -m src.main --project-dir ".\IED-DES" --process-all --collaborator "COLABORADOR-EXEMPLO" --atu-path ".\IED-ATU" --his-path ".\IED-HIS"
```

Simular sem criar ZIP nem mover arquivos:

```powershell
.\.venv\Scripts\python.exe -m src.main --project-dir ".\IED-DES" --project-type sel --process-all --dry-run --collaborator "COLABORADOR-EXEMPLO" --atu-path ".\IED-ATU" --his-path ".\IED-HIS"
```

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

## Arquitetura

A regra geral de backup fica em:

```text
src/core/backup_service.py
```

As regras especificas por fabricante/software ficam em:

```text
src/core/project_types/
```

Tipos registrados atualmente:

- `digsi5`: `src/core/project_types/digsi.py`
- `sel`: `src/core/project_types/sel.py`
- `pcm600`: `src/core/project_types/pcm600.py`
- `ingeteam`: `src/core/project_types/ingeteam.py`

Para adicionar outro tipo de IED, crie um novo adaptador em
`src/core/project_types/` com extensoes suportadas, identificador de projeto,
software/versao e arquivos relacionados, depois registre em
`src/core/project_types/registry.py`.

## Desenvolvimento

Validar qualidade e testes:

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
```

## Roadmap

Itens desejados para evolucoes futuras:

- Adicionar novos tipos de IED conforme surgirem arquivos reais de teste.
- Criar ferramenta de limpeza controlada para backups antigos.
- Permitir politicas de limpeza por idade, por exemplo backups com mais de 30
  dias.
- Permitir politicas de limpeza por tamanho ocupado em disco.
- Melhorar relatorios operacionais quando a base de uso real crescer.

## Releases

As versoes publicadas ficam em `releases/vX.Y.Z/`, sempre com:

- executavel versionado;
- `RELEASE_NOTES.md`;
- tag Git correspondente quando a versao for consolidada.
