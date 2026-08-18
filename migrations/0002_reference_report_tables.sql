-- 0002_reference_report_tables.sql
-- Raw staging and trusted history for a production-style report.
--
-- Report-specific SHAPE lives here because the columns are business columns.
-- The ENGINE that fills these tables is Factory Core and is report-agnostic.
-- A new report adds its own migration; it never edits this one.

CREATE TABLE IF NOT EXISTS raw.production (
    -- business columns, all text at staging: typing happens in clean (Part 6)
    production_date    VARCHAR,
    line               VARCHAR,
    order_number       VARCHAR,
    model_code         VARCHAR,
    produced_qty       VARCHAR,
    defect_qty         VARCHAR,
    category           VARCHAR,
    -- lineage stamped on every staged row (Part 7.7)
    _run_id            VARCHAR NOT NULL,
    _report_id         VARCHAR NOT NULL,
    _source_id         VARCHAR NOT NULL,
    _source_file       VARCHAR,
    _source_file_hash  VARCHAR,
    _source_sheet      VARCHAR,
    _source_row_number BIGINT,
    _extracted_at      VARCHAR,
    _schema_version    VARCHAR
);

CREATE TABLE IF NOT EXISTS clean.production (
    production_date    DATE          NOT NULL,
    line               VARCHAR       NOT NULL,
    order_number       VARCHAR       NOT NULL,
    model_code         VARCHAR       NOT NULL,
    produced_qty       DECIMAL(18,4) NOT NULL,
    defect_qty         DECIMAL(18,4) NOT NULL,
    category           VARCHAR,
    business_key_hash  VARCHAR       NOT NULL,
    row_content_hash   VARCHAR       NOT NULL,
    _run_id            VARCHAR       NOT NULL,
    _source_id         VARCHAR,
    _source_file       VARCHAR,
    _source_row_number BIGINT
);

-- Trusted history: the single truth. Only the history engine writes it, and
-- only inside a transaction (Part 8.5).
CREATE TABLE IF NOT EXISTS analytics.history_production (
    production_date    DATE          NOT NULL,
    line               VARCHAR       NOT NULL,
    order_number       VARCHAR       NOT NULL,
    model_code         VARCHAR       NOT NULL,
    produced_qty       DECIMAL(18,4) NOT NULL,
    defect_qty         DECIMAL(18,4) NOT NULL,
    category           VARCHAR,
    business_key_hash  VARCHAR       NOT NULL,
    row_content_hash   VARCHAR       NOT NULL,
    is_active          BOOLEAN       NOT NULL DEFAULT TRUE,
    first_seen_run_id  VARCHAR       NOT NULL,
    last_seen_run_id   VARCHAR       NOT NULL,
    _source_file       VARCHAR,
    _source_row_number BIGINT
);
