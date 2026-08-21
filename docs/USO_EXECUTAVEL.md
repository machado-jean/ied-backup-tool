# IED Backup Manager - Uso do Executável

[Português](USO_EXECUTAVEL.md) | [English](EXECUTABLE_USAGE.en.md)

Este guia explica como usar o `IED_Backup_Manager.exe` para gerar backups
padronizados de projetos de IED. Nesta versão, os tipos disponíveis são DIGSI 5
(`.dz5`), SEL (`.rdb`), ABB PCM600 (`.pcmp`/`.apcmp`), INGETEAM
(`.efsPro`/`.ITPro2`) e GE Multilin / EnerVista UR (`.urs`/`.urk` em subpastas).

Para uma visão visual do fluxo, consulte também o `README.md` e
`docs/HELP.md`, que contém capturas públicas da tela principal, configurações,
instruções de uso e limpeza `HIS`.

Para entender a regra técnica de cada tipo de IED, incluindo os casos especiais
de INGETEAM e GE Multilin, consulte `docs/LOGICA_IDENTIFICACAO_IEDS.md`.

## 1. Estrutura esperada

O executável deve ficar na pasta do projeto que será processada. Essa mesma
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
├─ GE-IED-A/
│  ├─ GE-IED-A.urs
│  ├─ GE-IED-A.cid
```

O programa não precisa que a pasta `BKPs` exista quando estiver em uso real.
Elé sempre processa a pasta onde o executável está localizado.

## 2. Primeira abertura

Ao abrir o executável pela primeira vez, a tela de instruções será exibida. Ela
mostra a estrutura recomendada de pastas e as regras de nomes dos arquivos.

Nessa tela, você pode:

- Alternar o idioma entre português e inglês pelo botão de bandeira.
- Marcar `Não exibir novamente` para não mostrar essa tela nas próximas
  aberturas.

Depois, a tela de configurações será exibida. Preencha:

- `Colaborador`: nome usado no arquivo final do backup.
- `Pasta ATU`: pasta onde ficará o backup atual de cada projeto.
- `Pasta HIS`: pasta onde ficará o histórico de backups antigos.

Depois clique em `Salvar`.

O programa criara ou atualizara o arquivo `config.json` ao lado do executável.
Não é necessário criar uma pasta `config`.

Ao salvar, o programa também valida `Pasta ATU` e `Pasta HIS`:

- se alguma pasta não existir, será perguntado se deseja criá-la;
- `ATU` e `HIS` não podem apontar para a mesma pasta;
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

Ao abrir o programa, uma tela de instruções apresenta a estrutura recomendada de
pastas e as regras de nomes dos arquivos. Se marcar `Não exibir novamente`, essa
preferência será salva no `config.json`.

Use o botão de bandeira para alternar entre português e inglês. Ele existe na
tela de instruções e também na tela principal, ao lado de `Configurações`.

A preferência fica salva no `config.json`.

## 4. Abrir ajuda

Use o botão `Ajuda` na tela principal para abrir o documento operacional no
GitHub:

```text
https://github.com/machado-jean/ied-backup-tool/blob/master/docs/HELP.md
```

Esse documento resume estrutura de pastas, regras de nomes, exemplos de saída,
metadados internos dos ZIPs, limitações conhecidas, solução de problemas e
cuidados de privacidade.

## 5. Verificar atualizações

Ao abrir o aplicativo, ele consulta o último release público no GitHub.

Se existir uma versão mais recente, será exibido o aviso `Nova versão
disponível` no canto inferior esquerdo da tela principal. Clique no aviso para
iniciar o download direto do executável mais recente no navegador.

Se o computador estiver sem internet, com GitHub bloqueado ou se você já estiver
na versão mais recente, o aplicativo continua funcionando normalmente.

O programa não baixa nem substitui o executável automaticamente.

## 6. Selecionar tipos de IED

Marque os tipos de IED que deseja processar.

As opções marcadas ficam salvas no `config.json`. Ao abrir o programa novamente,
a seleção anterior será restaurada.

Se nenhuma preferência estiver salva, o programa inicia sem tipo selecionado.
Selecione ao menos um tipo para liberar a prévia do lote.

## 7. Selecionar etapa

Antes de gerar backups, selecione a etapa da entrega.

Etapas disponíveis:

- `DEV`
- `PRE-TAF`
- `TAF`
- `POS-TAF`
- `PRE-TAC`
- `TAC`
- `POS-TAC`
- `Descrição livre`

A etapa entra no nome do backup gerado. Ela não bloqueia retornos de etapa. Por
exemplo, se um projeto já passou por `TAC` e depois precisar voltar para `DEV`,
o backup poderá ser gerado normalmente.

Ao selecionar `Descrição livre`, um campo `Descrição` será exibido. Esse campo
pode ser preenchido manualmente, por exemplo para indicar um backup antes de uma
grande alteração, ou pode ficar vazio quando o caso não se enquadrar nas etapas
anteriores.

## 8. Tipos de arquivo suportados

### DIGSI 5

O backup DIGSI 5 usa o arquivo `.dz5`.

O programa le o marcador interno `.dp5v###` ou `.dp4v###` dentro do `.dz5` para
identificar a família e a versão do DIGSI. Exemplos:

