-- 0001_create_system_tables.sql
-- System, quality and staging tables (Constitution Part 25.1).
-- Ordered and immutable: once applied anywhere, never edit — write a new one.

CREATE TABLE IF NOT EXISTS sys.run (
    run_id                VARCHAR PRIMARY KEY,
    report_id             VARCHAR NOT NULL,
    report_version        INTEGER NOT NULL,
    application_version   VARCHAR NOT NULL,
    requested_period      VARCHAR,
    status                VARCHAR NOT NULL,
    stage                 VARCHAR,
    started_at            TIMESTAMP NOT NULL,
    finished_at           TIMESTAMP,
    rows_extracted        BIGINT DEFAULT 0,
    rows_rejected         BIGINT DEFAULT 0,
    rows_inserted         BIGINT DEFAULT 0,
    rows_updated          BIGINT DEFAULT 0,
    rows_unchanged        BIGINT DEFAULT 0,
    rows_filtered         BIGINT DEFAULT 0,
    quality_status        VARCHAR,
    archive_status        VARCHAR,
    sql_sync_status       VARCHAR,
    demo_data             BOOLEAN DEFAULT FALSE,
    error_code            VARCHAR,
    error_message         VARCHAR,
    output_json           VARCHAR,
    output_html           VARCHAR
);

CREATE TABLE IF NOT EXISTS sys.source_file (
    run_id                     VARCHAR NOT NULL,
    source_id                  VARCHAR NOT NULL,
    source_role                VARCHAR,
    file_name                  VARCHAR NOT NULL,
    safe_path_reference        VARCHAR,
    physical_file_hash_before  VARCHAR NOT NULL,
    physical_file_hash_after   VARCHAR,
    logical_content_hash       VARCHAR,
    file_size                  BIGINT,
    modified_time              VARCHAR,
    workbook_identity          VARCHAR,
    sheet_name                 VARCHAR,
    rows_extracted             BIGINT DEFAULT 0
);

CREATE TABLE IF NOT EXISTS sys.checkpoint (
    run_id             VARCHAR NOT NULL,
    source_id          VARCHAR NOT NULL,
    sheet_name         VARCHAR,
    chunk_number       INTEGER NOT NULL,
    first_row          BIGINT,
    last_completed_row BIGINT,
    rows_staged        BIGINT,
    chunk_hash         VARCHAR,
    completed_at       TIMESTAMP
);

CREATE TABLE IF NOT EXISTS sys.schema_migration (
    version             INTEGER PRIMARY KEY,
    name                VARCHAR NOT NULL,
    checksum            VARCHAR NOT NULL,
    applied_at          TIMESTAMP NOT NULL,
    application_version VARCHAR
);

CREATE TABLE IF NOT EXISTS quality.check_result (
    run_id      VARCHAR NOT NULL,
    check_id    VARCHAR NOT NULL,
    scope       VARCHAR,
    severity    VARCHAR NOT NULL,
    status      VARCHAR NOT NULL,
    expected    VARCHAR,
    actual      VARCHAR,
    difference  VARCHAR,
    tolerance   VARCHAR,
    message     VARCHAR,
    evidence    VARCHAR,
    checked_at  TIMESTAMP NOT NULL
);

-- Nothing is ever silently deleted (Part 9.5).
CREATE TABLE IF NOT EXISTS quality.quarantine (
    run_id            VARCHAR NOT NULL,
    report_id         VARCHAR NOT NULL,
    source_id         VARCHAR,
    source_sheet      VARCHAR,
    source_row        BIGINT,
    business_key_hash VARCHAR,
    reason_code       VARCHAR NOT NULL,
    reason_message    VARCHAR,
    raw_values        VARCHAR,
    resolution_status VARCHAR DEFAULT 'OPEN'
);

CREATE TABLE IF NOT EXISTS sys.sync_queue (
    sync_id         VARCHAR PRIMARY KEY,
    run_id          VARCHAR NOT NULL,
    target          VARCHAR NOT NULL,
    batch_reference VARCHAR,
    status          VARCHAR NOT NULL,
    attempts        INTEGER DEFAULT 0,
    next_attempt_at TIMESTAMP,
    last_error      VARCHAR,
    created_at      TIMESTAMP NOT NULL,
    completed_at    TIMESTAMP
);
