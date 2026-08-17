# Migrations

Ordered, immutable database migrations (Constitution Parts 13.1, 16.4).

Rules:

1. **Never change a production schema by hand.** Every change is a migration.
2. Migrations are ordered and immutable. Once applied anywhere, a migration file
   is never edited — write a new one.
3. Each runs inside a transaction. A failure rolls back, retains the prior
   version, and blocks application start if the schema is incompatible
   (Part 27.5).
4. `sys.schema_migration` records version, name, checksum, applied_at and
   application_version.
5. Keep the `raw`, `clean`, `quality`, `analytics` and `sys` schemas separate
   (Part 23.3).

Naming: `NNNN_short_description.sql`, e.g. `0001_create_system_tables.sql`.
