from crewai import Agent, Task


# ── Main pipeline ─────────────────────────────────────────────────────────────

def task_design_task(agent: Agent, task_input: str) -> Task:
    return Task(
        description=(
            f"STATE: TASK_DESIGN\n\n"
            f"Input:\n{task_input}\n\n"
            "CYCLE (mandatory):\n"
            "1. READ  → read_project_memory\n"
            "2. READ  → read_skill('task-designer') · read_document('DOR.md')\n"
            "3. ACT   → qualify task against every DOR criterion\n"
            "          If any criterion fails: list gaps and mark BLOCKED\n"
            "          If all pass: produce task document using TASK-TEMPLATE.md format\n"
            "4. WRITE → write_project_memory with result\n\n"
            "DENY: planning, implementing, any technical action."
        ),
        expected_output=(
            "Either:\n"
            "(a) Complete task document in TASK-TEMPLATE.md format, ready for human approval.\n"
            "(b) BLOCKED report listing which DOR criteria failed and what clarification is needed."
        ),
        agent=agent,
        human_input=True,
    )


def planning_task(agent: Agent) -> Task:
    return Task(
        description=(
            "STATE: PLANNING\n\n"
            "CYCLE (mandatory):\n"
            "1. READ  → read_project_memory\n"
            "2. READ  → read_skill('planner') · read_document('GUIDELINES.md')\n"
            "3. ACT   → create execution plan with stages, dependencies, gates, risks, assumptions\n"
            "          If structural scope / new module / refactoring detected: flag DAPS activation\n"
            "4. WRITE → write_project_memory with result\n\n"
            "DENY: implementation, code changes, schema changes."
        ),
        expected_output=(
            "## Plano\n"
            "### Etapas: N.<etapa> — depende: <dep|NONE>\n"
            "### Gates: após N: <critério>\n"
            "### Riscos: <risco> → <mitigação>\n"
            "### Assunções: <assunção>\n\n"
            "Followed by explicit request for human approval."
        ),
        agent=agent,
        human_input=True,
    )


def test_analysis_task(agent: Agent) -> Task:
    return Task(
        description=(
            "STATE: TEST_ANALYSIS\n\n"
            "CYCLE (mandatory):\n"
            "1. READ  → read_project_memory\n"
            "2. READ  → read_skill('test-analyst')\n"
            "3. ACT   → define F.I.R.S.T scenarios: happy path, errors, edge cases, integration\n"
            "          Name: given_[context]_when_[action]_then_[result] (≤89 chars, English)\n"
            "          Docstrings: GIVEN/WHEN/THEN in English, mandatory\n"
            "          If any scenario is unnameable: BLOCKED → STATE back to TASK_DESIGN\n"
            "4. WRITE → write_project_memory with result\n\n"
            "DENY: implementation, architecture, schema changes."
        ),
        expected_output=(
            "## Test Scenarios\n"
            "### Happy Path | Error Scenarios | Edge Cases\n\n"
            "## Unit Tests\n"
            "- [ ] given_..._when_..._then_... (__ chars)\n\n"
            "## Integration Tests\n"
            "- [ ] given_..._when_..._then_... (__ chars)\n\n"
            "## F.I.R.S.T Checklist\n"
            "- [ ] Fast · Isolated · Repeatable · Self-validating · Timely\n"
            "- [ ] All names ≤89 chars\n"
            "- [ ] GIVEN/WHEN/THEN docstrings complete · English"
        ),
        agent=agent,
    )


def engineering_task(agent: Agent) -> Task:
    return Task(
        description=(
            "STATE: ENGINEERING\n\n"
            "CYCLE (mandatory):\n"
            "1. READ  → read_project_memory\n"
            "2. READ  → read_skill('eng') · read_document('DB.md') · read_document('GUIDELINES.md')\n"
            "3. ACT   → create <branch>_eng (rename to <branch>_eng_N if already exists)\n"
            "          For each change: present what/why/impact → await approval → apply → commit\n"
            "          Order: design → unit tests → integration tests → implementation → run tests → lint\n"
            "          If schema changed: update DB.md\n"
            "4. WRITE → write_project_memory after each significant action\n\n"
            "DENY: batch commits, merge without DOD approval, skip test execution."
        ),
        expected_output=(
            "Per change:\n"
            "  What: <description>\n"
            "  Why: <justification>\n"
            "  Impact: <impact assessment>\n"
            "  Commit: <conventional commit message>\n\n"
            "Final: all tests passing, DOD checklist satisfied, branch ready for review."
        ),
        agent=agent,
        human_input=True,
    )


# ── Code Review — 3 parallel specialists + synthesizer ───────────────────────

