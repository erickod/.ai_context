---
name: dod
description: >
  Definition of Done — critérios obrigatórios que uma TASK deve atender para ser considerada
  concluída. Use esta skill para verificar se uma TASK está pronta para ser declarada done,
  ao finalizar implementação, ou quando houver dúvida sobre completude. Controle de execução
  e loop de validação técnica são orquestrados pelo AGENTS.md.
---
ROLE: dod
PRINCIPLE: "Done" = entregável correto, validado e verificável. Sem conclusões parciais, implícitas ou subjetivas.

CRITERIA:
  objetivo:     completamente atendido · sem parciais/pendentes · coerente com escopo aprovado
  aceitação:    todos satisfeitos · cada um com evidência verificável · DENY: ignorar ou reinterpretar
  design:       proposto antes da implementação · validado explicitamente · alterações registradas no log
  testes.unit:  escritos conforme TASK · cobrem sucesso e falha · determinísticos · todos passando
  testes.integ: escritos conforme TASK · validam interação entre componentes · não violam DB.md/WORKFLOWS.md · todos passando
  impl:         segue GUIDELINES.md · não viola ROLES · não sai do escopo · sem efeitos colaterais não documentados
  regressões:   nenhuma introduzida · impactos indiretos avaliados · riscos registrados no log
  log:          atualizado · decisões técnicas registradas · bloqueios/mudanças/validações constam · append-only

DECLARATION:
  done SE: todos CRITERIA atendidos · Test Gate (AGENTS.md) satisfeito · estado atualizado para `done`
  DENY: conclusão parcial · done com testes falhando · done por interpretação subjetiva

VIOLATION:
  task permanece: em execução · ou marcada como `blocked`
  obrigatório: indicar explicitamente o que falta para atingir o DOD
