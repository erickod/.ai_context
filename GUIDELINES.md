# KYC Workflow Coding Guidelines

## 1. Objetivo

Estas guidelines definem a estrutura, convenções e regras de
implementação do projeto **KYC Workflow**.

Objetivos: - previsibilidade para desenvolvimento humano - geração
consistente de código por LLMs - isolamento entre domínio, aplicação e
infraestrutura - preservar a regra central do projeto

> O workflow decide o próximo fato; o handler apenas reage.

------------------------------------------------------------------------

# 2. Regras Arquiteturais Centrais

## 2.1 Fronteira do Runtime

A única fronteira pública de mutação do runtime é:

    WorkflowExecution.run(input)

Nenhuma outra parte do sistema deve: - escolher step diretamente -
transitar step diretamente - emitir InteractionRequest - decidir
progressão do fluxo

------------------------------------------------------------------------

## 2.2 Regra de decisão

Responsabilidades:

WorkflowExecution - decide qual step executar

StepExecution - executa lógica local do step

UseCase - coordena aplicação

Handler - reage a eventos

------------------------------------------------------------------------

## 2.3 Direção de dependência

    UseCase → WorkflowExecution → StepExecution

Nunca o inverso.

Proibido:

-   StepExecution chamar UseCase
-   StepExecution chamar Adapter
-   StepExecution chamar Handler
-   Handler decidir próximo step

------------------------------------------------------------------------

# 3. Estrutura do Projeto

Context principal:

    app/

Estrutura recomendada:

    app/
    ├── infra/
    │   ├── adapters/
    │   ├── external_services/
    │   ├── mappers/
    │   ├── repositories/
    │   ├── orm/
    │   ├── http/
    │   └── event_bus/
    │
    ├── domain/
    │   ├── entities/
    │   ├── events/
    │   ├── value_objects/
    │   ├── protocols/
    │   └── exceptions/
    │
    ├── application/
    │   ├── usecases/
    │   ├── event_handlers/
    │   ├── dtos/
    │   └── tests/

------------------------------------------------------------------------

# 4. Convenções de Naming

## Arquivos

snake_case

Exemplos:

    workflow_execution.py
    step_execution.py
    process_events.py
    workflow_execution_repository.py

------------------------------------------------------------------------

## Classes

PascalCase

Sufixos:

Repository\
UseCase\
Handler\
Mapper\
Protocol\
Exception\
Adapter

------------------------------------------------------------------------

## Funções

snake_case

Exemplo:

    run_workflow_usecase
    customer_chat_started_handler
    map_webhook_to_command

------------------------------------------------------------------------

# 5. Camadas

## Domain

Não depende de: - application - infra

Contém:

-   entidades
-   value objects
-   protocols
-   events
-   exceptions

------------------------------------------------------------------------

## Application

Responsável por:

-   carregar aggregate
-   executar usecase
-   chamar WorkflowExecution.run()
-   persistir
-   publicar eventos

------------------------------------------------------------------------

## Infra

Contém:

-   adapters
-   http
-   orm
-   event bus
-   clients externos

Nunca contém lógica de negócio.

------------------------------------------------------------------------

# 6. WorkflowExecution

Aggregate principal.

Responsabilidades:

-   decidir step executável
-   entregar input ao step
-   coletar facts
-   emitir InteractionRequest

API pública mínima:

    run(input)

------------------------------------------------------------------------

# 7. StepExecution

Responsável por lógica local do step.

Estados mínimos:

    PENDING
    WAITING
    COMPLETED
    FAILED

Métodos esperados:

    run(input, context)
    get_events()

------------------------------------------------------------------------

# 8. StepDefinition

Blueprint estático.

Nunca contém estado runtime.

Contém:

-   name
-   direction
-   dependencies
-   placeholder_keys
-   timeout_policy
-   retry_policy
-   transitions

------------------------------------------------------------------------

# 9. UseCases

Responsabilidades:

-   interpretar intenção externa
-   carregar workflow
-   chamar run()
-   persistir
-   publicar eventos

Use cases nunca escolhem step.

------------------------------------------------------------------------

# 10. Event Handlers

Tipos:

Inbound - webhooks - mensagens externas

Reaction - reagem a InteractionRequest

Handlers nunca decidem fluxo.

------------------------------------------------------------------------

# 11. DTOs

DTOs ficam em:

    application/dtos/

Regras:

-   usar dataclass
-   sempre nome explícito
-   evitar dict anônimo atravessando camadas

------------------------------------------------------------------------

# 12. Protocols

Dependências externas devem ser abstraídas.

Exemplos:

    WorkflowExecutionRepositoryProtocol
    EventBusProtocol
    MessageBridgeProtocol
    CompanyLookupProtocol
    PixPaymentProtocol
    BiometricValidationProtocol

------------------------------------------------------------------------

# 13. Integrações Externas

Providers utilizados:

PIX → StarkBank\
Biometria → IDWall

Fluxo correto:

    Webhook
    → Adapter
    → Mapper
    → Input tipado
    → UseCase
    → Workflow.run()

------------------------------------------------------------------------

# 14. Exceções

Tipos:

DomainException\
ApplicationException\
InfrastructureException

Nunca usar Exception genérica.

------------------------------------------------------------------------

# 15. Regras para LLMs

LLMs devem sempre preservar:

1.  Workflow.run() é a única mutação
2.  StepExecution não chama adapter
3.  InteractionRequest só sai do workflow
4.  Handler não decide fluxo
5.  Webhooks viram input tipado

------------------------------------------------------------------------

# 16. MVP (15 dias)

Escopo mínimo:

Steps:

-   check_phone
-   collect_company_cnpj
-   validate_company_cnpj
-   show_terms
-   accept_terms

Objetivo:

-   validar engine de workflow
-   validar saga reentrante
-   validar InteractionRequest

------------------------------------------------------------------------

# 17. Regra Final

Sempre que houver dúvida:

"Isso decide o fluxo ou apenas reage?"

Se decide → Workflow\
Se reage → Handler / Infra
