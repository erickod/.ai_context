---
name: jira-task-scope
description: >
  Consulta a API do Jira Cloud para extrair resumo e descrição de uma issue
  a partir da sua chave (ex: PROJ-123 · LEND-456).
  Ativar quando o usuário mencionar chave de tarefa Jira · pedir "escopo" ·
  "detalhes" · "contextualizar" · "buscar" issue · antes de desenvolvimento ·
  documentação · revisão · planejamento.
---
ROLE: jira-task-scope
ENV SOURCES: JIRA_SERVER_URL · JIRA_USER_EMAIL · JIRA_API_TOKEN
PRINCIPLE: sem escopo confirmado → sem execução técnica.

PRE:
  - verificar vars: JIRA_SERVER_URL · JIRA_USER_EMAIL · JIRA_API_TOKEN
  - identificar <issue_key> na solicitação do usuário (ex: LEND-7146)
  - confirmar lib instalada: pip install jira

DO:
  - executar: python scripts/get_scope.py <issue_key>
  - capturar stdout → JSON
  - extrair campos: summary · description
  - tratar description=null → registrar ausência · prosseguir sem falha
  - se description longa → sumarizar antes de repassar ao contexto principal
  - usar summary · description como contexto para tarefa solicitada

OUTPUT.ok:
  format: JSON · stdout
  fields: key · summary · description · status=ok

OUTPUT.err:
  format: JSON · stdout
  fields: key · status=error · error_code · message

ERROR_CODES:
  NOT_FOUND        → issue key inexistente · ação: confirmar chave com usuário
  AUTH_FAILED      → credenciais inválidas | sem permissão · ação: checar vars de ambiente
  CONNECTION_ERROR → falha de rede | URL incorreta · ação: verificar JIRA_SERVER_URL
  UNKNOWN          → erro inesperado da API · ação: inspecionar campo message

DENY:
  ✗ exibir JIRA_API_TOKEN em logs · respostas · outputs
  ✗ buscar campos além de summary · description
  ✗ iniciar trabalho técnico sem escopo capturado com status=ok
  ✗ tratar description=null como erro fatal
  ✗ repassar description longa sem sumarização prévia

GATE.out: vars=configuradas · issue_key=identificada · status=ok ·