```text
SE-ZZZ_20260622_1350.dp5v100 -> DIGSI5-V10.00
SE-ZZZ_20260622_1350.dp5v75  -> DIGSI5-V7.50
SE-ZZZ_20260622_1350.dp5v98  -> DIGSI5-V9.80
SE-ZZZ_20260622_1350.dp4v75  -> DIGSI4-V7.50
```

### SEL

O backup SEL sempre usa o arquivo `.rdb` gerado pelo QuickSet.

Quando existir um arquivo Architect com o mesmo nome-base do `.rdb`, ele também
será incluído no ZIP final:

```text
ESD-AAA.rdb      -> entra no ZIP
ESD-AAA.scd      -> entra no ZIP, se existir
ESD-AAA.selaprj  -> entra no ZIP, se existir
```

O programa tenta detectar automaticamente:

- versão QuickSet no `.rdb`;
- versão AcSELerator Architect no `.scd` ou `.selaprj`, quando existir.

Se a versão QuickSet não for encontrada, um campo `Versão do software` aparece
na tela. Preencha a versão manualmente para liberar a prévia e a geração do
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

Como esses formatos podem conter várias versões internas de componentes, a
versão do software INGETEAM deve ser informada pelo usuário. Ao marcar
`INGETEAM (.efsPro, .ITPro2)`, um campo `v` aparece na mesma linha. Preencha
apenas o número da versão, por exemplo:

```text
5.5.4
```

Essa versão fica salva no `config.json` em `software_versions.ingeteam` e gera
o prefixo de software:

```text
INGESYS-V5.5.4
```

### GE Multilin / EnerVista UR

O backup GE usa a pasta da SE/aplicação como projeto. Dentro dela, o programa
procura subpastas diretas que contenham `.urs` ou `.urk`.

Quando uma subpasta é identificada como IED GE, entram no ZIP apenas:

```text
.urs
.urk
.cid
.icd
```

O `.ENV` do topo da pasta também entra quando existir.

A versão usada no nome do ZIP é a maior versão encontrada entre:

- headers `GEMULTILIN` ou `GEVERNOVA` na primeira linha de `.urs/.urk`;
- cabeçalhos `GE Digital Energy UR Setup` ou `Multilin UR Setup` em `.cid/.icd`.

Exemplo:

```text
HEADER,GEVERNOVA,5,T60,870,...
Created by Multilin UR Setup 8.71

Saída: GE-MULTILIN-V8.71
```

No `IEDS-BACKUP-INFO.txt`, o programa mantém o resumo por IED, incluindo a
versão de aplicação do relé e a versão do software usado no desenvolvimento,
quando encontradas.

