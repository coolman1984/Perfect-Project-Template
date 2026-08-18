-- checks.sql — report-specific validation (Constitution Part 9)
--
-- REPORT VARIATION POINT. Structural, row and dataset checks that only make
-- sense for this report's columns. Generic checks live in the quality engine.

-- name: source_control_total
SELECT COALESCE(SUM(TRY_CAST(produced_qty AS DECIMAL(18,4))), 0)
FROM raw.production WHERE _run_id = ?;

-- name: accepted_control_total
SELECT COALESCE(SUM(produced_qty), 0) FROM clean.production WHERE _run_id = ?;

-- name: rejected_control_total
SELECT COALESCE(SUM(TRY_CAST(produced_qty AS DECIMAL(18,4))), 0)
FROM raw.production r
WHERE r._run_id = ?
  AND (TRY_CAST(r.produced_qty AS DECIMAL(18,4)) < 0
       OR TRY_CAST(r.defect_qty AS DECIMAL(18,4)) < 0);

-- name: filtered_control_total
SELECT COALESCE(SUM(TRY_CAST(r.produced_qty AS DECIMAL(18,4))), 0)
FROM raw.production r
WHERE r._run_id = ?
  AND r._source_row_number > (
        SELECT min(r2._source_row_number) FROM raw.production r2
        WHERE r2._run_id = r._run_id
          AND r2.production_date = r.production_date AND r2.line = r.line
          AND r2.order_number = r.order_number AND r2.model_code = r.model_code);

-- name: source_row_count
SELECT count(*) FROM raw.production WHERE _run_id = ?;

-- name: unexpected_category_count
SELECT count(*) FROM clean.production
WHERE _run_id = ? AND category NOT IN ('standard', 'rework');
