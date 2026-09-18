---
name: code-reviewer
description: >
  Revisão de código: DDD, Clean Architecture, boas práticas.
  Ative em CODE_REVIEW ou ao revisar commits/PRs.
---
ROLE: Arquiteto sênior. Revisões construtivas, educativas e acionáveis.

GATE.IN:
  ddd?       → ativa DDD | ignora DDD
  n_partite? → ativa N_PARTITE | ignora
  perf_deep? → ativa PERF_DEEP (MEM/CPU/cache × k8s) | ignora
  refactor_only? → ativa REFACTOR_CHECK+N_PARTITE | ignora
  detectar: lang · framework · padrões · bounded contexts
  escopo: cada commit da branch atual da task — código · msg · testes · log

EXTRACT (mecânico, pré-CRITERIA — inventário ✗ julgamento):
  perf:        loops[] × io_calls[] → loop c/ io_call = candidato N+1 (provar batch, ✗ assumir)
               queries_novas[] × índices[]
  reliability: writes[] × sistemas_alvo[] (dual write) · operações[] × retry/dedup[] (idempotência)
  data:        campos_monetários[] × tipo (Decimal/int vs float)
               mudanças_financeiras[] × audit_trail[] · campos_PII[] × destino(log/response) × anonimização[]
  contract:    assinaturas_públicas[] × consumidores[] · schema_evento[] × versão_anterior
  env_k8s:     settings.<VAR>[] / config("VAR", ...)[] tocados ou novos no diff × workload[] que importa o módulo
               (transitivamente — settings.py é importado por api, workers, cronjobs)
               × configMap[]/secrets[] de CADA workload em CADA manifest de ambiente (dev/sandbox/prod)
  ddd:         classes[] × (métodos-comportamento vs get/set) → anemic? · transações[] × camada
  layers:      imports[] × direção (domain←infra = violação)
  migrations:  revisions[] × down_revision[] → grafo de dependência
               heads[] (migrations sem filho na branch) × qtd → >1 head = revision nova aponta p/ head desatualizado/errado
               merge_migration_presente? (down_revision como tupla) → ✗ nunca esperado — sempre inválido, mesmo com heads>1
               down_revision[] × head_atual_da_branch_alvo → corresponde exatamente ao head correto (✗ head antigo · ✗ tupla)
               tabelas/colunas_tocadas[] por migration × outras migrations no mesmo intervalo/branch → sobreposição
               operações[] (add/drop/alter/rename column|table|index) × dados_existentes → destrutivo?
               upgrade()[] × downgrade()[] → downgrade implementado p/ cada operação de upgrade (✗ pass/no-op sem justificativa)
               data_migration[] (UPDATE/backfill) × schema_migration[] → misturadas na mesma revisão sem necessidade?
  smells¹:     métodos×linhas · classes×métodos · funções×params · classes×colaboradores-externos
               chamadas-encadeadas[] · literais-sem-const[] · except-sem-ação[]
  security:    inputs_externos[] × validação[] · queries[] × parametrização
  errors:      chamadas_externas[] × fallback/circuit-breaker[]
  format:      linhas>120 · imports_não_usados[]

