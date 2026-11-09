# ADR 009 — Publicação de release por publicador com gates

- Estado: Aceita
- Data: 2026-11-08 (registro retrospectivo)
- Responsável: mantenedor do projeto
- Substitui: nenhuma
- Substituída por: nenhuma

## Contexto

Executável, ferramenta de diagnóstico, notas e hashes precisam corresponder ao
mesmo commit aprovado. Criar release antes do CI da tag pode expor artefatos
sem a validação prevista.

## Decisão

`scripts/release.ps1` gera e verifica os artefatos locais. O
`PUBLISH_RELEASE.ps1` gerado controla a tag e a publicação depois de confirmar
worktree limpo, `HEAD == origin/master`, GitHub CLI autenticado, lint/testes,
hashes, notas, assets e CI de `master` no commit exato.

O publicador envia/reutiliza a tag, aguarda o CI da tag no mesmo commit, mostra
relatório `CORRETO`/`INCORRETO` e solicita confirmação final. Somente resposta
afirmativa com gates aprovados permite `gh release create --verify-tag`.
Releases usam título e tag `vX.Y.Z`. Artefatos locais permanecem ignorados pelo
Git.

## Consequências

- tag não deve ser criada manualmente no fluxo normal;
- CI de tag com falha pode deixar a tag para diagnóstico, mas não um release;
- build local precisa ser reproduzível e livre de DLLs externas coletadas pelo
  ambiente;
- publicação e uploads continuam dependendo de autorização humana explícita.

## Evidências

- `docs/RELEASE.md`;
- `scripts/release.ps1`;
- `scripts/PUBLISH_RELEASE.Template.ps1`;
- `scripts/Check-ReleaseCi.ps1`;
- `.github/workflows/ci.yml`.
