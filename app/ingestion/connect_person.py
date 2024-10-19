import asyncio
import json
import os
import uuid

from dotenv import load_dotenv
from loguru import logger
from neo4j import AsyncGraphDatabase

from app.utils.util import Color, process_candidate_data

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


async def create_person_nodes(driver, person_data):
    async with driver.session() as session:
        for person in person_data:
            person_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, person["person"]["name"]))
            person_props = {
                "id": person_id,
                "name": person["person"].get("name"),
                "summary": person["person"].get("summary"),
                "dob": person["person"].get("dob"),
                "location": person["person"].get("location"),
                "phone": person["person"].get("phone"),
                "portfolio": person["person"].get("portfolio"),
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
                    f"{g} Created/merged Person node: {q} {person_props['name']} {g} with ID {q} {person_props['id']}"
                )

            except Exception as e:
                logger.error(
                    f"{r} Error creating Person node for {q} {person_props['name']}: {e}"
                )

            # Handle relationships for work experience
            for work in person.get("work_experience", []):
                work_place_uuid = str(
                    uuid.uuid5(uuid.NAMESPACE_DNS, work["work_place"])
                )
                position_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, work["role"]))

                try:
                    await session.run(
                        """
                        MATCH (w:Workplace {id: $work_place_uuid})
                        MERGE (p:Person {id: $person_id})
                        MERGE (p)-[:WORKED_AT {role: $role, start_date: $start_date, end_date: $end_date, responsibilities: $responsibilities, achievements: $achievements}]->(w)
                        """,
                        person_id=person_props["id"],
                        work_place_uuid=work_place_uuid,
                        role=work.get("role"),
                        start_date=work["start_date"],
                        end_date=work.get("end_date"),
                        responsibilities=work.get("responsibilities", []),
                        achievements=work.get("achievements", []),
                    )
                    logger.info(
                        f"{g} Created WORKED_AT relationship for {q} {person_props['name']} {g} at {q} {work['work_place']}"
                    )

                except Exception as e:
                    logger.error(
                        f"{r} Error creating WORKED_AT relationship for {q} {person_props['name']} {r} at {q} {work['work_place']}: {e}"
                    )

            # Handle relationships for skills
            # for skill in person.get('skills', []):
            #     skill_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, skill))

            #     try:
            #         await session.run(
            #             """
            #             MATCH (s:Skill {id: $skill_uuid})
            #             MERGE (p:Person {id: $person_id})
            #             MERGE (p)-[:HAD]->(s)
            #             """,
            #             person_id=person_props["id"],
            #             skill_uuid=skill_uuid
            #         )
            #         logger.info(f"Created HAD relationship for {person_props['name']} with skill {skill}")

            #     except Exception as e:
            #         logger.error(f"Error creating HAD relationship for {person_props['name']} with skill {skill}: {e}")

            # Handle relationships for positions
            for position in person.get("positions", []):
                position_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, position["role"]))

                try:
                    await session.run(
                        """
                        MATCH (po:Position {id: $position_uuid})
                        MERGE (p:Person {id: $person_id})
                        MERGE (p)-[:WORKED_AS {role: $role, duration: $duration, responsibilities: $responsibilities, achievements: $achievements}]->(po)
                        """,
                        person_id=person_props["id"],
                        position_uuid=position_uuid,
                        role=position.get("role"),
                        duration=position.get("duration"),
                        responsibilities=position.get("responsibilities", []),
                        achievements=position.get("achievements", []),
                    )
                    logger.info(
                        f"{g} Created WORKED_AS relationship for {q} {person_props['name']} {g} as {q} {position['role']}"
                    )

                except Exception as e:
                    logger.error(
                        f"{r} Error creating WORKED_AS relationship for {q} {person_props['name']} {r} as {q} {position['role']}: {e}"
                    )

            # Handle relationships for education
            for edu in person.get("education", []):
                university_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, edu["university"]))

                try:
                    await session.run(
                        """
                        MATCH (u:University {id: $university_uuid})
                        MERGE (p:Person {id: $person_id})
                        MERGE (p)-[:STUDIED_AT {degree: $degree, start_year: $start_year, end_year: $end_year, achievement: $achievement}]->(u)
                        """,
                        person_id=person_props["id"],
                        university_uuid=university_uuid,
                        degree=edu.get("degree"),
                        start_year=edu.get("start_year"),
                        end_year=edu.get("end_year"),
                        achievement=edu.get("achievement"),
                    )
                    logger.info(
                        f"{g} Created STUDIED_AT relationship for {q} {person_props['name']} {g} at {q} {edu['university']}"
                    )

                except Exception as e:
                    logger.error(
                        f"{r} Error creating STUDIED_AT relationship for {q} {person_props['name']} {r} at {q} {edu['university']}: {e}"
                    )

            # Handle certifications
            for cert in person.get("certification", []):
                certification_uuid = str(
                    uuid.uuid5(uuid.NAMESPACE_DNS, cert["category"])
                )

                try:
                    await session.run(
                        """
                        MATCH (c:Certification {id: $certification_uuid})
                        MERGE (p:Person {id: $person_id})
                        MERGE (p)-[:EARNED {name: $name}]->(c)
                        """,
                        person_id=person_props["id"],
                        certification_uuid=certification_uuid,
                        name=cert.get("name"),
                    )
                    logger.info(
                        f"{g} Created EARNED relationship for {q} {person_props['name']} {g} with certification {q} {cert['name']}"
                    )

                except Exception as e:
                    logger.error(
                        f"{r} Error creating EARNED relationship for {q} {person_props['name']} {r} with certification {q} {cert['name']}: {e}"
                    )

            # Handle publications
            for pub in person.get("publications", []):
                publication_uuid = str(uuid.uuid5(uuid.NAMESPACE_DNS, pub["category"]))

                try:
                    await session.run(
                        """
                        MATCH (pub:Publication {id: $publication_uuid})
                        MERGE (p:Person {id: $person_id})
                        MERGE (p)-[:PUBLISHED {conference_name: $conference_name, date: $date}]->(pub)
                        """,
                        person_id=person_props["id"],
                        publication_uuid=publication_uuid,
                        conference_name=pub.get("conference_name"),
                        date=pub.get("date"),
                    )
                    logger.info(
                        f"{g} Created PUBLISHED relationship for {q} {person_props['name']} {g} with publication {q} {pub.get('conference_name')}"
                    )

                except Exception as e:
                    logger.error(
                        f"{r} Error creating PUBLISHED relationship for {q} {person_props['name']} {r} with publication {q} {pub.get('conference_name')}: {e}"
                    )


