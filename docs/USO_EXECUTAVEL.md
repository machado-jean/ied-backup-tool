# IED Backup Manager - Uso do Executavel

Este guia explica como usar o `IED_Backup_Manager.exe` para gerar backups
padronizados de projetos de IED. Nesta versao, os tipos disponiveis sao DIGSI 5
(`.dz5`), SEL (`.rdb`), ABB PCM600 (`.pcmp`/`.apcmp`) e INGETEAM (`.efsPro`/`.ITPro2`).

## 1. Estrutura esperada

O executavel deve ficar na pasta do projeto que sera processada. Essa mesma
pasta deve conter os arquivos de projeto suportados.

Exemplo:

```text
Pasta do projeto/
├─ IED_Backup_Manager.exe
├─ config.json
├─ SE-AAA_20260529_1624.dz5
├─ SE-AAA_20260529_1625.dz5
├─ ESD-AAA.rdb
├─ ESD-AAA.scd
├─ SE-DDD_20260619_1230.pcmp
├─ SE-EEE_20260619_1230.apcmp
```

O programa nao precisa que a pasta `BKPs` exista quando estiver em uso real.
Ele sempre processa a pasta onde o executavel esta localizado.

## 2. Primeira abertura

Ao abrir o executavel pela primeira vez, a tela de instrucoes sera exibida. Ela
mostra a estrutura recomendada de pastas e as regras de nomes dos arquivos.

Nessa tela, voce pode:

- Alternar o idioma entre portugues e ingles pelo botao de bandeira.
- Marcar `Nao exibir novamente` para nao mostrar essa tela nas proximas
  aberturas.

Depois, a tela de configuracoes sera exibida. Preencha:

- `Colaborador`: nome usado no arquivo final do backup.
- `Pasta ATU`: pasta onde ficara o backup atual de cada projeto.
- `Pasta HIS`: pasta onde ficara o historico de backups antigos.

Depois clique em `Salvar`.

O programa criara ou atualizara o arquivo `config.json` ao lado do executavel.
Nao e necessario criar uma pasta `config`.

Ao salvar, o programa tambem valida `Pasta ATU` e `Pasta HIS`:

- se alguma pasta nao existir, sera perguntado se deseja cria-la;
- `ATU` e `HIS` nao podem apontar para a mesma pasta;
- se uma pasta estiver dentro da outra, o programa mostra um aviso antes de
  continuar.

Exemplo de `config.json`:

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
  "show_startup_instructions": true,
  "history_cleanup": {
    "retention_days": 30
  }
}
```

## 3. Selecionar idioma

Ao abrir o programa, uma tela de instrucoes apresenta a estrutura recomendada de
pastas e as regras de nomes dos arquivos. Se marcar `Nao exibir novamente`, essa
preferencia sera salva no `config.json`.

Use o botao de bandeira para alternar entre portugues e ingles. Ele existe na
tela de instrucoes e tambem na tela principal, ao lado de `Configuracoes`.

A preferencia fica salva no `config.json`.

## 4. Abrir ajuda

Use o botao `Ajuda` na tela principal para abrir o documento operacional no
GitHub:

```text
https://github.com/machado-jean/ied-backup-tool/blob/master/docs/HELP.md
```

Esse documento resume estrutura de pastas, regras de nomes, exemplos de saida,
metadados internos dos ZIPs, limitacoes conhecidas, solucao de problemas e
cuidados de privacidade.

## 5. Verificar atualizacoes

Ao abrir o aplicativo, ele consulta o ultimo release publico no GitHub.

Se existir uma versao mais recente, sera exibido o aviso `Nova versão
disponível` no canto inferior esquerdo da tela principal. Clique no aviso para
abrir a pagina do release no navegador.

Se o computador estiver sem internet, com GitHub bloqueado ou se voce ja estiver
na versao mais recente, o aplicativo continua funcionando normalmente.

O programa nao baixa nem substitui o executavel automaticamente.

## 6. Selecionar tipos de IED

Marque os tipos de IED que deseja processar.

As opcoes marcadas ficam salvas no `config.json`. Ao abrir o programa novamente,
a selecao anterior sera restaurada.

Se nenhuma preferencia estiver salva, o programa inicia sem tipo selecionado.
Selecione ao menos um tipo para liberar a previa do lote.

## 7. Selecionar etapa

Antes de gerar backups, selecione a etapa da entrega.

Etapas disponiveis:

- `DEV`
- `PRE-TAF`
- `TAF`
- `POS-TAF`
- `PRE-TAC`
- `TAC`
- `POS-TAC`
- `Descrição livre`

A etapa entra no nome do backup gerado. Ela nao bloqueia retornos de etapa. Por
exemplo, se um projeto ja passou por `TAC` e depois precisar voltar para `DEV`,
o backup podera ser gerado normalmente.

Ao selecionar `Descrição livre`, um campo `Descrição` sera exibido. Esse campo
pode ser preenchido manualmente, por exemplo para indicar um backup antes de uma
grande alteracao, ou pode ficar vazio quando o caso nao se enquadrar nas etapas
anteriores.

## 8. Tipos de arquivo suportados

### DIGSI 5

O backup DIGSI 5 usa o arquivo `.dz5`.

O programa le o marcador interno `.dp5v###` ou `.dp4v###` dentro do `.dz5` para
identificar a familia e a versao do DIGSI. Exemplos:

