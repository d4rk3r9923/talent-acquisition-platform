// Generated query
MATCH (p:Person)
WHERE p.dob IS NOT NULL AND p.dob <> '' AND date(p.dob) IS NOT NULL AND date().year - date(p.dob).year < 100
MATCH (p)-[r:WORKED_AS]->()
WITH p, sum(r.duration) AS total_yoe
WHERE total_yoe >= 0
RETURN DISTINCT(p) LIMIT 10