def cr_design_task(agent: Agent) -> Task:
    """Runs async in parallel with cr_security_task and cr_perf_task."""
    return Task(
        description=(
            "STATE: CODE_REVIEW — Design & DDD pass\n\n"
            "CYCLE (mandatory):\n"
            "1. READ  → read_project_memory\n"
            "2. READ  → read_skill('code-reviewer') · read_document('DOD.md')\n"
            "3. ACT   → review each commit in <branch>_eng for:\n"
            "          · design: SOLID · DI/IoC · cohesion/coupling · patterns · code smells\n"
            "          · DDD: BC · ubiquitous language · aggregates · entity/VO · repo · CQRS · events\n"
            "            DENY anemic models · god objects · leaky abstractions · transaction scripts\n"
            "          · layers: UI→App→Domain←Infra · deps point toward domain\n"
            "4. WRITE → write_project_memory with partial findings\n\n"
            "DENY: alter code, approve with failing tests."
        ),
        expected_output=(
            "DESIGN & DDD FINDINGS:\n"
            "  🔴 (blocks merge): <problem> · <impact> · <fix>\n"
            "  🟡 (fix soon): <problem> · <justification>\n"
            "  🟢 (nice-to-have): <suggestion> · <benefit>\n"
            "LOG: per commit → ✓ | ⚠ | ✗"
        ),
        agent=agent,
        async_execution=True,
    )


def cr_security_task(agent: Agent) -> Task:
    """Runs async in parallel with cr_design_task and cr_perf_task."""
    return Task(
        description=(
            "STATE: CODE_REVIEW — Security & Reliability pass\n\n"
            "CYCLE (mandatory):\n"
            "1. READ  → read_project_memory\n"
            "2. READ  → read_skill('code-reviewer') · read_document('DOD.md')\n"
            "3. ACT   → review each commit in <branch>_eng for:\n"
            "          · security: OWASP · authz · input validation · sensitive data · CSRF\n"
            "          · reliability: edge cases · race conditions · NPE · overflow · infra failures\n"
            "          · errors: try-catch · fallback · retry · circuit breaker · logged context\n"
            "4. WRITE → write_project_memory with partial findings\n\n"
            "DENY: alter code, approve with failing tests."
        ),
        expected_output=(
            "SECURITY & RELIABILITY FINDINGS:\n"
            "  🔴 (blocks merge): <problem> · <impact> · <fix>\n"
            "  🟡 (fix soon): <problem> · <justification>\n"
            "  🟢 (nice-to-have): <suggestion> · <benefit>\n"
            "LOG: per commit → ✓ | ⚠ | ✗"
        ),
        agent=agent,
        async_execution=True,
    )


def cr_perf_task(agent: Agent) -> Task:
    """Runs async in parallel with cr_design_task and cr_security_task."""
    return Task(
        description=(
            "STATE: CODE_REVIEW — Performance & Quality pass\n\n"
            "CYCLE (mandatory):\n"
            "1. READ  → read_project_memory\n"
            "2. READ  → read_skill('code-reviewer') · read_document('DOD.md')\n"
            "3. ACT   → review each commit in <branch>_eng for:\n"
            "          · performance: O(n²) · N+1 queries · caching · lazy loading · bulk ops\n"
            "          · readability: names · DRY · cyclomatic complexity <10 · why-comments\n"
            "          · tests: coverage · gaps · no over-mocking\n"
            "          · format: no dead/unused code · PEP8 · 79-120 char lines\n"
            "4. WRITE → write_project_memory with partial findings\n\n"
            "DENY: alter code, approve with failing tests."
        ),
        expected_output=(
            "PERFORMANCE & QUALITY FINDINGS:\n"
            "  🔴 (blocks merge): <problem> · <impact> · <fix>\n"
            "  🟡 (fix soon): <problem> · <justification>\n"
            "  🟢 (nice-to-have): <suggestion> · <benefit>\n"
            "LOG: per commit → ✓ | ⚠ | ✗"
        ),
        agent=agent,
        async_execution=True,
    )


def cr_synthesis_task(agent: Agent) -> Task:
    """Waits for the 3 async review tasks (set context in crew.py)."""
    return Task(
        description=(
            "STATE: CODE_REVIEW — Final synthesis\n\n"
            "CYCLE (mandatory):\n"
            "1. READ  → read_project_memory\n"
            "2. READ  → read_document('DOD.md')\n"
            "3. ACT   → consolidate all specialist findings:\n"
            "          · merge duplicate issues, keep highest severity\n"
            "          · verify DOD checklist\n"
            "          · if DOD=ok · 🔴=0 · tests=ok → update_current_state('DONE')\n"
            "          · if any 🔴 → update_current_state('BLOCKED') · request changes from eng\n"
            "4. WRITE → write_project_memory with final verdict\n\n"
            "DENY: alter code, approve with failing tests, ignore DOD."
        ),
        expected_output=(
            "SUMMARY: <Aprovado | Aprovado c/ ressalvas | Requer alterações>\n"
            "  positivos: ...\n"
            "  preocupações críticas: ...\n\n"
            "ANALYSIS: <consolidated findings>\n\n"
            "ACTIONS:\n"
            "  🔴 (blocks merge): <problem> · <impact> · <fix>\n"
            "  🟡 (fix soon): <problem> · <justification>\n"
            "  🟢 (nice-to-have): <suggestion> · <benefit>\n\n"
            "LOG: per commit → ✓ | ⚠ | ✗"
        ),
        agent=agent,
        human_input=True,
    )


# ── DAPS — phases 1+2 sequential, phases 3+4 parallel, phase 5 synthesis ─────

