param(
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"

$Root = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $Root

$VersionFile = Join-Path $Root "src\version.py"
$VersionText = Get-Content -LiteralPath $VersionFile -Raw
if ($VersionText -notmatch 'APP_VERSION\s*=\s*"([^"]+)"') {
    throw "Could not read APP_VERSION from src\version.py"
}

$Version = $Matches[1]
$Tag = "v$Version"
$ExeName = "IED Backup Manager $Tag"
$ExePath = Join-Path $Root "dist\$ExeName.exe"
$ReleaseDir = Join-Path $Root "releases\$Tag"
$ReleaseExe = Join-Path $ReleaseDir "$ExeName.exe"
$ReleaseNotes = Join-Path $ReleaseDir "RELEASE_NOTES.md"

if (-not $SkipTests) {
    .\.venv\Scripts\python.exe -m ruff check .
    .\.venv\Scripts\python.exe -m pytest
}

.\.venv\Scripts\python.exe -m PyInstaller `
    --noconfirm `
    --clean `
    --onefile `
    --windowed `
    --icon "assets\app_icon.ico" `
    --add-data "assets;assets" `
    --add-data "docs\HELP.md;docs" `
    --name $ExeName `
    --paths . `
    src\gui\app.py

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

Write-Host "Release generated: $ReleaseExe"
Write-Host "Release notes: $ReleaseNotes"
