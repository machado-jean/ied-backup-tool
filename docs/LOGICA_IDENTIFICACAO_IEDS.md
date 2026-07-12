# Logica de Identificacao dos Tipos de IED

Este documento explica como o IED Backup Manager identifica cada tipo de backup,
como escolhe os arquivos incluidos no ZIP e como determina a versao usada no nome
do backup.

O objetivo e deixar claro quais regras sao automaticas, quais dependem de
entrada manual do usuario e quais casos exigem cuidado especial.

## Regra Geral do Projeto

Para a maioria dos tipos de IED, o projeto, SE, ETD, vao ou equipamento e
identificado pelo texto antes do primeiro sublinhado `"_"` no nome do arquivo.

Exemplo:

```text
SE-AAA_COMENTARIO-GENERICO_20260712_1030.dz5 -> Projeto: SE-AAA
ETD-BBB_OUTRO-COMENTARIO.rdb                 -> Projeto: ETD-BBB
```

Todo texto depois do primeiro sublinhado `"_"` e tratado como comentario do
usuario e nao entra na chave tecnica do backup.

## Siemens DIGSI

Arquivos considerados:

```text
.dz5
```

Regra:

- o arquivo principal e o `.dz5`;
- o projeto e identificado pelo texto antes do primeiro sublinhado `"_"`;
- cada `.dz5` e processado como um backup individual;
- a versao e detectada automaticamente por marcadores internos como `.dp4v###`
  ou `.dp5v###`.

Exemplos:

```text
dp5v100 -> DIGSI5-V10.00
dp5v98  -> DIGSI5-V9.80
dp5v75  -> DIGSI5-V7.50
```

Resumo:

```text
Automatica: sim
Versao manual: nao
Arquivos adicionais: nao
```

## SEL QuickSet / Architect

Arquivos considerados:

```text
.rdb
.scd
.selaprj
```

Regra:

- o arquivo principal e o `.rdb`;
- o projeto e identificado pelo texto antes do primeiro sublinhado `"_"`;
- arquivos `.scd` ou `.selaprj` com o mesmo nome-base entram como acompanhantes;
- a versao do QuickSet e lida no `.rdb`;
- a versao do Architect e lida no `.scd` ou `.selaprj`, quando existir.

Exemplo:

```text
QUICKSET-V7.5.3.10-ARCHITECT-V2.4.2.34_SE-AAA_YYYYMMDD-HHMM_COLABORADOR_ETAPA.zip
```

Se o arquivo SEL for muito antigo e nao contiver a versao do QuickSet, o
aplicativo pode solicitar uma versao manual.

Resumo:

```text
Automatica: normalmente sim
Versao manual: somente quando a versao do QuickSet nao for encontrada
Arquivos adicionais: .scd ou .selaprj com mesmo nome-base
```

## ABB PCM600

Arquivos considerados:

```text
.pcmp
.apcmp
```

Regra:

- o arquivo principal e o pacote `.pcmp` ou `.apcmp`;
- o projeto e identificado pelo texto antes do primeiro sublinhado `"_"`;
- o pacote e inspecionado como arquivo compactado;
- a versao e lida em `ProjectDataServer%versions.ini`, no campo
  `ProductVersion`.

Exemplo:

```text
ProductName=PCM600_210
ProductVersion=2.10

Saida: PCM600-V2.10
```

Resumo:

```text
Automatica: sim
Versao manual: nao
Arquivos adicionais: nao
```

## INGETEAM INGESYS

Arquivos considerados:

```text
.efsPro
.ITPro2
```

Regra:

- o arquivo principal e o `.efsPro` ou `.ITPro2`;
- o projeto e identificado pelo texto antes do primeiro sublinhado `"_"`;
- a versao nao e determinada automaticamente;
- o usuario informa a versao do software INGETEAM/INGESYS em uso;
- a versao informada e salva no `config.json`.

Motivo da regra manual:

Nos testes analisados, os arquivos INGETEAM podem conter identificadores,
componentes ou estruturas importadas de versoes mais novas mesmo quando o projeto
foi trabalhado em uma versao mais antiga do software. Isso torna arriscado usar
apenas os marcadores internos para definir a versao do backup.

Por esse motivo, a regra mais segura e operacionalmente clara e exigir que o
usuario informe a versao em uso no momento do backup.

