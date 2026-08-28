---
name: github-pr-open
description: Abre PR no GitHub via CLI com dados do Jira/diff e vincula a stacked PRs via gh-stack.
triggers: ["abrir PR", "criar PR", "subir PR", "open PR", "empilhar PR", "stacked PR", "gh stack"]
---

ROLE: github-pr-open
PRINCIPLE: PR autoexplicativo, conciso e estritamente em en-US. Stack sempre perguntada, nunca assumida.

PIPELINE:

  1. PRE-FLIGHT:
     - Jira: status=ok via `jira-task-scope` (summary + description disponíveis).
     - Git/CLI: `gh auth status` válido; branch com commits prontos; base identificada (padrão: `main`).
     - Template: carregar `.github/pull_request_template.md` (fallback: raiz).

  2. PAYLOAD GENERATION:
     - Title: `[feat|fix]/lend-<issue_number>-<slug>` (kebab-case, en-US, sem artigos, máx 72 chars).
     - Body (injetar no template preservando seções/headings):
       * ## Description: 1–2 frases do propósito (Jira summary + diff). Sem preâmbulos como "this PR".
       * **Changes:**: Bullets no formato `* <verb> <object>` baseados apenas em mudanças comportamentais observáveis.
       * ## Jira Card: `[<issue_key>](<JIRA_SERVER_URL>/browse/<issue_key>)`.
       * ## How tested: Manter comandos padrão; incluir novos apenas se indispensáveis.

  3. EXECUTE:
     gh pr create --title "<TITLE>" --body "<BODY>" --base <base_branch> --head <current_branch>

  4. POST-EXECUTE (STACK):
     - Perguntar: "Essa PR faz parte de uma stack? Se sim, informe os números das PRs da base ao topo (bottom -> top)."
     - Se informado [PR_BASE, PR_TOPO...]:
       gh stack link <PR_BASE> <PR_TOPO>
       gh stack checkout <STACK_ID_RETORNADO>
       gh stack view --short
     - Se não: Finalizar (PR simples).

GUARDS & RESTRIÇÕES:
  - NUNCA vazar segredos, tokens ou IDs internos/tags de teste (TS-1, UT-1).
  - NUNCA traduzir título/body para pt-BR ou alterar estrutura do template.
  - NUNCA inventar IDs de stack ou rodar `gh stack link` fora da ordem bottom -> top.
  - NUNCA executar merge sem todas as PRs da stack estarem aprovadas.

STACK UTILS (Sob demanda):
  - Inspecionar: `gh stack view`
  - Adicionar/Sincronizar: `gh stack add <branch>` | `gh stack sync`
  - Publicar/Rebasear: `gh stack submit` | `gh stack rebase`
  - Finalizar: `gh stack merge` (bottom -> top) | `gh stack unstack`

GATE.out:
  PR simples:
    título=válido · body=template-preenchido · jira-link=presente · gh-cli=autenticado · ask-stack=respondido(não|vazio) → PR aberto
  PR stacked:
    acima + ask-stack=respondido(sim) · stack=criada|atualizada · ordem=bottom→top confirmada · gh-stack-view=validado → PR(s) aberta(s) em stack
