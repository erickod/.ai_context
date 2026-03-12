# Guidelines de Desenvolvimento de Software

## Project Structure

Este projeto é organizado em bounded contexts. Cada context deve estar isolado e seguir a seguinte estrutura de diretórios e responsabilidades:

```
base_dir/app/context_name/      # base_dir é o diretório criado pelo git clone
├── infra/                      # Implementações concretas e adapters
│   ├── mappers/                # Conversão entre camadas
│   │   ├── {entity}_mapper.py
│   │   └── __init__.py
│   ├── repositories/           # Implementações de persistência
│   │   ├── {entity}_repository.py
│   │   └── __init__.py
│   ├── orm/                    # Configuração de ORMs
│   │   ├── tortoise/
│   │   │   ├── models.py
│   │   │   ├── config.py
│   │   │   └── __init__.py
│   │   └── sqlalchemy/
│   │       ├── models.py
│   │       ├── config.py
│   │       └── __init__.py
│   ├── external_services/      # Integrações com APIs externas
│   │   ├── {service}_client.py
│   │   └── __init__.py
│   ├── event_bus/              # Implementação do barramento de eventos
│   │   ├── event_bus.py
│   │   └── __init__.py
│   ├── http/                   # Implementação de HTTP servers
│   │   ├── server/
│   │   │   ├── app.py
│   │   │   ├── config.py
│   │   │   └── __init__.py
│   │   ├── routes/
│   │   │   ├── {entity}_routes.py
│   │   │   └── __init__.py
│   │   ├── schemas/            # Pydantic, Marshmallow, etc
│   │   │   ├── {entity}_schema.py
│   │   │   └── __init__.py
│   │   ├── middleware/         # Middlewares HTTP
│   │   │   ├── {middleware}_middleware.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   ├── cli/                    # Command Line Interfaces
│   │   ├── commands/
│   │   │   ├── {command}_command.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   └── __init__.py
│
├── domain/                     # Lógica de negócio pura (zero dependências externas)
│   ├── events/                 # Eventos de domínio
│   │   ├── {entity}_events.py
│   │   └── __init__.py
│   ├── entities/               # Agregados e entidades
│   │   ├── {entity}.py
│   │   └── __init__.py
│   ├── value_objects/          # Objetos de valor imutáveis
│   │   ├── {value_object}.py
│   │   └── __init__.py
│   ├── protocols/              # Interfaces/ABCs (abstrações esperadas)
│   │   ├── {entity}_repository.py
│   │   ├── {service}_service.py
│   │   └── __init__.py
│   └── __init__.py
│
├── application/                # Casos de uso e orquestração
│   ├── usecases/               # Implementações dos casos de uso
│   │   ├── {usecase}_usecase.py
│   │   └── __init__.py
│   ├── event_handlers/         # Handlers que reagem a eventos de domínio
│   │   ├── {event}_handler.py
│   │   └── __init__.py
│   ├── dtos/                   # Data Transfer Objects
│   │   ├── {entity}_input.py
│   │   ├── {entity}_output.py
│   │   └── __init__.py
│   ├── exceptions/             # Exceções da application (não reaplicáveis)
│   │   ├── {entity}_exceptions.py
│   │   └── __init__.py
│   ├── __init__.py
│   └── tests/                  # Testes da application
│       ├── integration/
│       │   ├── test_{usecase}_integration.py
│       │   └── __init__.py
│       ├── unit/
│       │   ├── test_{usecase}_unit.py
│       │   └── __init__.py
│       └── __init__.py
│
└── __init__.py
```

---

## Convenções de Naming

### Arquivos e Diretórios
- Use `snake_case` para nomes de arquivos e diretórios
- Use nomes no **plural** para diretórios que contêm múltiplos arquivos de mesmo tipo (`repositories/`, `entities/`, `handlers/`)
- Use nomes no **singular** para arquivos (`user_repository.py`, `user_entity.py`, não `users_repository.py`)

