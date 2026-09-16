#!/usr/bin/env python3
"""
crossword_engine.py — motor de encaixe e exportação .ipuz
==========================================================

NÃO contém vocabulário. Recebe uma lista de palavras+dicas (já escolhidas
pelo model/usuário) em um arquivo JSON e devolve um .ipuz validado.

Formato de entrada (JSON), lista de objetos:
    [
      {"word": "CASA", "clue": "Lugar onde se mora"},
      {"word": "GATO", "clue": "Animal doméstico que mia"},
      ...
    ]
`word` deve estar em MAIÚSCULAS SEM ACENTOS/ESPAÇOS (A-Z apenas) — é o que
vai na grade. Acentos/hífens ficam só na dica, se fizer sentido.

Uso:
    python3 crossword_engine.py --words words.json --count 50 \
        --title "Cruzadinha" --author "Claude" --lang pt-br \
        --out cruzadinha.ipuz

Saída: arquivo .ipuz + relatório de validação no stdout (JSON).
Exit code 0 = sucesso e validado. Exit code 1 = falha (ver stderr).
"""

import argparse
import json
import re
import sys

MAX_DIM_TRIES = [11, 13, 15, 17, 19, 21, 23, 25, 27, 29, 31]


def normalize_word(w: str) -> str:
    return re.sub(r"[^A-Z]", "", w.upper())


def can_place(grid, blocked, word, r, c, direction):
    L = len(word)
    dr, dc = (0, 1) if direction == 'A' else (1, 0)
    br, bc = r - dr, c - dc
    er, ec = r + dr * L, c + dc * L
    if (br, bc) in grid or (er, ec) in grid:
        return None
    crossings = 0
    cells = []
    for i in range(L):
        rr, cc = r + dr * i, c + dc * i
        cells.append((rr, cc))
        if (rr, cc) in blocked:
            return None
        existing = grid.get((rr, cc))
        if existing is not None:
            if existing != word[i]:
                return None
            crossings += 1
        else:
            if direction == 'A':
                n1, n2 = (rr - 1, cc), (rr + 1, cc)
            else:
                n1, n2 = (rr, cc - 1), (rr, cc + 1)
            if n1 in grid or n2 in grid:
                return None
    if crossings == 0 and grid:
        return None
    return crossings, cells, (br, bc), (er, ec)


def build_grid(words, seed_idx, max_dim, target=None):
    grid, blocked, placements = {}, set(), []
    remaining = list(range(len(words)))
    w0 = words[seed_idx][0]
    for i, ch in enumerate(w0):
        grid[(0, i)] = ch
    blocked.add((0, -1)); blocked.add((0, len(w0)))
    placements.append({"idx": seed_idx, "word": w0, "dir": 'A', "r": 0, "c": 0, "len": len(w0)})
    remaining.remove(seed_idx)

    def bbox():
        rs = [p["r"] for p in placements] + [p["r"] + (p["len"] - 1 if p["dir"] == 'D' else 0) for p in placements]
        cs = [p["c"] for p in placements] + [p["c"] + (p["len"] - 1 if p["dir"] == 'A' else 0) for p in placements]
        return min(rs), max(rs), min(cs), max(cs)

    progress = True
    while progress and remaining:
        if target and len(placements) >= target:
            break
        progress = False
        minr0, maxr0, minc0, maxc0 = bbox()
        best = None
        for idx in remaining:
            w = words[idx][0]
            for i, ch in enumerate(w):
                for (rr, cc), gch in list(grid.items()):
                    if gch != ch:
                        continue
                    for r0, c0, d in ((rr, cc - i, 'A'), (rr - i, cc, 'D')):
                        res = can_place(grid, blocked, w, r0, c0, d)
                        if not res:
                            continue
                        cr, cells, bufb, bufe = res
                        L = len(w)
                        if d == 'A':
                            wr0, wr1, wc0, wc1 = r0, r0, c0, c0 + L - 1
                        else:
                            wr0, wr1, wc0, wc1 = r0, r0 + L - 1, c0, c0
                        newh = max(maxr0, wr1) - min(minr0, wr0) + 1
                        neww = max(maxc0, wc1) - min(minc0, wc0) + 1
                        if newh > max_dim or neww > max_dim:
                            continue
                        growth = newh * neww - (maxr0 - minr0 + 1) * (maxc0 - minc0 + 1)
                        score = cr * 1000 - growth
                        if best is None or score > best[0]:
                            best = (score, cr, idx, r0, c0, d, cells, bufb, bufe)
        if best:
            _, cr, idx, r0, c0, d, cells, bufb, bufe = best
            w = words[idx][0]
            for (rr, cc), ch in zip(cells, w):
                grid[(rr, cc)] = ch
            blocked.add(bufb); blocked.add(bufe)
            placements.append({"idx": idx, "word": w, "dir": d, "r": r0, "c": c0, "len": len(w)})
            remaining.remove(idx)
            progress = True
    return grid, placements, remaining


