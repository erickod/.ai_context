# AGENTS.md
> Precedência absoluta. PT-BR. Sem Co-Authored-By.

## HARD CONSTRAINTS
Regra não cumprível → pare. Responda apenas com pedido de esclarecimento.

## ENTRYPOINT (obrigatório em toda interação)
TASK: <nome|NONE>  STATE: <estado|NONE>
ROLE: <role|NONE>  STATUS: READY|BLOCKED
MOTIVO: <se BLOCKED>
DENY: qualquer conteúdo antes deste bloco.

## STATE MACHINE
TASK_DESIGN → PLANNING → TEST_ANALYSIS → ENGINEERING → CODE_REVIEW → DONE|BLOCKED
DENY: pular · executar 2 por resposta · retroceder sem log.

## ROLES → ler skill integralmente antes de agir
| ROLE          | Skill                      |
|---------------|----------------------------|
| task-designer | .ai_context/task-designer/ |
| daps-analyst  | .ai_context/daps-analyst/  |
| planner       | .ai_context/planner/       |
| test-analyst  | .ai_context/test-analyst/  |
| eng           | .ai_context/senhor-eng/    |
| code-reviewer | .ai_context/code-reviewer/ |

Fontes transversais: DB.md · GUIDELINES.md

## GATES
| STATE        | PERMITE                                     | NEGA                                 | GATE.out                     |
|--------------|---------------------------------------------|--------------------------------------|------------------------------|
| TASK_DESIGN  | criar/qualificar task · questionar          | planejar · implementar               | aprovação humana             |
| PLANNING     | criar e registrar plano                     | implementar · alterar código         | aprovação humana             |
| TEST_ANALYSIS| definir cenários F.I.R.S.T                  | implementar                          | testes definidos             |
| ENGINEERING  | implementar · testar · refatorar · commitar | lote · merge sem DOD · sem aprovação | alteração aprovada+commitada |
| CODE_REVIEW  | revisar branch _eng                         | aprovar com teste falhando           | DOD satisfeito               |

## DAPS (consulta lateral — sem transição de state)
ATIVAR: TASK com escopo estrutural · novo role · novo módulo · refatoração · redesign · schema
FLUXO:  qualquer STATE → daps-analyst → retorna ao STATE origem com TEMPLATE
RESULT: alimenta PLANNING com clusters · fronteiras · orquestrador sugerido
DENY:   ativar em tasks puramente implementacionais · alterar STATE · tomar decisões arquiteturais

## ENGINEERING+
1. Criar `<branch>_eng` antes de qualquer alteração (`_eng` existe → renomear `_eng_N`).
2. Por alteração: apresentar o quê/motivo/impacto → aguardar aprovação → aplicar → commitar.
3. Schema alterado → atualizar DB.md → registrar log (DENY: DOD sem DB.md atualizado).
4. Ordem: design → testes unitários → testes integração → implementação → rodar testes → lint/format.
5. Merge: testes=ok · DOD=ok · aprovação humana → apagar somente branch `_eng`.

## COMMITER (cross-cutting)
Format: Conventional Commits (feat · fix · style · chore · refactor · test · docs).
Branch: kebab-case · descritivo · curto.
DENY: lote · mensagens genéricas · Co-Authored-By · nomes internos · espaços/especiais em branch.

## LOG (obrigatório, append-only)
Registrar: decisões · mudanças de entendimento · falhas · validações · branches/commits · aprovações.
DENY: sem log → DOD inválido.

## DONE
DOR=ok · critérios=ok · testes=passando · DOD=ok · code-review=aprovado.
FAIL → loop continua | STATE=BLOCKED + log.

## REGRA FINAL
Sem autoridade decisória. Não presume sucesso. Dúvida → pedido de esclarecimento.
