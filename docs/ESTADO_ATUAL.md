# Estado atual e ponto de retomada

[Português](ESTADO_ATUAL.md) | [English](CURRENT_STATE.en.md)

Atualizado em: **8 de novembro de 2026**.

## Produto vigente

- aplicação: IED Backup Manager;
- versão em `src/version.py`: **1.18.1**;
- branch principal: `master`;
- plataforma: Windows 10/11;
- runtime de desenvolvimento/CI: Python 3.13;
- GUI: PySide6;
- distribuição: executável único `IED_Backup_Manager.exe` por PyInstaller.

O README descreve v1.18.1 como a versão pública atual. O histórico dos marcos e
as funções implementadas estão em `PLANO_MELHORIAS.md` e nas releases do GitHub.

## Capacidades consolidadas

- prévia antes de alterações;
- processamento individual, em lote e agrupado como `IED-PACK`;
- adaptadores DIGSI, SEL, PCM600, INGESYS e GE Multilin/EnerVista UR;
- metadados e SHA256 no ZIP;
- integridade, duplicidades e quarentena operacional;
- atualização de `ATU` e histórico em `HIS`;
- limpeza controlada do histórico;
- workers para prévia e execução;
- cancelamento em limites seguros;
- interface PT-BR/English e temas claro/escuro;
- logs, detecção de encerramento inesperado e diagnóstico consentido;
- consulta e download passivos de nova versão;
- CI Windows com Ruff e Pytest;
- build e publicação de release com hashes e confirmação manual.

## Estrutura atual

O núcleo está em `src/core/`, os adaptadores em
`src/core/project_types/`, a GUI em `src/gui/`, a configuração em
`src/config/` e a CLI em `src/main.py`. A arquitetura detalhada está em
`ARQUITETURA.md`.

## Última validação observada

Em 8 de novembro de 2026:

- `python -m ruff check .`: aprovado;
- `python -m pytest`: **176 testes aprovados** em Python 3.13.16;
- verificação de links Markdown relativos: aprovada;
- `git diff --check`: aprovado.

Após o sucesso dos testes, o callback de encerramento do Pytest registrou
`PermissionError` ao inspecionar `pytest-current` no diretório temporário do
perfil Windows. O processo terminou com código zero e nenhum teste falhou. Esse
aviso descreve limitação de limpeza do ambiente, não evidência de falha do
produto.

## Próxima prioridade conhecida

O roadmap ativo aponta **v1.19.0 — novos tipos de IED**. Um novo tipo somente
deve ser iniciado quando existir amostra limpa/sanitizada ou descrição técnica
confiável que permita testar:

- arquivo principal e extensões;
- arquivos acompanhantes;
- extração automática ou entrada manual de versão;
- identidade técnica e interação com `IED-PACK`;
- conteúdo do ZIP e metadados;
- compatibilidade com `ATU`, `HIS`, integridade e duplicidades.

Não há fabricante adicional aprovado ou amostra pública registrada neste
documento. Portanto, a retomada não deve inventar um novo adaptador.

## Ponto de retomada recomendado

1. Confirmar `git status --short --branch` e ler alterações locais.
2. Ler `AGENTS.md`, este documento, `PLANO_MELHORIAS.md` e ADRs relevantes.
3. Executar Ruff e Pytest antes de nova implementação.
4. Para novo IED, obter primeiro os insumos seguros e documentar a regra.
5. Criar testes do adaptador antes de integrá-lo ao registry e à GUI.
6. Atualizar documentação pública e este estado quando a etapa terminar.

## Decisões ou riscos abertos

- assinatura de código permanece pausada por custo e gestão de certificado;
- relatórios operacionais e integridade externa `.sha256` permanecem fora do
  roadmap ativo;
- builds automáticos a cada alteração não fazem parte do fluxo normal;
- novos tipos de IED dependem de amostras seguras e verificáveis;
- dados reais e configurações locais continuam fora do Git e precisam de backup
  privado separado.

## Como atualizar este arquivo

Atualize a data e somente fatos observáveis. Registre o último gate executado
quando encerrar uma etapa material. Remova pendências resolvidas, mas mova
decisões históricas importantes para ADRs ou roadmap antes de removê-las. Não
transforme este arquivo em changelog ou diário de conversa.
