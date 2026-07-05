# IED Backup Manager - Help

Este documento resume o uso operacional do IED Backup Manager. Ele usa apenas
exemplos genericos para que possa ser publicado junto do projeto.

## Objetivo

O IED Backup Manager padroniza backups de projetos de IED. Ele identifica os
arquivos de trabalho na pasta local, gera ZIPs com nomes consistentes, mantem o
backup atual em `ATU` e arquiva backups anteriores em `HIS`.

## Estrutura Recomendada

O executavel deve ficar dentro da pasta que contem os arquivos de trabalho da
subestacao, aplicacao, vao ou equipamento.

```text
Pasta local/
+-- Pasta da SE, ETD, vao ou equipamento/
    +-- IED Backup Manager.exe
    +-- config.json
    +-- SE-AAA_COMENTARIO-GENERICO_20260622_1350.dz5
    +-- ETD-BBB_OUTRO-COMENTARIO.rdb
    +-- ETD-BBB_OUTRO-COMENTARIO.scd
    +-- VAO-ZZZ_COMENTARIO-GENERICO_20260619_1230.pcmp
    +-- outros arquivos de trabalho
```

O programa processa a pasta onde o executavel esta localizado. As pastas `ATU`
e `HIS` podem ficar em outro local, desde que estejam configuradas.

## Regras de Nome

- O nome da SE, ETD, vao ou equipamento deve vir antes do primeiro sublinhado
  `"_"`.
- Use hifen `"-"` para separar textos dentro do nome da SE, ETD, vao ou
  equipamento.
- Todo texto depois do primeiro sublinhado `"_"` e tratado como comentario do
  usuario e nao entra na chave tecnica do backup.
- Confira sempre a coluna `Projeto` na previa do lote antes de gerar backups.

Exemplo:

```text
SE-AAA_COMENTARIO-GENERICO_20260622_1350.dz5 -> Projeto: SE-AAA
ETD-BBB_OUTRO-COMENTARIO.rdb                 -> Projeto: ETD-BBB
VAO-ZZZ_COMENTARIO-GENERICO_20260619_1230.pcmp -> Projeto: VAO-ZZZ
```

Evite nomes como:

```text
SE_AAA_20260622_1350.dz5
CLIENTE_SE-AAA_20260622_1350.dz5
DEV_SE-AAA_20260622_1350.dz5
```

Nesses casos, o projeto pode ser identificado incorretamente.

## Tipos Suportados

| Tipo | Extensoes | Versao usada no ZIP |
| --- | --- | --- |
| Siemens DIGSI | `.dz5` | Detectada no pacote, gerando `DIGSI4-Vx.xx` ou `DIGSI5-Vx.xx`. |
| SEL QuickSet / Architect | `.rdb`, com `.scd` ou `.selaprj` opcional | QuickSet e Architect quando encontrados. |
| ABB PCM600 | `.pcmp`, `.apcmp` | Detectada no arquivo interno `ProjectDataServer%versions.ini`. |
| INGETEAM INGESYS | `.efsPro`, `.ITPro2` | Informada manualmente pelo usuario e salva em `config.json`. |

## Fluxo Basico

1. Coloque o executavel na pasta dos arquivos de trabalho.
2. Abra o programa.
3. Configure colaborador, `ATU`, `HIS`, idioma e tipos de IED.
4. Selecione a etapa.
5. Confira a previa do lote.
6. Clique em `Gerar backups`.
7. Aguarde a conclusao ou use `Cancelar` se precisar interromper antes do
   proximo arquivo.

## Previa do Lote

A previa mostra:

- `Acao`: o que sera feito.
- `Arquivo`: arquivo principal identificado.
- `Projeto`: trecho usado como chave do projeto.
- `Versao`: software e versao detectados.
- `Data/Hora`: data usada no nome final.
- `Destino`: local previsto para o backup.

Se aparecer `Conflito SHA`, a execucao fica bloqueada porque existe um backup
com a mesma identidade tecnica, mas conteudo diferente. Verifique o arquivo
indicado antes de continuar.

## Saidas Esperadas

Backup DIGSI:

```text
Entrada:
SE-AAA_COMENTARIO-GENERICO_20260622_1350.dz5

Saida:
DIGSI5-V10.00_SE-AAA_20260622-1350_COLABORADOR-EXEMPLO_TAF.zip
```

Backup SEL:

```text
Entrada:
ETD-BBB_OUTRO-COMENTARIO.rdb
ETD-BBB_OUTRO-COMENTARIO.scd

Saida:
QUICKSET-V7.5.3.10-ARCHITECT-V2.4.2.34_ETD-BBB_20260612-0350_COLABORADOR-EXEMPLO_TAF.zip
```

Backup agrupado:

```text
Entrada:
ETD-BBB_COMENTARIO-GENERICO_20260612_0350.dz5
ETD-BBB_OUTRO-COMENTARIO.rdb

Saida:
IED-PACK_ETD-BBB_20260612-0350_COLABORADOR-EXEMPLO_TAF.zip
```

## Metadados no ZIP

Todos os ZIPs gerados incluem `IEDS-BACKUP-INFO.txt`.

Exemplo simplificado:

```text
IED Backup Manager - Backup Information

Backup: DIGSI5-V10.00_SE-AAA_20260622-1350_COLABORADOR-EXEMPLO_TAF.zip
Project: SE-AAA
Software: DIGSI5-V10.00
Timestamp: 20260622-1350
Collaborator: COLABORADOR-EXEMPLO
Stage: TAF

Included files:
- SE-AAA_COMENTARIO-GENERICO_20260622_1350.dz5
  Modified: 20260622-1350
  Size: 12345678 bytes
  SHA256: exemplo-de-hash-sha256
```

O SHA256 ajuda a identificar quando dois arquivos possuem a mesma identidade
tecnica, mas conteudo diferente.

## Limitacoes Conhecidas

- Arquivos muito grandes podem demorar para compactar e copiar.
- Pastas sincronizadas por OneDrive, SharePoint ou similares podem atrasar ou
  bloquear arquivos enquanto a sincronizacao esta em andamento.
- Arquivos abertos nos softwares de engenharia podem ficar bloqueados pelo
  Windows.
- O projeto sempre e identificado pelo texto antes do primeiro sublinhado
  `"_"`; nomes fora da politica precisam ser corrigidos antes do backup.
- ZIPs antigos sem `IEDS-BACKUP-INFO.txt` continuam compativeis, mas nao
  possuem dados de SHA256 para comparacao.

## Solucao de Problemas

### O programa demora para abrir

No executavel `.exe`, o Windows pode levar alguns segundos para extrair e
preparar a aplicacao. O splash screen indica que o carregamento esta em
andamento.

### O programa nao abre em pasta sincronizada

Teste copiar o executavel para uma pasta local nao sincronizada. Se abrir
normalmente, a causa provavel e bloqueio, sincronizacao pendente ou permissao da
pasta sincronizada.

### O backup falha por arquivo bloqueado

Feche DIGSI, QuickSet, Architect, PCM600 ou INGESYS antes de gerar backups.
Depois atualize a previa e tente novamente.

### O projeto foi identificado errado

Confira a coluna `Projeto`. Se estiver incorreta, renomeie o arquivo para que o
nome da SE, ETD, vao ou equipamento fique antes do primeiro sublinhado `"_"`.

### Apareceu Conflito SHA

Existe um backup com a mesma identidade tecnica, mas conteudo diferente.
Compare os arquivos indicados, confirme qual e o correto e ajuste manualmente
`ATU`/`HIS` antes de tentar novamente.

## Privacidade

Nao publique arquivos reais de backup, `config.json` local, caminhos internos de
empresa ou nomes reais de colaboradores em repositorios publicos. Para exemplos,
use nomes genericos como `SE-AAA`, `ETD-BBB`, `VAO-ZZZ` e
`COLABORADOR-EXEMPLO`.

## Licenca

Copyright (c) 2026 Jean Carlos Machado.

O IED Backup Manager e disponibilizado para uso gratuito e nao comercial,
conforme a licenca do projeto:

```text
https://github.com/machado-jean/ied-backup-tool
```