```text
SE-ZZZ_20260622_1350.dp5v100 -> DIGSI5-V10.00
SE-ZZZ_20260622_1350.dp5v75  -> DIGSI5-V7.50
SE-ZZZ_20260622_1350.dp5v98  -> DIGSI5-V9.80
SE-ZZZ_20260622_1350.dp4v75  -> DIGSI4-V7.50
```

### SEL

O backup SEL sempre usa o arquivo `.rdb` gerado pelo QuickSet.

Quando existir um arquivo Architect com o mesmo nome-base do `.rdb`, ele tambem
sera incluido no ZIP final:

```text
ESD-AAA.rdb      -> entra no ZIP
ESD-AAA.scd      -> entra no ZIP, se existir
ESD-AAA.selaprj  -> entra no ZIP, se existir
```

O programa tenta detectar automaticamente:

- versao QuickSet no `.rdb`;
- versao AcSELerator Architect no `.scd` ou `.selaprj`, quando existir.

Se a versao QuickSet nao for encontrada, um campo `Versão do software` aparece
na tela. Preencha a versao manualmente para liberar a previa e a geracao do
backup.

### ABB PCM600

O backup ABB PCM600 usa arquivos `.pcmp` ou `.apcmp`.

O programa trata `.pcmp` e `.apcmp` como pacotes ZIP e procura o arquivo:

```text
ProjectDataServer%versions.ini
```

Dentro desse arquivo, o programa usa:

```text
ProductName=PCM600_210
ProductVersion=2.10
```

O exemplo acima gera o prefixo:

```text
PCM600-V2.10
```

### INGETEAM

O backup INGETEAM usa arquivos `.efsPro` ou `.ITPro2`.

Como esses formatos podem conter varias versoes internas de componentes, a
versao do software INGETEAM deve ser informada pelo usuario. Ao marcar
`INGETEAM (.efsPro, .ITPro2)`, um campo `v` aparece na mesma linha. Preencha
apenas o numero da versao, por exemplo:

```text
5.5.4
```

Essa versao fica salva no `config.json` em `software_versions.ingeteam` e gera
o prefixo de software:

```text
INGESYS-V5.5.4
```

### Agrupamento por subestacao

Quando apenas um tipo de IED estiver selecionado, o programa gera backups
individuais daquele tipo.

Quando dois ou mais tipos estiverem selecionados, o programa avalia os arquivos
por subestacao/projeto. Assim, se a pasta tiver arquivos DIGSI e SEL da mesma
subestacao, e ambos os tipos estiverem marcados, eles entram no mesmo ZIP.

