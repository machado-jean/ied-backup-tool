# Checklist de transferência para outro computador

## Antes da transferência

- [ ] O repositório remoto contém todos os commits necessários.
- [ ] A branch principal e o remoto correto estão documentados.
- [ ] O working tree está limpo ou todas as mudanças locais estão explicadas.
- [ ] Arquivos ignorados e não rastreados foram classificados.
- [ ] Segredos e dados operacionais estão fora do Git.
- [ ] Dados privados necessários possuem backup autorizado e restaurável.
- [ ] Dependências e versões de ferramentas estão documentadas.
- [ ] Instalação, execução, testes e build possuem comandos verificáveis.
- [ ] `AGENTS.md` aponta para as fontes de verdade.
- [ ] O estado atual e o próximo passo estão registrados.
- [ ] Decisões duráveis estão documentadas.
- [ ] Releases e artefatos necessários estão preservados.
- [ ] Links e placeholders da documentação foram verificados.
- [ ] Testes proporcionais ao risco foram executados.

## No novo computador

- [ ] Instalar Git e o toolchain documentado.
- [ ] Clonar o repositório em uma pasta limpa.
- [ ] Confirmar branch, remoto e commit esperado.
- [ ] Recriar o ambiente sem copiar caches da máquina antiga.
- [ ] Instalar dependências pelas fontes versionadas.
- [ ] Executar lint, testes e build.
- [ ] Executar smoke test ou fluxo mínimo do produto.
- [ ] Restaurar somente dados privados realmente necessários.
- [ ] Usar o prompt de retomada.
- [ ] Confirmar que o próximo trabalho pode começar sem a conversa antiga.

## Critério final

A transferência está comprovada quando o projeto pode ser entendido, testado e
executado usando apenas o repositório e os backups privados explicitamente
documentados.
