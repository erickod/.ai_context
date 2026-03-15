## dev-workflow

> Activate venv
RUN:
  source .venv/bin/activate

> Start Web Server
RUN:
  uvicorn hades.api.main:app --reload

> Run Unit Testes
RUN:
  bash -c "source .venv/bin/activate && make unit-test"

> Run Integration Testes
RUN:
  bash -c "source .venv/bin/activate && make integration-test"

> Run Linters and Format
RUN:
  bash -c "source .venv/bin/activate && mypy ."
  bash -c "source .venv/bin/activate && based-pyright ."

> Generate Migration with model changes
RUN:
  bash -c "source .venv/bin/activate && make db_generate_revision"
