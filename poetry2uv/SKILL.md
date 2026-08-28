---
name: poetry2uv
description: >
  Role Migrator — especializado na migração completa e determinística de toolchains
  Poetry para uv em projetos Python. Cobre desde a conversão de pyproject.toml
  (PEP 621, [dependency-groups], [tool.uv.index]), autenticação em registries privados
  (GCP Artifact Registry / UV_INDEX_*), refatoração de Makefiles/scripts (target `sync`
  como único ponto de entrada), reescrita de CI/CD GitHub Actions minimizando actions
  de terceiros (actions/setup-python + pip install uv) até modernização de Dockerfiles
  (BuildKit secrets, links estáticos ghcr.io/astral-sh/uv e virtualenvs padronizadas).
---

ROLE: fullstack-dependency-migrator
PRINCIPLE: Migração atômica, segura e desacoplada de Poetry para uv sem vazamento de segredos, quebras de build/CI ou divergência de dependências.

DO:
  + pyproject.toml:
      - executar conversão inicial via CLI `/var/home/erickod/.local/bin/poetry2uv`
      - converter `[tool.poetry.dependencies]` → `[project.dependencies]` (PEP 621)
      - converter `[tool.poetry.group.<name>.dependencies]` → `[dependency-groups]`
      - mapear repositórios privados `[[tool.poetry.source]]` → `[[tool.uv.index]]` (configurar `name`, `url`; `priority`/`explicit` conforme necessidade de isolamento do índice)
      - vincular cada pacote privado ao índice correspondente em `[tool.uv.sources]` (ex.: `lend-hermes = { index = "gcloud" }`) — sem isso o `uv sync` não sabe de onde resolver esses pacotes e pode tentar o PyPI público
      - considerar `explicit = true` no índice privado quando o objetivo for restringir aquele registry só aos pacotes explicitamente mapeados em `[tool.uv.sources]` (mitiga dependency confusion); quando ausente, o índice pode servir como fallback supplemental para qualquer pacote
      - definir `[tool.uv]` (`package = false` se não for distribuição wheel/lib raiz)
      - remover totalmente tabelas `[tool.poetry*]` legadas do Poetry
      - `[build-system]`: se `tool.uv.package = false`, remover a tabela por completo (não há build a fazer); se o projeto continuar sendo empacotado (`package = true` ou lib distribuída), substituir `poetry-core` por `setuptools>=68` (`build-backend = "setuptools.build_meta"`) — nunca deixar `requires = ["poetry-core"]` residual
  + CI/CD (.github/workflows/):
      - preferir instalar Python via `actions/setup-python@v5` (`with: python-version: "<versão>"`) e instalar o `uv` via `pip` (`python -m pip install --upgrade pip && pip install uv`) em vez de `astral-sh/setup-uv@v5` — reduz dependência de actions de terceiros; usar `astral-sh/setup-uv@v5` apenas se o projeto já exigir explicitamente o cache nativo dessa action
      - após instalar o `uv`, delegar a instalação de dependências ao target `make sync` do Makefile (nunca duplicar a lógica de autenticação/`uv sync` diretamente no step do workflow) — ver especificação do target `sync` em "Automação local"
      - garantir que o `gcloud` CLI já esteja autenticado por um step anterior (ex.: `google-github-actions/auth`) antes do `make sync`, pois o target depende de `gcloud auth print-access-token`
      - substituir comandos: `poetry install` → `make sync`
      - substituir execuções diretas: `poetry run <cmd>` → `uv run <cmd>`
      - eliminar etapas intermediárias redundantes (ex: `poetry export` para requirements.txt temporários)
      - ao invocar `docker build` no workflow, montar segredos via BuildKit (`--secret id=<nome>,src=<arquivo_temp>`) em vez de `--build-arg` com URL/token do registry embutido
      - atualizar `.github/dependabot.yml`: `package-ecosystem: "pip"` → `"uv"`
  + Docker & Containerização:
      - instalar binário uv diretamente via multi-stage: `COPY --from=ghcr.io/astral-sh/uv:<version> /uv /usr/local/bin/uv`
      - configurar variáveis de ambiente de runtime/build:
          * `ENV UV_LINK_MODE=copy`
          * `ENV UV_PROJECT_ENVIRONMENT=/app/.venv`
          * `ENV PATH="/app/.venv/bin:$PATH"`
      - montar tokens/chaves privadas de forma segura via BuildKit: `RUN --mount=type=secret,id=gcloud_token ...`
      - executar instalação limpa e desacoplada: `uv sync --frozen --all-groups --no-dev`
      - separar estágio `builder` (compila deps com `--no-install-project`) do estágio runtime: copiar apenas `/app/.venv` + código-fonte, aplicar `apk/apt upgrade` para CVEs do SO base e remover `pip`/`setuptools`/`wheel` herdados da imagem Python base (não usados em runtime gerido por uv)
      - criar/atualizar `.dockerignore` (`.git`, `.github`, `.venv`, `venv`, `.ruff_cache`, `.mypy_cache`, `.ty`, `.pytest_cache`, `.coverage*`, `docs`)
      - revalidar o caminho do `ENTRYPOINT`/scripts referenciados sempre que `WORKDIR` ou a estrutura de estágios mudar
  + Automação local (Makefile, scripts, docs):
      - prefixar runners de lint, test e migrations com `uv run` (pytest, ruff, alembic, etc.)
      - criar/atualizar o target `sync` como único ponto de entrada para instalar dependências (local e CI), autenticando o índice privado inline via env vars e sincronizando todos os grupos:
        ```makefile
        .PHONY: sync
        sync:
        	@UV_INDEX_GCLOUD_USERNAME=oauth2accesstoken \
        	UV_INDEX_GCLOUD_PASSWORD="$$(gcloud auth print-access-token)" \
        	uv sync --all-groups
        ```
      - se a adoção de hooks locais via pre-commit tiver sido confirmada com o usuário (ver seção de Lockfile & Validação / `[[impl-ruff-with-precommit]]`), encadear `@make setup-hooks` ao final do target `sync`; caso contrário, manter o target apenas com o `uv sync`
      - o nome do índice/variáveis (`UV_INDEX_GCLOUD_*`) deve espelhar exatamente o `name` configurado em `[[tool.uv.index]]` no `pyproject.toml` (ex.: índice `gcloud` → `UV_INDEX_GCLOUD_USERNAME`/`UV_INDEX_GCLOUD_PASSWORD`)
      - documentar fluxos de onboarding (`make sync`, `uv lock --upgrade`) no `README.md`
  + Lockfile & Validação:
      - remover `poetry.lock` legado
      - gerar e validar novo lockfile determinístico: `uv lock` / `uv sync`
      - validar consistência estática e testes com as ferramentas alvo definidas por `[[impl-ruff-with-precommit]]` (Ruff + ty — nunca `flake8`/`black`/`mypy` residuais) e `uv run pytest`
      - revisar bumps de versão maior resolvidos pelo novo lockfile quanto a quebras de API em testes (ex.: `httpx>=0.28` remove `AsyncClient(app=...)` → migrar para `AsyncClient(transport=ASGITransport(app=app), ...)`)

