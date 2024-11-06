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

async def create_query(data):
    roles = data.get("roles", [])
    skills = data.get("skills", [])
    certifications = data.get("certifications", [])
    degrees = data.get("degrees", [])
    query = "MATCH (p:Person)\n"

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
            query += f"MATCH (p)-[:STUDIED_AT]->(:Education {{degree: '{degree}'}})\n"

    query += "RETURN p.name AS Candidates"
    
    with open("./app/graphdb/filter.cql", "w") as f:
        f.write("// Generated query\n")
        f.write(query)

    logger.info(f"{g}Generated query:{q}\n{query}")
    return query

async def find_person_nodes():
    driver = await connect_to_neo4j(NEO4J_URI, NEO4J_DATABASE, NEO4J_USERNAME, NEO4J_PASSWORD)
    logger.info(f"{g}Connected to Neo4j{q}")
    
    async with driver.session(database=NEO4J_DATABASE) as session:
        data = {"roles": ["IT Support"], "skills": ["Java", "Networking"], "certifications": ["Information Technology"], "degrees": ["Bachelor Degree"]}
        query = await create_query(data)
        logger.info(f"{g}Running query:{q}\n{query}")
        result = await session.run(query, roles=data.get("roles", []), skills=data.get("skills", []), certifications=data.get("certifications", []), degrees=data.get("degrees", []))

        async for record in result:
            logger.info(f"{g}Found person node:{q} {record.get('Candidates')}")
    
    await driver.close()
    logger.info(f"{g}Disconnected from Neo4j{q}")

if __name__ == "__main__":
    asyncio.run(find_person_nodes())
