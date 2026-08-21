# Lógica de Identificação dos Tipos de IED

[Português](LOGICA_IDENTIFICACAO_IEDS.md) | [English](IED_IDENTIFICATION_LOGIC.en.md)

Este documento explica como o IED Backup Manager identifica cada tipo de backup,
como escolhe os arquivos incluídos no ZIP e como determina a versão usada no nome
do backup.

O objetivo é deixar claro quais regras são automáticas, quais dependem de
entrada manual do usuário e quais casos exigem cuidado especial.

## Regra Geral do Projeto

Para a maioria dos tipos de IED, o projeto, SE, ETD, vao ou equipamento e
identificado pelo texto antes do primeiro sublinhado `"_"` no nome do arquivo.

Exemplo:

```text
SE-AAA_COMENTARIO-GENERICO_20260712_1030.dz5 -> Projeto: SE-AAA
ETD-BBB_OUTRO-COMENTARIO.rdb                 -> Projeto: ETD-BBB
```

Todo texto depois do primeiro sublinhado `"_"` é tratado como comentário do
usuário e não entra na chave técnica do backup.

## Siemens DIGSI

Arquivos considerados:

```text
.dz5
```

Regra:

- o arquivo principal é o `.dz5`;
- o projeto é identificado pelo texto antes do primeiro sublinhado `"_"`;
- cada `.dz5` e processado como um backup individual;
- a versão é detectada automaticamente por marcadores internos como `.dp4v###`
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
Versão manual: não
Arquivos adicionais: não
```

## SEL QuickSet / Architect

Arquivos considerados:

```text
.rdb
.scd
.selaprj
```

Regra:

- o arquivo principal é o `.rdb`;
- o projeto é identificado pelo texto antes do primeiro sublinhado `"_"`;
- arquivos `.scd` ou `.selaprj` com o mesmo nome-base entram como acompanhantes;
- a versão do QuickSet é lida no `.rdb`;
- a versão do Architect é lida no `.scd` ou `.selaprj`, quando existir.

Exemplo:

```text
QUICKSET-V7.5.3.10-ARCHITECT-V2.4.2.34_SE-AAA_YYYYMMDD-HHMM_COLABORADOR_ETAPA.zip
```

Se o arquivo SEL for muito antigo e não contiver a versão do QuickSet, o
aplicativo pode solicitar uma versão manual.

Resumo:

```text
Automatica: normalmente sim
Versão manual: somente quando a versão do QuickSet não for encontrada
Arquivos adicionais: .scd ou .selaprj com mesmo nome-base
```

## ABB PCM600

Arquivos considerados:

```text
.pcmp
.apcmp
```

Regra:

- o arquivo principal é o pacote `.pcmp` ou `.apcmp`;
- o projeto é identificado pelo texto antes do primeiro sublinhado `"_"`;
- o pacote é inspecionado como arquivo compactado;
- a versão é lida em `ProjectDataServer%versions.ini`, no campo
  `ProductVersion`.

Exemplo:

```text
ProductName=PCM600_210
ProductVersion=2.10

