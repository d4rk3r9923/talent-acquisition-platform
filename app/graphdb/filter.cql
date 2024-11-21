// Generated query
MATCH (p:Person)
MATCH (p)-[:WORKED_AS]->(:Position {name: 'IT Support'})
MATCH (p)-[:HAS]->(:Skill {name: 'Java'})
MATCH (p)-[:EARNED]->(:Certification {field: 'Information Technology'})
MATCH (p)-[:HOLDS]->(:Degree {name: 'Bachelor Degree'})
MATCH (p)-[:STUDIED_AT]->(edu:Education) WHERE edu.name CONTAINS 'University of Technology' OR (edu.name CONTAINS 'University') OR (edu.name CONTAINS 'of' OR edu.name CONTAINS 'Technology')
WITH p, edu, size([keyword IN ['University', 'of', 'Technology'] WHERE edu.name CONTAINS keyword]) AS edu_match_count,
     size([keyword IN ['University', 'of', 'Technology'] WHERE edu.name CONTAINS 'University']) AS first_keyword_count
ORDER BY first_keyword_count DESC, edu_match_count DESC
MATCH (p)-[:WORKED_AT]->(work:Workplace) WHERE work.name CONTAINS 'Hanoi Club' OR (work.name CONTAINS 'Hanoi') OR (work.name CONTAINS 'Club')
WITH p, work, size([keyword IN ['Hanoi', 'Club'] WHERE work.name CONTAINS keyword]) AS work_match_count,
     size([keyword IN ['Hanoi', 'Club'] WHERE work.name CONTAINS 'Hanoi']) AS first_keyword_count
ORDER BY first_keyword_count DESC, work_match_count DESC
RETURN DISTINCT(p) LIMIT 10