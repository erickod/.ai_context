---
name: db
description: >
  Fonte única e autoritativa do schema de dados do projeto. Use esta skill sempre que houver
  dúvida sobre tabelas, campos, constraints, relacionamentos ou modelo de dados. Ative também
  ao iniciar qualquer TASK que envolva persistência, ao revisar alterações de schema, ou ao
  validar conformidade entre código e documentação. Se houver discrepância entre código e este
  documento, atualizar este documento primeiro, depois continuar.
---

ROLE: db
PRINCIPLE: Fonte única de verdade do schema. Discrepância código vs doc → atualizar doc primeiro.

CONTEXT:
  ORM: SQLModel (SQLAlchemy + Pydantic)
  DB:  SQLite (dev)
  CFG: easy_lease/config.py → Settings.database_url
  FILE: database.db (raiz · gitignored)

CONVENTIONS:
  PK:       UUID7 via default_factory (exceto JOB_QUEUE.id → INTEGER autoincrement)
  soft-del: deleted_at (DATETIME · nullable)
  money:    centavos inteiros (INTEGER)
  cross-ctx: sem FK explícita · gerenciado pela aplicação
  upsert:   INSERT ... ON CONFLICT DO UPDATE → preserva created_at

TABLES:
  ACCOUNT              account     conta/tenant
  OWNER_ACCOUNT        account     papel Owner (1:1 ACCOUNT)
  RENTER_ACCOUNT       account     papel Renter (1:1 ACCOUNT)
  RENTABLE_ITEM        inventory   item físico para aluguel
  RENTABLE_ITEM_TAG    inventory   tags do item (N:1)
  RENTABLE_ITEM_SHADOW marketplace projeção desnormalizada do item
  ANNOUNCED_ITEM       marketplace anúncio na vitrine
  ANNOUNCED_ITEM_ORIGIN marketplace origem geográfica (1:1 ANNOUNCED_ITEM)
  ACCOUNT_SHADOW       orders      projeção de OwnerAccount
  ORDERS               orders      ordem de aluguel
  ORDER_ITEMS          orders      item dentro de Order (N:1)
  ORDER_DESTINATIONS   orders      destino de entrega (1:1 ORDER)
  JOB_QUEUE            shared      fila de jobs assíncrona

REF: detalhes completos de campos · constraints · relacionamentos → DB.md (raiz)

GOVERNANCE:
  alteração de schema: atualizar DB.md · registrar no log da TASK
  DENY: DOD sem DB.md atualizado

CHANGELOG:
  > append-only