Exemplo:

```text
Versao informada pelo usuario: 5.5.4
Saida: INGESYS-V5.5.4
```

Resumo:

```text
Automatica: nao
Versao manual: sim
Arquivos adicionais: nao
```

## GE Multilin / EnerVista UR

Este e um caso especial. Ao contrario dos outros tipos, o backup GE nao e
representado por um unico arquivo na raiz da pasta. Ele representa um ambiente
da SE/aplicacao contendo varias subpastas de IED.

Estrutura esperada:

```text
SE-AAA/
+-- SE-AAA - Enervista UR Environment.ENV
+-- GE-IED-A/
|   +-- GE-IED-A.urs
|   +-- GE-IED-A.cid
|   +-- GE-IED-A.icd
+-- GE-IED-B/
|   +-- GE-IED-B.urk
+-- RDPC-EXEMPLO/
|   +-- RDPC-EXEMPLO.cfg
+-- SW-EXEMPLO
```

Regra de identificacao:

- o projeto e o nome da pasta da SE/aplicacao;
- uma subpasta e considerada IED GE quando contem pelo menos um arquivo `.urs`
  ou `.urk`;
- o `.ENV` do topo da pasta e incluido quando existir, mas nao e obrigatorio;
- o `.ENV` sozinho nao caracteriza um backup GE valido.

Arquivos incluidos:

```text
.ENV do topo, se existir
.urs
.urk
.cid
.icd
```

Arquivos nao incluidos automaticamente:

```text
.cfg
.xml
.rt430
.msf
arquivos sem extensao
pastas sem .urs ou .urk
```

Isso evita incluir configuracoes de RDP, switches, GPS ou outros equipamentos
que podem estar na mesma pasta de trabalho, mas nao fazem parte do backup GE UR.

Regra de versao:

1. O aplicativo procura a maior versao `GE Digital Energy UR Setup` encontrada
   nos arquivos `.cid` e `.icd`.
2. Se encontrar, usa essa versao no nome do ZIP.
3. Se nao houver `.cid/.icd` com versao de UR Setup, usa a maior versao
   `GEMULTILIN` encontrada nos headers `.urs/.urk`.

Exemplo com SCL:

```text
Created by GE Digital Energy UR Setup 8.61

Saida: GE-URSETUP-V8.61
```

Exemplo somente com `.urs`:

```text
HEADER,GEMULTILIN,5,C60-UE3,840,...

Saida: GE-MULTILIN-V8.40
```

Metadados especiais:

No `IEDS-BACKUP-INFO.txt`, o GE inclui uma secao adicional com:

- pasta do ambiente;
- arquivo `.ENV`, quando existir;
- `Environment Version` e `Application Version`, quando existirem no `.ENV`;
- pastas de IED incluidas;
- versao `GE UR Setup` usada no desenvolvimento, quando encontrada;
- versao de aplicacao do IED encontrada nos `.urs/.urk`.

Resumo:

```text
Automatica: sim
Versao manual: nao, salvo se surgirem arquivos antigos sem marcadores suficientes
Arquivos adicionais: .ENV opcional e subpastas GE com .urs/.urk/.cid/.icd
```

## IED-PACK

Quando mais de um tipo de IED esta selecionado e mais de um tipo real e
encontrado para o mesmo projeto, o aplicativo cria um `IED-PACK`.

Regra:

- se apenas um tipo real for encontrado, o backup usa o nome desse tipo;
- se dois ou mais tipos reais forem encontrados para o mesmo projeto, o backup
  usa `IED-PACK`;
- dentro do ZIP, o arquivo `IEDS-BACKUP-INFO.txt` registra as versoes detectadas
  de cada tipo incluido.

Exemplo:

```text
IED-PACK_SE-AAA_YYYYMMDD-HHMM_COLABORADOR_ETAPA.zip
```

## Quando Atualizar Esta Logica

Este documento deve ser atualizado sempre que:

- um novo fabricante/software for adicionado;
- uma nova extensao for suportada;
- a regra de versao mudar;
- um tipo passar a exigir versao manual;
- arquivos adicionais passarem a entrar ou sair do ZIP;
- forem descobertos casos reais que mudem a interpretacao de um formato.
