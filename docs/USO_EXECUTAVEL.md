# IED Backup Manager - Uso do Executavel

Este guia explica como usar o `IED Backup Manager v1.1.2.exe` para gerar backups
padronizados de projetos de IED. Nesta versao, os tipos disponiveis sao DIGSI 5
(`.dz5`) e SEL (`.rdb`).

## 1. Estrutura esperada

O executavel deve ficar na pasta do projeto que sera processada. Essa mesma
pasta deve conter os arquivos de projeto suportados.

Exemplo:

```text
Pasta do projeto/
├─ IED Backup Manager v1.1.2.exe
├─ config.json
├─ SE-GVM_20260529_1624.dz5
├─ SE-GVM_20260529_1625.dz5
├─ ESD-PDO.rdb
├─ ESD-PDO.scd
```

O programa nao precisa que a pasta `BKPs` exista quando estiver em uso real.
Ele sempre processa a pasta onde o executavel esta localizado.

## 2. Primeira abertura

Ao abrir o executavel pela primeira vez, a tela de configuracoes sera exibida.
Preencha:

- `Colaborador`: nome usado no arquivo final do backup.
- `Pasta ATU`: pasta onde ficara o backup atual de cada projeto.
- `Pasta HIS`: pasta onde ficara o historico de backups antigos.

Depois clique em `Salvar`.

O programa criara ou atualizara o arquivo `config.json` ao lado do executavel.
Nao e necessario criar uma pasta `config`.

Exemplo de `config.json`:

```json
{
  "colaborador": "JEAN-CARLOS-MACHADO",
  "atu_path": "C:/Users/Jean/OneDrive/BKP/ATU",
  "his_path": "C:/Users/Jean/OneDrive/BKP/HIS",
  "language": "pt_BR",
  "project_types": ["digsi5", "sel"]
}
```

## 3. Selecionar idioma

Use o botao de bandeira no canto superior para alternar entre portugues e
ingles.

A preferencia fica salva no `config.json`.

## 4. Selecionar tipos de IED

Marque os tipos de IED que deseja processar.

As opcoes marcadas ficam salvas no `config.json`. Ao abrir o programa novamente,
a selecao anterior sera restaurada.

Se nenhuma preferencia estiver salva, o programa inicia sem tipo selecionado.
Selecione ao menos um tipo para liberar a previa do lote.

## 5. Selecionar etapa

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

## 6. Tipos de arquivo suportados

### DIGSI 5

O backup DIGSI 5 usa o arquivo `.dz5`.

### SEL

O backup SEL sempre usa o arquivo `.rdb` gerado pelo QuickSet.

Quando existir um arquivo Architect com o mesmo nome-base do `.rdb`, ele tambem
sera incluido no ZIP final:

```text
ESD-PDO.rdb      -> entra no ZIP
ESD-PDO.scd      -> entra no ZIP, se existir
ESD-PDO.selaprj  -> entra no ZIP, se existir
```

O programa tenta detectar automaticamente:

- versao QuickSet no `.rdb`;
- versao AcSELerator Architect no `.scd` ou `.selaprj`, quando existir.

Se a versao QuickSet nao for encontrada, um campo `Versão do software` aparece
na tela. Preencha a versao manualmente para liberar a previa e a geracao do
backup.

### Agrupamento por subestacao

Quando apenas um tipo de IED estiver selecionado, o programa gera backups
individuais daquele tipo.

Quando dois ou mais tipos estiverem selecionados, o programa avalia os arquivos
por subestacao/projeto. Assim, se a pasta tiver arquivos DIGSI e SEL da mesma
subestacao, e ambos os tipos estiverem marcados, eles entram no mesmo ZIP.

Se apenas um tipo for encontrado para uma subestacao, mesmo com varios tipos
marcados, o nome do backup continua sendo o nome individual daquele tipo. Nesse
caso, ele nao usa `IED-PACK`.

Exemplo:

```text
SE-GVM_20260619_1200.dz5
SE-GVM.rdb
SE-GVM.scd
```

Com `DIGSI 5` e `SEL` selecionados, o resultado sera um unico pacote:

```text
IED-PACK_SE-GVM_20260619-1230_JEAN-CARLOS-MACHADO_TAF.zip
```

Dentro do ZIP ficarao somente os arquivos dos tipos selecionados. Se `SEL` nao
estiver marcado, o `.rdb` e o `.scd` nao entram no pacote.

Se existir mais de um arquivo principal do mesmo tipo para a mesma subestacao,
o pacote usa somente o mais recente daquele tipo. Exemplo: dois `.dz5` da mesma
SE resultam em apenas o `.dz5` mais recente dentro do pacote.

Todo pacote `IED-PACK` inclui tambem o arquivo `IED-PACK-MANIFEST.txt`, que
lista:

- nome do backup;
- projeto/subestacao;
- data/hora usada no pacote;
- colaborador e etapa;
- versoes detectadas por tipo;
- arquivos incluidos no ZIP.

## 7. Padrao de nome dos arquivos de origem

Para os tipos suportados, o programa identifica o projeto/subestacao pelo nome
do arquivo. Pela politica atual, o projeto e sempre o primeiro bloco antes do
primeiro `_`.

Para DIGSI 5, o padrao recomendado e:

```text
SE-XXXXXX_OUTROS-TEXTOS_AAAAMMDD_HHMM.dz5
```

O programa considera como `Projeto` apenas `SE-XXXXXX`. Textos depois do
primeiro `_` sao ignorados para identificar o projeto, mas podem continuar no
nome do arquivo de origem para controle interno da equipe.

