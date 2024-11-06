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

async def drop_all(driver):
    async with driver.session(database=NEO4J_DATABASE) as session:
        try:
            await session.run("MATCH (a)-[r]->(b) DELETE a, r")
            await session.run("MATCH (n) DETACH DELETE n")
            await session.run("CALL apoc.schema.assert({}, {}, true) YIELD label, key RETURN *")
            logger.info(f"{g}Deleted all nodes and relationships in the database{q}")
        except Exception as e:
            logger.error(f"{r}Error deleting all nodes and relationships: {q}{e}")

async def reset_database():
    driver = None
    try:
        driver = await connect_to_neo4j(NEO4J_URI, NEO4J_DATABASE, NEO4J_USERNAME, NEO4J_PASSWORD)
        logger.info(f"{g}Connected to Neo4j{q}")
        await drop_all(driver)
    except Exception as e:
        logger.error(f"{r}Error connecting to Neo4j: {q}{e}")
    finally:
        if driver:
            await driver.close()
            logger.info(f"{g}Database has been reset to blank. Disconnected from Neo4j{q}")

if __name__ == "__main__":
    asyncio.run(reset_database())
