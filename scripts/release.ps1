param(
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

$VersionFile = Join-Path $Root "src\version.py"
$VersionText = Get-Content -LiteralPath $VersionFile -Raw
if ($VersionText -notmatch 'APP_VERSION\s*=\s*"([^"]+)"') {
    throw "Could not read APP_VERSION from src\version.py"
}

$Version = $Matches[1]
$Tag = "v$Version"
$ExeName = "IED_Backup_Manager"
$ExePath = Join-Path $Root "dist\$ExeName.exe"
$BuildDir = Join-Path $Root "build"
$DistDir = Join-Path $Root "dist"
$ReleaseDir = Join-Path $Root "releases\$Tag"
$ReleaseExe = Join-Path $ReleaseDir "$ExeName.exe"
$ReleaseNotes = Join-Path $ReleaseDir "RELEASE_NOTES.md"
$ReleaseHashes = Join-Path $ReleaseDir "SHA256SUMS.txt"
$PublishTemplate = Join-Path $Root "scripts\PUBLISH_RELEASE.Template.ps1"
$PublishScript = Join-Path $ReleaseDir "PUBLISH_RELEASE.ps1"
$TestTempDir = Join-Path $Root ".pytest-release"
$RuntimeTempDir = Join-Path $Root ".temp-release"
$VenvScripts = Join-Path $Root ".venv\Scripts"
$SystemPath = @(
    $VenvScripts,
    "$env:SystemRoot\System32",
    "$env:SystemRoot",
    "$env:SystemRoot\System32\Wbem",
    "$env:SystemRoot\System32\WindowsPowerShell\v1.0"
) -join [IO.Path]::PathSeparator

if (-not $SkipTests) {
    .\.venv\Scripts\python.exe -m ruff check .
    if ($LASTEXITCODE -ne 0) {
        throw "Lint failed; release build aborted."
    }

    foreach ($TemporaryTestPath in @($TestTempDir, $RuntimeTempDir)) {
        if (Test-Path -LiteralPath $TemporaryTestPath) {
            Remove-Item -LiteralPath $TemporaryTestPath -Recurse -Force
        }
    }
    New-Item -ItemType Directory -Path $RuntimeTempDir | Out-Null
    $OriginalTemp = $env:TEMP
    $OriginalTmp = $env:TMP
    try {
        $env:TEMP = $RuntimeTempDir
        $env:TMP = $RuntimeTempDir
        .\.venv\Scripts\python.exe -m pytest --basetemp $TestTempDir
        if ($LASTEXITCODE -ne 0) {
            throw "Tests failed; release build aborted."
        }
    }
    finally {
        $env:TEMP = $OriginalTemp
        $env:TMP = $OriginalTmp
        foreach ($TemporaryTestPath in @($TestTempDir, $RuntimeTempDir)) {
            if (Test-Path -LiteralPath $TemporaryTestPath) {
                Remove-Item -LiteralPath $TemporaryTestPath -Recurse -Force
            }
        }
    }
}

$OriginalPath = $env:PATH
try {
    # Keep PyInstaller from collecting unrelated DLLs injected by developer tools.
    $env:PATH = $SystemPath
    .\.venv\Scripts\python.exe -m PyInstaller `
        --noconfirm `
        --clean `
        --onefile `
        --windowed `
        --icon "assets\app_icon.ico" `
        --add-data "assets;assets" `
        --name $ExeName `
        --paths . `
        src\gui\app.py
    if ($LASTEXITCODE -ne 0) {
        throw "PyInstaller failed; release build aborted."
    }
}
finally {
    $env:PATH = $OriginalPath
}

New-Item -ItemType Directory -Force -Path $ReleaseDir | Out-Null
Copy-Item -LiteralPath $ExePath -Destination $ReleaseExe -Force

$SpecPath = Join-Path $Root "$ExeName.spec"
if (Test-Path -LiteralPath $SpecPath) {
    Remove-Item -LiteralPath $SpecPath -Force
}

if (-not (Test-Path -LiteralPath $ReleaseNotes)) {
    @"
# IED Backup Manager $Tag

Data: $(Get-Date -Format "dd/MM/yyyy")

## Resumo

Descreva aqui o objetivo desta versao.

## Alteracoes

- 

## Compatibilidade

- 

## Arquivo

- $ExeName.exe
"@ | Set-Content -LiteralPath $ReleaseNotes -Encoding utf8
}

if (-not (Test-Path -LiteralPath $PublishTemplate -PathType Leaf)) {
    throw "Publish template not found: $PublishTemplate"
}
$ReleaseHash = (Get-FileHash -LiteralPath $ReleaseExe -Algorithm SHA256).Hash
"$ReleaseHash  $ExeName.exe" | Set-Content -LiteralPath $ReleaseHashes -Encoding ascii
Copy-Item -LiteralPath $PublishTemplate -Destination $PublishScript -Force

& $PublishScript -VerifyOnly

foreach ($TemporaryBuildPath in @($BuildDir, $DistDir)) {
    if (Test-Path -LiteralPath $TemporaryBuildPath) {
        Remove-Item -LiteralPath $TemporaryBuildPath -Recurse -Force
    }
}

Write-Host "Release generated: $ReleaseExe"
Write-Host "Release notes: $ReleaseNotes"
Write-Host "Release hashes: $ReleaseHashes"
Write-Host "Publish script: $PublishScript"
Write-Host "Temporary PyInstaller folders removed."
