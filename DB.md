# Database Schema Documentation

Se houver discrepância entre o código e este documento,
atualize este documento para refletir o código antes de continuar.
Só depois disso, continue.

---

## Contexto

- ORM: SQLModel (SQLAlchemy + Pydantic)
- Banco de dados: SQLite (desenvolvimento)
- Configuração: `easy_lease/config.py` → `Settings.database_url`
- Arquivo do banco: `database.db` (raiz do projeto, ignorado pelo git)

---

## Tabelas

### ACCOUNT

Representa uma conta (tenant/inquilino) no sistema.

**Arquivo:** `easy_lease/account/infra/orm/sqlalchemy/models.py`

**Campos:**
- `id` (PK): Identificador único (UUID7, gerado automaticamente)
- `name`: Nome da conta (TEXT, obrigatório)
- `register_code`: Código único de registro da conta (TEXT, obrigatório)
- `created_at`: Timestamp de criação (DATETIME, obrigatório)
- `updated_at`: Timestamp de última atualização (DATETIME, obrigatório)
- `deleted_at`: Timestamp de deleção lógica (DATETIME, opcional — soft delete)

**Constraints:**
- `id` é gerado com `uuid7` como `default_factory`
- Soft delete via `deleted_at` (registro não é removido fisicamente)

**Relacionamentos:**
- `OWNER_ACCOUNT.account_id` → FK para `ACCOUNT.id`
- `RENTER_ACCOUNT.account_id` → FK para `ACCOUNT.id`

---

### OWNER_ACCOUNT

Representa o vínculo de papel Owner de uma conta. Existe no máximo um registro por `Account` (relação 1:1).

**Arquivo:** `easy_lease/account/infra/orm/sqlalchemy/models.py`

**Campos:**
- `id` (PK): Identificador único (UUID7, gerado automaticamente)
- `account_id` (FK → `account.id`): Referência ao Account proprietário (obrigatório)
- `version`: Versão para controle de lock otimista (INTEGER, default=1, obrigatório)
- `created_at`: Timestamp de criação (DATETIME, obrigatório)
- `updated_at`: Timestamp de última atualização (DATETIME, obrigatório)
- `deleted_at`: Timestamp de deleção lógica (DATETIME, opcional — soft delete)

**Constraints:**
- `id` é gerado com `uuid7` como `default_factory`
- `UNIQUE(account_id)` — constraint `uq_owner_account_account_id` — garante no máximo um `OwnerAccount` por `Account`
- Soft delete via `deleted_at` (registro não é removido fisicamente)
- `version` inicia em 1 para novos registros; incrementado a cada update pela implementação concreta do repositório

**Relacionamentos:**
- `account_id` → FK para `ACCOUNT.id`

---

### RENTER_ACCOUNT

Representa o vínculo de papel Renter de uma conta. Existe no máximo um registro por `Account` (relação 1:1).

**Arquivo:** `easy_lease/account/infra/orm/sqlalchemy/models.py`

**Campos:**
- `id` (PK): Identificador único (UUID7, gerado automaticamente)
- `account_id` (FK → `account.id`): Referência ao Account proprietário (obrigatório)
- `version`: Versão para controle de lock otimista (INTEGER, default=1, obrigatório)
- `created_at`: Timestamp de criação (DATETIME, obrigatório)
- `updated_at`: Timestamp de última atualização (DATETIME, obrigatório)
- `deleted_at`: Timestamp de deleção lógica (DATETIME, opcional — soft delete)

**Constraints:**
- `id` é gerado com `uuid7` como `default_factory`
- `UNIQUE(account_id)` — constraint `uq_renter_account_account_id` — garante no máximo um `RenterAccount` por `Account`
- Soft delete via `deleted_at` (registro não é removido fisicamente)
- `version` inicia em 1 para novos registros; incrementado a cada update pela implementação concreta do repositório

**Relacionamentos:**
- `account_id` → FK para `ACCOUNT.id`

---

### RENTABLE_ITEM

