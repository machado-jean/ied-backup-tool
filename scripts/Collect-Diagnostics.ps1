param(
    [Parameter(Mandatory = $true)]
    [string]$ExecutablePath,

    [ValidateRange(5, 120)]
    [int]$WaitSeconds = 10,

    [string]$OutputDirectory = [Environment]::GetFolderPath("Desktop"),

    [string]$LauncherVersion = "",

    [switch]$KeepApplicationOpen
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$ApiUrl = "https://api.github.com/repos/machado-jean/ied-backup-tool/releases/latest"
$CollectorVersion = "1.1.0"
$CompatibleLauncherVersion = "1.1.0"
$StartedAt = Get-Date
$RunId = "{0}-{1}" -f $StartedAt.ToString("yyyyMMdd-HHmmss"), ([guid]::NewGuid().ToString("N").Substring(0, 8))
$Executable = (Resolve-Path -LiteralPath $ExecutablePath).Path
$OutputDirectory = if ([string]::IsNullOrWhiteSpace($OutputDirectory)) {
    (Get-Location).Path
}
else {
    $OutputDirectory
}
$Output = [IO.Path]::GetFullPath($OutputDirectory)
$TemporaryRoot = Join-Path ([IO.Path]::GetTempPath()) "IED-Backup-Manager-Diagnostics-$RunId"
$ProjectDirectory = Join-Path $TemporaryRoot "project"
$IsolatedLocalAppData = Join-Path $TemporaryRoot "localappdata"
$PackageDirectory = Join-Path $TemporaryRoot "package"
$ZipPath = Join-Path $Output "IED-Backup-Manager-Diagnostics-$RunId.zip"
$Process = $null
$ProcessClosed = $false
$ApplicationExitCode = $null
$ExecutableProcessName = [IO.Path]::GetFileNameWithoutExtension($Executable)

function ConvertTo-SanitizedText {
    param([AllowEmptyString()][string]$Text)

    if ([string]::IsNullOrEmpty($Text)) {
        return $Text
    }

    $Sanitized = $Text
    $Replacements = [ordered]@{
        $TemporaryRoot = "<DIAGNOSTIC_WORKDIR>"
        $Executable = "<EXECUTABLE_PATH>"
        $env:USERPROFILE = "%USERPROFILE%"
        $env:USERNAME = "<USER>"
        $env:COMPUTERNAME = "<COMPUTER>"
    }
    foreach ($Entry in $Replacements.GetEnumerator()) {
        if (-not [string]::IsNullOrWhiteSpace([string]$Entry.Key)) {
            $Sanitized = $Sanitized -replace [regex]::Escape([string]$Entry.Key), [string]$Entry.Value
        }
    }
    return $Sanitized
}

function Write-Utf8File {
    param(
        [string]$Path,
        [AllowEmptyString()][string]$Content
    )

    # Windows PowerShell 5.1 writes a BOM with `-Encoding utf8`. Use the .NET
    # encoder explicitly so diagnostic JSON is portable across Windows versions.
    $Utf8WithoutBom = [Text.UTF8Encoding]::new($false)
    [IO.File]::WriteAllText($Path, $Content, $Utf8WithoutBom)
}

function Get-TcpCheck {
    param(
        [string]$HostName,
        [int]$Port,
        [int]$TimeoutMilliseconds = 5000
    )

    $Client = [Net.Sockets.TcpClient]::new()
    try {
        $Pending = $Client.BeginConnect($HostName, $Port, $null, $null)
        if (-not $Pending.AsyncWaitHandle.WaitOne($TimeoutMilliseconds)) {
            return [pscustomobject]@{ Success = $false; Detail = "Timeout" }
        }
        $Client.EndConnect($Pending)
        return [pscustomobject]@{ Success = $true; Detail = "Connected" }
    }
    catch {
        return [pscustomobject]@{
            Success = $false
            Detail = ConvertTo-SanitizedText $_.Exception.Message
        }
    }
    finally {
        $Client.Dispose()
    }
}

function Get-UpdateCheckConclusion {
    param([string]$LogText)

    $Finished = [regex]::Matches(
        $LogText,
        'Update check finished: current=(?<Current>[^,]+), latest=(?<Latest>[^,]+), available=(?<Available>\S+)'
    )
    if ($Finished.Count -gt 0) {
        $Last = $Finished[$Finished.Count - 1]
        return [pscustomobject]@{
            Status = "Completed"
            Detail = "current=$($Last.Groups['Current'].Value); latest=$($Last.Groups['Latest'].Value); available=$($Last.Groups['Available'].Value)"
            Current = $Last.Groups["Current"].Value
            Latest = $Last.Groups["Latest"].Value
            Available = $Last.Groups["Available"].Value -eq "True"
        }
    }

    $Failed = [regex]::Matches($LogText, 'Update check failed silently: (?<Error>.+)')
    if ($Failed.Count -gt 0) {
        return [pscustomobject]@{
            Status = "Failed"
            Detail = $Failed[$Failed.Count - 1].Groups["Error"].Value.Trim()
            Current = ""
            Latest = ""
            Available = $null
        }
    }

    if ($LogText -match 'Starting update check') {
        return [pscustomobject]@{
            Status = "StartedWithoutResult"
            Detail = "The update check started but no completion or failure line was logged."
            Current = ""
            Latest = ""
            Available = $null
        }
    }

    return [pscustomobject]@{
        Status = "NotStarted"
        Detail = "No update-check line was found in the isolated application log."
        Current = ""
        Latest = ""
        Available = $null
    }
}

function Get-LogDurationMilliseconds {
    param(
        [string]$LogText,
        [string]$StartPattern,
        [string]$EndPattern
    )

    $StartMatch = [regex]::Match($LogText, "(?m)^(?<Time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*$StartPattern")
    $EndMatch = [regex]::Match($LogText, "(?m)^(?<Time>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}).*$EndPattern")
    if (-not $StartMatch.Success -or -not $EndMatch.Success) {
        return $null
    }
    $Format = "yyyy-MM-dd HH:mm:ss,fff"
    $StartTime = [datetime]::ParseExact($StartMatch.Groups["Time"].Value, $Format, $null)
    $EndTime = [datetime]::ParseExact($EndMatch.Groups["Time"].Value, $Format, $null)
    return [int][math]::Max(0, ($EndTime - $StartTime).TotalMilliseconds)
}

function Get-LaunchedApplicationProcesses {
    $Candidates = @(Get-Process -Name $ExecutableProcessName -ErrorAction SilentlyContinue)
    return @(
        $Candidates | Where-Object {
            try {
                $_.Path -eq $Executable -and $_.StartTime -ge $StartedAt.AddSeconds(-2)
            }
            catch {
                $false
            }
        }
    )
}

if (-not (Test-Path -LiteralPath $Executable -PathType Leaf)) {
    throw "Executavel nao encontrado: $ExecutablePath"
}
if ([IO.Path]::GetExtension($Executable) -ne ".exe") {
    throw "O arquivo informado deve possuir extensao .exe."
}
if (
    -not [string]::IsNullOrWhiteSpace($LauncherVersion) -and
    $LauncherVersion -ne $CompatibleLauncherVersion
) {
    throw "Arquivos do coletor incompativeis. Use o CMD e o PS1 do mesmo pacote."
}

New-Item -ItemType Directory -Force -Path $Output | Out-Null
New-Item -ItemType Directory -Force -Path $ProjectDirectory | Out-Null
New-Item -ItemType Directory -Force -Path $IsolatedLocalAppData | Out-Null
New-Item -ItemType Directory -Force -Path $PackageDirectory | Out-Null
$DiagnosticAtu = Join-Path $TemporaryRoot "ATU"
$DiagnosticHis = Join-Path $TemporaryRoot "HIS"
New-Item -ItemType Directory -Force -Path $DiagnosticAtu | Out-Null
New-Item -ItemType Directory -Force -Path $DiagnosticHis | Out-Null
$DiagnosticConfig = [ordered]@{
    nome = "DIAGNOSTICO"
    sobrenome = "SUPORTE"
    colaborador = "DIAGNOSTICO SUPORTE"
    atu_path = $DiagnosticAtu
    his_path = $DiagnosticHis
    language = "pt_BR"
    project_types = @()
    software_versions = @{}
    show_startup_instructions = $false
    history_cleanup = @{ retention_days = 30 }
}
Write-Utf8File `
    -Path (Join-Path $ProjectDirectory "config.json") `
    -Content ($DiagnosticConfig | ConvertTo-Json -Depth 5)

try {
    $ExecutableItem = Get-Item -LiteralPath $Executable
    $ExecutableHash = (Get-FileHash -LiteralPath $Executable -Algorithm SHA256).Hash

    Write-Host "Abrindo o IED Backup Manager em ambiente isolado..." -ForegroundColor Cyan
    $PreviousLocalAppData = $env:LOCALAPPDATA
    try {
        $env:LOCALAPPDATA = $IsolatedLocalAppData
        $Arguments = @("--project-dir", ('"{0}"' -f $ProjectDirectory))
        $Process = Start-Process `
            -FilePath $Executable `
            -ArgumentList $Arguments `
            -WorkingDirectory $ProjectDirectory `
            -PassThru
    }
    finally {
        $env:LOCALAPPDATA = $PreviousLocalAppData
    }

    Write-Host "Aguardando $WaitSeconds segundos para a verificacao de atualizacao..." -ForegroundColor Cyan
    Start-Sleep -Seconds $WaitSeconds

    if (-not $KeepApplicationOpen) {
        foreach ($Attempt in 1..10) {
            $RunningApplicationProcesses = @(Get-LaunchedApplicationProcesses)
            if ($RunningApplicationProcesses.Count -eq 0) {
                break
            }
            foreach ($RunningProcess in $RunningApplicationProcesses) {
                [void]$RunningProcess.CloseMainWindow()
            }
            Start-Sleep -Seconds 1
        }
    }

    $ProcessClosed = @(Get-LaunchedApplicationProcesses).Count -eq 0
    $Process.Refresh()
    if ($Process.HasExited) {
        $ApplicationExitCode = $Process.ExitCode
    }

    $LogDirectory = Join-Path $IsolatedLocalAppData "IED Backup Manager\logs"
    $CombinedLog = [Text.StringBuilder]::new()
    if (Test-Path -LiteralPath $LogDirectory -PathType Container) {
        $CollectedLogDirectory = Join-Path $PackageDirectory "logs"
        New-Item -ItemType Directory -Path $CollectedLogDirectory | Out-Null
        foreach ($LogFile in Get-ChildItem -LiteralPath $LogDirectory -File -Filter "*.log") {
            $Text = Get-Content -LiteralPath $LogFile.FullName -Raw
            $Sanitized = ConvertTo-SanitizedText $Text
            [void]$CombinedLog.AppendLine($Sanitized)
            Write-Utf8File -Path (Join-Path $CollectedLogDirectory $LogFile.Name) -Content $Sanitized
        }
    }

    $UpdateConclusion = Get-UpdateCheckConclusion $CombinedLog.ToString()
    $LoggedVersionMatch = [regex]::Matches(
        $CombinedLog.ToString(),
        'Version: (?<Version>\d+\.\d+\.\d+)'
    )
    $LoggedVersion = if ($LoggedVersionMatch.Count -gt 0) {
        $LoggedVersionMatch[$LoggedVersionMatch.Count - 1].Groups["Version"].Value
    }
    else {
        ""
    }
    $StartupDurationMilliseconds = Get-LogDurationMilliseconds `
        -LogText $CombinedLog.ToString() `
        -StartPattern "Application logging started" `
        -EndPattern "Entering Qt event loop"
    $UpdateDurationMilliseconds = Get-LogDurationMilliseconds `
        -LogText $CombinedLog.ToString() `
        -StartPattern "Starting update check" `
        -EndPattern "Update check (finished|failed silently)"
    $ThemeMatch = [regex]::Matches(
        $CombinedLog.ToString(),
        'Theme applied: effective=(?<Effective>\w+), preference=(?<Preference>\w+), native_title_bar=(?<TitleBar>\w+)'
    )
    $ThemeResult = if ($ThemeMatch.Count -gt 0) {
        $LastTheme = $ThemeMatch[$ThemeMatch.Count - 1]
        [ordered]@{
            Effective = $LastTheme.Groups["Effective"].Value
            Preference = $LastTheme.Groups["Preference"].Value
            NativeTitleBarSynchronized = $LastTheme.Groups["TitleBar"].Value -eq "True"
        }
    }
    else {
        [ordered]@{
            Effective = "unknown"
            Preference = "unknown"
            NativeTitleBarSynchronized = $null
        }
    }
    $CandidateBuild = $false
    if ($UpdateConclusion.Status -eq "Completed") {
        try {
            $CandidateBuild = [version]$UpdateConclusion.Current -gt [version]$UpdateConclusion.Latest
        }
        catch {
            $CandidateBuild = $false
        }
    }

    $ApiStopwatch = [Diagnostics.Stopwatch]::StartNew()
    try {
        $LatestRelease = Invoke-RestMethod `
            -Uri $ApiUrl `
            -Headers @{ Accept = "application/vnd.github+json"; "User-Agent" = "IED-Backup-Manager-Diagnostics" } `
            -TimeoutSec 10
        $ApiResult = [pscustomobject]@{
            Success = $true
            LatestTag = [string]$LatestRelease.tag_name
            DurationMilliseconds = $ApiStopwatch.ElapsedMilliseconds
            Error = ""
        }
    }
    catch {
        $ApiResult = [pscustomobject]@{
            Success = $false
            LatestTag = ""
            DurationMilliseconds = $ApiStopwatch.ElapsedMilliseconds
            Error = ConvertTo-SanitizedText $_.Exception.Message
        }
    }
    finally {
        $ApiStopwatch.Stop()
    }

    try {
        $DnsAddresses = @([Net.Dns]::GetHostAddresses("api.github.com") | ForEach-Object { $_.ToString() })
        $DnsResult = [pscustomobject]@{ Success = $true; Addresses = $DnsAddresses; Error = "" }
    }
    catch {
        $DnsResult = [pscustomobject]@{
            Success = $false
            Addresses = @()
            Error = ConvertTo-SanitizedText $_.Exception.Message
        }
    }

    $TcpResult = Get-TcpCheck -HostName "api.github.com" -Port 443
    $SuggestedDiagnosis = "Nenhuma falha tecnica foi identificada automaticamente."
    if (-not $DnsResult.Success) {
        $SuggestedDiagnosis = "Falha de DNS: o Windows nao conseguiu resolver api.github.com."
    }
    elseif (-not $TcpResult.Success) {
        $SuggestedDiagnosis = "Conexao TCP 443 bloqueada ou indisponivel para api.github.com."
    }
    elseif (-not $ApiResult.Success) {
        $SuggestedDiagnosis = "O Windows alcancou a rede, mas a API do GitHub falhou. Verifique HTTPS, proxy ou firewall."
    }
    elseif (
        $UpdateConclusion.Status -eq "Failed" -and
        $UpdateConclusion.Detail -match "CERTIFICATE_VERIFY_FAILED" -and
        $ApiResult.Success
    ) {
        $SuggestedDiagnosis = (
            "A aplicacao recusou o certificado TLS, mas o Windows acessou o GitHub. " +
            "Verifique a cadeia de certificados ou a inspecao HTTPS corporativa."
        )
    }
    elseif ($UpdateConclusion.Status -eq "NotStarted") {
        $SuggestedDiagnosis = "A aplicacao terminou ou ficou bloqueada antes de iniciar a consulta de atualizacao."
    }
    elseif ($UpdateConclusion.Status -eq "StartedWithoutResult") {
        $SuggestedDiagnosis = "A consulta iniciou, mas nao registrou conclusao dentro da janela de coleta."
    }
    elseif (-not $ProcessClosed) {
        $SuggestedDiagnosis = "A aplicacao permaneceu aberta depois da tentativa de encerramento normal."
    }
    $InternetSettings = Get-ItemProperty `
        -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings" `
        -ErrorAction SilentlyContinue
    $AutoConfigUrlConfigured = $false
    $ProxyEnabled = $false
    if ($null -ne $InternetSettings) {
        if ($InternetSettings.PSObject.Properties.Name -contains "ProxyEnable") {
            $ProxyEnabled = [bool]$InternetSettings.ProxyEnable
        }
        if ($InternetSettings.PSObject.Properties.Name -contains "AutoConfigURL") {
            $AutoConfigUrlConfigured = -not [string]::IsNullOrWhiteSpace(
                [string]$InternetSettings.AutoConfigURL
            )
        }
    }
    $WindowMetrics = Get-ItemProperty `
        -Path "HKCU:\Control Panel\Desktop\WindowMetrics" `
        -ErrorAction SilentlyContinue
    $AppliedDpi = if (
        $null -ne $WindowMetrics -and
        $WindowMetrics.PSObject.Properties.Name -contains "AppliedDPI"
    ) {
        [int]$WindowMetrics.AppliedDPI
    }
    else {
        0
    }
    $Personalize = Get-ItemProperty `
        -Path "HKCU:\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize" `
        -ErrorAction SilentlyContinue
    $AppsUseLightTheme = if (
        $null -ne $Personalize -and
        $Personalize.PSObject.Properties.Name -contains "AppsUseLightTheme"
    ) { [bool]$Personalize.AppsUseLightTheme } else { $null }
    $SystemUsesLightTheme = if (
        $null -ne $Personalize -and
        $Personalize.PSObject.Properties.Name -contains "SystemUsesLightTheme"
    ) { [bool]$Personalize.SystemUsesLightTheme } else { $null }
    $DesktopSettings = Get-ItemProperty `
        -Path "HKCU:\Control Panel\Desktop" `
        -ErrorAction SilentlyContinue
    $FontSmoothing = if ($null -ne $DesktopSettings) {
        [string]$DesktopSettings.FontSmoothing
    } else { "" }
    $FontSmoothingType = if (
        $null -ne $DesktopSettings -and
        $DesktopSettings.PSObject.Properties.Name -contains "FontSmoothingType"
    ) { [int]$DesktopSettings.FontSmoothingType } else { 0 }
    $Screens = @()
    $HighContrast = $false
    try {
        Add-Type -AssemblyName System.Windows.Forms
        $HighContrast = [Windows.Forms.SystemInformation]::HighContrast
        $Screens = @([Windows.Forms.Screen]::AllScreens | ForEach-Object {
            [ordered]@{
                Device = $_.DeviceName
                Width = $_.Bounds.Width
                Height = $_.Bounds.Height
                Primary = $_.Primary
            }
        })
    }
    catch {
        $Screens = @()
    }

    $SystemInfo = [ordered]@{
        CollectedAt = (Get-Date).ToString("o")
        WindowsVersion = [Environment]::OSVersion.VersionString
        Is64BitOperatingSystem = [Environment]::Is64BitOperatingSystem
        Is64BitProcess = [Environment]::Is64BitProcess
        PowerShellVersion = $PSVersionTable.PSVersion.ToString()
        Culture = [Globalization.CultureInfo]::CurrentCulture.Name
        TimeZone = [TimeZoneInfo]::Local.Id
        AppliedDpi = $AppliedDpi
        ScalePercent = if ($AppliedDpi -gt 0) { [int][math]::Round($AppliedDpi / 96 * 100) } else { 0 }
        Screens = $Screens
        AppsUseLightTheme = $AppsUseLightTheme
        SystemUsesLightTheme = $SystemUsesLightTheme
        HighContrast = $HighContrast
        FontSmoothingEnabled = $FontSmoothing -eq "2"
        FontSmoothingType = $FontSmoothingType
        ProxyEnabled = $ProxyEnabled
        AutoConfigUrlConfigured = $AutoConfigUrlConfigured
        HttpProxyEnvironmentConfigured = -not [string]::IsNullOrWhiteSpace([string]$env:HTTP_PROXY)
        HttpsProxyEnvironmentConfigured = -not [string]::IsNullOrWhiteSpace([string]$env:HTTPS_PROXY)
    }
    Write-Utf8File `
        -Path (Join-Path $PackageDirectory "system-info.json") `
        -Content ($SystemInfo | ConvertTo-Json -Depth 4)

    $ApplicationInfo = [ordered]@{
        FileName = $ExecutableItem.Name
        SizeBytes = $ExecutableItem.Length
        LastWriteTime = $ExecutableItem.LastWriteTime.ToString("o")
        FileVersion = $ExecutableItem.VersionInfo.FileVersion
        ProductVersion = $ExecutableItem.VersionInfo.ProductVersion
        LoggedApplicationVersion = $LoggedVersion
        SHA256 = $ExecutableHash
        ProcessStarted = $null -ne $Process
        ProcessClosedNormallyByCollector = $ProcessClosed
        ExitCode = $ApplicationExitCode
        WaitSeconds = $WaitSeconds
        StartupDurationMilliseconds = $StartupDurationMilliseconds
        UpdateCheckDurationMilliseconds = $UpdateDurationMilliseconds
        CandidateBuild = $CandidateBuild
        Theme = $ThemeResult
        CollectorVersion = $CollectorVersion
        LauncherVersion = $LauncherVersion
    }
    Write-Utf8File `
        -Path (Join-Path $PackageDirectory "application-info.json") `
        -Content ($ApplicationInfo | ConvertTo-Json -Depth 4)

    $NetworkInfo = [ordered]@{
        GitHubApi = $ApiResult
        Dns = $DnsResult
        Tcp443 = $TcpResult
    }
    Write-Utf8File `
        -Path (Join-Path $PackageDirectory "network-check.json") `
        -Content ($NetworkInfo | ConvertTo-Json -Depth 6)

    $ApplicationStatus = if ($null -ne $Process -and $ApplicationExitCode -eq 0) { "OK" } else { "FALHA" }
    $CloseStatus = if ($ProcessClosed) { "OK" } else { "FALHA" }
    $DnsStatus = if ($DnsResult.Success) { "OK" } else { "FALHA" }
    $HttpsStatus = if ($ApiResult.Success -and $TcpResult.Success) { "OK" } else { "FALHA" }
    $CertificateStatus = if ($UpdateConclusion.Status -eq "Completed") {
        "OK"
    }
    elseif ($UpdateConclusion.Detail -match "CERTIFICATE_VERIFY_FAILED") {
        "FALHA"
    }
    else {
        "NAO TESTADO"
    }
    $UpdateStatus = if ($UpdateConclusion.Status -eq "Completed") { "OK" } else { "FALHA" }
    $CompatibilityStatus = if (
        [string]::IsNullOrWhiteSpace($LauncherVersion) -or
        $LauncherVersion -eq $CompatibleLauncherVersion
    ) { "OK" } else { "FALHA" }

    $PrivacyStatus = "OK"
    $PackageText = (Get-ChildItem -LiteralPath $PackageDirectory -File -Recurse | ForEach-Object {
        Get-Content -LiteralPath $_.FullName -Raw
    }) -join "`n"
    foreach ($SensitiveValue in @($TemporaryRoot, $Executable, $env:USERPROFILE, $env:USERNAME, $env:COMPUTERNAME)) {
        if (
            -not [string]::IsNullOrWhiteSpace([string]$SensitiveValue) -and
            $PackageText.IndexOf([string]$SensitiveValue, [StringComparison]::OrdinalIgnoreCase) -ge 0
        ) {
            $PrivacyStatus = "FALHA"
        }
    }

    $Summary = [ordered]@{
        CollectorVersion = $CollectorVersion
        LauncherCompatibility = $CompatibilityStatus
        Application = $ApplicationStatus
        NormalClose = $CloseStatus
        Dns = $DnsStatus
        Https = $HttpsStatus
        WindowsCertificates = $CertificateStatus
        UpdateCheck = $UpdateStatus
        PrivacySanitization = $PrivacyStatus
        CandidateBuild = $CandidateBuild
        Diagnosis = $SuggestedDiagnosis
    }
    Write-Utf8File `
        -Path (Join-Path $PackageDirectory "diagnostic-summary.json") `
        -Content ($Summary | ConvertTo-Json -Depth 4)

    $Report = @"
IED Backup Manager - Relatorio de diagnostico
=============================================

Coletado em: $((Get-Date).ToString("o"))
Versao do coletor: $CollectorVersion
Compatibilidade CMD/PS1: $CompatibilityStatus

RESUMO
------
Aplicacao: $ApplicationStatus
Encerramento normal: $CloseStatus
DNS: $DnsStatus
HTTPS: $HttpsStatus
Certificados do Windows: $CertificateStatus
Consulta de atualizacao: $UpdateStatus
Privacidade da coleta: $PrivacyStatus

DETALHES
--------
Codigo de saida: $ApplicationExitCode
Versao executada: $LoggedVersion
Versao publica: $($ApiResult.LatestTag)
Build candidato ainda nao publicado: $CandidateBuild
Inicializacao da interface (ms): $StartupDurationMilliseconds
Consulta de atualizacao (ms): $UpdateDurationMilliseconds
Tema efetivo: $($ThemeResult.Effective)
Preferencia de tema: $($ThemeResult.Preference)
Barra de titulo sincronizada: $($ThemeResult.NativeTitleBarSynchronized)
Resultado tecnico: $($UpdateConclusion.Status)
Detalhe tecnico: $($UpdateConclusion.Detail)

DIAGNOSTICO SUGERIDO
--------------------
$SuggestedDiagnosis

O executavel foi iniciado com projeto e LOCALAPPDATA isolados. Nao foram
coletados config.json real, projetos de engenharia, backups ATU/HIS,
credenciais, dumps ou logs gerais de eventos do Windows.
"@
    Write-Utf8File -Path (Join-Path $PackageDirectory "diagnostic-report.txt") -Content $Report

    $Readme = @"
IED Backup Manager - Pacote de diagnostico

Arquivos:
- diagnostic-report.txt: conclusao resumida.
- diagnostic-summary.json: estados OK/FALHA para leitura automatica.
- application-info.json: versao, hash e resultado do processo.
- network-check.json: DNS, TCP 443 e consulta a API publica do GitHub.
- system-info.json: versao do Windows, PowerShell, idioma, fuso e indicadores de proxy/escala.
- logs/: logs da execucao isolada, com caminhos, usuario e computador sanitizados.

Nao coletado:
- config.json;
- arquivos de engenharia;
- backups ATU/HIS;
- credenciais ou conteudo de proxy;
- dump de memoria;
- log de eventos do Windows.

Revise o conteudo e envie o ZIP ao responsavel pelo IED Backup Manager.
"@
    Write-Utf8File -Path (Join-Path $PackageDirectory "COMO-ENVIAR.txt") -Content $Readme

    if (Test-Path -LiteralPath $ZipPath) {
        Remove-Item -LiteralPath $ZipPath -Force
    }
    Compress-Archive -Path (Join-Path $PackageDirectory "*") -DestinationPath $ZipPath

    Write-Host "" 
    Write-Host "Diagnostico concluido." -ForegroundColor Green
    Write-Host "Resultado da atualizacao: $($UpdateConclusion.Status)"
    Write-Host "Aplicacao: $ApplicationStatus | DNS: $DnsStatus | HTTPS: $HttpsStatus | Certificados: $CertificateStatus"
    Write-Host "ZIP: $ZipPath"
    if (-not $ProcessClosed) {
        Write-Warning "O aplicativo permaneceu aberto. Feche-o normalmente apos revisar a coleta."
    }
    Write-Host "Revise o ZIP e envie-o ao responsavel pelo IED Backup Manager." -ForegroundColor Yellow
}
finally {
    $CanRemoveTemporaryFiles = $null -eq $Process
    if ($null -ne $Process) {
        $CanRemoveTemporaryFiles = @(Get-LaunchedApplicationProcesses).Count -eq 0
    }
    if ($CanRemoveTemporaryFiles) {
        if (Test-Path -LiteralPath $TemporaryRoot) {
            Remove-Item -LiteralPath $TemporaryRoot -Recurse -Force -ErrorAction SilentlyContinue
        }
    }
}