### Classes
- Use `PascalCase` para classes
- Sufixos padrão:
  - `Repository` - Implementações de persistência (ex: `UserRepository`)
  - `UseCase` - Casos de uso baseados em classes (ex: `CreateUserUseCase`)
  - `Handler` - Manipuladores de eventos baseados em classes (ex: `UserCreatedHandler`)
  - `Service` - Serviços da application (ex: `EmailService`) - **nunca no domain**
  - `Protocol` - Interfaces/ABCs (ex: `UserRepositoryProtocol`)
  - `Exception` - Exceções customizadas (ex: `UserNotFoundException`)
  - `Mapper` - Conversores entre objetos (ex: `UserMapper`)
  - `Schema` - Schemas de validação (ex: `CreateUserSchema`)

### Funções
- Use `snake_case` para funções
- Sufixos padrão para funções:
  - `_usecase` ou `_handler` - Casos de uso ou handlers implementados como funções (ex: `get_user_usecase`, `user_created_handler`)
- Funções assincronizadas devem ser prefixadas com `async def`

### Constantes
- Use `UPPER_SNAKE_CASE` para constantes globais
- Constantes privadas/internas com prefixo `_` (ex: `_DEFAULT_TIMEOUT`)

### Variáveis
- Use `snake_case` para variáveis locais
- Variáveis privadas de classe/instância com prefixo `_` (ex: `self._internal_state`)

---

## Princípios de Design

### Inversão de Dependência
- A camada `domain/` **nunca** deve depender de outras camadas
- A camada `application/` pode depender de `domain/` e seus próprios `protocols/`
- A camada `infra/` implementa os `protocols/` do `domain/` e `application/`
- Use `Protocol` para abstrair dependências

### Isolamento de Contextos
- Cada bounded context é independente
- Comunicação entre contexts deve ocorrer apenas através de:
  - Event Bus (para events publicados)
  - APIs HTTP (para chamadas síncronas)
  - Nunca importe diretamente classes de outro context

### Exceções
- **Domain exceptions**: Representam violações de regras de negócio (herdam de `DomainException`)
- **Application exceptions**: Representam erros de orquestração (herdam de `ApplicationException`)
- **Infrastructure exceptions**: Wrappadas e convertidas em exceptions da camada application/domain
- Sempre defina exceções customizadas ao invés de usar exceções genéricas

Exemplo:
```python
# domain/exceptions/user_exceptions.py
class UserException(Exception):
    """Base para exceções de usuário"""
    pass

class UserNotFound(UserException):
    """Usuário não encontrado"""
    def __init__(self, user_id: str):
        self.user_id = user_id
        super().__init__(f"User not found: {user_id}")

class InvalidUserEmail(UserException):
    """Email do usuário é inválido"""
    def __init__(self, email: str):
        self.email = email
        super().__init__(f"Invalid email: {email}")
```

---

## Implementação de UseCases

A escolha entre classe ou função deve ser baseada na complexidade e número de dependências:

### Padrão 1: Classes (Recomendado para múltiplas dependências)

Use para:
- Múltiplas dependências (≥ 2)
- Múltiplas responsabilidades ou etapas complexas
- Quando há estado que precisa ser mantido

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

@dataclass
class CreateUserInput:
    """Input para criar um novo usuário"""
    name: str
    email: str

@dataclass
class CreateUserOutput:
    """Output após criar um usuário"""
    user_id: str
    created_at: datetime

class CreateUserUseCase:
    """
    Use case para criar um novo usuário.
    
    Responsabilidades:
    - Validar dados de entrada
    - Criar entidade de usuário
    - Persistir usuário
    - Publicar evento de criação
    - Enviar email de boas-vindas
    """
    
    def __init__(
        self,
        *,
        user_repository: UserRepositoryProtocol,
        email_service: EmailServiceProtocol,
        event_bus: EventBusProtocol,
    ) -> None:
        self._user_repository = user_repository
        self._email_service = email_service
        self._event_bus = event_bus

    async def execute(self, input_dto: CreateUserInput) -> CreateUserOutput:
        """Executa o caso de uso."""
        # Criar entidade de domínio
        user = User.create(name=input_dto.name, email=input_dto.email)
        
        # Persistir
        await self._user_repository.save(user)
        
        # Publicar eventos de domínio
        await self._event_bus.publish(user.events)
        
        # Executar ações secundárias
        await self._email_service.send_welcome_email(user.email)
        
        return CreateUserOutput(user_id=user.id, created_at=user.created_at)