### Agrupamento por subestação

Quando apenas um tipo de IED estiver selecionado, o programa gera backups
individuais daquele tipo.

Quando dois ou mais tipos estiverem selecionados, o programa avalia os arquivos
por subestação/projeto. Assim, se a pasta tiver arquivos DIGSI e SEL da mesma
subestação, e ambos os tipos estiverem marcados, eles entram no mesmo ZIP.

Se apenas um tipo for encontrado para uma subestação, mesmo com vários tipos
marcados, o nome do backup continua sendo o nome individual daquele tipo. Nesse
caso, ele não usa `IED-PACK`.

Quando apenas um tipo real for encontrado para a subestação, o processamento
segue o modo normal desse tipo: com `Processar apenas a partir do backup atual`
desmarcado, todos os backups encontrados podem ser avaliados para `ATU`/`HIS`.
Com a opção marcada, somente o atual e os mais recentes entram na prévia.

Exemplo:

```text
SE-AAA_20260619_1200.dz5
SE-AAA.rdb
SE-AAA.scd
```

Com `DIGSI 5` e `SEL` selecionados, o resultado será um único pacote:

```text
IED-PACK_SE-AAA_20260619-1230_COLABORADOR-EXEMPLO_TAF.zip
```

Dentro do ZIP ficaráo somente os arquivos dos tipos selecionados. Se `SEL` não
estiver marcado, o `.rdb` e o `.scd` não entram no pacote.

Se existir mais de um arquivo principal do mesmo tipo para a mesma subestação,
o pacote usa somente o mais recente daquele tipo. Exemplo: dois `.dz5` da mesma
SE resultam em apenas o `.dz5` mais recente dentro do pacote.

Todos os ZIPs gerados incluem também o arquivo `IEDS-BACKUP-INFO.txt`, que
lista:

- nome do backup;
- projeto/subestação;
- data/hora usada no pacote;
- colaborador e etapa;
- versões detectadas por tipo;
- arquivos incluídos no ZIP;
- tamanho dos arquivos incluídos;
- data de modificação dos arquivos incluídos;
- SHA256 dos arquivos incluídos.

## 9. Padrão de nome dos arquivos de origem

Para os tipos suportados, o programa identifica o projeto/subestação pelo nome
do arquivo. Pela política atual, o projeto é sempre o primeiro bloco antes do
primeiro sublinhado `"_"`.

Para DIGSI 5, o padrão recomendado e:

```text
SE-XXXXXX_OUTROS-TEXTOS_AAAAMMDD_HHMM.dz5
```

O programa considera como `Projeto` apenas `SE-XXXXXX`. Textos depois do
primeiro sublinhado `"_"` são ignorados para identificar o projeto, mas podem
continuar no nome do arquivo de origem para controle interno da equipe.

Exemplos:

```text
SE-AAA_20260529_1624.dz5           -> Projeto: SE-AAA
SE-BBB_DEV_01_20260619_0013.dz5    -> Projeto: SE-BBB
SE-ABC_REVISAO_FINAL_20260619_1015.dz5 -> Projeto: SE-ABC
ESD-AAA.rdb                        -> Projeto: ESD-AAA
```

Para SEL, o mesmo critério do primeiro bloco antes do sublinhado `"_"` é usado
quando o nome tem textos adicionais. Se o arquivo não tiver sublinhado `"_"`, o
nome-base inteiro será usado como projeto.

Cuidados:

- Para DIGSI 5, mantenha o nome terminando com data e hora no formato
  `_AAAAMMDD_HHMM`.
- Textos adicionais devem ficar depois do primeiro sublinhado `"_"` e antes da
  data/hora.
- Evite usar a data/hora no meio do nome se ela não for o sufixo final.
- Mesmo quando houver textos intermediarios, o projeto será sempre apenas o
  primeiro bloco antes do primeiro sublinhado `"_"`.
