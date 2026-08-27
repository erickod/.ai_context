---
name: github-pr-open
description: >
  Abre PR no GitHub via CLI lendo pull_request_template.md do repositório,
  preenchendo com contexto do diff e da issue Jira, e executando gh pr create.
  Ativar quando usuário pedir "abrir PR" · "criar PR" · "subir PR" · "open PR" ·
  informar issue_key + branch pronta para revisão.
  Depende de jira-task-scope com status=ok.
---
ROLE: github-pr-open
SOURCES: jira-task-scope → git diff → pull_request_template.md
PRINCIPLE: PR mínimo · assertivo · revisável sem contexto externo.

PRE:
  - jira-task-scope executado com status=ok → summary · description disponíveis
  - branch atual com commits prontos para revisão
  - gh CLI autenticado: gh auth status
  - confirmar <issue_key> (ex: LEND-7164)

DO:
  - derivar título: [feat|fix]/lend-<issue_number>-<slug-descritivo>¹
  - analisar git diff → extrair mudanças relevantes em bullet points (en-us · conciso)
  - preencher pull_request_template.md:
      ## Description  → 1–2 frases do propósito da mudança
      Changes         → bullets derivados do diff · mínimos · assertivos
      ## Jira Card    → LEND-<issue_number> com link: <JIRA_SERVER_URL>/browse/LEND-<issue_number>
      ## How tested   → manter padrão do template | ajustar se contexto exigir
  - executar:
      gh pr create \
        --title "<título>" \
        --body "$(cat pull_request_template.md preenchido)" \
        --base <base_branch> \
        --head <current_branch>

TITLE:
  format:  [feat|fix]/lend-<issue_number>-<description>
  rules:   kebab-case · en-us · máx 72 chars · sem artigos · descritivo

BODY:
  lang:    en-us
  tone:    conciso · assertivo · sem preâmbulo
  fields:
    description → propósito da mudança · máx 2 frases
    changes     → bullets do diff · somente o que mudou · sem "e" · sem redundância
    jira_card   → link completo: <JIRA_SERVER_URL>/browse/<issue_key>
    how_tested  → comandos existentes | ajuste mínimo se necessário

DENY:
  ✗ abrir PR sem jira-task-scope status=ok
  ✗ título sem prefixo feat|fix
  ✗ título em pt-BR · camelCase · snake_case
  ✗ description vaga · genérica · que não reflita o diff
  ✗ omitir link Jira no campo ## Jira Card
  ✗ alterar estrutura do pull_request_template.md
  ✗ expor JIRA_API_TOKEN · credenciais em qualquer campo do PR

GATE.out: título=válido · body=template-preenchido · jira-link=presente · gh-cli=autenticado → PR aberto

---
¹ slug: lowercase · kebab-case · máx 5 palavras · derivado do summary Jira | diff
](ROLE: github-pr-open
SOURCES: jira-task-scope → git diff → pull_request_template.md
PRINCIPLE: PR mínimo · assertivo · revisável sem contexto externo.

PRE:
  - jira-task-scope executado com status=ok → summary · description disponíveis
  - branch atual com commits prontos para revisão
  - gh CLI autenticado: gh auth status
  - confirmar <issue_key> (ex: LEND-7164)
  - localizar template: cat .github/pull_request_template.md | pull_request_template.md¹

READ.template:
  - ler pull_request_template.md → mapear seções:
      ## Description  → slot: propósito
      **Changes:**    → slot: bullets do diff
      ## Jira Card    → slot: link da issue
      ## How tested   → slot: comandos de teste
  - preservar estrutura exata · headings · marcadores · espaçamento

READ.diff:
  - executar: git diff <base_branch>...<current_branch>
  - identificar: arquivos alterados · funções adicionadas|removidas · comportamento novo
  - comprimir em bullets: en-us · ação + objeto · máx 1 linha por mudança relevante

FILL.template:
  ## Description:
    - 1–2 frases · propósito da mudança · derivado de summary Jira + diff
    - en-us · sem "this PR" · sem preâmbulo
  **Changes:**:
    - bullets derivados de READ.diff
    - formato: `* <verb> <object> [context]`
    - somente mudanças observáveis · sem detalhe de implementação interna
  ## Jira Card:
    - substituir "LEND-" por: [<issue_key>](<JIRA_SERVER_URL>/browse/<issue_key>)
  ## How tested?:
    - manter comandos padrão do template
    - adicionar comando específico somente se contexto exigir

TITLE:
  format: [feat|fix]/lend-<issue_number>-<slug>
  rules:  kebab-case · en-us · máx 72 chars · sem artigos · slug derivado do summary Jira | diff²

EXECUTE:
  gh pr create \
    --title "<TITLE>" \
    --body "<FILL.template>" \
    --base <base_branch> \
    --head <current_branch>

DENY:
  ✗ abrir PR sem jira-task-scope status=ok
  ✗ pular READ.template · preencher de memória
  ✗ alterar estrutura · headings · ordem de seções do template
  ✗ título sem prefixo feat|fix
  ✗ título em pt-BR · camelCase · snake_case
  ✗ description vaga · genérica · que não reflita o diff
  ✗ omitir link Jira no campo ## Jira Card
  ✗ expor JIRA_API_TOKEN · credenciais em qualquer campo do PR
  ✗ expor quaisquer credenciais ou secrets em qualquer campo do PR
  ✗ mensagens extras · Co-Authored-By · nomes internos (TS-1, UT-1, IT-1)


GATE.out: template=lido · diff=analisado · slots=preenchidos · título=válido · jira-link=presente · gh-cli=autenticado → PR aberto

---
¹ fallback: pull_request_template.md na raiz do repo
² slug: lowercase · kebab-case · máx 5 palavras)