def find_best_layout(words, min_words, limit_to=None, max_dim_tries=MAX_DIM_TRIES):
    best = None
    seeds = [i for i, w in enumerate(words) if len(w[0]) >= 6] or list(range(len(words)))
    for max_dim in max_dim_tries:
        for seed in seeds:
            grid, placements, remaining = build_grid(words, seed, max_dim)
            if len(placements) >= min_words:
                score = len(placements)
                if best is None or score > best[0]:
                    best = (score, max_dim, seed, grid, placements, remaining)
        if best and best[0] >= min_words:
            break
    if best is None:
        raise RuntimeError(
            f"Não foi possível encaixar {min_words} palavras com o vocabulário fornecido "
            f"({len(words)} palavras disponíveis). Forneça mais palavras (com letras em comum) "
            f"ou reduza --count."
        )
    _, max_dim, seed, grid, placements, remaining = best

    if limit_to and len(placements) > limit_to:
        cellcount = {}
        for p in placements:
            dr, dc = (0, 1) if p["dir"] == 'A' else (1, 0)
            for i in range(p["len"]):
                key = (p["r"] + dr * i, p["c"] + dc * i)
                cellcount[key] = cellcount.get(key, 0) + 1

        def crossings_of(p):
            dr, dc = (0, 1) if p["dir"] == 'A' else (1, 0)
            return sum(1 for i in range(p["len"]) if cellcount[(p["r"] + dr * i, p["c"] + dc * i)] >= 2)

        placements = sorted(placements, key=lambda p: -crossings_of(p))[:limit_to]
        grid = {}
        for p in placements:
            dr, dc = (0, 1) if p["dir"] == 'A' else (1, 0)
            for i, ch in enumerate(p["word"]):
                grid[(p["r"] + dr * i, p["c"] + dc * i)] = ch

    return grid, placements


def build_ipuz(words, grid, placements, title, author, notes):
    rs = [p["r"] for p in placements] + [p["r"] + (p["len"] - 1 if p["dir"] == 'D' else 0) for p in placements]
    cs = [p["c"] for p in placements] + [p["c"] + (p["len"] - 1 if p["dir"] == 'A' else 0) for p in placements]
    minr, maxr, minc, maxc = min(rs), max(rs), min(cs), max(cs)
    H, W = maxr - minr + 1, maxc - minc + 1

    norm = [{"idx": p["idx"], "word": p["word"], "dir": p["dir"],
             "r": p["r"] - minr, "c": p["c"] - minc, "len": p["len"]} for p in placements]

    # bloco = "#" tanto em puzzle quanto em solution (exigência do ipuz v2)
    sol = [['#' for _ in range(W)] for _ in range(H)]
    for r in range(H):
        for c in range(W):
            ch = grid.get((r + minr, c + minc))
            if ch:
                sol[r][c] = ch

    def is_block(ch):
        return ch == "#"

    def len_across(r, c):
        n = 0
        while c + n < W and not is_block(sol[r][c + n]):
            n += 1
        return n

    def len_down(r, c):
        n = 0
        while r + n < H and not is_block(sol[r + n][c]):
            n += 1
        return n

    puzzle_grid = [[None] * W for _ in range(H)]
    num = 1
    numbering_across, numbering_down = [], []
    for r in range(H):
        for c in range(W):
            if is_block(sol[r][c]):
                puzzle_grid[r][c] = "#"
                continue
            is_a = (c == 0 or is_block(sol[r][c - 1])) and len_across(r, c) > 1
            is_d = (r == 0 or is_block(sol[r - 1][c])) and len_down(r, c) > 1
            if is_a or is_d:
                puzzle_grid[r][c] = num
                if is_a:
                    numbering_across.append((num, r, c, len_across(r, c)))
                if is_d:
                    numbering_down.append((num, r, c, len_down(r, c)))
                num += 1
            else:
                puzzle_grid[r][c] = 0

    def clue_for(r, c, length, direction):
        match = next(p for p in norm if p["dir"] == direction and p["r"] == r and p["c"] == c and p["len"] == length)
        clue = words[match["idx"]][2]
        return f"{clue} ({length})"

    across_list = [[n, clue_for(r, c, L, 'A')] for (n, r, c, L) in numbering_across]
    down_list = [[n, clue_for(r, c, L, 'D')] for (n, r, c, L) in numbering_down]

    ipuz = {
        "version": "http://ipuz.org/v2",
        "kind": ["http://ipuz.org/crossword#1"],
        "copyright": "",
        "title": title,
        "author": author,
        "notes": notes,
        "difficulty": "medium",
        "dimensions": {"width": W, "height": H},
        "puzzle": puzzle_grid,
        "solution": sol,
        "clues": {"Across": across_list, "Down": down_list},
    }
    return ipuz, norm, minr, minc