Se apenas um tipo for encontrado para uma subestacao, mesmo com varios tipos
marcados, o nome do backup continua sendo o nome individual daquele tipo. Nesse
caso, ele nao usa `IED-PACK`.

Quando apenas um tipo real for encontrado para a subestacao, o processamento
segue o modo normal desse tipo: com `Processar apenas a partir do backup atual`
desmarcado, todos os backups encontrados podem ser avaliados para `ATU`/`HIS`.
Com a opcao marcada, somente o atual e os mais recentes entram na previa.

Exemplo:

```text
SE-AAA_20260619_1200.dz5
SE-AAA.rdb
SE-AAA.scd
```

Com `DIGSI 5` e `SEL` selecionados, o resultado sera um unico pacote:

```text
IED-PACK_SE-AAA_20260619-1230_COLABORADOR-EXEMPLO_TAF.zip
```

Dentro do ZIP ficarao somente os arquivos dos tipos selecionados. Se `SEL` nao
estiver marcado, o `.rdb` e o `.scd` nao entram no pacote.

Se existir mais de um arquivo principal do mesmo tipo para a mesma subestacao,
o pacote usa somente o mais recente daquele tipo. Exemplo: dois `.dz5` da mesma
SE resultam em apenas o `.dz5` mais recente dentro do pacote.

Todos os ZIPs gerados incluem tambem o arquivo `IEDS-BACKUP-INFO.txt`, que
lista:

- nome do backup;
- projeto/subestacao;
- data/hora usada no pacote;
- colaborador e etapa;
- versoes detectadas por tipo;
- arquivos incluidos no ZIP;
- tamanho dos arquivos incluidos;
- data de modificacao dos arquivos incluidos;
- SHA256 dos arquivos incluidos.

## 9. Padrao de nome dos arquivos de origem

Para os tipos suportados, o programa identifica o projeto/subestacao pelo nome
do arquivo. Pela politica atual, o projeto e sempre o primeiro bloco antes do
primeiro sublinhado `"_"`.

Para DIGSI 5, o padrao recomendado e:

```text
SE-XXXXXX_OUTROS-TEXTOS_AAAAMMDD_HHMM.dz5
```

O programa considera como `Projeto` apenas `SE-XXXXXX`. Textos depois do
primeiro sublinhado `"_"` sao ignorados para identificar o projeto, mas podem
continuar no nome do arquivo de origem para controle interno da equipe.

Exemplos:

```text
SE-AAA_20260529_1624.dz5           -> Projeto: SE-AAA
SE-BBB_DEV_01_20260619_0013.dz5    -> Projeto: SE-BBB
SE-ABC_REVISAO_FINAL_20260619_1015.dz5 -> Projeto: SE-ABC
ESD-AAA.rdb                        -> Projeto: ESD-AAA
```

Para SEL, o mesmo criterio do primeiro bloco antes do sublinhado `"_"` e usado
quando o nome tem textos adicionais. Se o arquivo nao tiver sublinhado `"_"`, o
nome-base inteiro sera usado como projeto.

Cuidados:

- Para DIGSI 5, mantenha o nome terminando com data e hora no formato
  `_AAAAMMDD_HHMM`.
- Textos adicionais devem ficar depois do primeiro sublinhado `"_"` e antes da
  data/hora.
- Evite usar a data/hora no meio do nome se ela nao for o sufixo final.
- Mesmo quando houver textos intermediarios, o projeto sera sempre apenas o
  primeiro bloco antes do primeiro sublinhado `"_"`.
- Nao coloque sublinhado `"_"` dentro do nome da subestacao/projeto. Exemplo:
  `SE_BBB_20260619_0013.dz5` sera identificado como projeto `SE`, nao `SE_BBB`.
- Nao coloque textos antes da subestacao/projeto. Exemplo:
  `CLIENTE_SE-BBB_20260619_0013.dz5` sera identificado como projeto `CLIENTE`.
- Nao use nomes que comecem com etapa/revisao antes da subestacao. Exemplo:
  `DEV_SE-BBB_20260619_0013.dz5` sera identificado como projeto `DEV`.