- Não coloque sublinhado `"_"` dentro do nome da subestação/projeto. Exemplo:
  `SE_BBB_20260619_0013.dz5` será identificado como projeto `SE`, não `SE_BBB`.
- Não coloque textos antes da subestação/projeto. Exemplo:
  `CLIENTE_SE-BBB_20260619_0013.dz5` será identificado como projeto `CLIENTE`.
- Não use nomes que comecem com etapa/revisão antes da subestação. Exemplo:
  `DEV_SE-BBB_20260619_0013.dz5` será identificado como projeto `DEV`.
- Confira sempre a coluna `Projeto` na prévia antes de gerar backups.

## 10. Conferir a prévia do lote

Depois de selecionar a etapa, a tela mostra uma prévia dos arquivos suportados
encontrados na pasta.

Colunas principais:

- `Ação`: o que o programa pretende fazer.
- `Arquivo`: arquivo principal de origem (`.dz5`, `.rdb`, `.pcmp`, `.apcmp`, `.efsPro`,
  `.ITPro2`) ou primeiro arquivo do pacote agrupado.
- `Projeto`: identificador do projeto.
- `Versão`: versão encontrada no arquivo ou conjunto de versões do pacote.
- `Data/Hora`: data do arquivo usada no nome do backup.
- `Destino`: destino previsto em formato compacto, como `ATU\arquivo.zip` ou
  `HIS\arquivo.zip`. O caminho completo aparece ao passar o mouse sobre a
  célula.

Status possiveis:

- `Novo`: cria um novo backup em `ATU`.
- `Atualiza ATU`: move o backup atual para `HIS` é salva o novo em `ATU`.
- `Arquivar HIS`: salva o arquivo antigo em `HIS`, sem alterar `ATU`.
- `Corrigir ATU`: encontrou mais de um backup atual para o mesmo projeto.
- `Conflito SHA`: existe backup com a mesma identidade técnica, mas SHA256
  diferente dos arquivos de origem. A execução fica bloqueada até o usuário
  verificar o arquivo problemático.
- `Ignorado`: o arquivo é antigo e já existe no histórico.
- `Ja atual`: o arquivo já corresponde ao backup atual em `ATU`.

## 11. Modo de processamento

A opção `Processar apenas a partir do backup atual` evita reprocessar arquivos
antigos que vieram antes do backup atual já existente em `ATU`.

Use essa opção quando a pasta tiver muitos arquivos antigos e você quiser
processar somente o backup atual e os arquivos mais novos.

## 12. Gerar backups

Clique em `Gerar backups`.

Antes de executar, o programa mostra uma confirmação com a quantidade de
arquivos que seráo processados.

Nesse momento, o programa revalida `ATU` e `HIS`. Se alguma pasta tiver sido
apagada, desconectada ou ficar indisponível depois da configuração, a execução
será bloqueada até o usuário corrigir ou recriar a pasta.

Durante a execução, uma barra de progresso mostra o arquivo atual, a etapa da
operação e o progresso por bytes. A execução roda em segundo plano para manter a
interface responsiva.

Se clicar em `Cancelar` durante a compactação, o ZIP temporario será descartado
e não será copiado para `ATU`/`HIS`. Se a cópia final para `ATU`/`HIS` já tiver
comecado, o programa finaliza essa cópia antes de parar para preservar a
consistencia do backup.

Aguarde a conclusão ou o cancelamento controlado antes de fechar o programa.

Ao final, será exibido um resumo com:

- Total analisado.
- Apenas os contadores com valor, como novos backups, atualizações em `ATU`,
  históricos arquivados, correções, ignorados ou arquivos já atuais.

Se ocorrer uma falha rara de cópia, publicação ou arquivamento, o programa pode
mover arquivos parciais ou suspeitos para `IED-QUARENTENA`, criada ao lado de
`ATU`/`HIS`. Essa pasta inclui um `.txt` com origem, motivo e data/hora para
análise manual. Quando houver erro do sistema operacional, como falta de espaco,
permissão negada ou arquivo bloqueado, esse erro também é registrado no `.txt`.

