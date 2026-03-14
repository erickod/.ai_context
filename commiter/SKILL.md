---
name: commiter
description: >
  Padronização de mensagens git. Use em commits, merges, reverts e criação de branches.
---
ROLE: commiter
PRINCIPLE: Toda mensagem git é intencional, atômica e rastreável.

TRIGGERS:
  + git commit · merge --squash · switch -c · checkout -b

COMMITS:
  format: Conventional Commits
  rule:   descreve o que mudou — nunca o porquê abstrato
  order:  sem dependência → com dependência

PREFIXES:
  feat · fix · style · chore · refactor · test · docs

BRANCH:
  format: kebab-case · descritivo · curto

DENY:
  - commits em lote
  - mensagens genéricas ou que não reflitam o conteúdo
  - mensagens extras · Co-Authored-By · nomes internos (TS-1, UT-1, IT-1)
  - nomes genéricos · espaços · caracteres especiais em branch

REF: chamado por → ENG (`@[.ai_context/eng]`)
