-- Trusted cross-source calculations for the synthetic Supply Chain reference.
-- Formulas live once here; Python orchestrates and the browser only renders.

-- name: ordered_qty
SELECT COALESCE(SUM(ordered_qty), 0)
FROM analytics.history_reference_supply_chain_orders
WHERE is_active = TRUE;

-- name: fulfilled_qty
SELECT COALESCE(SUM(fulfilled_qty), 0)
FROM analytics.history_reference_supply_chain_orders
WHERE is_active = TRUE;

-- name: fulfillment_rate
SELECT CASE WHEN COALESCE(SUM(ordered_qty), 0) = 0 THEN NULL
            ELSE SUM(fulfilled_qty) / SUM(ordered_qty) * 100 END
FROM analytics.history_reference_supply_chain_orders
WHERE is_active = TRUE;

-- name: latest_order_date
SELECT max(order_date)
FROM analytics.history_reference_supply_chain_orders
WHERE is_active = TRUE;

-- name: on_hand_qty
WITH latest AS (
    SELECT max(snapshot_date) AS snapshot_date
    FROM analytics.history_reference_supply_chain_inventory
    WHERE is_active = TRUE
)
SELECT COALESCE(SUM(i.on_hand_qty), 0)
FROM analytics.history_reference_supply_chain_inventory i
JOIN latest l ON i.snapshot_date = l.snapshot_date
WHERE i.is_active = TRUE;

-- name: shortage_by_item
WITH demand AS (
    SELECT item_id, SUM(ordered_qty - fulfilled_qty) AS open_demand_qty
    FROM analytics.history_reference_supply_chain_orders
    WHERE is_active = TRUE
    GROUP BY item_id
), latest AS (
    SELECT max(snapshot_date) AS snapshot_date
    FROM analytics.history_reference_supply_chain_inventory
    WHERE is_active = TRUE
), inventory AS (
    SELECT i.item_id, SUM(i.on_hand_qty) AS on_hand_qty
    FROM analytics.history_reference_supply_chain_inventory i
    JOIN latest l ON i.snapshot_date = l.snapshot_date
    WHERE i.is_active = TRUE
    GROUP BY i.item_id
)
SELECT m.item_name,
       GREATEST(COALESCE(d.open_demand_qty, 0) - COALESCE(i.on_hand_qty, 0), 0) AS shortage_qty
FROM analytics.history_reference_supply_chain_item_master m
LEFT JOIN demand d ON d.item_id = m.item_id
LEFT JOIN inventory i ON i.item_id = m.item_id
WHERE m.is_active = TRUE
ORDER BY shortage_qty DESC, m.item_name;

-- name: inventory_by_warehouse
WITH latest AS (
    SELECT max(snapshot_date) AS snapshot_date
    FROM analytics.history_reference_supply_chain_inventory
    WHERE is_active = TRUE
)
SELECT i.warehouse_id, SUM(i.on_hand_qty) AS on_hand_qty
FROM analytics.history_reference_supply_chain_inventory i
JOIN latest l ON i.snapshot_date = l.snapshot_date
WHERE i.is_active = TRUE
GROUP BY i.warehouse_id
ORDER BY i.warehouse_id;

-- name: orders_lineage_rows
SELECT count(*)
FROM analytics.history_reference_supply_chain_orders
WHERE is_active = TRUE;
