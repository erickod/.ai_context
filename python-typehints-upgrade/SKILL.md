---
name: python-typehints-upgrade
description: Atualiza sintaxe e typehints para a versão alvo do Python priorizando Ruff com fallback para pyupgrade.
triggers: ["atualizar typehints", "upgrade typehints", "modernizar tipos", "update types python", "pyupgrade", "ruff up"]
---

ROLE: python-typehints-upgrade
PRINCIPLE: Execução idempotente, mínima intervenção em regras fora de tipos/sintaxe e estrita preservação da semântica. Prioridade absoluta para Ruff (`UP`); fallback transparente para `pyupgrade`.

PIPELINE:

  1. DISCOVERY & TARGET:
     - Detectar versão alvo do Python:
       * 1º: `pyproject.toml` (`target-version` ou `requires-python`).
       * 2º: `.python-version` / `runtime.txt`.
       * Fallback: Perguntar ao usuário (ex: `py310`, `py311`, `py312`).
     - Detectar arquivos/escopo: argumentos do comando ou arquivos `.py` rastreados (`git ls-files '*.py'`).

  2. TOOL RESOLUTION:
     - Checar disponibilidade do Ruff: `command -v ruff`.
     - Se `ruff` disponível -> ENGINE=RUFF.
     - Se `ruff` ausente:
       * Checar `command -v pyupgrade`.
       * Se disponível -> ENGINE=PYUPGRADE.
       * Se ausente -> Alertar e sugerir instalação: `pip install ruff` (ou `pip install pyupgrade`).

  3. EXECUTION:
     - Se ENGINE=RUFF:
       ```bash
       ruff check --select UP,FA --target-version <TARGET_VER> --fix <TARGET_PATHS>
       ruff format <TARGET_PATHS> # apenas se formatação for explicitamente requisitada
       ```
     - Se ENGINE=PYUPGRADE:
       ```bash
       # Mapear target (ex: py310 -> --py310-plus)
       pyupgrade --<TARGET_VER>-plus <TARGET_FILES>
       ```

  4. VERIFICATION:
     - Rodar `git diff --stat` para exibir resumo de alterações.
     - Validar sintaxe com `python -m py_compile <MODIFIED_FILES>`.

GUARDS & RESTRIÇÕES:
  - NUNCA aplicar regras destrutivas de linter fora de `UP` (Ruff) sem autorização.
  - NUNCA reescrever typehints para sintaxes não suportadas pela versão mínima do projeto (ex: `|` em Python < 3.10 sem `from __future__ import annotations`).
  - NUNCA commitar alterações automaticamente sem revisão do `git diff`.

GATE.out:
  - target_version=definido · engine=resolvido(ruff|pyupgrade) · execution=sucesso · syntax_check=passed · diff=apresentado → Typehints modernizados com sucesso.
