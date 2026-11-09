# Prompt para retomar o desenvolvimento

```text
Quero retomar o desenvolvimento de <NOME_DO_PROJETO> neste computador.

Antes de alterar qualquer arquivo, faça uma descoberta somente leitura.

Leia integralmente:
- AGENTS.md;
- <INDICE_DA_DOCUMENTACAO>;
- <ESTADO_ATUAL>;
- <ARQUITETURA>;
- <AMBIENTE>;
- <ROADMAP>;
- <CATALOGO_DE_ADRS> e as ADRs relevantes;
- <GUIA_DE_CONTRIBUICAO_OU_RUNBOOK>.

Confira branch, Git status, versão, estrutura de código/testes, comandos reais,
roadmap, pendências, próximo passo e possíveis contradições documentais.

Se o ambiente ainda não existir, informe os comandos necessários antes de
instalar qualquer coisa. Não modifique código, documentação, configuração, Git
ou serviços externos nesta primeira etapa.

Ao terminar, apresente:
- compreensão do produto;
- arquitetura e invariantes;
- estado atual;
- próxima prioridade;
- bloqueios e decisões que dependem de mim;
- plano pequeno e verificável.

Não dependa de conversas anteriores. Use o repositório como fonte de verdade.
```

## Iniciar trabalho depois da análise

```text
A análise está correta. Trabalhe somente em <ESCOPO_APROVADO>.

Antes de implementar, identifique arquivos afetados, testes, critérios de
aceitação, riscos e decisões que precisam de confirmação. Não faça commit,
push, tag, publicação ou implantação sem autorização explícita.
```
