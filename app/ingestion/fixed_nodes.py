import asyncio
import os
import uuid

from dotenv import load_dotenv
from loguru import logger
from neo4j import AsyncGraphDatabase

from app.preprocessing.fixed_schema import (
    list_certifications,
    list_positions,
    list_publications,
    list_skills,
    list_universites,
    list_workplaces,
)
from app.utils.util import Color

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")


async def connect_to_neo4j(uri, database, user, password):
    driver = AsyncGraphDatabase.driver(uri, database=database, auth=(user, password))
    return driver


def generate_uuid(value):
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, value))


def prepare_nodes():
    university_nodes = [
        {"id": generate_uuid(uni.name), "name": uni.name, "field": uni.field}
        for uni in list_universites
    ]

    workplace_nodes = [
        {
            "id": generate_uuid(wp.name),
            "name": wp.name,
            "domain_expertise": wp.domain_expertise,
            "size": wp.size,
        }
        for wp in list_workplaces
    ]

    position_nodes = [
        {
            "id": generate_uuid(pos.name),
            "name": pos.name,
            "description": pos.description,
        }
        for pos in list_positions
    ]

    skill_nodes = [
        {
            "id": generate_uuid(skill.name),
            "name": skill.name,
            "category": skill.category,
        }
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

    return (
        university_nodes,
        workplace_nodes,
        position_nodes,
        skill_nodes,
        certification_nodes,
        publication_nodes,
    )


async def create_constraints(driver):
    async with driver.session() as session:
        try:
            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (n:University) REQUIRE n.id IS UNIQUE"
            )
            logger.info(
                f"{Color.GREEN}Unique constraint created for University nodes"
            )

            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Workplace) REQUIRE n.id IS UNIQUE"
            )
            logger.info(
                f"{Color.GREEN}Unique constraint created for Workplace nodes"
            )

            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Position) REQUIRE n.id IS UNIQUE"
            )
            logger.info(
                f"{Color.GREEN}Unique constraint created for Position nodes"
            )

            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Skill) REQUIRE n.id IS UNIQUE"
            )
            logger.info(
                f"{Color.GREEN}Unique constraint created for Skill nodes"
            )

            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Certification) REQUIRE n.id IS UNIQUE"
            )
            logger.info(
                f"{Color.GREEN}Unique constraint created for Certification nodes"
            )

            await session.run(
                "CREATE CONSTRAINT IF NOT EXISTS FOR (n:Publication) REQUIRE n.id IS UNIQUE"
            )
            logger.info(
                f"{Color.GREEN}Unique constraint created for Publication nodes"
            )

        except Exception as e:
            logger.error(f"{Color.RED}Error creating constraints:{Color.RESET} {e}")


async def add_nodes_to_db(driver, nodes, node_type):
    async with driver.session() as session:
        for node in nodes:
            try:
                await session.run(
                    f"MERGE (n:{node_type} {{id: $props.id}}) " f"SET n += $props",
                    props=node,
                )
                # logger.info(f"{Color.RED}Merged {node_type} node:{Color.RESET} {node}")
            except Exception as e:
                logger.error(
                    f"{Color.RED}Error adding {node_type} node {node}:{Color.RESET} {e}"
                )


async def main():
    driver = await connect_to_neo4j(
        NEO4J_URI, NEO4J_DATABASE, NEO4J_USERNAME, NEO4J_PASSWORD
    )

    await create_constraints(driver)

    (
        university_nodes,
        workplace_nodes,
        position_nodes,
        skill_nodes,
        certification_nodes,
        publication_nodes,
    ) = prepare_nodes()

    await add_nodes_to_db(driver, university_nodes, "University")
    await add_nodes_to_db(driver, workplace_nodes, "Workplace")
    await add_nodes_to_db(driver, position_nodes, "Position")
    await add_nodes_to_db(driver, skill_nodes, "Skill")
    await add_nodes_to_db(driver, certification_nodes, "Certification")
    await add_nodes_to_db(driver, publication_nodes, "Publication")

    await driver.close()


if __name__ == "__main__":
    logger.info(f"{Color.RED}Starting to add nodes to Neo4j")
    asyncio.run(main())
    logger.info(f"{Color.RED}Finished adding nodes to Neo4j")