def validate(ipuz, norm):
    sol = ipuz["solution"]
    puzzle = ipuz["puzzle"]
    H, W = ipuz["dimensions"]["height"], ipuz["dimensions"]["width"]

    mismatches = sum(
        1 for r in range(H) for c in range(W)
        if (sol[r][c] == "#") != (puzzle[r][c] == "#")
    )

    declared_across = {(p["r"], p["c"], p["len"]) for p in norm if p["dir"] == 'A'}
    declared_down = {(p["r"], p["c"], p["len"]) for p in norm if p["dir"] == 'D'}

    problems = []
    for r in range(H):
        c = 0
        while c < W:
            if sol[r][c] == '#':
                c += 1; continue
            start = c
            while c < W and sol[r][c] != '#':
                c += 1
            L = c - start
            if L > 1 and (r, start, L) not in declared_across:
                problems.append({"tipo": "linha", "index": r, "start": start, "len": L})
    for c in range(W):
        r = 0
        while r < H:
            if sol[r][c] == '#':
                r += 1; continue
            start = r
            while r < H and sol[r][c] != '#':
                r += 1
            L = r - start
            if L > 1 and (start, c, L) not in declared_down:
                problems.append({"tipo": "coluna", "index": c, "start": start, "len": L})

    return mismatches, problems


def main():
    ap = argparse.ArgumentParser(description="Motor de layout + exportação .ipuz (agnóstico de idioma).")
    ap.add_argument("--words", required=True, help="JSON com lista de {word, clue}")
    ap.add_argument("--count", type=int, default=50, help="Nº de palavras desejado na cruzadinha final")
    ap.add_argument("--title", default="Cruzadinha")
    ap.add_argument("--author", default="Claude")
    ap.add_argument("--notes", default="Gerado automaticamente.")
    ap.add_argument("--out", required=True, help="Caminho do .ipuz de saída")
    args = ap.parse_args()

    with open(args.words, encoding="utf-8") as f:
        raw = json.load(f)

    words = []
    seen = set()
    for item in raw:
        w = normalize_word(item["word"])
        if len(w) < 3 or w in seen:
            continue
        seen.add(w)
        words.append((w, item.get("clue", "")))
    # ordena por comprimento (semente melhor entre as maiores) - mantém ordem estável
    words = [(w, c) for w, c in words]
    # formato interno esperado por build_ipuz: (word, extra, clue) -> usamos (word, word, clue)
    words3 = [(w, w, c) for w, c in words]

    if len(words3) < args.count:
        print(json.dumps({
            "ok": False,
            "error": f"Vocabulário insuficiente: {len(words3)} palavras únicas válidas, "
                     f"mas --count pede {args.count}. Forneça mais palavras."
        }, ensure_ascii=False))
        sys.exit(1)

    try:
        grid, placements = find_best_layout(words3, min_words=min(args.count, len(words3)), limit_to=args.count)
    except RuntimeError as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        sys.exit(1)

    ipuz, norm, minr, minc = build_ipuz(words3, grid, placements, args.title, args.author, args.notes)
    mismatches, problems = validate(ipuz, norm)

    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(ipuz, f, ensure_ascii=False, indent=4)

    report = {
        "ok": mismatches == 0 and len(problems) == 0,
        "words_placed": len(placements),
        "words_requested": args.count,
        "dimensions": ipuz["dimensions"],
        "mismatches_solution_vs_puzzle": mismatches,
        "separation_problems": problems,
        "output_file": args.out,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    sys.exit(0 if report["ok"] else 1)


if __name__ == "__main__":
    main()
