# Releases

Cada versao publicada deve ter uma pasta propria:

```text
releases/
├─ v1.0.0/
│  ├─ IED Backup Manager v1.0.0.exe
│  └─ RELEASE_NOTES.md
├─ v1.0.1/
│  ├─ IED Backup Manager v1.0.1.exe
│  └─ RELEASE_NOTES.md
```

## Padrao

- O nome da pasta deve seguir a tag Git: `vX.Y.Z`.
- O executavel deve manter a mesma versao no nome.
- Cada versao deve ter um `RELEASE_NOTES.md`.
- A tag Git deve apontar para o commit que representa aquela versao.

## Rollback

Para voltar a usar uma versao anterior, use o executavel da pasta correspondente.
Exemplo:

```text
releases/v1.0.0/IED Backup Manager v1.0.0.exe
```
