---
name: db
description: >
  Fonte única e autoritativa do schema de dados do projeto. Use esta skill sempre que houver
  dúvida sobre tabelas, campos, constraints, relacionamentos ou modelo de dados. Ative também
  ao iniciar qualquer TASK que envolva persistência, ao revisar alterações de schema, ou ao
  validar conformidade entre código e documentação. Se houver discrepância entre código e este
  documento, atualizar este documento primeiro, depois continuar.
---

# DB — Schema de Dados

> Se houver discrepância entre código e este documento:
> **atualize este documento para refletir o código antes de continuar.**

## Contexto

- ORM: SQLModel (SQLAlchemy + Pydantic)
- Banco: SQLite (desenvolvimento)
- Config: `easy_lease/config.py` → `Settings.database_url`
- Arquivo: `database.db` (raiz do projeto, ignorado pelo git)

---

## Convenções globais

- PKs: UUID7 gerado via `default_factory` (exceto `JOB_QUEUE.id` → INTEGER autoincrement)
- Soft delete: campo `deleted_at` (DATETIME, nullable)
- Valores monetários: centavos inteiros (INTEGER)
- Referencias cross-context: sem FK explícita no banco, gerenciadas pela aplicação
- Upsert: `INSERT ... ON CONFLICT DO UPDATE` — preserva `created_at`

---

## Tabelas

Para detalhes completos de cada tabela, leia o arquivo `DB.md` original na raiz do projeto.

### Resumo

| Tabela | Contexto | Descrição |
|---|---|---|
| `ACCOUNT` | account | Conta/tenant do sistema |
| `OWNER_ACCOUNT` | account | Vínculo de papel Owner (1:1 com ACCOUNT) |
| `RENTER_ACCOUNT` | account | Vínculo de papel Renter (1:1 com ACCOUNT) |
| `RENTABLE_ITEM` | inventory | Item físico disponível para aluguel |
| `RENTABLE_ITEM_TAG` | inventory | Tags de um RentableItem (N:1) |
| `RENTABLE_ITEM_SHADOW` | marketplace | Projeção desnormalizada do RentableItem |
| `ANNOUNCED_ITEM` | marketplace | Anúncio na vitrine do Marketplace |
| `ANNOUNCED_ITEM_ORIGIN` | marketplace | Origem geográfica de um AnnouncedItem (1:1) |
| `ACCOUNT_SHADOW` | orders | Projeção de OwnerAccount no contexto orders |
| `ORDERS` | orders | Ordem de aluguel criada no checkout |
| `ORDER_ITEMS` | orders | Item individual dentro de uma Order (N:1) |
| `ORDER_DESTINATIONS` | orders | Destino de entrega de uma Order (1:1) |
| `JOB_QUEUE` | shared | Fila de jobs para processamento assíncrono |

---

## Governança

Qualquer alteração de schema exige:
1. Atualizar `DB.md` (fonte da verdade)
2. Registrar no log da TASK
3. 🚫 DOD não pode ser satisfeito sem isso

## Log de alterações

> append-only — registrar aqui toda alteração de schema com data e TASK de referência