- Confira sempre a coluna `Projeto` na previa antes de gerar backups.

## 10. Conferir a previa do lote

Depois de selecionar a etapa, a tela mostra uma previa dos arquivos suportados
encontrados na pasta.

Colunas principais:

- `Acao`: o que o programa pretende fazer.
- `Arquivo`: arquivo principal de origem (`.dz5`, `.rdb`, `.pcmp`, `.apcmp`, `.efsPro`,
  `.ITPro2`) ou primeiro arquivo do pacote agrupado.
- `Projeto`: identificador do projeto.
- `Versao`: versao encontrada no arquivo ou conjunto de versoes do pacote.
- `Data/Hora`: data do arquivo usada no nome do backup.
- `Destino`: pasta ou arquivo de destino previsto.

Status possiveis:

- `Novo`: cria um novo backup em `ATU`.
- `Atualiza ATU`: move o backup atual para `HIS` e salva o novo em `ATU`.
- `Arquivar HIS`: salva o arquivo antigo em `HIS`, sem alterar `ATU`.
- `Corrigir ATU`: encontrou mais de um backup atual para o mesmo projeto.
- `Conflito SHA`: existe backup com a mesma identidade tecnica, mas SHA256
  diferente dos arquivos de origem. A execucao fica bloqueada ate o usuario
  verificar o arquivo problemático.
- `Ignorado`: o arquivo e antigo e ja existe no historico.
- `Ja atual`: o arquivo ja corresponde ao backup atual em `ATU`.

## 11. Modo de processamento

A opcao `Processar apenas a partir do backup atual` evita reprocessar arquivos
antigos que vieram antes do backup atual ja existente em `ATU`.

Use essa opcao quando a pasta tiver muitos arquivos antigos e voce quiser
processar somente o backup atual e os arquivos mais novos.

## 12. Gerar backups

Clique em `Gerar backups`.

Antes de executar, o programa mostra uma confirmacao com a quantidade de
arquivos que serao processados.

Nesse momento, o programa revalida `ATU` e `HIS`. Se alguma pasta tiver sido
apagada, desconectada ou ficar indisponivel depois da configuracao, a execucao
sera bloqueada ate o usuario corrigir ou recriar a pasta.

Durante a execucao, uma barra de progresso mostra o arquivo atual, a etapa da
operacao e o progresso por bytes. A execucao roda em segundo plano para manter a
interface responsiva.

Se clicar em `Cancelar` durante a compactacao, o ZIP temporario sera descartado
e nao sera copiado para `ATU`/`HIS`. Se a copia final para `ATU`/`HIS` ja tiver
comecado, o programa finaliza essa copia antes de parar para preservar a
consistencia do backup.

Aguarde a conclusao ou o cancelamento controlado antes de fechar o programa.

Ao final, sera exibido um resumo com:

- Total analisado.
- Apenas os contadores com valor, como novos backups, atualizacoes em `ATU`,
  historicos arquivados, correcoes, ignorados ou arquivos ja atuais.

Se ocorrer uma falha rara de copia, publicacao ou arquivamento, o programa pode
mover arquivos parciais ou suspeitos para `IED-QUARENTENA`, criada ao lado de
`ATU`/`HIS`. Essa pasta inclui um `.txt` com origem, motivo e data/hora para
analise manual. Quando houver erro do sistema operacional, como falta de espaco,
permissao negada ou arquivo bloqueado, esse erro tambem e registrado no `.txt`.

Quando a falha for resolvida e um backup da mesma chave tecnica for concluido
com timestamp igual ou mais recente, os itens correspondentes da quarentena sao
removidos automaticamente. Se a pasta ficar vazia, ela tambem e apagada.

## 13. Limpeza HIS

Use o botao `Limpeza HIS` para revisar backups antigos da pasta `HIS`.

A regra padrao e:

