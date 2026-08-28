---
name: github-pr-open
description: >
  Abre PR no GitHub via CLI lendo pull_request_template.md do repositório,
  preenchendo com contexto do diff e da issue Jira, e executando gh pr create.
  Depois de abrir, pergunta se a PR faz parte de uma stack com outra(s) PR(s)
  já aberta(s) e, se sim, registra a cadeia via `gh stack link`.
  Ativar quando usuário pedir "abrir PR" · "criar PR" · "subir PR" · "open PR" ·
  "empilhar PR" · "stacked PR" · "gh stack" · informar issue_key + branch pronta
  para revisão. Depende de jira-task-scope com status=ok.
---
ROLE: github-pr-open
SOURCES: jira-task-scope → git diff → pull_request_template.md → gh-stack¹ (se usuário confirmar stack)
PRINCIPLE: PR mínimo · assertivo · revisável sem contexto externo. Stack nunca assumida — sempre perguntada.

PRE:
  - jira-task-scope executado com status=ok → summary · description disponíveis
  - branch atual com commits prontos para revisão
  - gh CLI autenticado: gh auth status
  - confirmar <issue_key> (ex: LEND-7164)
  - localizar template: cat .github/pull_request_template.md | pull_request_template.md²
  - base_branch: main | branch de integração, salvo se usuário já indicar que esta PR nasce de
    outra branch com PR aberta (predecessora) — nesse caso base_branch = predecessora

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
  rules:  kebab-case · en-us · máx 72 chars · sem artigos · slug derivado do summary Jira | diff³

EXECUTE:
  gh pr create \
    --title "<TITLE>" \
    --body "<FILL.template>" \
    --base <base_branch> \
    --head <current_branch>

ASK.stack (sempre, depois de EXECUTE):
  - perguntar ao usuário: "Essa PR faz parte de uma stack com outra(s) PR(s) já aberta(s)?
    Se sim, informe os números, da base (bottom) pro topo (top)."
  - resposta com números de PR → STACK.link
  - resposta negativa | sem resposta → encerra, PR permanece única (GATE.out: PR simples)
  - exceção: usuário já pediu stack explicitamente antes de EXECUTE, citando uma branch
    predecessora sem PR ainda → pular a pergunta, ir direto a STACK.new

STACK.link (PRs já abertas, números fornecidos pelo usuário):
  gh stack link <pr-numero-base> <pr-numero-topo> [...]   # ordem sempre bottom → top
  gh stack checkout <stack-number>⁴                        # importa tracking local
  gh stack view --short                                    # confirma a cadeia com o usuário

STACK.new (exceção — predecessora ainda sem PR, usuário já confirmou stack antes de EXECUTE):
  gh stack link <branch-predecessora> <branch-atual>       # cria PR(s) com base chaining correto

STACK.manage (usar só quando o usuário pedir explicitamente):
  gh stack view                     # status visual: ✓ merged · ◎ queued · ○ open · ⚠ needs rebase
  gh stack add <nova-branch>        # empilha uma nova branch no topo da stack atual
  gh stack sync                     # sincroniza tracking local com o estado remoto
  gh stack submit                   # push de todas as branches ativas + cria/atualiza as PRs
  gh stack rebase                   # rebase da cadeia inteira, branch a branch
  gh stack merge                    # merge da stack inteira, em ordem, bottom → top
  gh stack unstack                  # remove o agrupamento (local + GitHub), PRs continuam existindo

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
  ✗ pular ASK.stack · assumir sozinho (sim ou não) se a PR entra numa stack
  ✗ gh stack link fora de ordem bottom → top
  ✗ gh stack merge com qualquer PR da stack ainda não aprovada
  ✗ inventar <stack-number> · sempre obter da saída de gh stack link ou de gh stack view

GATE.out:
  PR simples:   título=válido · body=template-preenchido · jira-link=presente · gh-cli=autenticado → PR aberto
  PR stacked:   acima + ASK.stack respondida · stack=criada|atualizada · ordem=bottom→top confirmada · gh stack view reflete a cadeia → PR(s) aberta(s) em stack

---
¹ extensão `gh-stack` (github/gh-stack) — confirmar instalada: `gh extension list | grep stack`; senão `gh extension install github/gh-stack`
² fallback: pull_request_template.md na raiz do repo
³ slug: lowercase · kebab-case · máx 5 palavras · derivado do summary Jira | diff
⁴ stack-number: nunca inventar — vem da saída de `gh stack link` (ex.: "Created stack with 2 PRs (stack #478)") ou de `gh stack view`