Representa um item físico disponível para aluguel, pertencente a um proprietário (owner account).

**Arquivo:** `easy_lease/inventory/infra/orm/sqlalchemy/models.py`

**Campos:**
- `id` (PK): Identificador único (UUID7, gerado automaticamente)
- `owner_account_id`: UUID de referência externa ao account proprietário (UUID, obrigatório — sem FK explícita no banco, referência cross-context)
- `name`: Nome do item (TEXT, obrigatório)
- `description`: Descrição do item (TEXT, obrigatório)
- `base_amount_cents`: Preço base em centavos (INTEGER, obrigatório, > 0)
- `conservation_level`: Nível de conservação (TEXT, obrigatório, default='UNKNOWN')
- `created_at`: Timestamp de criação (DATETIME, obrigatório)
- `updated_at`: Timestamp de última atualização (DATETIME, obrigatório)

**Constraints:**
- `id` é gerado com `uuid7` como `default_factory`
- `base_amount_cents` deve ser > 0 (garantido pela camada de domínio via `Amount`)
- `conservation_level` deve ser um dos valores: `UNKNOWN`, `BRAND_NEW`, `EXCELLENT`, `USED`, `WORN_OUT`

**Relacionamentos:**
- `RENTABLE_ITEM_TAG.rentable_item_id` → FK para `RENTABLE_ITEM.id`

---

### RENTABLE_ITEM_TAG

Armazena as tags individuais associadas a um `RentableItem`. Relação N:1 com `RENTABLE_ITEM`.

**Arquivo:** `easy_lease/inventory/infra/orm/sqlalchemy/models.py`

**Campos:**
- `id` (PK): Identificador único (UUID7, gerado automaticamente)
- `rentable_item_id` (FK → `rentable_item.id`): Referência ao item proprietário da tag (UUID, obrigatório)
- `value`: Valor textual da tag (TEXT, obrigatório)

**Constraints:**
- `id` é gerado com `uuid7` como `default_factory`
- `rentable_item_id` não pode ser nulo

**Relacionamentos:**
- `rentable_item_id` → FK para `RENTABLE_ITEM.id`

---

### RENTABLE_ITEM_SHADOW

Projeção desnormalizada de um `RentableItem` no contexto marketplace. Armazena os dados relevantes do item em um campo JSONB para leituras otimizadas, evitando joins cross-context.

**Arquivo:** `easy_lease/marketplace/infra/orm/sqlalchemy/models.py`

**Campos:**
- `id` (PK): Identificador único — mesmo UUID do `RentableItem` original (UUID7, sem geração automática)
- `content`: Dados desnormalizados do item (JSONB, obrigatório) — inclui: `owner_account_id`, `name`, `description`, `base_amount_cents`, `conservation_level`, `tags` (lista de strings)
- `created_at`: Timestamp de criação da projeção (DATETIME, obrigatório)
- `updated_at`: Timestamp da última sincronização (DATETIME, obrigatório)
- `deleted_at`: Timestamp de deleção lógica (DATETIME, opcional — soft delete)

**Constraints:**
- `id` é o mesmo UUID do `RentableItem` de origem (sem `default_factory`)
- Upsert via `INSERT ... ON CONFLICT DO UPDATE` — apenas `content`, `updated_at` e `deleted_at` são atualizados em conflito; `created_at` é preservado
- Sem FK explícita para `RENTABLE_ITEM` — referência cross-context gerenciada pela aplicação

**Relacionamentos:**
- Nenhum relacionamento de banco de dados — referência ao `RentableItem` original é feita pela igualdade de `id`

---

### ANNOUNCED_ITEM

Representa um anúncio de item na vitrine do Marketplace, vinculado a uma `RentableItemShadow`.

**Arquivo:** `easy_lease/marketplace/infra/orm/sqlalchemy/models.py`

