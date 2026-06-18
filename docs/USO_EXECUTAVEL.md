# IED Backup Manager - Uso do Executavel

Este guia explica como usar o `IED Backup Manager v1.0.2.exe` para gerar backups
padronizados de projetos de IED. Nesta versao, o tipo disponivel e DIGSI 5
(`.dz5`).

## 1. Estrutura esperada

O executavel deve ficar na pasta do projeto que sera processada. Essa mesma
pasta deve conter os arquivos de projeto suportados.

Exemplo:

```text
Pasta do projeto/
├─ IED Backup Manager v1.0.0.exe
├─ config.json
├─ SE-GVM_20260529_1624.dz5
├─ SE-GVM_20260529_1625.dz5
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
  "language": "pt_BR"
}
```

## 3. Selecionar idioma

Use o botao de bandeira no canto superior para alternar entre portugues e
ingles.

A preferencia fica salva no `config.json`.

## 4. Selecionar etapa

Antes de gerar backups, selecione a etapa da entrega.

Etapas disponiveis:

- `DEV`
- `PRE-TAF`
- `TAF`
- `POS-TAF`
- `PRE-TAC`
- `TAC`
- `POS-TAC`
- `PRODUCAO`
- `CUSTOM`

A etapa entra no nome do backup gerado. Ela nao bloqueia retornos de etapa. Por
exemplo, se um projeto ja passou por `TAC` e depois precisar voltar para `DEV`,
o backup podera ser gerado normalmente.

## 5. Conferir a previa do lote

Depois de selecionar a etapa, a tela mostra uma previa dos arquivos suportados
encontrados na pasta.

Colunas principais:

- `Arquivo`: arquivo `.dz5` de origem.
- `Projeto`: identificador do projeto.
- `Versao`: versao DIGSI encontrada no arquivo.
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

## 6. Modo de processamento

A opcao `Processar apenas a partir do backup atual` evita reprocessar arquivos
antigos que vieram antes do backup atual ja existente em `ATU`.

Use essa opcao quando a pasta tiver muitos arquivos antigos e voce quiser
processar somente o backup atual e os arquivos mais novos.

## 7. Gerar backups

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

## 8. Resultado dos arquivos

O nome final do backup segue o padrao:

```text
SOFTWARE_PROJETO_DATAHORA_COLABORADOR_ETAPA.zip
```

Exemplo:

```text
DIGSI-V100_SE-GVM_20260529-1625_JEAN-CARLOS-MACHADO_TAF.zip
```

Regras principais:

- `ATU` mantem apenas o backup mais recente de cada projeto.
- `HIS` mantem os backups anteriores.
- A comparacao tecnica considera `SOFTWARE_PROJETO_DATAHORA`.
- Mudancas apenas de colaborador ou etapa nao criam duplicidade tecnica.

## 9. Abrir pastas ATU e HIS

Use os botoes:

- `Abrir ATU`
- `Abrir HIS`

Eles abrem as pastas configuradas diretamente no Windows Explorer.

## 10. Cuidados recomendados

- Feche o DIGSI antes de gerar backups, para evitar arquivo bloqueado.
- Confira a previa antes de clicar em `Gerar backups`.
- Nao altere manualmente arquivos dentro de `ATU`, a menos que seja necessario.
- Se aparecer `Corrigir ATU`, leia o arquivo problematico informado antes de
  confirmar a correcao.
- Mantenha o `config.json` junto do executavel.

## 11. Atualizacao de versao

Quando receber uma nova versao do executavel:

1. Feche o programa.
2. Substitua o `.exe` antigo pelo novo.
3. Mantenha o mesmo `config.json`.
4. Abra o novo executavel.

O arquivo `config.json` nao precisa ser recriado a cada versao.
