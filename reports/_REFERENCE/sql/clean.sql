-- clean.sql — raw to typed clean data (Constitution Part 6, layer 5)
--
-- REPORT VARIATION POINT. Adapt the typing and the reject rules to your columns.
-- The engine that runs this file is Factory Core and does not change.
--
-- PROOF REQUIRED: zero nulls in the business key after this step.

-- name: build_clean
INSERT INTO clean.production
    (production_date, line, order_number, model_code, produced_qty, defect_qty,
     category, business_key_hash, row_content_hash,
     _run_id, _source_id, _source_file, _source_row_number)
SELECT
    CAST(r.production_date AS DATE),
    trim(r.line),
    trim(r.order_number),
    trim(r.model_code),
    -- DECIMAL, never FLOAT: this is what makes reconciliation land on exactly
    -- zero instead of approximately zero (Part 7.4).
    CAST(r.produced_qty AS DECIMAL(18,4)),
    CAST(r.defect_qty   AS DECIMAL(18,4)),
    trim(r.category),
    md5(concat_ws(chr(31), trim(r.production_date), trim(r.line),
                  trim(r.order_number), trim(r.model_code))),
    md5(concat_ws(chr(31), trim(r.category),
                  CAST(CAST(r.defect_qty   AS DECIMAL(18,4)) AS VARCHAR),
                  CAST(CAST(r.produced_qty AS DECIMAL(18,4)) AS VARCHAR))),
    r._run_id, r._source_id, r._source_file, r._source_row_number
FROM raw.production r
WHERE r._run_id = ?
  -- Rejected rows are quarantined by the engine first; excluding them here
  -- keeps trusted history clean without losing the audit trail (Part 9.5).
  AND TRY_CAST(r.produced_qty AS DECIMAL(18,4)) >= 0
  AND TRY_CAST(r.defect_qty   AS DECIMAL(18,4)) >= 0
  AND r.production_date IS NOT NULL AND trim(r.production_date) <> ''
  AND r.order_number   IS NOT NULL AND trim(r.order_number)   <> ''
  -- Exact duplicates collapse to their first occurrence. A DIFFERING duplicate
  -- is never collapsed here; the quality gate fails the run instead.
  AND r._source_row_number = (
        SELECT min(r2._source_row_number) FROM raw.production r2
        WHERE r2._run_id = r._run_id
          AND r2.production_date = r.production_date AND r2.line = r.line
          AND r2.order_number = r.order_number AND r2.model_code = r.model_code);

-- name: negative_measure_rows
SELECT _source_row_number, production_date, line, order_number, model_code,
       produced_qty, defect_qty, category
FROM raw.production
WHERE _run_id = ?
  AND (TRY_CAST(produced_qty AS DECIMAL(18,4)) < 0
       OR TRY_CAST(defect_qty AS DECIMAL(18,4)) < 0);

-- name: exact_duplicate_rows
SELECT r._source_row_number, r.production_date, r.line, r.order_number,
       r.model_code, r.produced_qty, r.defect_qty, r.category
FROM raw.production r
WHERE r._run_id = ?
  AND r._source_row_number > (
        SELECT min(r2._source_row_number) FROM raw.production r2
        WHERE r2._run_id = r._run_id
          AND r2.production_date = r.production_date AND r2.line = r.line
          AND r2.order_number = r.order_number AND r2.model_code = r.model_code);

-- name: clean_row_count
SELECT count(*) FROM clean.production WHERE _run_id = ?;

-- name: null_business_key_count
SELECT count(*) FROM clean.production
WHERE _run_id = ?
  AND (production_date IS NULL OR line IS NULL
       OR order_number IS NULL OR model_code IS NULL);
