# Plano de Melhorias Tecnicas

Este documento registra o roadmap ativo, o historico de marcos implementados e
decisoes pausadas ou descartadas. Ele serve como referencia pesquisavel para
retomar decisoes tecnicas sem depender apenas do historico de conversa.

## Roadmap Ativo

As versoes abaixo sao estimativas pragmaticas. A ordem pode mudar se surgir uma
correcao urgente, um novo tipo de IED com arquivo real de teste ou uma melhoria
operacional claramente necessaria.

| Versao estimada | Marco | Entregas previstas |
| --- | --- | --- |
| `v1.16.0` | Melhorias guiadas por uso real | Pequenos ajustes de experiencia, robustez, mensagens, validacoes ou suporte, priorizados a partir de testes reais e feedback dos usuarios. |

## Historico Implementado

Esta secao registra os principais marcos ja entregues. Ela nao substitui release
notes detalhadas, mas ajuda a entender a evolucao tecnica do projeto.

| Versao | Marco | Entregas principais |
| --- | --- | --- |
| `v1.0.0` | Versao inicial funcional | Primeira versao consolidada do fluxo de backup, com processamento de arquivos de projeto, geracao de ZIP padronizado e organizacao entre backup atual e historico. |
| `v1.1.0` | Preparacao para multiplos tipos de IED | Estrutura preparada para receber adaptadores por fabricante/software, reduzindo acoplamento das regras especificas no fluxo principal. |
| `v1.4.2` | Seguranca operacional de pastas | Validacao de `ATU`/`HIS`, bloqueio de pastas iguais, criacao assistida de pastas ausentes, revalidacao antes de gerar backup e aviso para pastas sincronizadas. |
| `v1.5.0` | Metadados em todos os ZIPs | Criacao de `IEDS-BACKUP-INFO.txt` em todos os backups, com nome do backup, projeto, software, etapa, arquivos incluidos, tamanho e datas. |
| `v1.5.2` | SHA256 dos arquivos de origem | Registro de SHA256 dos arquivos incluidos no ZIP, sem colocar hash no nome do backup. |
| `v1.5.3` | Aviso para pastas sincronizadas | Alerta para `ATU`/`HIS` em pastas como OneDrive, SharePoint, Dropbox, Google Drive ou iCloud. |
| `v1.5.4` | ABB PCM600 `.apcmp` | Suporte ampliado de ABB PCM600 de `.pcmp` para `.pcmp` e `.apcmp`. |
| `v1.5.5` | Splash screen | Tela de carregamento e ajuste na ordem de inicializacao para melhorar a percepcao de abertura do executavel. |
| `v1.6.0` | Integridade avancada | Leitura de SHA256 em ZIPs existentes, deteccao de mesma identidade tecnica com conteudo divergente, status `Conflito SHA` e bloqueio da execucao enquanto houver conflito. |
| `v1.7.0` | Movimentacao mais transacional | Validacao do ZIP antes de tocar em `ATU`/`HIS`, copia temporaria dentro da pasta de destino, publicacao controlada e progresso real por bytes em compactacao/copia. |
| `v1.8.0` | Worker thread e cancelamento | Execucao em `QThread`, GUI responsiva durante backups grandes e cancelamento controlado antes de publicar o proximo backup. |
| `v1.9.0` | Ajuda publica/profissional | Criacao de `docs/HELP.md`, botao `Ajuda` / `Help`, documentacao de uso, limitacoes conhecidas, troubleshooting, privacidade e exemplos de metadados. |
| `v1.9.1` | Ajuda online no GitHub | Botao `Ajuda` apontando para o `HELP.md` publico no repositorio. |
| `v1.10.0` | Verificacao de atualizacoes | Consulta ao ultimo release publico no GitHub, aviso clicavel quando ha nova versao e tratamento silencioso de falhas de rede. |
| `v1.10.1` | Nome fixo do executavel | Executavel distribuido como `IED_Backup_Manager.exe`, mantendo a versao na interface, splash, release folder e tag Git. |
| `v1.10.2` | Licenca e autoria | Licenca non-commercial, notas publicas de licenca, indicador `©` na GUI e link para o repositorio. |
| `v1.10.3` | Download direto do executavel | Aviso de atualizacao abrindo o link fixo `/releases/latest/download/IED_Backup_Manager.exe`. |
| `v1.10.4` | Texto do aviso de atualizacao | Ajuste do texto para indicar que clicar no aviso baixa a nova versao. |
| `v1.10.5` | Revisao publica do repositorio | Varredura de dados sensiveis, exemplos genericos, confirmacao do `.gitignore` e ajuste de contraste do indicador `©`. |
| `v1.11.0` | Refatoracao estrutural | Extracao de componentes GUI, application service, renderizacao da previa, resumo/confirmacao textual, `BackupStatus`, planner, executor, duplicados e metadados em modulos menores. |
| `v1.12.0` | Quarentena operacional | Pasta `IED-QUARENTENA` para arquivos parciais ou suspeitos em falhas raras, nota `.txt` com origem/motivo/erro e limpeza automatica quando um backup valido cobre o caso. |
| `v1.13.0` | Limpeza controlada de HIS | Janela `Limpeza HIS`, retencao configuravel, preservacao do backup mais recente por `SOFTWARE + PROJETO + ETAPA`, previa com tamanho e exclusao apenas por selecao/confirmacao manual. |
| `v1.14.0` | Documentacao visual e contribuicao publica | Screenshots publicos, exemplos artificiais em `docs/examples`, README profissional, `CONTRIBUTING.md`, templates de issue/pull request e roadmap reorganizado para novos IEDs. |
| `v1.15.0` | GE Multilin / EnerVista UR | Novo adaptador para ambientes GE por pasta de SE, incluindo `.ENV` opcional e subpastas de IED com `.urs`/`.urk`; ZIP preserva subpastas e metadados registram resumo dos IEDs e versoes GE. |
| `v1.15.1` | Documentacao da logica de identificacao | Novo documento `docs/LOGICA_IDENTIFICACAO_IEDS.md` explicando regras de identificacao, arquivos incluidos, versao automatica/manual, casos especiais de INGETEAM e GE Multilin, e comportamento do `IED-PACK`. |

