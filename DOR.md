# Definition of Ready (DOR)

Uma task só pode ser iniciada pela IA quando **todos** os critérios
deste documento forem atendidos.

Caso qualquer item não seja satisfeito, a IA DEVE interromper
a execução e solicitar esclarecimentos explícitos.

---

## Critérios obrigatórios

### 1. Objetivo claro
- A task possui um objetivo único e bem definido
- Não há múltiplas intenções misturadas

### 2. Escopo definido
- O que está dentro do escopo está explicitado
- O que está fora do escopo está explicitado

### 3. Critérios de aceitação
- Existem critérios verificáveis
- Não são subjetivos (“funcionar bem”, “rápido”, etc.)

### 4. Contexto técnico suficiente
- Linguagem, stack ou módulo afetado estão claros
- Dependências relevantes são conhecidas

### 5. Restrições explícitas
- Limitações técnicas ou de negócio foram declaradas
- Regras de segurança, performance ou compliance foram informadas

---

## Comportamento obrigatório da IA

Antes de iniciar qualquer execução, a IA DEVE:

1. Repetir o entendimento da task de forma resumida
2. Listar suposições explícitas
3. Apontar ambiguidades ou lacunas
4. Aguardar validação humana explícita

Nenhuma etapa de design, teste ou código pode ser iniciada
antes dessa validação.

---

## Violação do DOR

Se o DOR não for atendido:
- A IA NÃO DEVE propor design
- A IA NÃO DEVE escrever testes
- A IA NÃO DEVE escrever código
