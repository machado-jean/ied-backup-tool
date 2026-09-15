param([switch]$VerifyOnly)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Repository = "machado-jean/ied-backup-tool"
$ReleaseDirectory = $PSScriptRoot
$Tag = Split-Path -Leaf $ReleaseDirectory
$ProjectRoot = (Resolve-Path (Join-Path $ReleaseDirectory "..\..")).Path
$ReleaseNotes = Join-Path $ReleaseDirectory "RELEASE_NOTES.md"
$HashFile = Join-Path $ReleaseDirectory "SHA256SUMS.txt"
$AssetNames = @("IED_Backup_Manager.exe", "SHA256SUMS.txt")
$Report = [System.Collections.Generic.List[object]]::new()
$LocationPushed = $false

function Add-ReportItem {
    param(
        [string]$Check,
        [ValidateSet("CORRETO", "INCORRETO")]
        [string]$Status,
        [string]$Detail
    )

    $script:Report.Add([pscustomobject]@{
        Verificacao = $Check
        Status = $Status
        Detalhe = $Detail
    })
}

function Confirm-Check {
    param([string]$Check, [string]$Detail)
    Add-ReportItem -Check $Check -Status "CORRETO" -Detail $Detail
}

function Stop-Check {
    param([string]$Check, [string]$Detail)
    Add-ReportItem -Check $Check -Status "INCORRETO" -Detail $Detail
    throw $Detail
}

function Show-VerificationReport {
    Write-Host ""
    Write-Host "RELATÓRIO DE VERIFICAÇÃO DO RELEASE $Tag" -ForegroundColor Cyan
    Write-Host ("=" * 76) -ForegroundColor DarkGray
    foreach ($Item in $script:Report) {
        $Color = if ($Item.Status -eq "CORRETO") { "Green" } else { "Red" }
        Write-Host ("[{0}] {1}" -f $Item.Status, $Item.Verificacao) -ForegroundColor $Color
        Write-Host ("          {0}" -f $Item.Detalhe)
    }
    Write-Host ("=" * 76) -ForegroundColor DarkGray
}