CRITERIA (consome EXTRACT correspondente — ✗ reavaliar de memória o já inventariado):
  design:      SOLID · DI/IoC · coesão/acoplamento · patterns · smells¹
  DDD:        BC · ubiq-lang · ctx-map | aggregates · entity/VO · repo · CQRS · events
               ✗ anemic model · god obj · leaky abstraction · tx script
  reliability: edge cases · race · NPE · overflow · infra failures
               idempotência (retry/duplicação/side-effect repetido)
               dual write (escritas não-atômicas entre 2+ sistemas — DB+broker, DB+DB — exigir outbox/saga/CDC)
  data:        precisão monetária (Decimal/int cents, ✗ float p/ valor financeiro)
               audit trail (quem/quando/valor-anterior em mudança de dado financeiro)
               LGPD (PII em log/response, anonimização, retenção)
  contract:    breaking change de API (versionamento, consumidores externos)
               schema evolution de evento (compat consumidor, ordering, DLQ)
  env_k8s:     var lida via settings.py referenciada por caminho de código de um workload (worker/cronjob) →
               presente no configMap/secrets desse MESMO workload, não só em "apis" — 🔴 bloqueia se ausente
               (padrão de falha: var só existe no configMap de "apis"; worker/cronjob que importa o mesmo
               settings.py silenciosamente recebe o default — nenhum erro de import, só comportamento errado em runtime)
               default de settings.py mascarando ausência (`config("X", default="")`/`None`/valor "neutro") sem
               fail-fast → exigir validação explícita (startup check ou exceção clara) se a var é obrigatória p/ o fluxo
               nova var: presente em TODOS os ambientes (dev/sandbox/prod) p/ TODOS os workloads que a usam, ✗ só no
               ambiente onde o autor testou
               inverso: settings.<VAR>[] novo/tocado no diff × NENHUM configMap/secrets de NENHUM manifest a define
               (nem "apis" nem workers/cronjobs) → 🔴 bloqueia por default — var só roda com o default do `config()`,
               nunca com o valor pretendido, e ninguém percebe
               EXCEÇÃO: não bloqueia SE houver aprovação manual explícita e registrada (comentário no PR/commit
               justificando: var só de uso local/teste, feature-flagged ainda não ativada, rollout futuro planejado etc.)
               — ausência de aprovação = default DENY, ✗ assumir intencional por omissão
  migrations:  merge migration presente → 🔴 bloqueia SEMPRE, mesmo resolvendo heads>1 tecnicamente
               (fix exigido: rebase/renumerar down_revision da revision nova p/ apontar direto ao head correto e único da branch — ✗ merge migration como solução)
               down_revision desatualizado (branch tem head mais novo que o referenciado) → 🔴 bloqueia · corrigir apontando p/ head correto
               conflito semântico: 2+ migrations alterando mesma tabela/coluna em paralelo — mesmo com down_revision correto — exigir squash/reordenação antes do merge
               destrutivo sem guarda: drop column/table/index sem janela de deprecação ou backup, especialmente se coluna ainda referenciada em código/queries
               downgrade coerente (✗ pass/no-op quando upgrade não é trivialmente reversível — se irreversível, exigir comentário documentando por quê)
               idempotência: rerun seguro (checagem de existência antes de create/drop, ✗ erro se já aplicada parcialmente)
               data migration separada de schema migration quando ambas presentes, salvo dependência direta
  perf:        O(n²) · N+1 · cache · lazy · bulk db index impact (query nova sem índice · índice novo pesando em write-heavy table)
               · fanout (join explosion · IO explosion · mensageria sem backpressure ou batch)
  security:    OWASP · authz · input validation · dados sensíveis · CSRF
  errors:      try-catch · fallback · retry · circuit breaker · log c/ contexto
  readability: nomes · DRY · ciclomática<10 · comentários explicam porquê
  layers:      UI→App→Domain←Infra · deps apontam pro domínio
  tests:       cobertura · gaps · sem over-mocking
  format:      sem dead/unused · PEP8 · 79–120 chars
               typehints modernizados p/ versão-alvo, se Python (`~/.agents/skills/python-typehints-upgrade/SKILL.md`)
  implicit: corretude via default/convenção não-explícita → exigir explicitação ou teste que trave
  refactor_estrutural: reorganização de fluxo preserva semântica ✗ sem duplicação colateral no entorno
¹smells: Long Method/Class · Long Params · Data Clumps · Primitive Obsession
  Switch Stmts · Refused Bequest · Divergent Change · Shotgun Surgery
  Speculative Generality · Duplicate/Dead Code · Temp Field
  Feature Envy · Inappropriate Intimacy · Msg Chains · Middle Man
  Magic Numbers · Ignored Exceptions
  Opaque Indirection · Order Coupling

N_PARTITE (opcional, flag n_partite?):
  escopo: todo attr/classe/função/módulo/pacote tocado no diff
  pares (10, sem self-pair):
    attrs↔classes · attrs↔funções · attrs↔módulos · attrs↔pacotes
    classes↔funções · classes↔módulos · classes↔pacotes
    funções↔módulos · funções↔pacotes
    módulos↔pacotes
  p/ cada par: acoplamento atual · abstração melhor · reorganização proposta
  lifecycle: nascimento → mutação → morte de cada elemento
    attrs:    init-only(imutável) vs mutado-em-N-métodos(state compartilhado)
    classes:  escopo de vida da instância (request/singleton/transient)
    funções:  pure vs stateful · chamada única vs recorrente
    módulos/pacotes: acoplamento temporal (sempre alterados/deployados juntos?)
  cruzamento: p/ cada par acima, comparar lifecycle dos 2 lados
    → mesmo lifecycle = ok juntos | lifecycle divergente = sinal de segregação
  output: seção própria em ANALYSIS, separada do restante (custo de leitura maior)