**Campos:**
- `id` (PK): Identificador único (UUID7, gerado automaticamente)
- `shadow_rentable_id`: UUID de referência à `RentableItemShadow` (UUID, obrigatório — sem FK explícita no banco, referência cross-context)
- `owner_account_id`: UUID de referência ao account proprietário (UUID, obrigatório — sem FK explícita no banco, referência cross-context)
- `name`: Override opcional do nome do item na vitrine (TEXT, nullable)
- `description`: Override opcional da descrição do item na vitrine (TEXT, nullable)
- `status`: Status atual do anúncio (TEXT, obrigatório) — valores: `REQUESTED`, `UNDER_REVISION`, `REVISION_APPROVED`, `CHANGES_REQUESTED`, `ACTIVE`, `PAUSED`, `ARCHIVED`
- `amount_cents`: Preço do aluguel em centavos inteiros (INTEGER, obrigatório)

**Constraints:**
- `id` é gerado com `uuid7` como `default_factory`
- `shadow_rentable_id` e `owner_account_id` são referências cross-context sem FK explícita no banco

**Relacionamentos:**
- `ANNOUNCED_ITEM_ORIGIN.announced_item_id` → FK para `ANNOUNCED_ITEM.id`

---

### ANNOUNCED_ITEM_ORIGIN

Armazena a origem geográfica de um `AnnouncedItem`. Relação 1:1 com `ANNOUNCED_ITEM`.

**Arquivo:** `easy_lease/marketplace/infra/orm/sqlalchemy/models.py`

**Campos:**
- `id` (PK): Identificador único (UUID7, gerado automaticamente)
- `announced_item_id` (FK → `announced_item.id`): Referência ao anúncio proprietário (UUID, obrigatório)
- `zipcode`: CEP da localização do item (TEXT, obrigatório)

**Constraints:**
- `id` é gerado com `uuid7` como `default_factory`
- `announced_item_id` não pode ser nulo

**Relacionamentos:**
- `announced_item_id` → FK para `ANNOUNCED_ITEM.id`

---

### ACCOUNT_SHADOW

Projeção (shadow) de uma conta de proprietário (owner account) no contexto `orders`. Armazena os dados mínimos necessários para operações cross-context sem joins.

**Arquivo:** `easy_lease/orders/infra/orm/sqlalchemy/models.py`

**Campos:**
- `id` (PK): Identificador único — mesmo UUID da `OwnerAccount` de origem (UUID, sem geração automática)
- `type`: Papel da conta shadowada (TEXT, obrigatório) — ex: `"OWNER"`
- `created_at`: Timestamp de criação da projeção (DATETIME, obrigatório)
- `updated_at`: Timestamp da última sincronização (DATETIME, obrigatório)
- `deleted_at`: Timestamp de deleção lógica (DATETIME, opcional — soft delete, default null)

**Constraints:**
- `id` espelha o UUID da `OwnerAccount` de origem (sem `default_factory`)
- Upsert via `INSERT ... ON CONFLICT DO UPDATE` — apenas `type`, `updated_at` e `deleted_at` são atualizados em conflito; `created_at` é preservado
- Sem FK explícita para `ACCOUNT` — referência cross-context gerenciada pela aplicação

**Relacionamentos:**
- Nenhum relacionamento de banco de dados — referência à `OwnerAccount` original é feita pela igualdade de `id`

---

### ORDERS

Representa uma ordem de aluguel criada no checkout.

**Arquivo:** `easy_lease/orders/infra/orm/sqlalchemy/models.py`

**Campos:**
- `id` (PK): Identificador único (UUID7, gerado automaticamente)
- `status`: Status atual da ordem (TEXT, obrigatório) — valores: `CREATED`, `PAYMENT_REQUESTED`, `CONFIRMED`, `FAILED`, `EXPIRED`, `CANCELED`, `REFUNDED`
- `subtotal_cents`: Soma dos `amount_cents` dos itens (INTEGER, obrigatório)
- `total_cents`: `subtotal_cents + discount_cents` (INTEGER, obrigatório, > 0)
- `discount_cents`: Valor do desconto em centavos (INTEGER, obrigatório, <= 0)
- `renter_account_id`: UUID de referência ao account locatário (UUID, obrigatório — sem FK explícita, referência cross-context)
- `owner_account_id`: UUID de referência ao account proprietário (UUID, obrigatório — sem FK explícita, referência cross-context)
- `start_date`: Data de início do período de aluguel (DATE, nullable)
- `end_date`: Data de fim do período de aluguel (DATE, nullable)
- `created_at`: Timestamp de criação (DATETIME, obrigatório)
- `updated_at`: Timestamp de última atualização (DATETIME, obrigatório)