- `Retenção em dias`: `30`;
- use `0` para desabilitar verificacoes de limpeza apos backup;
- arquivos mais novos que o periodo configurado sao mantidos;
- o backup mais recente de cada `SOFTWARE + PROJETO + ETAPA` e sempre mantido;
- tamanho total e tamanho candidato a limpeza sao exibidos apenas para apoio;
- a limpeza manual exige marcar os arquivos pelo checkbox e confirmar a
  exclusao.

Depois de um backup concluido, caso existam candidatos a limpeza, o resumo final
informa a quantidade de arquivos e o tamanho estimado. A remocao so acontece ao
abrir `Limpeza HIS`, selecionar os arquivos e confirmar manualmente.

Se `Retenção em dias` estiver como `0`, o programa nao verifica candidatos apos
o backup e nao mostra aviso no resumo final. A janela continua disponivel pelo
botao `Limpeza HIS`.

Arquivos ZIP fora do padrao de nome do IED Backup Manager sao ignorados pela
limpeza.

## 14. Resultado dos arquivos

O nome final do backup segue o padrao:

```text
SOFTWARE_PROJETO_DATAHORA_COLABORADOR_ETAPA.zip
```

Exemplo:

```text
DIGSI5-V10.00_SE-AAA_20260529-1625_COLABORADOR-EXEMPLO_TAF.zip
QUICKSET-V7.5.3.10-ARCHITECT-V2.4.2.34_ESD-AAA_20260623-0031_COLABORADOR-EXEMPLO_TAF.zip
PCM600-V2.10_SE-DDD_20260619-1230_COLABORADOR-EXEMPLO_TAF.zip
INGESYS-V5.5.4_SE-EEE_20260619-1230_COLABORADOR-EXEMPLO_TAF.zip
IED-PACK_SE-AAA_20260619-1230_COLABORADOR-EXEMPLO_TAF.zip
```

Regras principais:

- `ATU` mantem apenas o backup mais recente de cada projeto.
- `HIS` mantem os backups anteriores.
- A comparacao tecnica considera `SOFTWARE_PROJETO_DATAHORA`.
- Mudancas apenas de colaborador ou etapa nao criam duplicidade tecnica.

## 15. Abrir pastas ATU e HIS

Use os botoes:

- `Abrir ATU`
- `Abrir HIS`

Eles abrem as pastas configuradas diretamente no Windows Explorer.

Se a pasta tiver sido apagada depois da configuracao, o programa perguntara se
voce deseja recria-la antes de abrir. A pasta nao e recriada automaticamente
sem confirmacao.

## 16. Cuidados recomendados

- Feche o DIGSI antes de gerar backups, para evitar arquivo bloqueado.
- Feche QuickSet/Architect antes de gerar backups SEL, para evitar arquivo
  bloqueado.
- Confira a previa antes de clicar em `Gerar backups`.
- Nao altere manualmente arquivos dentro de `ATU`, a menos que seja necessario.
- Se aparecer `Corrigir ATU`, leia o arquivo problematico informado antes de
  confirmar a correcao.
- Se existir `IED-QUARENTENA`, leia o `.txt` correspondente antes de apagar ou
  restaurar qualquer arquivo que nao tenha sido limpo automaticamente.
- Antes de usar `Limpeza HIS`, confira a previa. A remocao exige selecao e
  confirmacao manual.
- Mantenha o `config.json` junto do executavel.

## 17. Atualizacao de versao

Quando receber uma nova versao do executavel:

1. Feche o programa.
2. Substitua o `IED_Backup_Manager.exe` antigo pelo novo.
3. Mantenha o mesmo `config.json`.
4. Abra o novo executavel.

O arquivo `config.json` nao precisa ser recriado a cada versao.

O download direto da versao mais recente pode usar sempre o mesmo link:

```text
https://github.com/machado-jean/ied-backup-tool/releases/latest/download/IED_Backup_Manager.exe
```

## 18. Licenca e autoria

Na tela principal, clique no simbolo `©` no canto inferior direito para ver a
nota curta de autoria e licenca.

O projeto e disponibilizado para uso gratuito e nao comercial. A atribuicao ao
autor original, Jean Carlos Machado, deve ser preservada.