```

### Padrão 2: Funções (Para casos simples)

Use para:
- Casos muito simples (1-2 etapas)
- Apenas 1 dependência ou nenhuma
- Sem estado compartilhado

```python
from dataclasses import dataclass

@dataclass
class GetUserInput:
    """Input para obter um usuário"""
    user_id: str

@dataclass
class GetUserOutput:
    """Output ao obter um usuário"""
    id: str
    name: str
    email: str

async def get_user_usecase(
    input_dto: GetUserInput,
    *,
    repository: UserRepositoryProtocol,
) -> GetUserOutput:
    """
    Use case para obter um usuário por ID.
    
    Args:
        input_dto: Dados de entrada com o ID do usuário
        repository: Repositório de usuários (keyword-only)
        
    Returns:
        GetUserOutput: Dados do usuário
        
    Raises:
        UserNotFound: Se o usuário não for encontrado
    """
    user = await repository.get_by_id(input_dto.user_id)
    
    if not user:
        raise UserNotFound(input_dto.user_id)
    
    return GetUserOutput(
        id=user.id,
        name=user.name,
        email=user.email,
    )
```

### Critérios de Decisão

| Número de Dependências | Complexidade | Recomendação |
|------------------------|--------------|--------------|
| 0-1 | Baixa (1-2 passos) | **Função** |
| 1 | Média | **Classe ou Função** (sua escolha) |
| ≥ 2 | Média ou Alta | **Classe** |

**Regra de ouro**: Se você vai precisar adicionar uma segunda dependência no futuro, comece com a classe desde o início.

---

## Event Handlers

Event handlers devem seguir o mesmo padrão dos usecases:

### Como Classe
```python
class UserCreatedHandler:
    """Handler que reage ao evento UserCreated"""
    
    def __init__(
        self,
        *,
        email_service: EmailServiceProtocol,
        analytics_service: AnalyticsServiceProtocol,
    ) -> None:
        self._email_service = email_service
        self._analytics_service = analytics_service

    async def handle(self, event: UserCreated) -> None:
        """Processa o evento."""
        await self._email_service.send_welcome_email(event.email)
        await self._analytics_service.track_user_signup(event.user_id)
```

### Como Função
```python
async def user_created_handler(
    event: UserCreated,
    *,
    email_service: EmailServiceProtocol,
) -> None:
    """Handler que envia email ao usuário ser criado"""
    await email_service.send_welcome_email(event.email)
```

---

## Parâmetros de Função

### Keyword-Only Arguments
- Se a função/método tiver **≥ 3 parâmetros**, use `*` para forçar parâmetros nomeados
- Dependências injetadas devem **sempre** ser keyword-only (use `*` ou coloque após `*`)

```python
# ❌ Evitar
async def create_user(name: str, email: str, repository, event_bus, email_service):
    pass

# ✅ Bom
async def create_user(
    name: str,
    email: str,
    *,
    repository: UserRepositoryProtocol,
    event_bus: EventBusProtocol,
    email_service: EmailServiceProtocol,
) -> User:
    pass

# ✅ Também aceitável para casos simples
async def get_user(user_id: str, *, repository: UserRepositoryProtocol) -> User:
    pass
```

### Parâmetros Posicionais
- Use apenas para parâmetros que são parte da "identidade" da função
- DTOs de entrada podem ser posicionais se forem o primeiro parâmetro
- Dependências **nunca** devem ser posicionais

---

## DTOs (Data Transfer Objects)

Use dataclasses para DTOs:

Os DTOs devem ser definidos como dataclasses no mesmo arquivo do UseCase  que os utiliza. Isso garante que o contrato de entrada e saída esteja sempre visível junto com a lógica de orquestração.

Regras:
  - Defina-os no topo do arquivo, antes da classe/função do UseCase.
  - Use o sufixo Input para dados de entrada e Output para dados de saída.
  - Cada UseCase deve ter seus próprios DTOs (evite reutilizar DTOs entre UseCases diferentes para manter o desacoplamento).

```python
from dataclasses import dataclass
from datetime import datetime

@dataclass
class CreateUserInput:
    """DTO de entrada para criar usuário"""
    name: str
    email: str

