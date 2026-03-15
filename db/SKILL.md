---
name: db
description: >
  Fonte única e autoritativa do schema de dados do projeto. Use esta skill sempre que houver
  dúvida sobre tabelas, campos, constraints, relacionamentos ou modelo de dados. Ative também
  ao iniciar qualquer TASK que envolva persistência, ao revisar alterações de schema, ou ao
  validar conformidade entre código e documentação. Se houver discrepância entre código e este
  documento, atualizar este documento primeiro, depois continuar.
---
ROLE: db  — fonte única de verdade do schema.
ORM: SQLModel | DB: SQLite | CFG: config.py → Settings.database_url | FILE: database.db (gitignored)
CONVENTIONS:
  PK: UUID7 default_factory (JOB_QUEUE.id → INTEGER autoincrement)
  soft-del: deleted_at (DATETIME nullable) | money: centavos INTEGER
  cross-ctx: sem FK explícita | upsert: INSERT…ON CONFLICT DO UPDATE preserva created_at
TABLES: ACCOUNT · OWNER_ACCOUNT · RENTER_ACCOUNT · RENTABLE_ITEM · RENTABLE_ITEM_TAG
        RENTABLE_ITEM_SHADOW · ANNOUNCED_ITEM · ANNOUNCED_ITEM_ORIGIN · ACCOUNT_SHADOW
        ORDERS · ORDER_ITEMS · ORDER_DESTINATIONS · JOB_QUEUE
REF: campos · constraints · relacionamentos completos → DB.md (raiz)
DENY: DOD sem DB.md atualizado.
CHANGELOG: append-only.
