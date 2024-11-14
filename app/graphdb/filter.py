import asyncio
import os


from dotenv import load_dotenv
from loguru import logger
from neo4j import GraphDatabase

from app.references.util import Color

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")

g = Color.GREEN
r = Color.RED
q = Color.RESET

def connect_to_neo4j(uri, database, user, password):
    return GraphDatabase.driver(uri, database=database, auth=(user, password))

def filter(data):
    roles = data.get("roles", [])
    skills = data.get("skills", [])
    certifications = data.get("certifications", [])
    degrees = data.get("degrees", [])
    age = data.get("age", "")
    yoe = data.get("yoe", "")
    summary = data.get("summary", [])
    location = data.get("location", [])
    education = data.get("education_name", "")
    workplace = data.get("workplace_name", "")
    query = "MATCH (p:Person)\n"

    # Fixed filters
    if roles:
        for role in roles:
            query += f"MATCH (p)-[:WORKED_AS]->(:Position {{name: '{role}'}})\n"

    if skills:
        for skill in skills:
            query += f"MATCH (p)-[:HAS]->(:Skill {{name: '{skill}'}})\n"

    if certifications:
        for cert in certifications:
            query += f"MATCH (p)-[:EARNED]->(:Certification {{field: '{cert}'}})\n"

    if degrees:
        for degree in degrees:
            query += f"MATCH (p)-[:HOLDS]->(:Degree {{name: '{degree}'}})\n"

    # Filters
    if age:        
        query += (
            "WHERE p.dob IS NOT NULL AND p.dob <> '' "
            "AND date(p.dob) IS NOT NULL "
            f"AND ({age.strip().replace("age", "(date().year - date(p.dob).year)")})\n"
        )

    if yoe:
        query += (
            "MATCH (p)-[r:WORKED_AS]->()\n"
            "WITH p, sum(r.duration) AS total_yoe\n"
            f"WHERE total_yoe {yoe.strip()}\n"
        )
    
    # Embedding comparison using cosine similarity
    if summary:
        query += (
            "MATCH (p:Person)\n"
            f"WHERE size(p.embedding_summary) = size({summary})\n"
            "WITH p, "
            "reduce(dot_product = 0.0, i IN range(0, size(p.embedding_summary)-1) | "
            f"dot_product + (p.embedding_summary[i] * {summary}[i])) AS dot_product, "
            "reduce(norm_p = 0.0, x IN p.embedding_summary | norm_p + x^2) AS norm_p, "
            f"reduce(norm_summary = 0.0, y IN {summary} | norm_summary + y^2) AS norm_summary\n"
            "WHERE dot_product / (sqrt(norm_p) * sqrt(norm_summary)) > 0.8\n"
        )

    if location:
        query += (
            "MATCH (p:Person)\n"
            f"WHERE size(p.embedding_location) = size({location})\n"
            "WITH p, "
            "reduce(dot_product = 0.0, i IN range(0, size(p.embedding_location)-1) | "
            f"dot_product + (p.embedding_location[i] * {location}[i])) AS dot_product, "
            "reduce(norm_p = 0.0, x IN p.embedding_location | norm_p + x^2) AS norm_p, "
            f"reduce(norm_location = 0.0, y IN {location} | norm_location + y^2) AS norm_location\n"
            "WHERE dot_product / (sqrt(norm_p) * sqrt(norm_location)) > 0.8\n"
        )

    # Partial filters
    if education:
        edu_keyword = education.split()
        edu_full_phrase_match = "edu.name CONTAINS '" + " ".join(edu_keyword) + "'"
        first_keyword_match = f"edu.name CONTAINS '{edu_keyword[0]}'"
        remaining_keywords_match = " OR ".join([f"edu.name CONTAINS '{kw}'" for kw in edu_keyword[1:]])

        if remaining_keywords_match:
            query += (
                f"MATCH (p)-[:STUDIED_AT]->(edu:Education) WHERE {edu_full_phrase_match} OR ({first_keyword_match}) OR ({remaining_keywords_match})\n"
                f"WITH p, edu, size([keyword IN {edu_keyword} WHERE edu.name CONTAINS keyword]) AS edu_match_count,\n"
                f"     size([keyword IN {edu_keyword} WHERE edu.name CONTAINS '{edu_keyword[0]}']) AS first_keyword_count\n"
                f"ORDER BY first_keyword_count DESC, edu_match_count DESC\n"
            )
        else:
            query += (
                f"MATCH (p)-[:STUDIED_AT]->(edu:Education) WHERE {edu_full_phrase_match} OR ({first_keyword_match})\n"
                f"WITH p, edu, size([keyword IN {edu_keyword} WHERE edu.name CONTAINS keyword]) AS edu_match_count,\n"
                f"     size([keyword IN {edu_keyword} WHERE edu.name CONTAINS '{edu_keyword[0]}']) AS first_keyword_count\n"
                f"ORDER BY first_keyword_count DESC, edu_match_count DESC\n"
            )

    if workplace:
        work_keyword = workplace.split()
        work_full_phrase_match = "work.name CONTAINS '" + " ".join(work_keyword) + "'"
        first_keyword_match = f"work.name CONTAINS '{work_keyword[0]}'"
        remaining_keywords_match = " OR ".join([f"work.name CONTAINS '{kw}'" for kw in work_keyword[1:]])

        if remaining_keywords_match:
            query += (
                f"MATCH (p)-[:WORKED_AT]->(work:Workplace) WHERE {work_full_phrase_match} OR ({first_keyword_match}) OR ({remaining_keywords_match})\n"
                f"WITH p, work, size([keyword IN {work_keyword} WHERE work.name CONTAINS keyword]) AS work_match_count,\n"
                f"     size([keyword IN {work_keyword} WHERE work.name CONTAINS '{work_keyword[0]}']) AS first_keyword_count\n"
                f"ORDER BY first_keyword_count DESC, work_match_count DESC\n"
            )
        else:
            query += (
                f"MATCH (p)-[:WORKED_AT]->(work:Workplace) WHERE {work_full_phrase_match} OR ({first_keyword_match})\n"
                f"WITH p, work, size([keyword IN {work_keyword} WHERE work.name CONTAINS keyword]) AS work_match_count,\n"
                f"     size([keyword IN {work_keyword} WHERE work.name CONTAINS '{work_keyword[0]}']) AS first_keyword_count\n"
                f"ORDER BY first_keyword_count DESC, work_match_count DESC\n"
            )

    query += "RETURN DISTINCT(p) LIMIT 10"

    return query

