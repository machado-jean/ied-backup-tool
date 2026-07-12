# Plano de Melhorias Técnicas

[Português](PLANO_MELHORIAS.md) | [English](ROADMAP.en.md)

Este documento registra o roadmap ativo, o histórico de marcos implementados e
decisões pausadas ou descartadas. Ele serve como referência pesquisável para
retomar decisões técnicas sem depender apenas do histórico de conversa.

## Roadmap Ativo

As versões abaixo são estimativas pragmaticas. A ordem pode mudar se surgir uma
correcao urgente, um novo tipo de IED com arquivo real de teste ou uma melhoria
operacional claramente necessária.

| Versão estimada | Marco | Entregas previstas |
| --- | --- | --- |
| `v1.16.0` | Documentação bilíngue e melhorias guiadas por uso real | Arquivos públicos separados em português/inglês, alternância entre idiomas no GitHub, botão `Ajuda` / `Help` abrindo a documentação conforme o idioma ativo e pequenos ajustes priorizados por testes reais. |

## Histórico Implementado

Esta secao registra os principais marcos já entregues. Ela não substitui release
notes detalhadas, mas ajuda a entender a evolução técnica do projeto.

| Versão | Marco | Entregas principais |
| --- | --- | --- |
| `v1.0.0` | Versão inicial funcional | Primeira versão consolidada do fluxo de backup, com processamento de arquivos de projeto, geração de ZIP padronizado e organização entre backup atual e histórico. |
| `v1.1.0` | Preparação para multiplos tipos de IED | Estrutura preparada para receber adaptadores por fabricante/software, reduzindo acoplamento das regras específicas no fluxo principal. |
| `v1.4.2` | Segurança operacional de pastas | Validação de `ATU`/`HIS`, bloqueio de pastas iguais, criação assistida de pastas ausentes, revalidação antes de gerar backup e aviso para pastas sincronizadas. |
| `v1.5.0` | Metadados em todos os ZIPs | Criação de `IEDS-BACKUP-INFO.txt` em todos os backups, com nome do backup, projeto, software, etapa, arquivos incluídos, tamanho e datas. |
| `v1.5.2` | SHA256 dos arquivos de origem | Registro de SHA256 dos arquivos incluídos no ZIP, sem colocar hash no nome do backup. |
| `v1.5.3` | Aviso para pastas sincronizadas | Alerta para `ATU`/`HIS` em pastas como OneDrive, SharePoint, Dropbox, Google Drive ou iCloud. |
| `v1.5.4` | ABB PCM600 `.apcmp` | Suporte ampliado de ABB PCM600 de `.pcmp` para `.pcmp` e `.apcmp`. |
| `v1.5.5` | Splash screen | Tela de carregamento e ajuste na ordem de inicialização para melhorar a percepção de abertura do executável. |
| `v1.6.0` | Integridade avançada | Leitura de SHA256 em ZIPs existentes, detecção de mesma identidade técnica com conteúdo divergente, status `Conflito SHA` e bloqueio da execução enquanto houver conflito. |
| `v1.7.0` | Movimentação mais transacional | Validação do ZIP antes de tocar em `ATU`/`HIS`, cópia temporária dentro da pasta de destino, publicação controlada e progresso real por bytes em compactação/cópia. |
| `v1.8.0` | Worker thread e cancelamento | Execução em `QThread`, GUI responsiva durante backups grandes e cancelamento controlado antes de publicar o próximo backup. |
| `v1.9.0` | Ajuda pública/profissional | Criação de `docs/HELP.md`, botão `Ajuda` / `Help`, documentação de uso, limitações conhecidas, troubleshooting, privacidade e exemplos de metadados. |
| `v1.9.1` | Ajuda online no GitHub | Botão `Ajuda` apontando para o `HELP.md` público no repositório. |
| `v1.10.0` | Verificação de atualizações | Consulta ao último release público no GitHub, aviso clicável quando há nova versão e tratamento silencioso de falhas de rede. |
| `v1.10.1` | Nome fixo do executável | Executável distribuído como `IED_Backup_Manager.exe`, mantendo a versão na interface, splash, release folder e tag Git. |
| `v1.10.2` | Licença e autoria | Licença non-commercial, notas públicas de licença, indicador `©` na GUI e link para o repositório. |
| `v1.10.3` | Download direto do executável | Aviso de atualização abrindo o link fixo `/releases/latest/download/IED_Backup_Manager.exe`. |
| `v1.10.4` | Texto do aviso de atualização | Ajuste do texto para indicar que clicar no aviso baixa a nova versão. |
| `v1.10.5` | Revisão pública do repositório | Varredura de dados sensíveis, exemplos genéricos, confirmação do `.gitignore` e ajuste de contraste do indicador `©`. |
| `v1.11.0` | Refatoração estrutural | Extração de componentes GUI, application service, renderização da prévia, resumo/confirmação textual, `BackupStatus`, planner, executor, duplicados e metadados em módulos menores. |
| `v1.12.0` | Quarentena operacional | Pasta `IED-QUARENTENA` para arquivos parciais ou suspeitos em falhas raras, nota `.txt` com origem/motivo/erro e limpeza automática quando um backup válido cobre o caso. |
| `v1.13.0` | Limpeza controlada de HIS | Janela `Limpeza HIS`, retenção configurável, preservação do backup mais recente por `SOFTWARE + PROJETO + ETAPA`, prévia com tamanho e exclusão apenas por seleção/confirmação manual. |
| `v1.14.0` | Documentação visual e contribuição pública | Screenshots públicos, exemplos artificiais em `docs/examples`, README profissional, `CONTRIBUTING.md`, templates de issue/pull request e roadmap reorganizado para novos IEDs. |
| `v1.15.0` | GE Multilin / EnerVista UR | Novo adaptador para ambientes GE por pasta de SE, incluindo `.ENV` opcional e subpastas de IED com `.urs`/`.urk`; ZIP preserva subpastas e metadados registram resumo dos IEDs e versões GE. |
| `v1.15.1` | Documentação da lógica de identificação | Novo documento `docs/LOGICA_IDENTIFICACAO_IEDS.md` explicando regras de identificação, arquivos incluídos, versão automática/manual, casos especiais de INGETEAM e GE Multilin, e comportamento do `IED-PACK`. |