## Itens Pausados ou Descartados

Estes itens foram avaliados, mas nao fazem parte do roadmap ativo no momento.

| Item | Decisao | Motivo |
| --- | --- | --- |
| Relatorios operacionais | Pausado/descartado por enquanto | Pode gerar ruido no fluxo principal e nao e uma necessidade operacional atual. |
| Integridade externa `.sha256` | Pausado/descartado por enquanto | O SHA256 interno dos arquivos de origem ja atende melhor ao escopo atual; arquivos externos adicionariam manutencao e possivel confusao. |
| Assinatura de codigo | Pausada | Pode reduzir alertas de SmartScreen, mas envolve custo, gestao de certificado e decisao de distribuicao. |
| Empacotamento automatico em cada alteracao | Fora do fluxo normal | O executavel deve ser gerado apenas quando a versao estiver validada e o usuario solicitar release. |

## Criterios Para Novos Tipos de IED

Para adicionar um novo fabricante/software, o projeto precisa de pelo menos uma
das seguintes entradas:

- arquivo publico, artificial, limpo ou sanitizado;
- backup gerado a partir de um projeto vazio no software do fabricante;
- descricao confiavel de onde extrair versao e quais arquivos devem compor o ZIP;
- regra clara de extensao principal e arquivos acompanhantes.

Arquivos compartilhados publicamente nao devem conter:

- nomes reais de clientes, projetos, subestacoes ou colaboradores;
- IPs, usuarios, credenciais ou caminhos internos;
- dados eletricos, ajustes, logicas, topologias ou comunicacao reais;
- qualquer informacao confidencial ou sem permissao de publicacao.

## Criterios Para Melhorias Operacionais

Melhorias futuras devem preferencialmente:

- resolver problema observado em teste real;
- reduzir risco operacional;
- melhorar clareza para o usuario;
- preservar a politica de nomes e versionamento;
- incluir testes quando alterarem comportamento;
- atualizar documentacao quando mudarem a experiencia visivel.

## Referencias Relacionadas

- [README.md](../README.md)
- [HELP.md](HELP.md)
- [USO_EXECUTAVEL.md](USO_EXECUTAVEL.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
