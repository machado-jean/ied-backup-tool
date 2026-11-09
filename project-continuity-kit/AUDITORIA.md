# Auditoria genérica de continuidade

Execute esta auditoria antes de preencher os modelos. A primeira etapa é
somente leitura: não mover, excluir, publicar nem versionar arquivos.

## 1. Identificar o projeto

- objetivo e usuários;
- tecnologias e plataformas;
- executáveis, serviços ou bibliotecas produzidos;
- versão atual e branch principal;
- responsável e restrições de acesso;
- ambientes externos dos quais depende.

## 2. Auditar Git, quando existir

```powershell
git status --short --branch
git remote -v
git branch --show-current
git log -10 --oneline --decorate
git tag --sort=-version:refname
git status --ignored --short
```

Confirmar commits não enviados, mudanças locais, arquivos não rastreados,
ignorados, tags, releases, submódulos e Git LFS. Não executar limpeza ou reset
destrutivo durante a descoberta.

## 3. Revisar conversas

Extrair apenas fatos materiais ainda não preservados:

- decisões e justificativas;
- requisitos, invariantes e não objetivos;
- causas de correções difíceis;
- compatibilidade, segurança e recuperação;
- comandos confiáveis;
- pendências e próximos passos;
- evidências de validação relevantes.

Não copiar transcrições completas, tentativas descartadas, saídas rotineiras ou
segredos. Conferir primeiro se o fato já existe no código, teste, commit, issue,
release ou documentação.

## 4. Inventariar arquivos locais

Classificar cada grupo como:

- fonte ou documentação indispensável;
- configuração de exemplo;
- configuração local recriável;
- dado operacional;
- segredo;
- artefato versionado;
- arquivo grande necessário;
- ambiente reproduzível;
- temporário ou descartável.

Definir o destino: Git público, Git privado, Releases, Git LFS, armazenamento
privado criptografado, gerenciador de segredos ou recriação.

## 5. Encontrar lacunas documentais

Verificar se uma pessoa sem contexto consegue descobrir:

- o que o projeto faz;
- como instalar e executar;
- como testar e gerar build;
- arquitetura e fontes de verdade;
- invariantes e limites de segurança;
- estado atual e próximo passo;
- como restaurar dados ou ambiente;
- como publicar uma versão;
- quais decisões não devem ser redescobertas.

Criar somente os documentos necessários para preencher lacunas reais.

## 6. Revisar segurança

Procurar credenciais, dados pessoais, caminhos internos, arquivos de clientes,
screenshots, dumps, bancos e artefatos grandes antes do primeiro push. Revisar
também o histórico quando houver suspeita de exposição anterior.

## 7. Validar

- lint e formatação;
- testes relevantes e bateria completa quando possível;
- build e smoke test;
- links Markdown;
- versões e comandos documentados;
- `git diff --check`;
- busca por placeholders não preenchidos.

## 8. Comprovar restauração

Clonar em local limpo, seguir apenas os documentos versionados, reconstruir o
ambiente e executar testes/build. Registrar qualquer dependência silenciosa da
máquina antiga e corrigir a documentação.

## Saída esperada da auditoria

- estado do Git;
- conhecimento relevante encontrado nas conversas;
- arquivos locais que podem ser perdidos;
- riscos e dados sensíveis;
- documentos propostos;
- armazenamento recomendado por categoria;
- validações executadas;
- decisões que dependem do responsável;
- ações externas ainda não autorizadas ou concluídas.
