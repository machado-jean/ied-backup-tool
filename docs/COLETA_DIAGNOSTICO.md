# Coleta de diagnóstico

[Português](COLETA_DIAGNOSTICO.md) | [English](DIAGNOSTIC_COLLECTION.en.md)

Os arquivos `scripts/COLETAR_DIAGNOSTICO.cmd` e
`scripts/Collect-Diagnostics.ps1` reproduzem a abertura do IED Backup Manager em
um ambiente isolado, aguardam a verificação de atualização e criam um ZIP que o
usuário envia diretamente ao responsável pelo programa.

Use sempre o `.cmd` e o `.ps1` fornecidos juntos. A versão `1.1.0` verifica a
compatibilidade entre os dois arquivos, apresenta um resumo `OK/FALHA`, detecta
problemas de DNS, HTTPS e certificados e registra tela, DPI, tema, alto
contraste e suavização de fontes sem coletar conteúdo operacional.

Ele não exige acesso de administrador e não coleta `config.json`, projetos de
engenharia, backups `ATU`/`HIS`, credenciais, dumps ou eventos do Windows.

## Uso simples

1. Coloque `COLETAR_DIAGNOSTICO.cmd` e `Collect-Diagnostics.ps1` na mesma pasta
   do `IED_Backup_Manager.exe`.
2. Clique duas vezes em `COLETAR_DIAGNOSTICO.cmd`.
3. Aguarde aproximadamente 10 segundos.
4. Localize na Área de Trabalho o ZIP iniciado por
   `IED-Backup-Manager-Diagnostics-`.
5. Envie o ZIP ao responsável pelo IED Backup Manager.

O usuário não precisa de Git, GitHub, Python ou acesso de administrador.

Também é possível arrastar o `IED_Backup_Manager.exe` sobre o arquivo `.cmd`.

## Uso pelo PowerShell

Abra o PowerShell e informe o executável que apresentou o problema:

```powershell
Set-Location "C:\caminho\para\ied-backup-tool"

.\scripts\Collect-Diagnostics.ps1 `
    -ExecutablePath "C:\caminho\para\IED_Backup_Manager.exe"
```

Se a política local impedir a execução direta do script:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
    -File ".\scripts\Collect-Diagnostics.ps1" `
    -ExecutablePath "C:\caminho\para\IED_Backup_Manager.exe"
```

Por padrão, o aplicativo permanece aberto por 10 segundos. O script tenta
fechar as janelas normalmente, sem finalizar o processo à força. Para manter a
aplicação aberta após a coleta, use `-KeepApplicationOpen`.

O ZIP é criado por padrão na Área de Trabalho com nome semelhante a:

```text
IED-Backup-Manager-Diagnostics-AAAAMMDD-HHMMSS-xxxxxxxx.zip
```

## Conteúdo do ZIP

- conclusão da verificação de atualização;
- versão, tamanho e SHA256 do executável;
- versão do Windows, PowerShell, idioma, fuso e escala disponível;
- resultado de DNS, conexão TCP 443 e consulta à API pública do GitHub;
- indicação da presença de proxy, sem copiar endereço, usuário ou senha;
- logs produzidos pela execução isolada;

Caminhos, usuário e nome do computador são substituídos por marcadores. Mesmo
assim, o responsável deve revisar os arquivos antes de usá-los em uma issue
pública.

## Limitações

- O diagnóstico comprova conectividade no momento da coleta, não em uma
  execução passada.
- Antivírus, proxy ou política corporativa podem bloquear tanto o aplicativo
  quanto o próprio teste.
- O print da janela inteira não é capturado automaticamente. Se solicitado,
  deve ser enviado separadamente após remoção de dados sensíveis.
