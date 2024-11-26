import asyncio
import os
import uuid

from dotenv import load_dotenv
from loguru import logger
from neo4j import AsyncGraphDatabase

from app.preprocessing.fixed_schema import (
    list_degrees,
    list_certifications,
    list_positions,
    list_publications,
    list_skills,
)
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


def generate_uuid(value):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, value))


def prepare_nodes():
    degree_nodes = [
        {"id": generate_uuid(degree.category), "name": degree.category}
        for degree in list_degrees
    ]
    position_nodes = [
        {"id": generate_uuid(pos.name), "name": pos.name}
        for pos in list_positions
    ]

    skill_nodes = [
        {"id": generate_uuid(skill.name), "name": skill.name, "category": skill.category}
        for skill in list_skills
    ]

    certification_nodes = [
        {"id": generate_uuid(cert.category), "field": cert.category}
        for cert in list_certifications
    ]

    publication_nodes = [
        {"id": generate_uuid(pub.category), "field": pub.category}
        for pub in list_publications
    ]

    return degree_nodes, position_nodes, skill_nodes, certification_nodes, publication_nodes


async def create_constraints(session):
    try:
        constraints = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Degree) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Position) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Skill) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Certification) REQUIRE n.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Publication) REQUIRE n.id IS UNIQUE",
        ]

        for constraint in constraints:
            await session.run(constraint)
        
        logger.info(f"{g}Unique constraint created")
    except Exception as e:
        logger.error(f"{r}Error creating unique constraint:{q} {e}")


async def add_nodes_to_db(session, nodes, node_type):
    for node in nodes:
        try:
            await session.run(
                f"MERGE (n:{node_type} {{id: $props.id}}) SET n += $props",
                props=node,
            )
            # logger.info(f"{g}Added {node_type} node:{q} {node.get("name", node.get("field"))}")
        except Exception as e:
            logger.error(f"{r}Error adding {node_type} node:{q} {node} {e}")


async def main():
    try:
        driver = await connect_to_neo4j(NEO4J_URI, NEO4J_DATABASE, NEO4J_USERNAME, NEO4J_PASSWORD)
        logger.info(f"{g}Connected to Neo4j")

        async with driver.session() as session:
            await create_constraints(session)
            nodes = prepare_nodes()
            node_types = ["Degree", "Position", "Skill", "Certification", "Publication"]

            for node_list, node_type in zip(nodes, node_types):
                await add_nodes_to_db(session, node_list, node_type)

            logger.info(f"{g}Nodes added to Neo4j")

    except Exception as e:
        logger.error(f"{r}Error running main function:{q} {e}")

    finally:
        await driver.close()
        logger.info(f"{g}Disconnected from Neo4j")


if __name__ == "__main__":
    asyncio.run(main())