async def create_constraints(driver):
    async with driver.session() as session:
        try:
            await session.run(
                """
                CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:WORKED_AT]-() REQUIRE r.role IS NOT NULL
                """
            )
            await session.run(
                """
                CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:WORKED_AT]-() REQUIRE r.start_date IS NOT NULL
                """
            )
            await session.run(
                """
                CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:WORKED_AT]-() REQUIRE r.responsibilities IS NOT NULL
                """
            )                            
            logger.info(f"Constraint created for WORKED_AT relationships")
            await session.run(
                """
                CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:WORKED_AS]-() REQUIRE r.responsibilities IS NOT NULL
                """
            )
            logger.info(f"Constraint created for WORKED_AS relationships")
            await session.run(
                """
                CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:STUDIED_AT]-() REQUIRE r.degree IS UNIQUE
                """
            )
            await session.run(
                """
                CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:STUDIED_AT]-() REQUIRE r.start_year IS NOT NULL
                """
            )
            logger.info(f"Constraint created for STUDIED_AT relationships")
            await session.run(
                """
                CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:EARNED]-() REQUIRE r.name IS UNIQUE
                """
            )
            logger.info(f"Constraint created for EARNED relationships")
            await session.run(
                """
                CREATE CONSTRAINT IF NOT EXISTS FOR ()-[r:PUBLISHED]-() REQUIRE r.conference_name IS UNIQUE
                """
            )
            logger.info(f"Constraint created for PUBLISHED relationships")

        except Exception as e:
            logger.error(f"Error creating constraints: {e}")


async def main():
    # with open(
    #     "./data/sample/sample.json",
    #     "r",
    # ) as file:
    #     candidate_data = json.load(file)
    #     candidate_data = process_candidate_data(candidate_data)
    
    with open(
        "./data/sample/added_positions.json",
        "r",
    ) as file:
        candidate_data = json.load(file)

    try:
        driver = await connect_to_neo4j(
            NEO4J_URI, NEO4J_DATABASE, NEO4J_USERNAME, NEO4J_PASSWORD
        )
        logger.info("Connected to Neo4j database")
        await create_constraints(driver)
        await create_person_nodes(driver, candidate_data)
        logger.info("Successfully added person nodes and relationships")
    except Exception as e:
        logger.error(f"{r} Error in main process: {q} {e}")
    finally:
        await driver.close()
        logger.info("Closed the Neo4j driver")


if __name__ == "__main__":
    asyncio.run(main())
