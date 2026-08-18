-- name: total_downtime_minutes
SELECT COALESCE(SUM(downtime_minutes),0) FROM analytics.history_downtime WHERE is_active=TRUE;
-- name: event_count
SELECT count(*) FROM analytics.history_downtime WHERE is_active=TRUE;
-- name: average_event_minutes
SELECT CASE WHEN count(*)=0 THEN NULL ELSE AVG(downtime_minutes) END FROM analytics.history_downtime WHERE is_active=TRUE;
-- name: active_row_count
SELECT count(*) FROM analytics.history_downtime WHERE is_active=TRUE;
-- name: latest_period
SELECT max(event_date) FROM analytics.history_downtime WHERE is_active=TRUE;
-- name: trend_by_date
SELECT event_date,SUM(downtime_minutes) FROM analytics.history_downtime WHERE is_active=TRUE GROUP BY event_date ORDER BY event_date;
-- name: pareto_by_line
SELECT line,SUM(downtime_minutes) AS downtime_minutes,SUM(SUM(downtime_minutes)) OVER (ORDER BY SUM(downtime_minutes) DESC,line ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW)/NULLIF(SUM(SUM(downtime_minutes)) OVER (),0)*100 FROM analytics.history_downtime WHERE is_active=TRUE GROUP BY line ORDER BY downtime_minutes DESC,line;
-- name: top_contributor
SELECT line,SUM(downtime_minutes) FROM analytics.history_downtime WHERE is_active=TRUE GROUP BY line ORDER BY SUM(downtime_minutes) DESC,line LIMIT 1;
-- name: lineage_for_line
SELECT event_date,line,event_id,machine,reason,downtime_minutes,_source_file,_source_row_number FROM analytics.history_downtime WHERE is_active=TRUE AND line=? ORDER BY event_date,event_id;
