---
name: crossword-ipuz
description: >
  Geração de cruzadinhas .ipuz: motor de encaixe determinístico + vocabulário
  novo gerado pelo model a cada execução, pt-br default.
  Ative ao pedir palavras cruzadas / cruzadinha / crossword, ou formato ipuz.
---
ROLE: Gerador de cruzadinhas .ipuz. Vocabulário sempre novo por run · motor faz só o encaixe/validação.

GATE.IN:
  lang?  → pt-br(default) | idioma explícito do usuário
  count? → 50(default) | ASK_USER se ausente e não inferível do histórico da conversa
  theme? → vocab girando no tema | vocab livre e variado

EXEC (sequencial, ✗ pular etapa):
  1 vocab: model gera lista NOVA (DENY reusar lista de run anterior)
    regras: n≥count×1.4 · únicas · A-Z maiúsc sem acento/espaço/hífen · 3-12 letras
            · clue curta sem citar resposta · ✗ nomes próprios
            · priorizar letras frequentes(vogais·R·S·T·N·M) p/ interseção
  2 grava words.json: [{word,clue}]
  3 roda scripts/crossword_engine.py --words --count --title --author --out
    (motor: encaixe guloso × bloco reservado × valida mismatch=0/fusão=0 — ✗ reescrever lógica)
  4 lê report(JSON):
    ok=true  → 5
    ok=false → amplia vocab(+itens · +variedade de letras) → volta a 1 · DENY editar .ipuz na mão
  5 present_files(out)

GATE.OUT:
  file=*.ipuz(ipuz.org/v2 · puzzle+solution usam "#"=bloco · clues{Across,Down}=[[num,"dica (N)"]])
  report{words_placed,dimensions,mismatches_solution_vs_puzzle=0,separation_problems=[]}

DENY: vocabulário fixo/reaproveitado de run anterior · pular pergunta de count quando ausente/ambíguo
  · editar .ipuz manualmente · aceitar mismatches>0 ou separation_problems≠[] · nomes próprios no vocab
  · reescrever a lógica de encaixe do motor

Arquivos: scripts/crossword_engine.py — motor agnóstico de idioma/tema, só recebe words.json + params CLI.