Exemplos:

```text
SE-GVM_20260529_1624.dz5           -> Projeto: SE-GVM
SE-CTU_DEV_01_20260619_0013.dz5    -> Projeto: SE-CTU
SE-ABC_REVISAO_FINAL_20260619_1015.dz5 -> Projeto: SE-ABC
ESD-PDO.rdb                        -> Projeto: ESD-PDO
```

Para SEL, o mesmo criterio do primeiro bloco antes do `_` e usado quando o nome
tem textos adicionais. Se o arquivo nao tiver `_`, o nome-base inteiro sera usado
como projeto.

Cuidados:

- Para DIGSI 5, mantenha o nome terminando com data e hora no formato
  `_AAAAMMDD_HHMM`.
- Textos adicionais devem ficar depois do primeiro `_` e antes da data/hora.
- Evite usar a data/hora no meio do nome se ela nao for o sufixo final.
- Mesmo quando houver textos intermediarios, o projeto sera sempre apenas o
  primeiro bloco antes do primeiro `_`.
- Nao coloque `_` dentro do nome da subestacao/projeto. Exemplo:
  `SE_CTU_20260619_0013.dz5` sera identificado como projeto `SE`, nao `SE_CTU`.
- Nao coloque textos antes da subestacao/projeto. Exemplo:
  `CLIENTE_SE-CTU_20260619_0013.dz5` sera identificado como projeto `CLIENTE`.
- Nao use nomes que comecem com etapa/revisao antes da subestacao. Exemplo:
  `DEV_SE-CTU_20260619_0013.dz5` sera identificado como projeto `DEV`.
- Confira sempre a coluna `Projeto` na previa antes de gerar backups.

## 8. Conferir a previa do lote

Depois de selecionar a etapa, a tela mostra uma previa dos arquivos suportados
encontrados na pasta.

Colunas principais:

- `Arquivo`: arquivo principal de origem (`.dz5` ou `.rdb`).
- `Projeto`: identificador do projeto.
- `Versao`: versao encontrada no arquivo ou conjunto de versoes do pacote.
- `Data/Hora`: data do arquivo usada no nome do backup.
- `Acao`: o que o programa pretende fazer.
- `Destino`: pasta ou arquivo de destino previsto.

Status possiveis:

- `Novo`: cria um novo backup em `ATU`.
- `Atualiza ATU`: move o backup atual para `HIS` e salva o novo em `ATU`.
- `Arquivar HIS`: salva o arquivo antigo em `HIS`, sem alterar `ATU`.
- `Corrigir ATU`: encontrou mais de um backup atual para o mesmo projeto.
- `Ignorado`: o arquivo e antigo e ja existe no historico.
- `Ja atual`: o arquivo ja corresponde ao backup atual em `ATU`.

## 9. Modo de processamento

A opcao `Processar apenas a partir do backup atual` evita reprocessar arquivos
antigos que vieram antes do backup atual ja existente em `ATU`.

Use essa opcao quando a pasta tiver muitos arquivos antigos e voce quiser
processar somente o backup atual e os arquivos mais novos.

## 10. Gerar backups

Clique em `Gerar backups`.

Antes de executar, o programa mostra uma confirmacao com a quantidade de
arquivos que serao processados.

Durante a execucao, uma barra de progresso mostra o arquivo atual. Aguarde a
conclusao antes de fechar o programa.

Ao final, sera exibido um resumo com:

- Total analisado.
- Novos backups criados.
- Atualizacoes em `ATU`.
- Historicos arquivados.
- Correcoes em `ATU`.
- Arquivos ignorados por serem antigos.
- Arquivos que ja estavam atuais.

## 11. Resultado dos arquivos

O nome final do backup segue o padrao:

```text
SOFTWARE_PROJETO_DATAHORA_COLABORADOR_ETAPA.zip
```

Exemplo:

```text
DIGSI-V100_SE-GVM_20260529-1625_JEAN-CARLOS-MACHADO_TAF.zip
SEL-QS7.5.3.10-AA2.4.2.34_ESD-PDO_20260623-0031_JEAN-CARLOS-MACHADO_TAF.zip
IED-PACK_SE-GVM_20260619-1230_JEAN-CARLOS-MACHADO_TAF.zip
```

Regras principais:

- `ATU` mantem apenas o backup mais recente de cada projeto.
- `HIS` mantem os backups anteriores.
- A comparacao tecnica considera `SOFTWARE_PROJETO_DATAHORA`.
- Mudancas apenas de colaborador ou etapa nao criam duplicidade tecnica.

## 12. Abrir pastas ATU e HIS

Use os botoes:

- `Abrir ATU`
- `Abrir HIS`

Eles abrem as pastas configuradas diretamente no Windows Explorer.

## 13. Cuidados recomendados

- Feche o DIGSI antes de gerar backups, para evitar arquivo bloqueado.
- Feche QuickSet/Architect antes de gerar backups SEL, para evitar arquivo
  bloqueado.
- Confira a previa antes de clicar em `Gerar backups`.
- Nao altere manualmente arquivos dentro de `ATU`, a menos que seja necessario.
- Se aparecer `Corrigir ATU`, leia o arquivo problematico informado antes de
  confirmar a correcao.
- Mantenha o `config.json` junto do executavel.

## 14. Atualizacao de versao

Quando receber uma nova versao do executavel:

1. Feche o programa.
2. Substitua o `.exe` antigo pelo novo.
3. Mantenha o mesmo `config.json`.
4. Abra o novo executavel.

O arquivo `config.json` nao precisa ser recriado a cada versao.