## Itens Pausados ou Descartados

Estes itens foram avaliados, mas não fazem parte do roadmap ativo no momento.

| Item | Decisão | Motivo |
| --- | --- | --- |
| Relatórios operacionais | Pausado/descartado por enquanto | Pode gerar ruído no fluxo principal e não é uma necessidade operacional atual. |
| Integridade externa `.sha256` | Pausado/descartado por enquanto | O SHA256 interno dos arquivos de origem já atende melhor ao escopo atual; arquivos externos adicionariam manutenção e possível confusão. |
| Assinatura de código | Pausada | Pode reduzir alertas de SmartScreen, mas envolve custo, gestão de certificado e decisão de distribuição. |
| Empacotamento automático em cada alteração | Fora do fluxo normal | O executável deve ser gerado apenas quando a versão estiver validada e o usuário solicitar release. |

## Critérios Para Novos Tipos de IED

Para adicionar um novo fabricante/software, o projeto precisa de pelo menos uma
das seguintes entradas:

- arquivo público, artificial, limpo ou sanitizado;
- backup gerado a partir de um projeto vazio no software do fabricante;
- descrição confiável de onde extrair versão e quais arquivos devem compor o ZIP;
- regra clara de extensão principal e arquivos acompanhantes.

Arquivos compartilhados publicamente não devem conter:

- nomes reais de clientes, projetos, subestações ou colaboradores;
- IPs, usuários, credenciais ou caminhos internos;
- dados elétricos, ajustes, lógicas, topologias ou comunicação reais;
- qualquer informação confidencial ou sem permissão de publicação.

## Critérios Para Melhorias Operacionais

Melhorias futuras devem preferencialmente:

- resolver problema observado em teste real;
- reduzir risco operacional;
- melhorar clareza para o usuário;
- preservar a política de nomes e versionamento;
- incluir testes quando alterarem comportamento;
- atualizar documentação quando mudarem a experiência visível.

## Referencias Relacionadas

- [README.md](../README.md)
- [HELP.md](HELP.md)
- [USO_EXECUTAVEL.md](USO_EXECUTAVEL.md)
- [CONTRIBUTING.md](../CONTRIBUTING.md)
