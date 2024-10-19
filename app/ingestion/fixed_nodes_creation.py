import csv
import os
import uuid
import asyncio
from dotenv import load_dotenv
from loguru import logger
from neo4j import AsyncGraphDatabase
from app.utils.util import Color

from app.preprocessing.fixed_schema import (
    list_certifications,
    list_positions,
    list_skills,
    list_universites,
    list_workplaces,
    list_publications,
)

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
        {"id": generate_uuid(cert.category), "category": cert.category}
        for cert in list_certifications
    ]

    publication_nodes = [
        {"id": generate_uuid(pub.category), "category": pub.category}
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


async def add_nodes_to_db(driver, nodes, node_type):
    async with driver.session() as session:
        for node in nodes:
            try:
                await session.run(
                    f"CREATE (n:{node_type} $props)",
                    props=node,
                )
                # logger.info(f"{Color.RED}Added {node_type} node:{Color.RESET} {node}")
            except Exception as e:
                logger.error(f"{Color.RED}Error adding {node_type} node {node}:{Color.RESET} {e}")


async def main():
    driver = await connect_to_neo4j(NEO4J_URI, NEO4J_DATABASE, NEO4J_USERNAME, NEO4J_PASSWORD)

    university_nodes, workplace_nodes, position_nodes, skill_nodes, certification_nodes, publication_nodes = prepare_nodes()

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