Quando a falha for resolvida e um backup da mesma chave técnica for concluído
com timestamp igual ou mais recente, os itens correspondentes da quarentena são
removidos automaticamente. Se a pasta ficar vazia, ela também é apagada.

## 13. Limpeza HIS

Use o botão `Limpeza HIS` para revisar backups antigos da pasta `HIS`.

A regra padrão é:

- `Retenção em dias`: `30`;
- use `0` para desabilitar verificações de limpeza após backup;
- arquivos mais novos que o período configurado são mantidos;
- o backup mais recente de cada `SOFTWARE + PROJETO + ETAPA` é sempre mantido;
- tamanho total e tamanho candidato a limpeza são exibidos apenas para apoio;
- a limpeza manual exige marcar os arquivos pelo checkbox e confirmar a
  exclusão.

Depois de um backup concluído, caso existam candidatos a limpeza, o resumo final
informa a quantidade de arquivos e o tamanho estimado. A remoção só acontece ao
abrir `Limpeza HIS`, selecionar os arquivos e confirmar manualmente.

Se `Retenção em dias` estiver como `0`, o programa não verifica candidatos após
o backup e não mostra aviso no resumo final. A janela continua disponível pelo
botão `Limpeza HIS` e ainda mostra o total de arquivos/tamanho em `HIS`, mas sem
candidatos para exclusão.

Arquivos ZIP fora do padrão de nome do IED Backup Manager são ignorados pela
limpeza.

## 14. Resultado dos arquivos

O nome final do backup segue o padrão:

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

- `ATU` mantém apenas o backup mais recente de cada projeto.
- `HIS` mantém os backups anteriores.
- A comparação técnica considera `SOFTWARE_PROJETO_DATAHORA`.
- Mudanças apenas de colaborador ou etapa não criam duplicidade técnica.

## 15. Abrir pastas ATU e HIS

Use os botoes:

- `Abrir ATU`
- `Abrir HIS`

Eles abrem as pastas configuradas diretamente no Windows Explorer.

Se a pasta tiver sido apagada depois da configuração, o programa perguntara se
você deseja recriá-la antes de abrir. A pasta não é recriada automaticamente
sem confirmação.

## 16. Cuidados recomendados

- Feche o DIGSI antes de gerar backups, para evitar arquivo bloqueado.
- Feche QuickSet/Architect antes de gerar backups SEL, para evitar arquivo
  bloqueado.
- Confira a prévia antes de clicar em `Gerar backups`.
- Não altere manualmente arquivos dentro de `ATU`, a menos que seja necessário.
- Se aparecer `Corrigir ATU`, leia o arquivo problemático informado antes de
  confirmar a correcao.
- Se existir `IED-QUARENTENA`, leia o `.txt` correspondente antes de apagar ou
  restaurar qualquer arquivo que não tenha sido limpo automaticamente.
- Antes de usar `Limpeza HIS`, confira a prévia. A remoção exige seleção e
  confirmação manual.
- Mantenha o `config.json` junto do executável.

## 17. Atualização de versão

Quando receber uma nova versão do executável:

1. Feche o programa.
2. Substitua o `IED_Backup_Manager.exe` antigo pelo novo.
3. Mantenha o mesmo `config.json`.
4. Abra o novo executável.

O arquivo `config.json` não precisa ser recriado a cada versão.

O download direto da versão mais recente pode usar sempre o mesmo link:

```text
https://github.com/machado-jean/ied-backup-tool/releases/latest/download/IED_Backup_Manager.exe
```

## 18. Licença e autoria

Na tela principal, clique no simbolo `©` no canto inferior direito para ver a
nota curta de autoria e licença.

O projeto é disponibilizado para uso gratuito e não comercial. A atribuição ao
autor original, Jean Carlos Machado, deve ser preservada.