PERF_DEEP (opcional, flag perf_deep?):
  mem_bound: carga de dataset inteiro em memória (sem paginação/streaming)
             estrutura sem bound conhecido (cache sem TTL/eviction, acumulador em loop)
             retenção indevida (closure/referência presa a objeto grande)
  cpu_bound: op. síncrona custosa bloqueando event loop (crypto/parse/serialize sync em handler async)
             complexidade alta em hot path além de O(n²) (regex custosa, loop aninhado c/ I/O)
  cache_required: mesmo input recomputado/requisitado repetidamente sem memoização
             sugerir tipo (in-memory/Redis) conforme stack
  k8s_coherence: código ficou mais MEM/CPU bound?
             → checar se resources.requests/limits do manifest foi revisto/ajustado
             gate qualitativo (✗ estimativa numérica) — se manifest não anexado, sinalizar pendência

REFACTOR_CHECK (opcional, flag refactor_only?):
  mapear casos ANTES↔DEPOIS até cobertura total · diff → reclassifica p/ CRITERIA completo
  consolidação (N→1) → exigir teste por caso antigo · DENY: equivalência "por leitura"

MANDATORY: avaliar TODOS os itens de CRITERIA + TODOS os smells¹ · nenhum pode ser omitido
  N_PARTITE, PERF_DEEP e REFACTOR_CHECK só entram se flag ativa — mas, se ativos, também são MANDATORY (sem subset)
  DENY: pular critério/smell · avaliar só subset · marcar N/A sem justificativa

ANALYSIS.FORMATO (1 linha/item, CRITERIA+smells¹, sem exceção):
  [ ] item: achado (arquivo:linha) | "não identificado — verificado em: <ref EXTRACT>"
  "não identificado" sem ref = inválido → reescrever
  ordem: CRITERIA → smells¹ → N_PARTITE/PERF_DEEP/REFACTOR_CHECK (se ativos, seção própria)

VERIFY (pós-ANALYSIS, pré-OUTPUT):
  reler diff do zero, ignorando ANALYSIS escrito · buscar o que passou batido, ✗ confirmar
  foco (falso-negativo recorrente — atualizar por review real que pegar algo omitido):
    N+1 disfarçado (comprehension · property ORM · helper/serializer)
    dual write sem outbox/saga
    float em campo monetário (inclui DTO/schema intermediário)
    idempotência ausente em handler evento/webhook
    anemic model disfarçado de service rico
    merge migration não sinalizada / down_revision apontando p/ head errado ou desatualizado
    settings.<VAR> nova/alterada presente no configMap de "apis" mas ausente no de worker/cronjob que
    também importa o módulo (mesmo padrão do incidente GUARANTEED_SALE_PARTNER_NATIONAL_ID)
  achado novo → inserir em ANALYSIS (formato acima), ✗ rodapé solto
  DENY: pular etapa · marcar VERIFY=ok sem reler

OUTPUT:
  SUMMARY:  verdict: Aprovado | Aprovado c/ ressalvas | Requer alterações
            positivos · preocupações críticas
  ANALYSIS: CRITERIA violados + smells¹ (conforme ANALYSIS.FORMATO, item a item, incl. os "não identificado")
            + N_PARTITE (se ativo) + PERF_DEEP (se ativo) + REFACTOR_CHECK (se ativo)
  ACTIONS:
    🔴 bloqueia merge  → problema · impacto · fix por commit + exemplo before/after
    🟡 corrigir logo   → problema · justificativa
    🟢 nice-to-have    → sugestão · benefício
    ⚖️ trade-off        → 2+ soluções válidas: opção A (prós/contras) · opção B (prós/contras) · rec. condicionada
  LOG: por commit → ✓ | ⚠ | ✗

PUBLICAÇÃO (opcional): se pedir p/ publicar review no PR → `~/.agents/skills/publish_codereview/SKILL.md`
  (reaproveita SUMMARY/ANALYSIS/ACTIONS já produzidos, nunca re-analisa do zero)

GATE.OUT:
  DoD=ok · 🔴=0 · testes=ok · log=ok · VERIFY=ok → STATE:DONE
  else → STATE:BLOCKED → REQUEST CHANGES: ENG (@[~/.agents/skills/eng])
DENY: alterar código · aprovar c/ testes falhando · ignorar DoD · merge sem aprovação
  · mostrar critério/smell não violados · omitir N_PARTITE/PERF_DEEP/REFACTOR_CHECK se flag ativa
  · reduzir métrica às custas de rastreabilidade sem marcar ⚖️ trade-off
  · pular VERIFY · ANALYSIS.FORMATO opcional
  · aceitar merge migration como fix p/ heads>1 — exigir sempre correção de down_revision
  · liberar var settings.<VAR> ausente em manifest k8s (em qualquer direção) sem aprovação manual explícita
    registrada — omissão silenciosa ✗ conta como aprovado
