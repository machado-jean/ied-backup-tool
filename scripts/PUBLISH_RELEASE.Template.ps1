param([switch]$VerifyOnly)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Repository = "machado-jean/ied-backup-tool"
$ReleaseDirectory = $PSScriptRoot
$Tag = Split-Path -Leaf $ReleaseDirectory
if ($Tag -notmatch '^v(?<Version>\d+\.\d+\.\d+)$') {
    throw "A pasta do release deve usar o formato releases/vX.Y.Z."
}
$ReleaseVersion = $Matches.Version
$ProjectRoot = (Resolve-Path (Join-Path $ReleaseDirectory "..\..")).Path
$VersionFile = Join-Path $ProjectRoot "src\version.py"
$ReleaseNotes = Join-Path $ReleaseDirectory "RELEASE_NOTES.md"
$HashFile = Join-Path $ReleaseDirectory "SHA256SUMS.txt"
$AssetNames = @("IED_Backup_Manager.exe", "SHA256SUMS.txt")

Push-Location $ProjectRoot
try {
    $VersionText = Get-Content -LiteralPath $VersionFile -Raw
    if ($VersionText -notmatch 'APP_VERSION\s*=\s*"([^"]+)"' -or $Matches[1] -ne $ReleaseVersion) {
        throw "Versão local incorreta; src/version.py deve conter $ReleaseVersion."
    }
    if (-not (Test-Path -LiteralPath $ReleaseNotes)) {
        throw "Arquivo ausente: RELEASE_NOTES.md"
    }
    if (-not (Test-Path -LiteralPath $HashFile)) {
        throw "Arquivo ausente: SHA256SUMS.txt"
    }

    $ExpectedHashes = @{}
    foreach ($Line in Get-Content -LiteralPath $HashFile) {
        if ($Line -notmatch '^([A-Fa-f0-9]{64})\s+\*?(.+)$') {
            throw "Linha inválida em SHA256SUMS.txt: $Line"
        }
        $ExpectedHashes[$Matches[2]] = $Matches[1].ToUpperInvariant()
    }

    $AssetPaths = foreach ($AssetName in $AssetNames) {
        $AssetPath = Join-Path $ReleaseDirectory $AssetName
        if (-not (Test-Path -LiteralPath $AssetPath -PathType Leaf)) {
            throw "Arquivo ausente: $AssetName"
        }
        if ($AssetName -ne "SHA256SUMS.txt") {
            if (-not $ExpectedHashes.ContainsKey($AssetName)) {
                throw "Hash ausente: $AssetName"
            }
            $ActualHash = (Get-FileHash -LiteralPath $AssetPath -Algorithm SHA256).Hash
            if ($ActualHash -ne $ExpectedHashes[$AssetName]) {
                throw "Hash incorreto: $AssetName"
            }
        }
        $AssetPath
    }

    Write-Host "Versão, notas, hashes e arquivos do $Tag aprovados."
    if ($VerifyOnly) {
        return
    }

    if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
        throw "GitHub CLI (gh) não encontrado."
    }
    gh auth status --hostname github.com
    if ($LASTEXITCODE -ne 0) {
        throw "Autentique o GitHub CLI com: gh auth login"
    }

    $Status = @(git status --porcelain --untracked-files=all)
    if ($LASTEXITCODE -ne 0 -or $Status.Count -ne 0) {
        throw "Faça commit de todas as alterações antes de publicar."
    }
    $Branch = (git branch --show-current).Trim()
    if ($LASTEXITCODE -ne 0 -or $Branch -ne "master") {
        throw "A publicação deve ser executada a partir da branch master."
    }
    $Commit = (git rev-parse HEAD).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Não foi possível identificar o commit local."
    }
    $RemoteCommit = (gh api "repos/$Repository/commits/master" --jq .sha).Trim()
    if ($LASTEXITCODE -ne 0 -or $RemoteCommit -ne $Commit) {
        throw "Envie o commit para master antes de publicar; HEAD deve corresponder ao remoto."
    }

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
            throw "Não foi possível consultar o CI de master."
        }
        $MainRun = @($MainRunJson | ConvertFrom-Json) | Select-Object -First 1
        if (-not $MainRun) {
            Start-Sleep -Seconds 5
        }
    } while (-not $MainRun -and (Get-Date) -lt $MainDeadline)

    if (-not $MainRun) {
        throw "O workflow CI de master para este commit ainda não foi encontrado."
    }
    if ($MainRun.status -ne "completed") {
        gh run watch $MainRun.databaseId --repo $Repository --exit-status
        if ($LASTEXITCODE -ne 0) {
            throw "O CI de master falhou; o release não será publicado."
        }
    }
    elseif ($MainRun.conclusion -ne "success") {
        throw "O CI de master terminou como '$($MainRun.conclusion)'."
    }

    $ExistingJson = gh release list --repo $Repository --limit 100 --json tagName
    if ($LASTEXITCODE -ne 0) {
        throw "Não foi possível verificar os releases existentes."
    }
    $ExistingRelease = @($ExistingJson | ConvertFrom-Json) |
        Where-Object { $_.tagName -eq $Tag } |
        Select-Object -First 1
    if ($ExistingRelease) {
        throw "O release $Tag já existe no GitHub."
    }

    gh release create $Tag @AssetPaths `
        --repo $Repository `
        --target $Commit `
        --title "IED Backup Manager $Tag" `
        --notes-file $ReleaseNotes
    if ($LASTEXITCODE -ne 0) {
        throw "Publicação não concluída. Confira o retorno do GitHub CLI."
    }

    $PublishedJson = gh release view $Tag --repo $Repository --json tagName,assets
    if ($LASTEXITCODE -ne 0) {
        throw "O release foi criado, mas não pôde ser verificado."
    }
    $Published = $PublishedJson | ConvertFrom-Json
    $PublishedAssetNames = @($Published.assets | ForEach-Object { $_.name })
    foreach ($AssetName in $AssetNames) {
        if ($AssetName -notin $PublishedAssetNames) {
            throw "O release foi criado sem o asset esperado: $AssetName"
        }
    }

    & (Join-Path $ProjectRoot "scripts\Check-ReleaseCi.ps1") -Tag $Tag
    if ($LASTEXITCODE -ne 0) {
        throw "O release foi publicado, mas a verificação do CI da tag falhou."
    }
    Write-Host "Release publicado e verificado: https://github.com/$Repository/releases/tag/$Tag"
}
finally {
    Pop-Location
}
