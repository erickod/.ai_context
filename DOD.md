# Definition of Done (DOD)

Uma TASK só pode ser considerada **concluída** quando **todos**
os critérios definidos neste documento forem atendidos.

O DOD define **o que significa “pronto”**.
O controle de execução, loop e validação técnica é orquestrado
pelo `AGENTS.md`.

---

## Princípio fundamental

> “Done” significa **entregável correto, validado e verificável**.  
> Não existem conclusões parciais, implícitas ou subjetivas.

---

## Critérios obrigatórios de conclusão

### 1. Objetivo atendido
- O objetivo descrito na TASK foi completamente atendido
- Não existem funcionalidades parciais, implícitas ou pendentes
- O resultado é coerente com o escopo aprovado

---

### 2. Critérios de aceitação satisfeitos
- Todos os critérios de aceitação definidos na TASK estão marcados como satisfeitos
- Cada critério possui evidência verificável
- Nenhum critério foi ignorado ou “reinterpretado”

---

### 3. Design validado
- A proposta de design foi apresentada antes da implementação
- O design foi validado explicitamente
- Alterações de design durante a execução foram registradas no log da TASK

---

### 4. Testes unitários
- Testes unitários foram escritos conforme a estratégia definida na TASK
- Cobrem cenários de sucesso e falha
- São determinísticos e reproduzíveis
- **Todos os testes unitários passam**

> A execução e validação dos testes é um gate técnico obrigatório,
> controlado pelo `AGENTS.md`.

---

### 5. Testes de integração
- Testes de integração foram escritos conforme a estratégia definida na TASK
- Validam interação entre componentes, serviços ou módulos
- Não burlam regras definidas em `DB.md` ou `WORKFLOWS.md`
- **Todos os testes de integração passam**

> A execução e validação dos testes é um gate técnico obrigatório,
> controlado pelo `AGENTS.md`.

---

### 6. Implementação aderente
- O código segue integralmente o `GUIDELINES.md`
- Não viola responsabilidades definidas pelas ROLES
- Não executa ações fora do escopo da TASK
- Não introduz efeitos colaterais não documentados

---

### 7. Ausência de regressões conhecidas
- Nenhuma regressão funcional conhecida foi introduzida
- Impactos indiretos foram avaliados
- Riscos identificados foram registrados no log da TASK

---

### 8. Log completo e consistente
- O log de decisões e alterações da TASK está atualizado
- Decisões técnicas relevantes foram registradas
- Bloqueios, mudanças de entendimento e validações humanas constam no log
- O log é **append-only** e não foi alterado retroativamente

---

## Declaração de conclusão

Uma TASK **só pode ser declarada como `done`** quando:

- Todos os critérios acima forem atendidos
- O Test Gate definido no `AGENTS.md` for satisfeito
- O estado da TASK for atualizado para `done`

A IA **NÃO DEVE**:
- Declarar conclusão parcial
- Declarar “done” com testes falhando
- Declarar “done” por interpretação subjetiva

---

## Violação do DOD

Se qualquer critério não for atendido:
- A TASK permanece em execução **ou**
- É explicitamente marcada como `blocked`
- A IA DEVE indicar claramente o que falta para atingir o DOD