**Constraints:**
- `id` é gerado com `uuid7` como `default_factory`
- `discount_cents` armazenado como <= 0 (zero = sem desconto)
- `total_cents` deve ser > 0 (garantido pela camada de domínio via `InvalidOrderTotal`)
- Sem FK explícita para `account` — referências cross-context gerenciadas pela aplicação

**Relacionamentos:**
- `ORDER_ITEMS.order_id` → FK para `ORDERS.id`
- `ORDER_DESTINATIONS.order_id` → FK para `ORDERS.id`

---

### ORDER_ITEMS

Representa um item individual dentro de uma `Order`. Relação N:1 com `ORDERS`.

**Arquivo:** `easy_lease/orders/infra/orm/sqlalchemy/models.py`

**Campos:**
- `id` (PK): Identificador único (UUID7, gerado automaticamente — técnico, sem identidade de domínio)
- `order_id` (FK → `orders.id`): Referência à ordem proprietária (UUID, obrigatório)
- `announced_item_id`: UUID de referência ao item anunciado (UUID, obrigatório — sem FK explícita, referência cross-context)
- `owner_account_id`: UUID de referência ao account proprietário do item (UUID, obrigatório — sem FK explícita, referência cross-context)
- `name`: Nome do item (TEXT, obrigatório)
- `description`: Descrição do item (TEXT, obrigatório)
- `unit_amount_cents`: Preço unitário por dia em centavos (INTEGER, obrigatório, > 0)
- `amount_cents`: `unit_amount_cents * quantity * days` (INTEGER, obrigatório, > 0)
- `quantity`: Quantidade de unidades (INTEGER, obrigatório, >= 1)
- `start_date`: Data de início do aluguel deste item (DATE, nullable)
- `end_date`: Data de fim do aluguel deste item (DATE, nullable)

**Constraints:**
- `id` é gerado com `uuid7` como `default_factory`
- `unit_amount_cents` e `amount_cents` devem ser > 0 (garantido pela camada de domínio)
- `quantity` deve ser >= 1 (garantido pelo VO `OrderItem`)
- `announced_item_id` e `owner_account_id` são referências cross-context sem FK explícita

**Relacionamentos:**
- `order_id` → FK para `ORDERS.id`

---

### ORDER_DESTINATIONS

Armazena o destino de entrega de uma `Order`. Relação 1:1 com `ORDERS`.

**Arquivo:** `easy_lease/orders/infra/orm/sqlalchemy/models.py`

**Campos:**
- `id` (PK): Identificador único (UUID7, gerado automaticamente — técnico, sem identidade de domínio)
- `order_id` (FK → `orders.id`): Referência à ordem proprietária (UUID, obrigatório)
- `zipcode`: CEP do destino de entrega (TEXT, obrigatório)
- `created_at`: Timestamp de criação (DATETIME, obrigatório)
- `updated_at`: Timestamp de última atualização (DATETIME, obrigatório)

**Constraints:**
- `id` é gerado com `uuid7` como `default_factory`
- `order_id` não pode ser nulo

**Relacionamentos:**
- `order_id` → FK para `ORDERS.id`

---

### JOB_QUEUE

Fila de jobs persistida para processamento assíncrono de tarefas. Infraestrutura transversal ao projeto, residente no contexto `shared`.

**Arquivo:** `easy_lease/shared/infra/orm/sqlalchemy/models.py`