@dataclass
class UserOutput:
    """DTO de saída com dados do usuário"""
    id: str
    name: str
    email: str
    created_at: datetime
    
class SomeUsecase:...
```

**Boas práticas:**
- Cada usecase deve ter seu próprio Input/Output DTO
- Reutilize apenas em casos muito simples
- Adicione docstrings aos DTOs
- Use validação com Pydantic quando necessário para input externo (HTTP)

---

## Repositories

Sempre defina uma `Protocol` (interface) no domain e implemente na infra:

```python
# domain/protocols/user_repository.py
from typing import Protocol, Optional

class UserRepositoryProtocol(Protocol):
    """Interface esperada do repositório de usuários"""
    
    async def save(self, user: User) -> None:
        """Persiste um usuário"""
        ...
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        """Obtém um usuário por ID"""
        ...
    
    async def delete(self, user_id: str) -> None:
        """Deleta um usuário"""
        ...

# infra/repositories/user_repository.py
from domain.protocols.user_repository import UserRepositoryProtocol
from infra.orm.tortoise.models import UserModel
from infra.mappers.user_mapper import UserMapper

class TortoiseUserRepository(UserRepositoryProtocol):
    """Implementação com Tortoise ORM"""
    
    async def save(self, user: User) -> None:
        model = UserMapper.to_persistence(user)
        await model.save()
    
    async def get_by_id(self, user_id: str) -> Optional[User]:
        model = await UserModel.get_or_none(id=user_id)
        return UserMapper.to_domain(model) if model else None
    
    async def delete(self, user_id: str) -> None:
        await UserModel.filter(id=user_id).delete()
```

---

## Testes

### Estrutura
- **Unit**: Testam lógica isolada (entities, value objects, funções puras)
- **Integration**: Testam a orquestração de componentes (usecases com mocks de infra)
- **E2E**: Testam fluxos completos (opcional, no projeto se houver)

### Exemplo de Teste de UseCase

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_create_user_success():
    # Arrange
    input_dto = CreateUserInput(name="John Doe", email="john@example.com")
    repository_mock = AsyncMock(spec=UserRepositoryProtocol)
    event_bus_mock = AsyncMock(spec=EventBusProtocol)
    email_service_mock = AsyncMock(spec=EmailServiceProtocol)
    
    usecase = CreateUserUseCase(
        user_repository=repository_mock,
        event_bus=event_bus_mock,
        email_service=email_service_mock,
    )
    
    # Act
    output = await usecase.execute(input_dto)
    
    # Assert
    assert output.user_id is not None
    repository_mock.save.assert_called_once()
    event_bus_mock.publish.assert_called_once()
    email_service_mock.send_welcome_email.assert_called_once_with("john@example.com")

@pytest.mark.asyncio
async def test_create_user_invalid_email():
    # Arrange
    input_dto = CreateUserInput(name="John Doe", email="invalid-email")
    repository_mock = AsyncMock(spec=UserRepositoryProtocol)
    event_bus_mock = AsyncMock(spec=EventBusProtocol)
    email_service_mock = AsyncMock(spec=EmailServiceProtocol)
    
    usecase = CreateUserUseCase(
        user_repository=repository_mock,
        event_bus=event_bus_mock,
        email_service=email_service_mock,
    )
    
    # Act & Assert
    with pytest.raises(InvalidUserEmail):
        await usecase.execute(input_dto)
```

---

## Imports

### Ordem de Imports
Siga a ordem padrão do PEP 8:

```python
# 1. Imports da biblioteca padrão
from datetime import datetime
from typing import Optional, Protocol
import asyncio

# 2. Imports de bibliotecas terceiras
from dataclasses import dataclass
import pytest

# 3. Imports locais (relativo)
from domain.entities.user import User
from domain.exceptions.user_exceptions import UserNotFound
from domain.protocols.user_repository import UserRepositoryProtocol
from application.dtos.user_output import UserOutput
```

### Evite Imports Circulares
- Use `TYPE_CHECKING` para imports apenas de tipo
- Não importe diretamente classes de outros contexts
- Prefira depender de Protocols/Interfaces

```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from domain.entities.user import User  # Apenas para type hints
```

---

## Documentação

### Docstrings
Use o padrão Google/NumPy style:

