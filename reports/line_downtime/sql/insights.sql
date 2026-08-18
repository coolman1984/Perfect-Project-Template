-- name: period_change_evidence
WITH daily AS (SELECT event_date,SUM(downtime_minutes) AS total_minutes FROM analytics.history_downtime WHERE is_active=TRUE GROUP BY event_date), ranked AS (SELECT event_date,total_minutes,row_number() OVER (ORDER BY event_date DESC) AS rn FROM daily) SELECT cur.event_date,cur.total_minutes,prev.event_date,prev.total_minutes FROM ranked cur LEFT JOIN ranked prev ON prev.rn=2 WHERE cur.rn=1;
-- name: top_contributor_evidence
SELECT line,SUM(downtime_minutes) AS total_minutes,SUM(downtime_minutes)/NULLIF(SUM(SUM(downtime_minutes)) OVER (),0)*100 AS share_pct FROM analytics.history_downtime WHERE is_active=TRUE GROUP BY line ORDER BY total_minutes DESC,line LIMIT 1;