**Campos:**
- `id` (PK): Identificador sequencial (INTEGER, autoincrement — BIGSERIAL no Postgres)
- `job_type`: Tipo do job (TEXT, obrigatório)
- `payload`: Dados do job (JSONB, obrigatório)
- `status`: Estado atual do job (TEXT, obrigatório, default=`'pending'`) — valores: `pending`, `processing`, `completed`, `failed`, `dead`
- `priority`: Prioridade do job (SMALLINT, obrigatório, default=`5`)
- `retry_count`: Número de tentativas realizadas (INTEGER, obrigatório, default=`0`)
- `max_retries`: Número máximo de tentativas permitidas (INTEGER, obrigatório, default=`3`)
- `scheduled_for`: Timestamp de agendamento para execução (TIMESTAMPTZ, obrigatório, default=now)
- `created_at`: Timestamp de criação (TIMESTAMPTZ, obrigatório, default=now)
- `started_at`: Timestamp de início do processamento (TIMESTAMPTZ, opcional)
- `completed_at`: Timestamp de conclusão (TIMESTAMPTZ, opcional)
- `error_message`: Mensagem de erro da última falha (TEXT, opcional)

**Constraints:**
- `valid_status`: CHECK `status IN ('pending', 'processing', 'completed', 'failed', 'dead')`

**Índices:**
- `idx_job_fetch`: `(status, scheduled_for, priority, created_at)` — parcial `WHERE status = 'pending'` — otimizado para fetch de jobs a processar
- `idx_job_monitor`: `(job_type, status, created_at)` — para monitoramento e observabilidade

**Relacionamentos:**
- Nenhum — tabela autônoma

---

## Log de Alterações

> Este log é append-only.

### [2026-02-21] — Adição da tabela OWNER_ACCOUNT (TASK-002)
- Adicionada tabela `OWNER_ACCOUNT` com campos: `id`, `account_id` (FK → `account.id`, unique), `version` (default=1), `created_at`, `updated_at`, `deleted_at`
- Constraint `uq_owner_account_account_id` documenta relação 1:1 com `ACCOUNT`
- Relacionamento de `ACCOUNT` atualizado para referenciar `OWNER_ACCOUNT`

### [2026-02-21] — Adição da tabela RENTER_ACCOUNT (TASK-003)
- Adicionada tabela `RENTER_ACCOUNT` com campos: `id`, `account_id` (FK → `account.id`, unique), `version` (default=1), `created_at`, `updated_at`, `deleted_at`
- Constraint `uq_renter_account_account_id` documenta relação 1:1 com `ACCOUNT`
- Relacionamento de `ACCOUNT` atualizado para referenciar `RENTER_ACCOUNT`

### [2026-02-21] — Adição das tabelas RENTABLE_ITEM e RENTABLE_ITEM_TAG (TASK-004)
- Adicionada tabela `RENTABLE_ITEM` com campos: `id`, `owner_account_id` (referência externa, sem FK), `name`, `description`, `base_amount_cents` (INTEGER, centavos), `conservation_level` (TEXT, default='UNKNOWN'), `created_at`, `updated_at`
- Adicionada tabela `RENTABLE_ITEM_TAG` com campos: `id`, `rentable_item_id` (FK → `rentable_item.id`), `value`
- Tags armazenadas em tabela separada (não como JSON)
- `base_amount_cents` armazena valor monetário em centavos inteiros para precisão numérica

### [2026-02-22] — Adição da tabela RENTABLE_ITEM_SHADOW (TASK-005)
- Adicionada tabela `RENTABLE_ITEM_SHADOW` no contexto marketplace
- Campo `content` do tipo JSONB armazena projeção desnormalizada do `RentableItem`
- `id` espelha o UUID do `RentableItem` original (sem geração automática)
- Upsert via `INSERT ... ON CONFLICT DO UPDATE` — atualiza `content`, `updated_at`, `deleted_at`; preserva `created_at`
- Sem FK explícita para `RENTABLE_ITEM` — referência cross-context gerenciada pela aplicação

