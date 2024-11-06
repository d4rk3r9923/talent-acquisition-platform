import asyncio
import json
import os
import uuid

from dotenv import load_dotenv
from loguru import logger
from neo4j import AsyncGraphDatabase

from app.references.util import Color, process_candidate_data

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")

g = Color.GREEN
r = Color.RED
q = Color.RESET


async def connect_to_neo4j(uri, database, user, password):
    driver = AsyncGraphDatabase.driver(uri, database=database, auth=(user, password))
    return driver


async def create_flex_nodes(driver, person_data):
    async with driver.session() as session:
        for person in person_data:
            person_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, person["person"]["name"]))
            person_props = {
                "id": person_id,
                "name": person["person"].get("name"),
                "summary": person["person"].get("summary"),
                "dob": person["person"].get("dob"),
                "location": person["person"].get("location"),
                "path_pdf": person["person"].get("path_pdf"),
                "embedding_summary": person["person"].get("embedding_summary"),
                "embedding_location": person["person"].get("embedding_location"),
            }

            try:
                # Create person node
                await session.run(
                    """
                    MERGE (p:Person {id: $id})
                    SET p += $props
                    """,
                    id=person_props["id"],
                    props=person_props,
                )
                logger.info(
                    f"{g}Created/merged Person node: {q}{person_props['name']} {g}with ID {q}{person_props['id']}"
                )

                # Connect existing Skills to Person node
                for skill in person.get("list_skill", []):
                    await session.run(
                        """
                        MATCH (s:Skill {name: $skill_name}), (p:Person {id: $person_id})
                        MERGE (p)-[:HAS]->(s)
                        """,
                        skill_name=skill["name"],
                        person_id=person_props["id"],
                    )
                    logger.info(f"{g}Linked Person {q}{person_props['name']} {g}to Skill {q}{skill['name']}")

                # Connect existing Certifications to Person node
                for cert in person.get("list_certification", []):
                    await session.run(
                        """
                        MATCH (c:Certification {field: $cert_category}), (p:Person {id: $person_id})
                        MERGE (p)-[:EARNED]->(c)
                        """,
                        cert_category=cert["category"],
                        person_id=person_props["id"],
                    )
                    logger.info(f"{g}Linked Person {q}{person_props['name']} {g}to Certification {q}{cert['category']}")

                # Connect existing Publications to Person node
                for pub in person.get("list_publications", []):
                    await session.run(
                        """
                        MATCH (pub:Publication {field: $pub_category}), (p:Person {id: $person_id})
                        MERGE (p)-[:PUBLISHED]->(pub)
                        """,
                        pub_category=pub["category"],
                        person_id=person_props["id"],
                    )
                    logger.info(f"{g}Linked Person {q}{person_props['name']} {g}to Publication {q}{pub['category']}")

                # Connect existing Positions to Work Experience
                for work in person.get("work_experience", []):
                    workplace_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, work["work_place"]))
                    workplace_props = {
                        "id": workplace_id,
                        "name": work["work_place"],
                    }

                    relationship_props = {
                        "role": work["role"],
                        "start_date": work["start_date"],
                        "end_date": work["end_date"],
                        "responsibilities": work.get("responsibilities", []),
                        "achievements": work.get("achievements", []),
                    }

                    await session.run(
                        """
                        MERGE (w:Workplace {id: $workplace_id})
                        SET w += $workplace_props
                        """,
                        workplace_id=workplace_id,
                        workplace_props=workplace_props,
                    )
                    logger.info(f"{g}Created/merged Workplace node: {q}{workplace_props['name']}")
                    await session.run(
                        """
                        MATCH (w:Workplace {id: $workplace_id}), (p:Person {id: $person_id})
                        MERGE (p)-[r:WORKED_AT]->(w)
                        SET r.role = $relationship_props.role,
                            r.start_date = $relationship_props.start_date,
                            r.end_date = $relationship_props.end_date,
                            r.responsibilities = $relationship_props.responsibilities,
                            r.achievements = $relationship_props.achievements
                        """,
                        workplace_id=workplace_id,
                        person_id=person_props["id"],
                        relationship_props=relationship_props,
                    )
                    logger.info(f"{g}Linked Person {q}{person_props['name']} {g}to Workplace {q}{workplace_props['name']}")

                # Create or merge Education nodes and link with Person
                for edu in person.get("education", []):
                    education_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, edu["name_education"]))
                    education_props = {
                        "id": education_id,
                        "name": edu["name_education"],
                        "degree": edu["degree"]
                    }

                    await session.run(
                        """
                        MERGE (e:Education {id: $education_id})
                        SET e += $education_props
                        """,
                        education_id=education_id,
                        education_props=education_props,
                    )
                    logger.info(f"{g}Created/merged Education node: {q}{education_props['name']}")
                    await session.run(
                        """
                        MATCH (e:Education {id: $education_id}), (p:Person {id: $person_id})
                        MERGE (p)-[:STUDIED_AT]->(e)
                        """,
                        education_id=education_id,
                        person_id=person_props["id"],
                    )
                    logger.info(f"{g}Linked Person {q}{person_props['name']} {g}to Education {q}{education_props['name']} with STUDIED_AT relationship")

                # Connect Projects to Person
                for project in person.get("list_project", []):
                    project_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, project["name"]))  # Unique UUID for each project based on name
                    project_props = {
                        "id": project_id,
                        "name": project["name"],
                        "description": project.get("description", "")
                    }

                    await session.run(
                        """
                        MERGE (proj:Project {id: $project_id})
                        SET proj += $project_props
                        """,
                        project_id=project_id,
                        project_props=project_props,
                    )
                    logger.info(f"{g}Created/merged Project node: {q}{project_props['name']}")
                    await session.run(
                        """
                        MATCH (proj:Project {id: $project_id}), (p:Person {id: $person_id})
                        MERGE (p)-[r:DID]->(proj)
                        """,
                        project_id=project_id,
                        person_id=person_props["id"],
                    )
                    logger.info(f"{g}Linked Person {q}{person_props['name']} {g}to Project {q}{project_props['name']} with DID relationship")

            except Exception as e:
                logger.error(f"{r}Error adding Person node or relationships for {q}{person_props['name']}: {e}")


