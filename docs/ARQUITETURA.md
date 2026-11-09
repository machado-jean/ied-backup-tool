# Arquitetura do IED Backup Manager

[Português](ARQUITETURA.md) | [English](ARCHITECTURE.en.md)

## Objetivo

A arquitetura separa interface, coordenação e regras de backup para que as
decisões críticas de integridade sejam testáveis sem depender da janela Qt.

```text
PySide6 GUI                 CLI (`src/main.py`)
       \                         /
        serviços de aplicação e planejamento
                       |
           domínio em `src/core/`
                       |
  adaptadores por IED + ZIP + filesystem + configuração
```

A interface não é fonte de verdade para nomes, identidade, versionamento ou
movimentação. Essas regras pertencem ao núcleo e aos adaptadores de projeto.

## Componentes

### Configuração

`src/config/config_manager.py` lê e salva o `config.json` local. A configuração
contém colaborador, caminhos `ATU`/`HIS`, versões manuais e preferências visuais.
Ela não é enviada automaticamente e está excluída do Git.

### Domínio e pipeline

- `backup_planner.py` e `backup_service.py`: constroem planos sem executar
  alterações e expõem os fluxos de processamento;
- `backup_executor.py`: executa um plano já calculado;
- `backup_models.py`: modelos e estados compartilhados;
- `naming.py`: etapas, normalização e composição do nome final;
- `backup_metadata.py` e `hashing.py`: metadados e SHA256;
- `zipper.py`: criação e validação do ZIP;
- `storage.py`: publicação entre `ATU` e `HIS`;
- `integrity.py` e `backup_duplicates.py`: conflitos e duplicidades;
- `history_cleanup.py`: seleção segura de itens antigos em `HIS`;
- `path_validation.py`: validações e avisos de armazenamento;
- `app_logging.py`: logs e marcadores de sessão para diagnóstico;
- `update_checker.py`: consulta passiva ao release mais recente.

### Tipos de projeto

`src/core/project_types/base.py` define o contrato. O registry mantém os tipos
disponíveis e cada módulo implementa detecção, versão e arquivos incluídos:

- Siemens DIGSI;
- SEL QuickSet / Architect;
- ABB PCM600;
- INGETEAM INGESYS;
- GE Multilin / EnerVista UR.

As regras detalhadas e exceções estão em
[`LOGICA_IDENTIFICACAO_IEDS.md`](LOGICA_IDENTIFICACAO_IEDS.md).

### Interface gráfica

`src/gui/app.py` inicializa logging, tema, splash e `QApplication`.
`main_window.py` coordena a janela, enquanto componentes menores cuidam de
configuração, prévia, confirmação, execução, resumo e limpeza do histórico.

Trabalho potencialmente demorado ocorre em workers:

- `preview_worker.py`: calcula a prévia sem bloquear a janela;
- `backup_worker.py`: executa o lote e publica progresso;
- `update_worker.py`: consulta atualizações;
- `backup_application_service.py`: serviço sem Qt que valida entradas e monta a
  prévia usada pela GUI.

### Interface de linha de comando

`src/main.py` resolve configuração e argumentos, permite `--dry-run`, processa
o arquivo mais recente ou todos os arquivos e reutiliza o mesmo núcleo da GUI.

## Fluxo de backup

```text
configuração e seleção
        ↓
detecção dos projetos e versões
        ↓
plano somente leitura + prévia
        ↓
confirmação explícita
        ↓
criação temporária e validação do ZIP
        ↓
publicação em ATU
        ↓
versão anterior em HIS, quando aplicável
        ↓
resumo, log e limpeza de temporários
```

Um plano pode representar criação, substituição, arquivamento, correção de
duplicidade, item já atual, item antigo ignorado ou conflito de integridade.
Estados que não autorizam escrita devem permanecer sem efeitos colaterais.

## Identidade e armazenamento

- `ATU` contém a cópia atual por identidade técnica;
- `HIS` preserva versões anteriores e itens históricos;
- a identidade considera família/tipo, projeto, etapa e composição relevante;
- mudança somente de versão pode atualizar o mesmo backup atual;
- famílias diferentes exigem decisão explícita quando houver ambiguidade;
- o `IED-PACK` agrupa tipos compatíveis do mesmo projeto;
- `IEDS-BACKUP-INFO.txt` registra origem, versões, arquivos, datas, tamanhos e
  SHA256 sem colocar o hash no nome do ZIP.

## Segurança e recuperação

O fluxo deve preservar a última cópia válida. O ZIP é validado antes da
publicação, cópias usam arquivos temporários no destino e falhas recuperáveis
podem gerar `IED-QUARENTENA`. Conflitos SHA não são resolvidos por
sobrescrita automática. A limpeza de `HIS` exige prévia, seleção e confirmação.

Dados operacionais reais nunca são fixtures públicas. Os testes usam diretórios
temporários e exemplos artificiais sob `docs/examples/`.

## Dependências permitidas

- GUI pode depender de serviços, configuração e núcleo;
- CLI pode depender de configuração e núcleo;
- núcleo não deve importar widgets Qt;
- adaptadores específicos podem depender dos contratos do núcleo;
- regras comuns não devem ser copiadas para cada fabricante.

## Evolução

Mudanças duráveis em formato, identidade, armazenamento, recuperação,
distribuição ou fronteiras devem criar uma ADR em `docs/decisions/`. Mudanças
visíveis ao usuário também devem atualizar os manuais e o roadmap aplicáveis.
