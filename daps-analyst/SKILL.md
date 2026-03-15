---
name: daps-analyst
description: >
  Framework de análise e síntese de design orientado a responsabilidades ortogonais.
  Ativar ao decompor, interrogar, mapear dependências ou sintetizar abstrações de design.
  Ativar em: TASK com escopo estrutural · novo módulo · refatoração  · redesign · arquitetura
version: 3b
---

ROLE: analista-de-design
SOURCES: sujeito → InventárioInicial → RelatórioAnalítico → GrafoDependências | MapaCicloVida → PropostaDeDesign
PRE:
  - sujeito definido e delimitado
  - teoria de design selecionada (OOP | funcional | event-sourcing)
DO:
  - executar fases 1–5 em sequência com contratos explícitos
  - executar fases 3 e 4 em paralelo
  - nomear todos os DTOs que cruzam fronteiras
DENY:
  - vazar artefato analítico para o design final
  - omitir DTO entre fases
  - adicionar `if` no orquestrador sem criar abstração correspondente
GATE.out: fases 1–5 concluídas · PropostaDeDesign gerada · orquestrador sem lógica própria → DONE

---

## FASE 1 — DECOMPOSIÇÃO BIPARTIDA

ENTREGA: `InventárioInicial { estruturas[] · ações[] }`

sub-passos:
- listar todas as estruturas — tudo que existe · responde "isso existe?"
- listar todas as ações — tudo que transforma · decide · produz · coordena
- descrever cada elemento em uma linha · sem agrupamento

REGRA: elemento ambíguo → ainda não decomposto · decompor até separação óbvia

---

## FASE 2 — INTERROGAÇÃO TELEOLÓGICA

ENTREGA: `RelatórioAnalítico { perfilTeleológico[] }`

sub-passos: aplicar as 5 perguntas a cada elemento de `InventárioInicial`¹

1. propósito — o que justifica a existência em uma frase?
2. razão de mudança — por que este muda? · sem resposta → absorver em outro
3. entrega — output concreto: valor | estado | decisão | efeito
4. fronteira — onde começa e termina · o que explicitamente não é responsabilidade
5. condição de existência — o que faz este existir? · condição ausente → elemento ausente

REGRA: mesma resposta em (2) → candidatos à fusão · respostas opostas em (4) → candidatos à separação

¹ estruturas e ações recebem as mesmas perguntas · o tipo informa as respostas, não as perguntas

---

## FASE 3 — MAPEAMENTO DE DEPENDÊNCIAS

ENTREGA: `GrafoDependências { arestas[] · clusters[] · métricas }`

EXECUÇÃO: paralelo com Fase 4 · ambas sobre `RelatórioAnalítico`

### 3.1 — TIPOS DE ARESTA

| tipo | descrição |
|---|---|
| usa | A chama ou lê B para funcionar |
| cria | A instancia ou produz B |
| transforma | A recebe B → entrega versão modificada |
| decide sobre | A determina comportamento ou existência de B |
| é composto por | A contém B como parte estrutural |
| notifica | A sinaliza B sem esperar resposta |

### 3.2 — MÉTRICAS QUANTITATIVAS

- fan-in: quantos dependem deste
- fan-out: quantos este depende
- ciclos: caminho de volta pelo grafo? → ⚠ alerta de acoplamento bidirecional

### 3.3 — IDENTIFICAÇÃO DE CLUSTERS

CRITÉRIOS: alta densidade interna · mesma razão de mudança · baixa conectividade externa
NOME: responsabilidade que une · não os membros que compõem

### 3.4 — ANÁLISE DE VOLATILIDADE

Para cada cluster: qual evento externo faria todos os elementos mudarem simultaneamente? → razão de mudança do cluster → razão de mudança da abstração resultante

---

## FASE 4 — MAPEAMENTO DE CICLO DE VIDA

ENTREGA: `MapaCicloVida { eventos[] }`

EXECUÇÃO: paralelo com Fase 3

Para cada elemento:
- nasce quando — evento | condição | chamada que faz o elemento existir
- morre quando — evento | condição | ausência que invalida o elemento
- pode ser estendido quando — condição de ganho de comportamento sem quebra de identidade

REGRA CRÍTICA: artefato analítico tem ciclo transitório · nasce na análise · morre ao virar abstração na Fase 5 · vazamento → síntese incompleta

INPUT PARA SÍNTESE:
- ciclo muito curto → função pura | valor imutável
- nunca morre → singleton | serviço
- estende-se frequentemente → abstração aberta (interface | classe base)

---

## FASE 5 — SÍNTESE DE DESIGN

ENTRADAS: `GrafoDependências` (Fase 3) · `MapaCicloVida` (Fase 4)
ENTREGA: `PropostaDeDesign { classes[] · contratos[] · orquestrador }`

### 5.1 — DEFINIÇÃO DE ABSTRAÇÕES

Para cada cluster → criar classe coesa:

- nome → responsabilidade do cluster · não enumeração dos membros
- métodos → ações do cluster
- atributos → estruturas do cluster
- ciclo de vida → evento de nascimento e morte do elemento de maior longevidade

### 5.2 — DEFINIÇÃO DE CONTRATOS

Para cada classe:
- métodos públicos com assinatura explícita: entradas · saídas · pré-condições
- DTOs nomeados para todo dado que cruza fronteira · dado sem nome = acoplamento implícito

REGRA: método público ✗ expõe tipo interno de outro cluster → introduzir DTO intermediário

### 5.3 — ORQUESTRADOR
```
Orquestrador.executar(sujeito):
  inventário     = Análise.decompor(sujeito)
  relatório      = Análise.interrogar(inventário)
  grafo          = Análise.mapearDependências(relatório)   ─┐ paralelo
  cicloDeVida    = CicloDeVida.mapear(relatório)           ─┘
  proposta       = Síntese.sintetizar(grafo, cicloDeVida)
  return proposta
```

DENY:
- ✗ orquestrador com lógica própria
- ✗ DTO sem nome ao cruzar fronteira
- ✗ ramificação com regra de negócio

REGRA FINAL: necessidade de `if` no orquestrador → abstração ausente → retornar a 5.1

---

GATE.out: R1–R14 sem violação · frontmatter presente · DENY declarado · GATE.out declarado → artefato válido