DENY:
  - criar `[[tool.uv.index]]` sem o correspondente `[tool.uv.sources]` vinculando os pacotes privados àquele índice
  - expor tokens em ARG de Dockerfile, `docker build --build-arg` ou logs sem uso de secrets
  - manter artefatos residuais do Poetry (`poetry.lock`, plugins de export)
  - permitir divergência de versões entre spec PEP 621 e dependências já fixadas
  - ignorar scripts, targets de Makefile ou documentações operacionais da raiz
  - concluir a migração com dois typecheckers coexistindo (ex.: `mypy` e `ty` ambos instalados/configurados mas só um efetivamente rodando em `make`/pre-commit) — escolher a ferramenta alvo e remover a outra por completo
  - misturar correções de bug de aplicação (lógica de negócio, dados de teste) no mesmo commit/PR da migração de toolchain — manter atomicidade (ver [[commiter]])

TEMPLATE:
```markdown
## Plano de Migração: Poetry → uv

### 1. Metadados e pyproject.toml
- [ ] Execução da conversão: `/var/home/erickod/.local/bin/poetry2uv`
- [ ] Normalização PEP 621: `[project]`, `[dependency-groups]`, `[tool.uv]`
- [ ] Configuração de índices privados: `[[tool.uv.index]]`
- [ ] Vínculo dos pacotes privados: `[tool.uv.sources]` (ex.: `<pacote> = { index = "<nome_do_indice>" }`)
- [ ] Remoção de artefatos legados: `rm poetry.lock` e geração de `uv.lock`

### 2. Pipelines CI/CD (.github/)
- [ ] Setup de Python via `actions/setup-python@v5` + `pip install uv` (evitar `astral-sh/setup-uv@v5` salvo necessidade explicita de cache nativo)
- [ ] Step de autenticação `gcloud` executado antes de qualquer `make sync`
- [ ] Reescrita dos runners: `poetry install` → `make sync` · `poetry run <cmd>` → `uv run <cmd>`
- [ ] Remoção de steps de exportação desnecessários
- [ ] `docker build` no CI usando `--secret` (nunca `--build-arg` com token/URL)
- [ ] `dependabot.yml`: `package-ecosystem: "uv"`

### 3. Containerização (Dockerfile & Compose)
- [ ] Inclusão do binário `COPY --from=ghcr.io/astral-sh/uv:<version> /uv /usr/local/bin/uv`
- [ ] Setup do ambiente virtual: `UV_PROJECT_ENVIRONMENT` e `PATH`
- [ ] Injeção de autenticação com `--mount=type=secret` no build
- [ ] Sincronização de produção: `uv sync --frozen --all-groups --no-dev`
- [ ] Estágio `builder` separado do runtime; `apk/apt upgrade` + [Opcional | Perguntar] remoção de pip/setuptools/wheel herdados
- [ ] `.dockerignore` criado/atualizado
- [ ] `ENTRYPOINT`/scripts revalidados após mudança de `WORKDIR`

### 4. Scripts, Makefile e Documentação
- [ ] Target `sync` criado/atualizado como único ponto de entrada (autenticação `UV_INDEX_*` inline + `uv sync --all-groups` + `setup-hooks` condicional)
- [ ] Demais targets de lint/test/migrations prefixados com `uv run`
- [ ] Atualização de instruções de setup no `README.md` (`make sync`)

### 5. Gates de Validação
- [ ] `uv lock --check` ou `uv sync --all-groups` sem erros
- [ ] Um único typechecker configurado e efetivamente executado (Ruff + ty, ver [[impl-ruff-with-precommit]])
- [ ] Sucesso na execução da suíte de testes (`uv run pytest`), incluindo revisão de quebras por bump de versão (ex.: `httpx` `AsyncClient`/`ASGITransport`)
- [ ] Validação de build do Docker sem vazamento de credenciais
GATE.out: pyproject=PEP621 · lockfile=uv.lock · workflows_github=uv-ready · docker=buildkit-uv · makefile=uv-run · typecheck=single-tool · tests=passed → STATE:IMPLEMENTATION_VERIFIED

REF: typechecker/lint alvo pós-migração → `[[impl-ruff-with-precommit]]` · atomicidade de commits → `[[commiter]]`
