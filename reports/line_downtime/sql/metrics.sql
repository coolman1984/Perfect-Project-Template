-- metrics.sql — trusted KPI calculations (Constitution Part 10.2)
--
-- REPORT VARIATION POINT, and the most important one.
-- This file is the ONLY place these numbers are computed. Python formats them;
-- JavaScript displays them. Neither recalculates them (rule 6).
--
-- Rules applied throughout:
--   * weighted rates come from summed numerator / summed denominator (26.5)
--   * a zero denominator yields NULL, never a false zero
--   * rounding happens at presentation only, after reconciliation

-- name: produced_total
SELECT COALESCE(SUM(produced_qty), 0) FROM analytics.history_production
WHERE is_active = TRUE;

-- name: defect_total
SELECT COALESCE(SUM(defect_qty), 0) FROM analytics.history_production
WHERE is_active = TRUE;

-- name: active_row_count
SELECT count(*) FROM analytics.history_production WHERE is_active = TRUE;

-- Weighted defect rate in parts per million. NULL when nothing was produced —
-- an undefined rate is not zero performance (Part 26.5).
-- name: defect_rate_ppm
SELECT CASE WHEN COALESCE(SUM(produced_qty), 0) = 0 THEN NULL
            ELSE SUM(defect_qty) / SUM(produced_qty) * 1000000 END
FROM analytics.history_production WHERE is_active = TRUE;

-- name: trend_by_date
SELECT production_date,
       SUM(produced_qty) AS produced_qty,
       SUM(defect_qty)   AS defect_qty,
       CASE WHEN SUM(produced_qty) = 0 THEN NULL
            ELSE SUM(defect_qty) / SUM(produced_qty) * 1000000 END AS defect_rate_ppm
FROM analytics.history_production
WHERE is_active = TRUE
GROUP BY production_date
ORDER BY production_date;

-- Pareto: sorted contributors plus cumulative share (Part 26.2).
-- name: pareto_by_model
SELECT model_code,
       SUM(defect_qty) AS defect_qty,
       SUM(SUM(defect_qty)) OVER (ORDER BY SUM(defect_qty) DESC,
                                  model_code
                                  ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)
           / NULLIF(SUM(SUM(defect_qty)) OVER (), 0) * 100 AS cumulative_share_pct
FROM analytics.history_production
WHERE is_active = TRUE
GROUP BY model_code
ORDER BY defect_qty DESC, model_code;

-- name: top_contributor
SELECT model_code, SUM(defect_qty) AS defect_qty
FROM analytics.history_production
WHERE is_active = TRUE
GROUP BY model_code
ORDER BY defect_qty DESC, model_code
LIMIT 1;

-- Period comparison for the insight engine. Complete periods only (Part 26.12).
-- name: latest_two_dates
SELECT production_date, SUM(produced_qty) AS produced_qty,
       SUM(defect_qty) AS defect_qty
FROM analytics.history_production
WHERE is_active = TRUE
GROUP BY production_date
ORDER BY production_date DESC
LIMIT 2;

-- Lineage drill-through: from a dashboard number back to its source rows.
-- name: lineage_for_model
SELECT production_date, line, order_number, model_code, produced_qty, defect_qty,
       _source_file, _source_row_number
FROM analytics.history_production
WHERE is_active = TRUE AND model_code = ?
ORDER BY production_date, line, order_number;