Saída: PCM600-V2.10
```

Resumo:

```text
Automatica: sim
Versão manual: não
Arquivos adicionais: não
```

## INGETEAM INGESYS

Arquivos considerados:

```text
.efsPro
.ITPro2
```

Regra:

- o arquivo principal é o `.efsPro` ou `.ITPro2`;
- o projeto é identificado pelo texto antes do primeiro sublinhado `"_"`;
- a versão não é determinada automaticamente;
- o usuário informa a versão do software INGETEAM/INGESYS em uso;
- a versão informada é salva no `config.json`.

Motivo da regra manual:

Nos testes analisados, os arquivos INGETEAM podem conter identificadores,
componentes ou estruturas importadas de versões mais novas mesmo quando o projeto
foi trabalhado em uma versão mais antiga do software. Isso torna arriscado usar
apenas os marcadores internos para definir a versão do backup.

Por esse motivo, a regra mais segura e operacionalmente clara é exigir que o
usuário informe a versão em uso no momento do backup.

Exemplo:

```text
Versão informada pelo usuário: 5.5.4
Saída: INGESYS-V5.5.4
```

Resumo:

```text
Automatica: não
Versão manual: sim
Arquivos adicionais: não
```

## GE Multilin / EnerVista UR

Este é um caso especial. Ao contrário dos outros tipos, o backup GE não é
representado por um único arquivo na raiz da pasta. Ele representa um ambiente
da SE/aplicação contendo várias subpastas de IED.

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

Regra de identificação:

- o projeto é o nome da pasta da SE/aplicação;
- uma subpasta é considerada IED GE quando contém pelo menos um arquivo `.urs`
  ou `.urk`;
- o `.ENV` do topo da pasta é incluído quando existir, mas não é obrigatório;
- o `.ENV` sozinho não caracteriza um backup GE válido.

Arquivos incluídos:

```text
.ENV do topo, se existir
.urs
.urk
.cid
.icd
```

Arquivos não incluídos automaticamente:

```text
.cfg
.xml
.rt430
.msf
arquivos sem extensão
pastas sem .urs ou .urk
```

Isso evita incluir configurações de RDP, switches, GPS ou outros equipamentos
que podem estar na mesma pasta de trabalho, mas não fazem parte do backup GE UR.

Regra de versão:

1. O aplicativo procura versões de IED/aplicação nos headers `.urs/.urk`.
2. Também procura a versão do software `UR Setup` nos arquivos `.cid/.icd`,
   quando existirem.
3. A maior versão encontrada entre essas fontes é usada no nome do ZIP.
4. As versões por IED continuam registradas no `IEDS-BACKUP-INFO.txt`.

Método de extração:

- o programa lê a primeira linha dos arquivos `.urs` e `.urk`;
- quando a linha segue o formato `HEADER,GEMULTILIN,...` ou
  `HEADER,GEVERNOVA,...`, o quinto campo é tratado como versão de
  IED/aplicação;
- valores numéricos de três dígitos são normalizados para versão pontuada:
  `780` vira `7.80`, `870` vira `8.70`;
- em `.cid/.icd`, cabeçalhos como `Created by GE Digital Energy UR Setup 8.61`
  ou `Created by Multilin UR Setup 8.71` também entram na comparação;
- quando houver vários IEDs ou versões de software na mesma pasta de ambiente,
  o maior valor encontrado é usado no nome do ZIP.

Exemplo com SCL:

```text
HEADER,GEVERNOVA,5,T60-UEM,870,...
Created by Multilin UR Setup 8.71

Saída: GE-MULTILIN-V8.71
```

Exemplo somente com `.urs`:

```text
HEADER,GEMULTILIN,5,C60-UE3,840,...

Saída: GE-MULTILIN-V8.40
```

Metadados especiais:

No `IEDS-BACKUP-INFO.txt`, o GE inclui uma seção adicional com:

- pasta do ambiente;
- arquivo `.ENV`, quando existir;
- `Environment Version` e `Application Version`, quando existirem no `.ENV`;
- pastas de IED incluídas;
- versão `GE UR Setup` usada no desenvolvimento, quando encontrada;
- versão de aplicação do IED encontrada nos `.urs/.urk`.

Resumo:

```text
Automatica: sim
Versão manual: não, salvo se surgirem arquivos antigos sem marcadores suficientes
Arquivos adicionais: .ENV opcional e subpastas GE com .urs/.urk/.cid/.icd
```

## IED-PACK

Quando mais de um tipo de IED está selecionado e mais de um tipo real é
encontrado para o mesmo projeto, o aplicativo cria um `IED-PACK`.

Regra:

- se apenas um tipo real for encontrado, o backup usa o nome desse tipo;
- se dois ou mais tipos reais forem encontrados para o mesmo projeto, o backup
  usa `IED-PACK`;
- dentro do ZIP, o arquivo `IEDS-BACKUP-INFO.txt` registra as versões detectadas
  de cada tipo incluído.

Exemplo:

```text
IED-PACK_SE-AAA_YYYYMMDD-HHMM_COLABORADOR_ETAPA.zip
```

## Quando Atualizar Esta Lógica

Este documento deve ser atualizado sempre que:

- um novo fabricante/software for adicionado;
- uma nova extensão for suportada;
- a regra de versão mudar;
- um tipo passar a exigir versão manual;
- arquivos adicionais passarem a entrar ou sair do ZIP;
- forem descobertos casos reais que mudem a interpretação de um formato.
