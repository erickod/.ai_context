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
  detectar: lang · framework · padrões · bounded contexts
  escopo: cada commit da branch atual da task — código · msg · testes · log

CRITERIA:
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
  perf:        O(n²) · N+1 · cache · lazy · bulk
               db index impact (query nova sem índice · índice novo pesando em write-heavy table)
  security:    OWASP · authz · input validation · dados sensíveis · CSRF
  errors:      try-catch · fallback · retry · circuit breaker · log c/ contexto
  readability: nomes · DRY · ciclomática<10 · comentários explicam porquê
  layers:      UI→App→Domain←Infra · deps apontam pro domínio
  tests:       cobertura · gaps · sem over-mocking
  format:      sem dead/unused · PEP8 · 79–120 chars
               typehints modernizados p/ versão-alvo, se Python (`~/.agents/skills/python-typehints-upgrade/SKILL.md`)
¹smells: Long Method/Class · Long Params · Data Clumps · Primitive Obsession
  Switch Stmts · Refused Bequest · Divergent Change · Shotgun Surgery
  Speculative Generality · Duplicate/Dead Code · Temp Field
  Feature Envy · Inappropriate Intimacy · Msg Chains · Middle Man
  Magic Numbers · Ignored Exceptions

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

MANDATORY: avaliar TODOS os itens de CRITERIA + TODOS os smells¹ · nenhum pode ser omitido
  N_PARTITE e PERF_DEEP só entram se flag ativa — mas, se ativos, também são MANDATORY (sem subset)
  DENY: pular critério/smell · avaliar só subset · marcar "N/A" sem justificativa

OUTPUT:
  SUMMARY:  verdict: Aprovado | Aprovado c/ ressalvas | Requer alterações
            positivos · preocupações críticas
  ANALYSIS: todos os CRITERIA + smells¹ (checklist item a item)
            + N_PARTITE (se ativo) + PERF_DEEP (se ativo)
  ACTIONS:
    🔴 bloqueia merge  → problema · impacto · fix por commit + exemplo before/after
    🟡 corrigir logo   → problema · justificativa
    🟢 nice-to-have    → sugestão · benefício
  LOG: por commit → ✓ | ⚠ | ✗

PUBLICAÇÃO (opcional): se pedir p/ publicar review no PR → `~/.agents/skills/publish_codereview/SKILL.md`
  (reaproveita SUMMARY/ANALYSIS/ACTIONS já produzidos, nunca re-analisa do zero)

GATE.OUT:
  DoD=ok · 🔴=0 · testes=ok · log=ok → STATE:DONE
  else → STATE:BLOCKED → REQUEST CHANGES: ENG (@[~/.agents/skills/eng])
DENY: alterar código · aprovar c/ testes falhando · ignorar DoD · merge sem aprovação
  · omitir critério/smell da checklist · omitir N_PARTITE/PERF_DEEP se flag ativa
