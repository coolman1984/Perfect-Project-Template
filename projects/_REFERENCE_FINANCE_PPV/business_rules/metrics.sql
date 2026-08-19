-- Trusted cross-source calculations for the synthetic Finance PPV reference.
--
-- Purchase Price Variance is defined exactly once, here:
--
--     ppv = (actual_unit_price - standard_unit_cost) * quantity
--
-- A positive PPV is unfavourable (paid above standard); a negative PPV is
-- favourable. The browser renders these numbers and never recomputes them
-- (V10 Part 14.4).

-- name: purchase_spend
SELECT COALESCE(SUM(line_amount), 0)
FROM analytics.history_reference_finance_ppv_purchases
WHERE is_active = TRUE;

-- name: standard_spend
SELECT COALESCE(SUM(s.standard_unit_cost * p.quantity), 0)
FROM analytics.history_reference_finance_ppv_purchases p
JOIN analytics.history_reference_finance_ppv_standard_cost s
  ON s.item_id = p.item_id AND s.is_active = TRUE
WHERE p.is_active = TRUE;

-- name: ppv_amount
SELECT COALESCE(SUM((p.actual_unit_price - s.standard_unit_cost) * p.quantity), 0)
FROM analytics.history_reference_finance_ppv_purchases p
JOIN analytics.history_reference_finance_ppv_standard_cost s
  ON s.item_id = p.item_id AND s.is_active = TRUE
WHERE p.is_active = TRUE;

-- name: ppv_rate
WITH v AS (
    SELECT SUM((p.actual_unit_price - s.standard_unit_cost) * p.quantity) AS ppv,
           SUM(s.standard_unit_cost * p.quantity) AS standard_spend
    FROM analytics.history_reference_finance_ppv_purchases p
    JOIN analytics.history_reference_finance_ppv_standard_cost s
      ON s.item_id = p.item_id AND s.is_active = TRUE
    WHERE p.is_active = TRUE
)
SELECT CASE WHEN COALESCE(standard_spend, 0) = 0 THEN NULL
            ELSE ppv / standard_spend * 100 END
FROM v;

-- name: latest_posting_date
SELECT max(posting_date)
FROM analytics.history_reference_finance_ppv_purchases
WHERE is_active = TRUE;

-- name: ppv_budget_amount
-- Optional source: a period with no approved budget yields no row, and the
-- KPI is legitimately NULL rather than a fabricated zero.
SELECT COALESCE(SUM(ppv_budget_amount), 0)
FROM analytics.history_reference_finance_ppv_ppv_budget
WHERE is_active = TRUE;

-- name: ppv_by_vendor
SELECT v.vendor_name,
       SUM((p.actual_unit_price - s.standard_unit_cost) * p.quantity) AS ppv_amount
FROM analytics.history_reference_finance_ppv_purchases p
JOIN analytics.history_reference_finance_ppv_standard_cost s
  ON s.item_id = p.item_id AND s.is_active = TRUE
JOIN analytics.history_reference_finance_ppv_vendors v
  ON v.vendor_id = p.vendor_id AND v.is_active = TRUE
WHERE p.is_active = TRUE
GROUP BY v.vendor_name
ORDER BY ppv_amount DESC, v.vendor_name;

-- name: ppv_by_category
SELECT s.category,
       SUM((p.actual_unit_price - s.standard_unit_cost) * p.quantity) AS ppv_amount
FROM analytics.history_reference_finance_ppv_purchases p
JOIN analytics.history_reference_finance_ppv_standard_cost s
  ON s.item_id = p.item_id AND s.is_active = TRUE
WHERE p.is_active = TRUE
GROUP BY s.category
ORDER BY ppv_amount DESC, s.category;

-- name: purchases_lineage_rows
SELECT count(*)
FROM analytics.history_reference_finance_ppv_purchases
WHERE is_active = TRUE;