```python
class CreateUserUseCase:
    """
    Use case para criar um novo usuário.
    
    Responsabilidades:
    - Validar dados de entrada
    - Criar entidade de usuário
    - Persistir usuário
    - Publicar evento de criação
    - Enviar email de boas-vindas
    
    Attributes:
        _user_repository: Repositório de usuários
        _email_service: Serviço de email
        _event_bus: Barramento de eventos
    """
    
    async def execute(self, input_dto: CreateUserInput) -> CreateUserOutput:
        """
        Executa o caso de uso de criação de usuário.
        
        Args:
            input_dto: Dados de entrada com nome e email do usuário
            
        Returns:
            CreateUserOutput: ID do usuário criado e data de criação
            
        Raises:
            InvalidUserEmail: Se o email for inválido
            UserAlreadyExists: Se um usuário com esse email já existe
            
        Example:
            >>> usecase = CreateUserUseCase(...)
            >>> output = await usecase.execute(
            ...     CreateUserInput(name="John", email="john@example.com")
            ... )
        """
```

### README.md por Context
Cada bounded context deve ter um `README.md` descrevendo:
- O propósito do context
- Entidades principais
- Casos de uso principais
- Como rodar testes
- Dependências externas

---

## Boas Práticas Gerais

### ✅ Faça
- Mantenha as funções pequenas e focadas (máximo 30-40 linhas)
- Use type hints em tudo
- Escreva testes antes ou junto com o código
- Publique eventos de domínio para comunicação entre aggregates
- Documente decisões arquiteturais com ADRs (Architecture Decision Records)
- Valide entrada na borda (HTTP schemas, CLI)
- O Uso de uma única linha em branco para separar as fases de um teste (Arrange, Act, Assert) é permitido.

### ❌ Evite
- Lógica de negócio na camada infra
- Dependências circulares entre modules
- Exceptions genéricas (Exception, RuntimeError)
- Acoplamento entre contexts
- Modificar entidades de domínio sem passar por behaviors
- Deixar variáveis mágicas sem documentação
- Evite o uso excessivo de linhas em branco; se uma função precisa de muitos separadores, ela deve ser dividida. 

---

## Exemplo Completo

Aqui um exemplo de um bounded context completo seguindo essas guidelines:

```
base_dir/app/context_name/
├── infra/
│   ├── repositories/
│   │   ├── tortoise_user_repository.py
│   │   └── __init__.py
│   ├── orm/tortoise/
│   │   ├── models.py
│   │   ├── config.py
│   │   └── __init__.py
│   ├── mappers/
│   │   ├── user_mapper.py
│   │   └── __init__.py
│   ├── external_services/
│   │   ├── sendgrid_email_client.py
│   │   └── __init__.py
│   ├── http/
│   │   ├── server/
│   │   │   ├── app.py
│   │   │   └── __init__.py
│   │   ├── routes/
│   │   │   ├── user_routes.py
│   │   │   └── __init__.py
│   │   ├── schemas/
│   │   │   ├── user_schema.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   └── __init__.py
│
├── domain/
│   ├── entities/
│   │   ├── user.py
│   │   └── __init__.py
│   ├── value_objects/
│   │   ├── email.py
│   │   └── __init__.py
│   ├── events/
│   │   ├── user_events.py
│   │   └── __init__.py
│   ├── protocols/
│   │   ├── user_repository.py
│   │   ├── email_service.py
│   │   └── __init__.py
│   ├── exceptions/
│   │   ├── user_exceptions.py
│   │   └── __init__.py
│   └── __init__.py
│
├── application/
│   ├── usecases/
│   │   ├── create_user_usecase.py
│   │   ├── get_user_usecase.py
│   │   └── __init__.py
│   ├── event_handlers/
│   │   ├── user_created_handler.py
│   │   └── __init__.py
│   ├── dtos/
│   │   ├── user_input.py
│   │   ├── user_output.py
│   │   └── __init__.py
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_create_user_usecase.py
│   │   │   └── __init__.py
│   │   ├── integration/
│   │   │   ├── test_create_user_integration.py
│   │   │   └── __init__.py
│   │   └── __init__.py
│   └── __init__.py
│
└── __init__.py
```
