# DOD.md — Definition of Done

Doc de referência (não é skill invocável). Critérios obrigatórios que uma TASK deve
atender para ser considerada concluída. Consultado por `eng` e `code-reviewer` ao
avaliar GATE.out. Controle de execução e loop de validação técnica são orquestrados
pela skill agentsmd.

ROLE: dod
PRINCIPLE: "Done" = entregável correto, validado e verificável. Sem conclusões parciais, implícitas ou subjetivas.

CRITERIA:
  objetivo:     completamente atendido · sem parciais/pendentes · coerente com escopo aprovado
  aceitação:    todos satisfeitos · cada um com evidência verificável · DENY: ignorar ou reinterpretar
  design:       proposto antes da implementação · validado explicitamente · alterações registradas no log
  testes.unit:  escritos conforme TASK · cobrem sucesso e falha · determinísticos · todos passando
  testes.integ: escritos conforme TASK · validam interação entre componentes · não violam DB.md/WORKFLOWS.md · todos passando
  impl:         segue ~/.agents/skills/guidelines/SKILL.md · não viola ROLES · não sai do escopo · sem efeitos colaterais não documentados
  regressões:   nenhuma introduzida · impactos indiretos avaliados · riscos registrados no log
  log:          atualizado · decisões técnicas registradas · bloqueios/mudanças/validações constam · append-only

DECLARATION:
  done SE: todos CRITERIA atendidos · Test Gate (agentsmd) satisfeito · estado atualizado para `done`
  DENY: conclusão parcial · done com testes falhando · done por interpretação subjetiva

VIOLATION:
  task permanece: em execução · ou marcada como `blocked`
  obrigatório: indicar explicitamente o que falta para atingir o DOD
