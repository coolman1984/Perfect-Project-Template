-- Evidence for reusable insight patterns (V10 Part 20). These statements only
-- shape already-trusted numbers into the (dimension, value, share) contract the
-- engine's reusable patterns consume. They never introduce a second definition
-- of PPV — the formula lives in metrics.sql alone.

-- name: top_unfavourable_vendor_evidence
WITH by_vendor AS (
    SELECT v.vendor_name AS vendor_name,
           SUM((p.actual_unit_price - s.standard_unit_cost) * p.quantity) AS ppv_amount
    FROM analytics.history_reference_finance_ppv_purchases p
    JOIN analytics.history_reference_finance_ppv_standard_cost s
      ON s.item_id = p.item_id AND s.is_active = TRUE
    JOIN analytics.history_reference_finance_ppv_vendors v
      ON v.vendor_id = p.vendor_id AND v.is_active = TRUE
    WHERE p.is_active = TRUE
    GROUP BY v.vendor_name
), scale AS (
    SELECT SUM(ABS(ppv_amount)) AS absolute_total FROM by_vendor
)
SELECT by_vendor.vendor_name,
       by_vendor.ppv_amount,
       CASE WHEN COALESCE(scale.absolute_total, 0) = 0 THEN NULL
            ELSE ABS(by_vendor.ppv_amount) / scale.absolute_total * 100 END
FROM by_vendor, scale
ORDER BY by_vendor.ppv_amount DESC, by_vendor.vendor_name
LIMIT 1;
