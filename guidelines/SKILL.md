---
name: guidelines
description: >
  Guidelines de arquitetura e código para bounded contexts (DDD/Clean Architecture).
  Fonte transversal autoritativa consultada por definition e eng. Ative ao planejar,
  implementar ou revisar estrutura de diretórios, naming, DI, DTOs, usecases,
  exceptions, imports ou testes.
disable-model-invocation: true
---

ROLE: guidelines
PRINCIPLE: bounded contexts isolados · domain sem dependências externas · DI via Protocol

CONTEXT:
  base_dir: definido pelo projeto consumidor (ex.: `argos`, `easy_lease`) — raiz de `app/context_name/`

STRUCTURE: `base_dir/app/context_name/`
  infra/        implementações concretas e adapters
    mappers/{entity}_mapper.py · repositories/{entity}_repository.py
    orm/{tortoise,sqlalchemy}/models.py+config.py
    external_services/{service}_client.py · event_bus/event_bus.py
    http/server|routes|schemas|middleware · cli/commands/{command}_command.py
  domain/       lógica de negócio pura · zero deps externas
    events/{entity}_events.py · entities/{entity}.py · value_objects/{value_object}.py
    protocols/{entity}_repository.py · {service}_service.py
  application/  casos de uso e orquestração
    usecases/{usecase}_usecase.py · event_handlers/{event}_handler.py
    dtos/{entity}_input.py · {entity}_output.py · exceptions/{entity}_exceptions.py
    tests/{unit,integration}/test_{usecase}_*.py

NAMING:
  files/dirs:  snake_case · dirs plural (repositories/) · arquivos singular (user_repository.py)
  classes:     PascalCase + sufixo — Repository · UseCase · Handler · Service(nunca domain) · Protocol · Exception · Mapper · Schema
  funções:     snake_case + sufixo _usecase|_handler · async def quando assíncrona
  constantes:  UPPER_SNAKE_CASE · privadas com prefixo _
  variáveis:   snake_case · privadas de instância com prefixo _

DESIGN:
  DI:         domain nunca depende de outras camadas · application depende de domain+seus protocols · infra implementa protocols · usar Protocol para abstrair
  isolamento: bounded contexts só comunicam via event bus (assíncrono) ou HTTP (síncrono) · DENY: import direto de classe de outro context
  exceptions: DomainException/ApplicationException próprias por camada · infra exceptions wrappadas antes de subir · DENY: Exception/RuntimeError genéricas

USECASES:
  decisão: 0-1 dep + baixa complexidade → função | ≥2 dep ou média/alta complexidade → classe
  regra de ouro: se uma 2ª dependência é previsível → comece com classe
  classe:  `__init__(self, *, dep_a: Protocol, dep_b: Protocol)` + `async def execute(self, input_dto) -> output_dto`
  função:  `async def {nome}_usecase(input_dto, *, dep: Protocol) -> Output`
  mesmo padrão vale para event handlers (método `handle` / função `{evento}_handler`)

DTOS:
  dataclass · definido no mesmo arquivo do usecase que o usa, no topo (antes da classe/função) · sufixo Input/Output
  DENY: reutilizar DTO entre usecases diferentes (exceto casos triviais) · omitir docstring

PARAMS:
  ≥3 parâmetros → forçar keyword-only (`*`) · dependências injetadas SEMPRE keyword-only, nunca posicionais
  posicional permitido só para o DTO de entrada como 1º parâmetro

REPOSITORIES:
  Protocol no domain (`domain/protocols/`) · implementação concreta na infra (`infra/repositories/`)
  DENY: lógica de negócio dentro do repository

TESTS:
  unit: entities/VOs/funções puras · integration: usecases com mocks de infra · e2e: opcional
  naming/F.I.R.S.T/given-when-then → REF: `test-analyst/SKILL.md` (não duplicar aqui)
  1 linha em branco entre Arrange/Act/Assert é permitida

IMPORTS:
  ordem PEP8: stdlib → third-party → local
  TYPE_CHECKING para imports só-de-tipo (evita ciclo) · DENY: import direto de classe de outro context

DOCS:
  docstrings estilo Google/NumPy em usecases · handlers · DTOs
  README.md por context: propósito · entidades principais · usecases principais · como testar · deps externas

BOAS PRÁTICAS:
  DO:   funções ≤30-40 linhas · type hints em tudo · eventos de domínio p/ side-effects entre aggregates · ADRs p/ decisões arquiteturais · validar entrada na borda (HTTP/CLI)
  DENY: lógica de negócio em infra · deps circulares entre modules · exceptions genéricas · acoplamento entre contexts · alterar entidade de domínio sem passar por behaviors · variáveis mágicas sem doc · linhas em branco excessivas (função com muitos separadores → dividir)
