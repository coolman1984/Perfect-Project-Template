-- history.sql — load behaviour for this report (Constitution Part 8)
--
-- This report declares load_mode = "upsert" with a 7-day lookback, because
-- production records can be corrected for a week after the fact.
--
-- The MERGE ITSELF is Factory Core (app/data/history.py) and is identical for
-- every report. This file holds only report-specific history queries.

-- name: history_row_count
SELECT count(*) FROM analytics.history_production WHERE is_active = TRUE;

-- name: record_by_key
SELECT production_date, line, order_number, model_code, produced_qty, defect_qty
FROM analytics.history_production
WHERE is_active = TRUE
  AND production_date = ? AND line = ? AND order_number = ? AND model_code = ?;

-- name: inactive_row_count
SELECT count(*) FROM analytics.history_production WHERE is_active = FALSE;
