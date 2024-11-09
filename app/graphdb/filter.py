import asyncio
import os


from dotenv import load_dotenv
from loguru import logger
from neo4j import AsyncGraphDatabase

from app.references.util import Color

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")

g = Color.GREEN
r = Color.RED
q = Color.RESET

async def connect_to_neo4j(uri, database, user, password):
    return AsyncGraphDatabase.driver(uri, database=database, auth=(user, password))

async def fixed_filter(data):
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
            "AND date().year - date(p.dob).year "
        )
        query += f"{age.strip()}\n"

    if yoe:
        query += (
            "MATCH (p)-[r:WORKED_AS]->()\n"
            "WITH p, sum(r.duration) AS total_yoe\n"
            "WHERE total_yoe "
        )
        query += f"{yoe.strip()}\n"
    
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

        query += (
            f"MATCH (p)-[:STUDIED_AT]->(edu:Education) WHERE {edu_full_phrase_match} OR ({first_keyword_match}) OR ({remaining_keywords_match})\n"
            f"WITH p, edu, size([keyword IN {edu_keyword} WHERE edu.name CONTAINS keyword]) AS edu_match_count,\n"
            f"     size([keyword IN {edu_keyword} WHERE edu.name CONTAINS '{edu_keyword[0]}']) AS first_keyword_count\n"
        )

        query += "ORDER BY first_keyword_count DESC, edu_match_count DESC\n"

    if workplace:
        work_keyword = workplace.split()
        work_full_phrase_match = "work.name CONTAINS '" + " ".join(work_keyword) + "'"
        first_keyword_match = f"work.name CONTAINS '{work_keyword[0]}'"
        remaining_keywords_match = " OR ".join([f"work.name CONTAINS '{kw}'" for kw in work_keyword[1:]])

        query += (
            f"MATCH (p)-[:WORKED_AT]->(work:Workplace) WHERE {work_full_phrase_match} OR ({first_keyword_match}) OR ({remaining_keywords_match})\n"
            f"WITH p, work, size([keyword IN {work_keyword} WHERE work.name CONTAINS keyword]) AS work_match_count,\n"
            f"     size([keyword IN {work_keyword} WHERE work.name CONTAINS '{work_keyword[0]}']) AS first_keyword_count\n"
        )

        query += "ORDER BY first_keyword_count DESC, work_match_count DESC\n"

    query += "RETURN DISTINCT(p) LIMIT 10"
    
    with open("./app/graphdb/filter.cql", "w") as f:
        f.write("// Generated query\n")
        f.write(query)

    logger.info(f"{g}Generated query:{q}\n{query}")
    return query

async def find_person_nodes():
    driver = await connect_to_neo4j(NEO4J_URI, NEO4J_DATABASE, NEO4J_USERNAME, NEO4J_PASSWORD)
    logger.info(f"{g}Connected to Neo4j{q}")
    
    async with driver.session(database=NEO4J_DATABASE) as session:
        data = {
            # "roles": ["IT Support"],
            # "skills": ["Java", "Networking"],
            # "certifications": ["Information Technology"],
            # "degrees": ["Bachelor Degree"],
            "age": "< 100",
            "yoe": ">= 0",
            # "summary": [],
            # "location": [],
            # "education_name": "FPT University",
            # "workplace_name": "FPT Software"
            }
        # TODOS: score ranking based on filters
        query = await fixed_filter(data)
        logger.info(f"{g}Running the query")
        result = await session.run(query)

        async for record in result:
            logger.info(f"{g}Found person node:{q} {record['p'].get('name')}")
    
    await driver.close()
    logger.info(f"{g}Disconnected from Neo4j{q}")

if __name__ == "__main__":
    asyncio.run(find_person_nodes())
