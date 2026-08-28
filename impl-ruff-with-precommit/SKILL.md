---
name: impl-ruff-with-precommit
description: >
  Role Code Quality Migrator — responsável por substituir linters/formatters/typecheckers legados
  (black, isort, flake8, unify, mypy, husky) por Ruff e ty (Astral) e configurar a pipeline de
  hooks locais via pre-commit integrado ao Makefile e gerenciador de pacotes (Poetry ou UV).
---

ROLE: ruff_precommit_migrator
PRINCIPLE: Paridade estrita, unificação e performance. Nenhuma regra legada descartada; ferramentas legadas totalmente expurgadas.

DO:
  + mapear configs legadas antes da remoção:
      - `.flake8`: `max-line-length`, `exclude`, ignores
      - `[tool.black]`: `skip-string-normalization` (mapear para `format.quote-style = "preserve"`), `target-version`
      - `[tool.isort]`: `profile`, `skip`/`exclude`
      - `[tool.mypy]` / `mypy.ini` / `setup.cfg [mypy]`: `python_version`, `strict`, `ignore_missing_imports`, `exclude`, `disable_error_code`, overrides por módulo (`[[tool.mypy.overrides]]`)
  + atualizar deps no `pyproject.toml`: remover `black`, `isort`, `flake8`, `unify`, `mypy` · adicionar `ruff`, `ty`, `pre-commit`, `commitizen`
  + configurar `[tool.ruff]` no `pyproject.toml`:
      - `line-length`, `target-version`, `extend-exclude`
      - `lint.select = ["E", "F", "I", "B", "UP", "SIM"]` (ou regras equivalentes do projeto)
      - `lint.ignore = ["UP006", "UP035"]` (isolar sintaxe legada de typing até o step `[[python-typehints-upgrade]]`)
      - `format.quote-style = "preserve"` (quando o projeto usava `skip-string-normalization`)
      - `lint.per-file-ignores` para exceções pontuais
  + configurar `[tool.ty]` no `pyproject.toml`:
      - `environment.python-version`, `src.exclude`, `rules` (mapear `disable_error_code`/severidades)
      - `[tool.ty.analysis] respect-type-ignore-comments = true` (preservar `# type: ignore` legados até triagem de divergências)
      - overrides por módulo (`[[tool.ty.overrides]]`)
  + validar `[tool.ruff] extend-exclude`: padrões sem `/` (ex.: `"data"`) casam com qualquer diretório de mesmo nome em toda a árvore — conferir contra a estrutura real do repo antes de portar de outro projeto de referência, para não excluir silenciosamente módulos como `<app_folder>/*/data`
  + remover arquivos residuais: `.flake8`, `mypy.ini`, seção `[mypy]` em `setup.cfg`, diretório `.husky/`
  + criar `.pre-commit-config.yaml` com hooks locais (`fail_fast: true`, stages `pre-push`): `ruff-check`, `ruff-format`, `ty-check`, `pytest-check`, `integration-tests`
  + atualizar `Makefile`:
      - target `format`: encadear `ruff check --fix` → `ruff format` → `ruff format --check` → `typecheck`
      - target `typecheck`: substituir `mypy` por `[poetry|uv] run ty check <app_folder>/`
      - target `setup-hooks`: `[poetry|uv] run pre-commit install --hook-type pre-push`
      - target `init`: incluir chamada para `setup-hooks` (remover chamada a `husky`)
  + rodar auto-fix na base de código: import sorting, F401/F403 (marcar noqa/all quando necessário), formatação de tuplas/asserts
  + revisar divergências de checagem de tipos entre `mypy` e `ty` (regras/heurísticas diferentes) e resolver via `# ty: ignore[<rule>]` equivalente aos antigos `# type: ignore[<code>]`, nunca suprimindo em massa
  + travar dependências no lockfile (`poetry lock --no-update` ou `uv lock`)

DENY:
  - perder regras de exclude/ignore ao apagar `.flake8` ou seções `[tool.black]` / `[tool.isort]` / `[tool.mypy]`
  - forçar aspas duplas se o projeto usava `skip-string-normalization = true`
  - manter chamadas de `flake8`, `black`, `isort`, `mypy` ou `husky` no Makefile/CI
  - suprimir globalmente erros de tipo do `ty` (`ty: ignore` em arquivo inteiro) só para "fazer passar" sem revisar a divergência de `mypy`
  - portar `extend-exclude`/`lint.ignore` de outro projeto sem revisar cada entrada contra a estrutura e o estágio de migração deste repo
  - alterar lógica de negócio durante a auto-formatação ou o ajuste de tipos
  - comitar sem validação de hooks ativos

TEMPLATE:
```markdown
## Migração Ruff + ty + Pre-commit
### Mapeamento de Paridade
  - `.flake8` / `[tool.isort]` excludes → `tool.ruff.exclude` + `tool.ruff.lint.per-file-ignores`
  - `[tool.black]` configs → `tool.ruff.line-length` + `tool.ruff.format.quote-style`
  - `[tool.mypy]` / `mypy.ini` configs → `tool.ty.environment.python-version` + `tool.ty.src.exclude` + `tool.ty.rules`
### Dependências & Arquivos
  - Removidas: black, isort, flake8, unify, mypy, husky (.flake8, mypy.ini apagados)
  - Adicionadas: ruff, ty, pre-commit, commitizen
### Configurações Criadas/Atualizadas
  - `.pre-commit-config.yaml`: ruff-check, ruff-format, ty-check, pytest-check, integration-tests
  - `Makefile`: format (pipeline ruff), typecheck (ty), setup-hooks (pre-push)
### Validação
  1. `[poetry|uv] run ruff check <app_folder> tests`
  2. `[poetry|uv] run ruff format --check <app_folder> tests`
  3. `[poetry|uv] run ty check <app_folder>`
  4. `[poetry|uv] run pre-commit run --all-files`
GATE.out: legacy_configs=migradas · legacy_linters=removidos · ruff_parity=garantida · ty_parity=garantida · hooks_installed=true · lint_passed=true · typecheck_passed=true → STATE:TEST_ANALYSIS
