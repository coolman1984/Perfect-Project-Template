-- name: active_history_count
SELECT count(*) FROM analytics.history_downtime WHERE is_active=TRUE;