try {
    if ($Tag -notmatch '^v(?<Version>\d+\.\d+\.\d+)$') {
        Stop-Check "Pasta do release" "A pasta deve usar o formato releases/vX.Y.Z."
    }
    $ReleaseVersion = $Matches.Version
    Confirm-Check "Pasta do release" "$Tag segue o formato esperado."

    Push-Location $ProjectRoot
    $LocationPushed = $true

    $VersionFile = Join-Path $ProjectRoot "src\version.py"
    $VersionText = Get-Content -LiteralPath $VersionFile -Raw
    if ($VersionText -notmatch 'APP_VERSION\s*=\s*"([^"]+)"' -or $Matches[1] -ne $ReleaseVersion) {
        Stop-Check "Versão da aplicação" "src/version.py deve conter $ReleaseVersion."
    }
    Confirm-Check "Versão da aplicação" "src/version.py contém $ReleaseVersion."

    if (-not (Test-Path -LiteralPath $ReleaseNotes -PathType Leaf)) {
        Stop-Check "Release notes" "Arquivo ausente: RELEASE_NOTES.md"
    }
    if ([string]::IsNullOrWhiteSpace((Get-Content -LiteralPath $ReleaseNotes -Raw))) {
        Stop-Check "Release notes" "RELEASE_NOTES.md está vazio."
    }
    Confirm-Check "Release notes" "RELEASE_NOTES.md existe e possui conteúdo."

    if (-not (Test-Path -LiteralPath $HashFile -PathType Leaf)) {
        Stop-Check "Arquivo de hashes" "Arquivo ausente: SHA256SUMS.txt"
    }

    $ExpectedHashes = @{}
    foreach ($Line in Get-Content -LiteralPath $HashFile) {
        if ($Line -notmatch '^([A-Fa-f0-9]{64})\s+\*?(.+)$') {
            Stop-Check "Arquivo de hashes" "Linha inválida em SHA256SUMS.txt: $Line"
        }
        $ExpectedHashes[$Matches[2]] = $Matches[1].ToUpperInvariant()
    }
    Confirm-Check "Arquivo de hashes" "SHA256SUMS.txt possui formato válido."

    $AssetPaths = foreach ($AssetName in $AssetNames) {
        $AssetPath = Join-Path $ReleaseDirectory $AssetName
        if (-not (Test-Path -LiteralPath $AssetPath -PathType Leaf)) {
            Stop-Check "Assets locais" "Arquivo ausente: $AssetName"
        }
        if ($AssetName -ne "SHA256SUMS.txt") {
            if (-not $ExpectedHashes.ContainsKey($AssetName)) {
                Stop-Check "Integridade do executável" "Hash ausente: $AssetName"
            }
            $ActualHash = (Get-FileHash -LiteralPath $AssetPath -Algorithm SHA256).Hash
            if ($ActualHash -ne $ExpectedHashes[$AssetName]) {
                Stop-Check "Integridade do executável" "Hash incorreto: $AssetName"
            }
        }
        $AssetPath
    }
    Confirm-Check "Assets locais" "Executável e SHA256SUMS.txt estão presentes."
    Confirm-Check "Integridade do executável" "O SHA256 do executável confere."

    if ($VerifyOnly) {
        Show-VerificationReport
        Write-Host "Verificação local concluída; nenhuma tag ou release foi criado."
        return
    }

    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        Stop-Check "GitHub CLI" "GitHub CLI (gh) não encontrado."
    }
    Confirm-Check "GitHub CLI" "GitHub CLI encontrado."

    gh auth status --hostname github.com
    if ($LASTEXITCODE -ne 0) {
        Stop-Check "Autenticação GitHub" "Autentique o GitHub CLI com: gh auth login"
    }
    Confirm-Check "Autenticação GitHub" "GitHub CLI autenticado."

    $Status = @(git status --porcelain --untracked-files=all)
    if ($LASTEXITCODE -ne 0 -or $Status.Count -ne 0) {
        Stop-Check "Estado do repositório" "Faça commit de todas as alterações antes de publicar."
    }
    Confirm-Check "Estado do repositório" "A árvore de trabalho está limpa."

    $Branch = (git branch --show-current).Trim()
    if ($LASTEXITCODE -ne 0 -or $Branch -ne "master") {
        Stop-Check "Branch local" "A publicação deve ser executada a partir da branch master."
    }
    Confirm-Check "Branch local" "Branch master selecionada."

    $Commit = (git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) {
        Stop-Check "Commit local" "Não foi possível identificar o commit local."
    }
    Confirm-Check "Commit local" "Commit identificado: $Commit"

    $RemoteCommit = (gh api "repos/$Repository/commits/master" --jq .sha).Trim()
    if ($LASTEXITCODE -ne 0 -or $RemoteCommit -ne $Commit) {
        Stop-Check "Sincronismo com GitHub" "Envie o commit para master; HEAD deve corresponder ao remoto."
    }
    Confirm-Check "Sincronismo com GitHub" "HEAD corresponde ao commit remoto de master."

    $Python = Join-Path $ProjectRoot ".venv\Scripts\python.exe"
    if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
        Stop-Check "Ambiente Python" "Ambiente Python ausente: $Python"
    }
    Confirm-Check "Ambiente Python" "Python do ambiente virtual encontrado."

    & $Python -m ruff check .
    if ($LASTEXITCODE -ne 0) {
        Stop-Check "Lint local" "O lint local falhou; nenhuma tag ou release foi criado."
    }
    Confirm-Check "Lint local" "Todas as verificações de lint passaram."

    & $Python -m pytest
    if ($LASTEXITCODE -ne 0) {
        Stop-Check "Testes locais" "Os testes locais falharam; nenhuma tag ou release foi criado."
    }
    Confirm-Check "Testes locais" "Todos os testes locais passaram."

    $MainDeadline = (Get-Date).AddMinutes(5)
    $MainRun = $null
    do {
        $MainRunJson = gh run list `
            --repo $Repository `
            --workflow CI `
            --branch master `
            --commit $Commit `
            --event push `
            --limit 1 `
            --json databaseId,status,conclusion
        if ($LASTEXITCODE -ne 0) {
            Stop-Check "CI de master" "Não foi possível consultar o CI de master."
        }
        $MainRun = @($MainRunJson | ConvertFrom-Json) | Select-Object -First 1
        if (-not $MainRun) {
            Start-Sleep -Seconds 5
        }
    } while (-not $MainRun -and (Get-Date) -lt $MainDeadline)

    if (-not $MainRun) {
        Stop-Check "CI de master" "O workflow CI de master para este commit não foi encontrado."
    }
    if ($MainRun.status -ne "completed") {
        gh run watch $MainRun.databaseId --repo $Repository --exit-status
        if ($LASTEXITCODE -ne 0) {
            Stop-Check "CI de master" "O CI de master falhou; o release não será publicado."
        }
    }
    elseif ($MainRun.conclusion -ne "success") {
        Stop-Check "CI de master" "O CI de master terminou como '$($MainRun.conclusion)'."
    }
    Confirm-Check "CI de master" "Workflow CI aprovado para o commit exato."

    $ExistingJson = gh release list --repo $Repository --limit 100 --json tagName
    if ($LASTEXITCODE -ne 0) {
        Stop-Check "Release existente" "Não foi possível consultar os releases existentes."
    }
    $ExistingRelease = @($ExistingJson | ConvertFrom-Json) |
        Where-Object { $_.tagName -eq $Tag } |
        Select-Object -First 1
    if ($ExistingRelease) {
        Stop-Check "Release existente" "O release $Tag já existe no GitHub."
    }
    Confirm-Check "Release existente" "Não existe GitHub Release para $Tag."

    $RemoteTagLines = @(git ls-remote --tags origin "refs/tags/$Tag" "refs/tags/$Tag^{}")
    if ($LASTEXITCODE -ne 0) {
        Stop-Check "Tag do release" "Não foi possível consultar a tag remota $Tag."
    }
    if ($RemoteTagLines.Count -eq 0) {
        git show-ref --verify --quiet "refs/tags/$Tag"
        if ($LASTEXITCODE -eq 0) {
            $LocalTagCommit = (git rev-list -n 1 $Tag).Trim()
            if ($LASTEXITCODE -ne 0 -or $LocalTagCommit -ne $Commit) {
                Stop-Check "Tag do release" "A tag local $Tag não aponta para o commit atual $Commit."
            }
        }
        else {
            git tag $Tag $Commit
            if ($LASTEXITCODE -ne 0) {
                Stop-Check "Tag do release" "Não foi possível criar a tag local $Tag."
            }
        }

        git push origin "refs/tags/$Tag"
        if ($LASTEXITCODE -ne 0) {
            Stop-Check "Tag do release" "Não foi possível enviar a tag $Tag; nenhum release foi criado."
        }
        Confirm-Check "Tag do release" "Tag $Tag criada e enviada para o commit atual."
    }
    else {
        $PeeledTagLine = $RemoteTagLines |
            Where-Object { $_ -match '\^\{\}$' } |
            Select-Object -First 1
        $ResolvedTagLine = if ($PeeledTagLine) {
            $PeeledTagLine
        }
        else {
            $RemoteTagLines | Select-Object -First 1
        }
        $RemoteTagCommit = ($ResolvedTagLine -split '\s+', 2)[0]
        if ($RemoteTagCommit -ne $Commit) {
            Stop-Check "Tag do release" "A tag remota $Tag aponta para $RemoteTagCommit, não para $Commit."
        }
        Confirm-Check "Tag do release" "A tag remota $Tag já aponta para o commit atual."
    }

    try {
        & (Join-Path $ProjectRoot "scripts\Check-ReleaseCi.ps1") `
            -Tag $Tag `
            -Commit $Commit
    }
    catch {
        Stop-Check "CI da tag" $_.Exception.Message
    }
    Confirm-Check "CI da tag" "Workflow CI da tag aprovado para o commit exato."

    Show-VerificationReport
    Write-Host "Publicar release com o release note e .exe?" -ForegroundColor Yellow
    $Confirmation = (Read-Host "Digite S para publicar ou N para cancelar").Trim().ToLowerInvariant()
    if ($Confirmation -notin @("s", "sim", "y", "yes")) {
        Write-Host "Publicação cancelada. A tag validada foi mantida e nenhum GitHub Release foi criado."
        return
    }

    gh release create $Tag @AssetPaths `
        --repo $Repository `
        --verify-tag `
        --title "IED Backup Manager $Tag" `
        --notes-file $ReleaseNotes
    if ($LASTEXITCODE -ne 0) {
        Stop-Check "Criação do GitHub Release" "A tag aprovada foi mantida para nova tentativa."
    }
    Confirm-Check "Criação do GitHub Release" "GitHub Release criado com release notes e assets."

    $PublishedJson = gh release view $Tag --repo $Repository --json tagName,assets
    if ($LASTEXITCODE -ne 0) {
        Stop-Check "Verificação da publicação" "O release foi criado, mas não pôde ser verificado."
    }
    $Published = $PublishedJson | ConvertFrom-Json
    $PublishedAssetNames = @($Published.assets | ForEach-Object { $_.name })
    foreach ($AssetName in $AssetNames) {
        if ($AssetName -notin $PublishedAssetNames) {
            Stop-Check "Verificação da publicação" "Asset ausente no release: $AssetName"
        }
    }
    Confirm-Check "Verificação da publicação" "Todos os assets esperados estão publicados."
    Show-VerificationReport
    Write-Host "Release publicado e verificado: https://github.com/$Repository/releases/tag/$Tag"
}
catch {
    $FailureMessage = $_.Exception.Message
    $HasIncorrectItem = @($Report | Where-Object { $_.Status -eq "INCORRETO" }).Count -gt 0
    if (-not $HasIncorrectItem) {
        Add-ReportItem -Check "Execução do publicador" -Status "INCORRETO" -Detail $FailureMessage
    }
    Show-VerificationReport
    throw
}
finally {
    if ($LocationPushed) {
        Pop-Location
    }
}