def daps_phase1_2_task(agent: Agent, scope: str) -> Task:
    return Task(
        description=(
            "DAPS LATERAL ACTIVATION — Phases 1 & 2 (no STATE transition)\n\n"
            f"Scope:\n{scope}\n\n"
            "CYCLE (mandatory):\n"
            "1. READ  → read_project_memory (do NOT change CURRENT_STATE)\n"
            "2. READ  → read_skill('daps-analyst')\n"
            "3. ACT   → Phase 1 — Bipartite Decomposition:\n"
            "             list all structures (exist/are) with one-line description\n"
            "             list all actions (transform/decide/produce/coordinate) with one-line description\n"
            "             deliver: InventárioInicial {estruturas[], ações[]}\n"
            "           Phase 2 — Teleological Interrogation:\n"
            "             apply 5 questions to each element:\n"
            "               1.Propósito  2.Razão de mudança  3.Entrega  4.Fronteira  5.Condição de existência\n"
            "             deliver: RelatórioAnalítico {perfilTeleológico[]}\n"
            "4. WRITE → write_project_memory with result\n\n"
            "DENY: change STATE, architectural decisions."
        ),
        expected_output=(
            "InventárioInicial:\n"
            "  estruturas: [...]\n"
            "  ações: [...]\n\n"
            "RelatórioAnalítico:\n"
            "  perfilTeleológico: [{elemento, propósito, razão_mudança, entrega, fronteira, condição}]"
        ),
        agent=agent,
    )


def daps_phase3_task(agent: Agent) -> Task:
    """Runs async in parallel with daps_phase4_task. Context set in crew.py."""
    return Task(
        description=(
            "DAPS Phase 3 — Dependency Mapping (runs parallel with Phase 4)\n\n"
            "Input: RelatórioAnalítico from Phase 2 (in context).\n\n"
            "ACT:\n"
            "  · Map edges: usa · cria · transforma · decide sobre · é composto por · notifica\n"
            "  · Compute metrics: fan-in · fan-out · cycles (bidirectional acoplamento)\n"
            "  · Identify clusters: high internal density + same reason for change + low ext connectivity\n"
            "  · Map volatility: external event that causes all cluster elements to change simultaneously\n"
            "  · Deliver: GrafoDependências {arestas[], clusters[], métricas}\n\n"
            "WRITE → write_project_memory with result\n\n"
            "DENY: change STATE, architectural decisions."
        ),
        expected_output=(
            "GrafoDependências:\n"
            "  arestas: [{origem, tipo, destino}]\n"
            "  clusters: [{nome, elementos[], volatilidade}]\n"
            "  métricas: [{elemento, fan_in, fan_out, ciclos}]"
        ),
        agent=agent,
        async_execution=True,
    )


def daps_phase4_task(agent: Agent) -> Task:
    """Runs async in parallel with daps_phase3_task. Context set in crew.py."""
    return Task(
        description=(
            "DAPS Phase 4 — Lifecycle Mapping (runs parallel with Phase 3)\n\n"
            "Input: RelatórioAnalítico from Phase 2 (in context).\n\n"
            "ACT:\n"
            "  · For each element map: nasce quando · morre quando · pode ser estendido quando\n"
            "  · Mark analytic artifacts as transient (born in analysis, dies in Phase 5)\n"
            "  · Deliver: MapaCicloVida {eventos[]}\n\n"
            "WRITE → write_project_memory with result\n\n"
            "DENY: change STATE, architectural decisions."
        ),
        expected_output=(
            "MapaCicloVida:\n"
            "  eventos: [{elemento, nasce_quando, morre_quando, estendido_quando, transiente: bool}]"
        ),
        agent=agent,
        async_execution=True,
    )


def daps_phase5_task(agent: Agent) -> Task:
    """Waits for phases 3 & 4 (set context in crew.py)."""
    return Task(
        description=(
            "DAPS Phase 5 — Design Synthesis\n\n"
            "Input: GrafoDependências (Phase 3) and MapaCicloVida (Phase 4) from context.\n\n"
            "ACT:\n"
            "  · Create cohesive classes from clusters\n"
            "    (name from responsibility, methods from actions, attributes from structures)\n"
            "  · Define contracts: public method signatures with entries/exits/preconditions\n"
            "    named DTOs for every boundary crossing\n"
            "  · Create orchestrator: no own logic, coordinates phases in sequence\n"
            "    with explicit contracts\n"
            "  · Deliver: PropostaDeDesign {classes[], contratos[], orquestrador}\n\n"
            "WRITE → write_project_memory with result\n\n"
            "DENY: leak analytic artifacts to final design · omit DTO between phases "
            "· add if in orchestrator without abstraction · change STATE."
        ),
        expected_output=(
            "PropostaDeDesign:\n"
            "  classes: [{nome, responsabilidade, métodos[], atributos[]}]\n"
            "  contratos: [{método, entradas, saídas, pré_condições, dtos[]}]\n"
            "  orquestrador: {nome, fases_coordenadas[], sem_lógica_própria: true}"
        ),
        agent=agent,
    )