def weighted_rrf_scoring(fixed_result, embedding_result, partial_result, weights, k=60):
    person_scores = {}

    def process_result(result, weight, query_name):
        for idx, record in enumerate(result):
            person_id = record['p'].get('id')
            score = (1 / (idx + k)) * weight  # Use k for smoothing
            if person_id in person_scores:
                person_scores[person_id] += score
            else:
                person_scores[person_id] = score
            logger.info(f"Query: {query_name}, Person ID: {person_id}, Rank: {idx + 1}, Score: {score}")
    
    process_result(fixed_result, weights["fixed"], "Fixed")
    process_result(embedding_result, weights["embedding"], "Embedding")
    process_result(partial_result, weights["partial"], "Partial")

    return sorted(person_scores.items(), key=lambda x: x[1], reverse=True)

def find_person_nodes():
    driver = connect_to_neo4j(NEO4J_URI, NEO4J_DATABASE, NEO4J_USERNAME, NEO4J_PASSWORD)
    
    with driver.session(database=NEO4J_DATABASE) as session:
        data_fixed = {
            "roles": ["IT Support"],
            "skills": ["Java"],
            "certifications": ["Information Technology"],
            "degrees": ["Bachelor Degree"],
            "age": "",
            "yoe": ""
        }

        data_embedding = {
            "summary": [],
            "location": []
        }

        data_partial = {
            "education_name": "University of Technology",
            "workplace_name": "Hanoi Club"
        }

        weights = {"fixed": 1, "embedding": 0.5, "partial": 0.25}

        fixed_query = filter(data_fixed)
        fixed_result = session.run(fixed_query)
        # for fixed_record in fixed_result:
        #     logger.info(f"{g}Found person node:{q} {fixed_record['p'].get('id')}")

        embedding_query = filter(data_embedding)
        embedding_result = session.run(embedding_query)
        # for embedding_record in embedding_result:
        #     logger.info(f"{g}Found person node:{q} {embedding_record['p'].get('id')}")

        partial_query = filter(data_partial)
        partial_result = session.run(partial_query)
        # for partial_record in partial_result:
        #     logger.info(f"{g}Found person node:{q} {partial_record['p'].get('id')}")

        data = {**data_fixed, **data_embedding, **data_partial}
        data_query = filter(data)

        with open("./app/graphdb/filter.cql", "w") as f:
            f.write("// Generated query\n")
            f.write(data_query)

        logger.info(f"{g}Generated query:{q}\n{data_query}")

        ranked_results = weighted_rrf_scoring(fixed_result, embedding_result, partial_result, weights)
        # data_result = session.run(data_query)
        for person_id, score in ranked_results:
            logger.info(f"{g}Person ID:{q} {person_id}{g}, Score:{q} {score}")

    driver.close()

if __name__ == "__main__":
    find_person_nodes()