async def create_constraints(driver):
    async with driver.session() as session:
        try:
            await session.run(
                """
                CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE
                """
            )
            await session.run(
                """
                CREATE CONSTRAINT IF NOT EXISTS FOR (pos:Position) REQUIRE pos.id IS UNIQUE
                """
            )
            await session.run(
                """
                CREATE CONSTRAINT IF NOT EXISTS FOR (wp:Workplace) REQUIRE wp.id IS UNIQUE
                """
            )
            await session.run(
                """
                CREATE CONSTRAINT IF NOT EXISTS FOR (proj:Project) REQUIRE proj.id IS UNIQUE
                """
            )
            await session.run(
                """
                CREATE CONSTRAINT IF NOT EXISTS FOR (edu:Education) REQUIRE edu.id IS UNIQUE
                """
            )
            await session.run(
                """
                CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:WORKED_AT]-() REQUIRE r.role IS NOT NULL
                """
            )
            await session.run(
                """
                CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:WORKED_AT]-() REQUIRE r.responsibilities IS NOT NULL
                """
            )
            logger.info(f"{g}Constraint created for WORKED_AT relationships")
            await session.run(
                """
                CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:WORKED_AS]-() REQUIRE r.responsibilities IS NOT NULL
                """
            )
            logger.info(f"{g}Constraint created for WORKED_AS relationships")
            await session.run(
                """
                CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:STUDIED_AT]-() REQUIRE r.degree IS UNIQUE
                """
            )
            logger.info(f"{g}Constraint created for STUDIED_AT relationships")
            await session.run(
                """
                CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:EARNED]-() REQUIRE r.name IS UNIQUE
                """
            )
            logger.info(f"{g}Constraint created for EARNED relationships")

        except Exception as e:
            logger.error(f"{r}Error creating constraints: {e}")


async def main():
    with open("./data/sample/50sample01.json", "r") as file:
        candidate_data = json.load(file)

    try:
        driver = await connect_to_neo4j(NEO4J_URI, NEO4J_DATABASE, NEO4J_USERNAME, NEO4J_PASSWORD)
        logger.info(f"{g}Connected to Neo4j")
        await create_constraints(driver)
        await create_flex_nodes(driver, candidate_data)
        logger.info(f"{g}Successfully added person nodes and relationships")
    except Exception as e:
        logger.error(f"{r}Error in main process: {q}{e}")
    finally:
        await driver.close()
        logger.info(f"{g}Disconnected from Neo4j")


if __name__ == "__main__":
    asyncio.run(main())
