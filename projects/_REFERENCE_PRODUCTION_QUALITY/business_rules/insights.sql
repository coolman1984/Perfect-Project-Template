-- insights.sql — verified evidence objects (Constitution Parts 10.3, 26.6)
--
-- Produces EVIDENCE, not sentences. The evidence object exists before any text,
-- and the text is a deterministic template over it.
--
-- Language discipline: a category correlated with defects is a CONTRIBUTOR or an
-- investigation priority. It is NOT a "root cause" until a governed
-- investigation confirms causality (Part 26.12).

-- name: period_change_evidence
WITH by_date AS (
    SELECT production_date,
           SUM(produced_qty) AS produced_qty,
           SUM(defect_qty)   AS defect_qty
    FROM analytics.history_reference_production_quality_production WHERE is_active = TRUE
    GROUP BY production_date ORDER BY production_date DESC LIMIT 2
), ranked AS (
    SELECT *, row_number() OVER (ORDER BY production_date DESC) AS position FROM by_date
)
SELECT
    (SELECT production_date FROM ranked WHERE position = 1) AS current_period,
    (SELECT produced_qty    FROM ranked WHERE position = 1) AS current_produced,
    (SELECT defect_qty      FROM ranked WHERE position = 1) AS current_defects,
    (SELECT production_date FROM ranked WHERE position = 2) AS comparison_period,
    (SELECT produced_qty    FROM ranked WHERE position = 2) AS comparison_produced,
    (SELECT defect_qty      FROM ranked WHERE position = 2) AS comparison_defects;

-- name: top_contributor_evidence
SELECT model_code,
       SUM(defect_qty) AS defect_qty,
       SUM(defect_qty) / NULLIF((SELECT SUM(defect_qty)
                                 FROM analytics.history_reference_production_quality_production
                                 WHERE is_active = TRUE), 0) * 100 AS share_pct
FROM analytics.history_reference_production_quality_production
WHERE is_active = TRUE
GROUP BY model_code
ORDER BY defect_qty DESC, model_code
LIMIT 3;