### [2026-02-22] — Adição das tabelas ANNOUNCED_ITEM e ANNOUNCED_ITEM_ORIGIN (TASK-006)
- Adicionada tabela `ANNOUNCED_ITEM` com campos: `id`, `shadow_rentable_id` (referência cross-context, sem FK), `owner_account_id` (referência cross-context, sem FK), `name` (nullable), `description` (nullable), `status` (TEXT), `amount_cents` (INTEGER)
- Adicionada tabela `ANNOUNCED_ITEM_ORIGIN` com campos: `id`, `announced_item_id` (FK → `announced_item.id`), `zipcode` (TEXT)
- Status inicial sempre `REQUESTED`; transições geridas por `AnnounceItemStatusMachine`
- `Amount` VO movido de `inventory` para `shared` (sem impacto de schema)

### [2026-02-23] — Adição das tabelas ORDERS, ORDER_ITEMS e ORDER_DESTINATIONS (TASK-007)
- Adicionada tabela `ORDERS` com campos: `id`, `status` (TEXT), `subtotal_cents`, `total_cents`, `discount_cents` (<=0), `renter_account_id` (cross-context, sem FK), `owner_account_id` (cross-context, sem FK), `start_date` (nullable), `end_date` (nullable), `created_at`, `updated_at`
- Adicionada tabela `ORDER_ITEMS` com campos: `id`, `order_id` (FK → `orders.id`), `announced_item_id` (cross-context, sem FK), `owner_account_id` (cross-context, sem FK), `name`, `description`, `unit_amount_cents` (>0), `amount_cents` (>0), `quantity` (>=1), `start_date` (nullable), `end_date` (nullable)
- Adicionada tabela `ORDER_DESTINATIONS` com campos: `id`, `order_id` (FK → `orders.id`), `zipcode`, `created_at`, `updated_at`
- `OrderItem` é VO no domínio; `id` na tabela `order_items` é apenas técnico
- `OrderDestination` é VO no domínio; `id` na tabela `order_destinations` é apenas técnico

### [2026-02-24] — Adição da tabela JOB_QUEUE (TASK-008)
- Adicionada tabela `JOB_QUEUE` no contexto `shared`
- Campo `id` como INTEGER autoincrement (BIGSERIAL no Postgres) — exceção intencional ao padrão UUID7
- Campo `payload` do tipo JSONB para armazenar dados arbitrários do job
- Campo `job_type` como TEXT simples
- Constraint `valid_status` garante valores válidos para o campo `status`
- Índice parcial `idx_job_fetch` otimizado para `WHERE status = 'pending'`
- Índice `idx_job_monitor` para observabilidade por `job_type` e `status`

### [2026-02-26] — Adição da tabela ACCOUNT_SHADOW (TASK-012)
- Adicionada tabela `ACCOUNT_SHADOW` no contexto `orders`
- Campo `id` espelha o UUID da `OwnerAccount` de origem (sem geração automática)
- Campo `type` como TEXT simples (ex: `"OWNER"`)
- Soft delete via `deleted_at` (nullable, default null)
- Upsert via `INSERT ... ON CONFLICT DO UPDATE` — preserva `created_at`
- Sem FK explícita para `ACCOUNT` — referência cross-context gerenciada pela aplicação

### [2026-02-21] — Inicialização do DB.md com schema real
- Removido conteúdo de exemplo (SYSTEM, ROLE, PERMISSION, USER_ROLE, ROLE_PERMISSION)
- Documentada tabela ACCOUNT conforme implementação em `easy_lease/account/infra/orm/sqlalchemy/models.py`

### [2026-03-11] — Adição da coluna deprecated_at em PERMISSIONS (TASK-sync-capabilities)
- Adicionada coluna `deprecated_at` (TIMESTAMPTZ, nullable, default NULL) na tabela `hades.permissions`
- Semântica: timestamp de deprecação lógica de uma capability — distinto de `deleted_at` (remoção física)
- Migração Alembic gerada: `hades/infra/alembic/versions/01f93e98700e_.py`
- Coluna populada pelo `SyncSystemCapabilitiesUseCase` via repositório
