---
name: dor
description: >
  Definition of Ready — critérios obrigatórios que uma TASK deve atender antes de qualquer
  execução pela IA. Use esta skill para verificar se uma TASK está pronta para iniciar, ao
  receber uma nova TASK, ou quando houver dúvida sobre completude. Se qualquer critério não
  for atendido, interromper e solicitar esclarecimentos.
---
ROLE: dor
PRINCIPLE: Task não qualificada → interromper e solicitar esclarecimentos. Sem exceções.

CRITERIA:
  objetivo:   único e bem definido · sem múltiplas intenções misturadas
  escopo:     dentro explicitado · fora explicitado
  aceitação:  critérios verificáveis · DENY: subjetivos ("funcionar bem" · "rápido")
  contexto:   linguagem/stack/módulo claros · dependências conhecidas
  restrições: limitações técnicas/negócio declaradas · segurança/performance/compliance informados

PRE-EXEC:
  1. repetir entendimento da TASK de forma resumida
  2. listar suposições explícitas
  3. apontar ambiguidades ou lacunas
  4. aguardar validação humana explícita → só então prosseguir

DENY:
  sem PRE-EXEC completo: propor design · escrever testes · escrever código
  sem todos CRITERIA: iniciar qualquer etapa de execução
