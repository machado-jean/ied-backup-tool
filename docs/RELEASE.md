# Build e publicação de release

Este é o procedimento canônico para gerar `IED_Backup_Manager.exe` e publicar
uma versão no GitHub. A publicação, criação de tag, push e upload exigem
autorização explícita do mantenedor.

## 1. Definir a versão

- patch: correção, compatibilidade, estabilidade, diagnóstico, documentação ou
  melhoria do processo de release;
- minor: novo comportamento funcional ou capacidade relevante;
- major: quebra intencional de fluxo ou compatibilidade.

## 2. Atualizar fontes de verdade

Sempre revisar:

- `src/version.py`;
- versão atual em `README.md` e `README.en.md`;
- `docs/ESTADO_ATUAL.md` e `docs/CURRENT_STATE.en.md`;
- `docs/PLANO_MELHORIAS.md` e `docs/ROADMAP.en.md`;
- documentos públicos afetados;
- ADRs e arquitetura quando houver decisão durável;
- `releases/vX.Y.Z/RELEASE_NOTES.md` local.

Não reescrever notas históricas de versões antigas. Exemplos, notas e imagens
públicas devem usar somente dados fictícios ou sanitizados. Quando a interface
mudar de forma material, regenerar as capturas pelo script versionado, usando
o workspace artificial em caminho genérico, e inspecionar visualmente cada PNG.

## 3. Validar antes do build

```powershell
.\.venv\Scripts\python.exe -m ruff check .
.\.venv\Scripts\python.exe -m pytest
git diff --check
```

Scripts PowerShell alterados devem passar pelo parser de
`System.Management.Automation.Language.Parser` antes da execução.

## 4. Gerar e verificar

```powershell
.\scripts\release.ps1
```

O script deve:

- executar lint e testes, salvo quando `-SkipTests` suceder validação
  equivalente na mesma tarefa de release;
- abortar quando Ruff, Pytest ou PyInstaller falhar;
- usar e remover temporários controlados dentro do projeto para evitar falhas
  silenciosas de permissão do diretório temporário do Windows;
- sanitizar `PATH` durante o PyInstaller para não coletar DLLs de ferramentas
  externas;
- gerar `IED_Backup_Manager.exe` em modo `--onefile`;
- criar ou preservar as notas da versão;
- gerar `SHA256SUMS.txt` e `PUBLISH_RELEASE.ps1`;
- empacotar a ferramenta de diagnóstico compatível;
- executar `PUBLISH_RELEASE.ps1 -VerifyOnly`;
- remover `.spec`, `build/` e `dist/` depois do sucesso.

Artefatos esperados:

```text
releases/vX.Y.Z/IED_Backup_Manager.exe
releases/vX.Y.Z/IED_Backup_Manager_Diagnostics_Tool.zip
releases/vX.Y.Z/RELEASE_NOTES.md
releases/vX.Y.Z/SHA256SUMS.txt
releases/vX.Y.Z/PUBLISH_RELEASE.ps1
```

`releases/` permanece ignorado pelo Git e nunca deve ser adicionado à força.
O título do GitHub Release e a tag usam apenas `vX.Y.Z`.

## 5. Smoke test

Abrir o executável empacotado usando diretórios isolados para projeto,
configuração e `LOCALAPPDATA`. Confirmar:

- janela principal aberta;
- workers encerrados corretamente;
- fechamento com código zero;
- saída normal do event loop registrada;
- ausência de novo crash da aplicação no Windows;
- ausência de marcador de sessão órfão.

Remover somente o diretório de smoke test criado explicitamente.

## 6. Conferência local final

Confirmar:

- todos os artefatos presentes;
- `-VerifyOnly` aprovado;
- `.spec`, `build/` e `dist/` ausentes;
- tamanho do executável coerente com a versão anterior;
- SHA256 local correspondente;
- versões CMD/PS1 iguais dentro da ferramenta de diagnóstico;
- `releases/` ainda ignorado;
- documentação e screenshots livres de dados operacionais.

O handoff deve informar caminhos, contagem de testes, tamanhos, hashes,
resultado do smoke test e se houve publicação.

## 7. Commit, push e publicação

Depois da validação do usuário, commit e push das alterações rastreadas podem
ser feitos quando explicitamente autorizados. No fluxo normal, não criar nem
enviar manualmente a tag; o publicador gerado é o responsável.

```powershell
.\releases\vX.Y.Z\PUBLISH_RELEASE.ps1 -VerifyOnly
.\releases\vX.Y.Z\PUBLISH_RELEASE.ps1
```

O publicador exige:

- worktree limpo;
- `HEAD == origin/master`;
- GitHub CLI autenticado;
- lint e testes locais aprovados;
- hashes, notas e artefatos corretos;
- CI de `master` aprovado no commit exato.

Depois desses gates, ele envia ou reutiliza a tag, aguarda o CI da tag no mesmo
commit, imprime o relatório `CORRETO`/`INCORRETO` e pede confirmação final. O
GitHub Release somente pode ser criado com resposta afirmativa e CI da tag
aprovado. Uma falha pode deixar a tag para diagnóstico, mas não deve publicar
release nem assets.

## 8. Registro pós-publicação

Registrar no estado atual ou nas notas aplicáveis:

- versão, tag e commit;
- URL e resultado do CI;
- assets publicados;
- tamanhos e hashes;
- resultado do teste da atualização;
- limitações ou ações de acompanhamento.
