# Diagnostic collection

[Português](COLETA_DIAGNOSTICO.md) | [English](DIAGNOSTIC_COLLECTION.en.md)

`scripts/COLETAR_DIAGNOSTICO.cmd` and `scripts/Collect-Diagnostics.ps1` start IED
Backup Manager in an isolated environment, wait for its update check, and
create a ZIP that the user sends directly to the application maintainer.

Always use the `.cmd` and `.ps1` distributed together. Version `1.1.0` checks
launcher compatibility, reports `OK/FAIL` states, diagnoses DNS, HTTPS and
certificate failures, and records display, DPI, theme, high-contrast and font
smoothing state without collecting operational content.

It does not require administrator access and does not collect `config.json`,
engineering projects, `ATU`/`HIS` backups, credentials, dumps, or Windows
events.

## Simple use

Place the `.cmd`, `.ps1`, and `IED_Backup_Manager.exe` in the same folder and
double-click `COLETAR_DIAGNOSTICO.cmd`. The diagnostic ZIP is created on the
Desktop after approximately 10 seconds. The user does not need Git, GitHub,
Python, administrator access, or command-line knowledge.

The executable can also be dragged onto the `.cmd` file.

## PowerShell use

```powershell
Set-Location "C:\path\to\ied-backup-tool"

.\scripts\Collect-Diagnostics.ps1 `
    -ExecutablePath "C:\path\to\IED_Backup_Manager.exe"
```

If the local execution policy blocks the script:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass `
    -File ".\scripts\Collect-Diagnostics.ps1" `
    -ExecutablePath "C:\path\to\IED_Backup_Manager.exe"
```

The application runs for 10 seconds by default. The collector attempts a normal
window close and never force-terminates the process. Use
`-KeepApplicationOpen` to leave the application open after collection.

The ZIP contains the update-check conclusion, executable version and SHA256,
sanitized isolated logs, limited system details, and network checks. User,
computer, and path values are replaced with placeholders.

The maintainer should review every file before using the ZIP in a public issue.
A full-window screenshot may be requested separately after sensitive data is
removed.
