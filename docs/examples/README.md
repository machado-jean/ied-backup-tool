# Example Files

This folder contains artificial files for public documentation screenshots and
manual testing. They do not contain real engineering data.

## Folders

- `sample-workspace/`: source files that simulate supported IED project backups.
- `sample-storage/ATU/`: sample current-backup folder.
- `sample-storage/HIS/`: sample history folder with old ZIPs for `Limpeza HIS`.

## Suggested GUI Test

Run the application against the sample workspace:

```powershell
.\.venv\Scripts\python.exe -m src.gui.app --project-dir ".\docs\examples\sample-workspace"
```

In `Configurações`, use:

```text
Colaborador: COLABORADOR-EXEMPLO
Pasta ATU: docs\examples\sample-storage\ATU
Pasta HIS: docs\examples\sample-storage\HIS
```

Then select the desired IED types and the `TAF` stage. For INGETEAM examples,
use software version `5.5.4`.

These files are intended for preview and screenshot generation. Avoid using
them as technical reference for real vendor file formats.
