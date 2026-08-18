-- name: source_control_total
SELECT COALESCE(SUM(TRY_CAST(downtime_minutes AS DECIMAL(18,4))),0) FROM raw.downtime WHERE _run_id=?;
-- name: accepted_control_total
SELECT COALESCE(SUM(downtime_minutes),0) FROM clean.downtime WHERE _run_id=?;
-- name: rejected_control_total
SELECT COALESCE(SUM(TRY_CAST(downtime_minutes AS DECIMAL(18,4))),0) FROM raw.downtime WHERE _run_id=? AND TRY_CAST(downtime_minutes AS DECIMAL(18,4))<0;
-- name: filtered_control_total
SELECT COALESCE(SUM(TRY_CAST(r.downtime_minutes AS DECIMAL(18,4))),0) FROM raw.downtime r WHERE r._run_id=? AND TRY_CAST(r.downtime_minutes AS DECIMAL(18,4))>=0 AND r._source_row_number>(SELECT min(r2._source_row_number) FROM raw.downtime r2 WHERE r2._run_id=r._run_id AND r2.event_date=r.event_date AND r2.line=r.line AND r2.event_id=r.event_id AND r2.machine=r.machine AND r2.reason=r.reason AND r2.downtime_minutes=r.downtime_minutes AND r2.planned_flag=r.planned_flag);
-- name: source_row_count
SELECT count(*) FROM raw.downtime WHERE _run_id=?;
