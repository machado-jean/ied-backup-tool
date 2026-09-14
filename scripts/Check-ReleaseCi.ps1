param(
    [Parameter(Mandatory = $true)]
    [string]$Tag,
    [int]$TimeoutMinutes = 10
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$Repository = "machado-jean/ied-backup-tool"
$Deadline = (Get-Date).AddMinutes($TimeoutMinutes)
$Run = $null

do {
    $RunJson = gh run list `
        --repo $Repository `
        --workflow CI `
        --branch $Tag `
        --event push `
        --limit 1 `
        --json databaseId,status,conclusion
    if ($LASTEXITCODE -ne 0) {
        throw "Não foi possível consultar o CI da tag $Tag."
    }
    $Run = @($RunJson | ConvertFrom-Json) | Select-Object -First 1
    if (-not $Run) {
        Start-Sleep -Seconds 5
    }
} while (-not $Run -and (Get-Date) -lt $Deadline)

if (-not $Run) {
    throw "O workflow CI da tag $Tag não foi encontrado em $TimeoutMinutes minuto(s)."
}

if ($Run.status -ne "completed") {
    gh run watch $Run.databaseId --repo $Repository --exit-status
    if ($LASTEXITCODE -ne 0) {
        throw "O CI da tag $Tag falhou."
    }
}
elseif ($Run.conclusion -ne "success") {
    throw "O CI da tag $Tag terminou como '$($Run.conclusion)'."
}

Write-Host "CI da tag $Tag aprovado."
