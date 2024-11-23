from app.preprocessing.extract_pdf import processing_pdf
from app.graphdb.flex import *
from app.graphdb.fixed import *
import asyncio
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")

g = Color.GREEN
r = Color.RED
q = Color.RESET

def list_pdfs(directory="uploads"):
    """List all PDF files in the specified directory."""
    if not os.path.exists(directory):
        os.makedirs(directory)  # Ensure the directory exists
    return [f for f in os.listdir(directory) if f.endswith(".pdf")]


async def extractFromPDF(pdf_paths: List[str]):
    # Run tasks concurrently for each PDF
    tasks = [processing_pdf(path, "jsontest.json") for path in pdf_paths]
    await asyncio.gather(*tasks)

async def flexFixedFunction(json_path):
    with open(json_path, "r") as file:
        candidate_data = json.load(file)

    try:
        driver = await connect_to_neo4j(NEO4J_URI, NEO4J_DATABASE, NEO4J_USERNAME, NEO4J_PASSWORD)
        logger.info(f"{g}Connected to Neo4j database")
        await create_constraints(driver)
        await create_flex_nodes(driver, candidate_data)
        logger.info(f"{g}Successfully added person nodes and relationships")
        async with driver.session() as session:
            await create_constraints(session)
            nodes = prepare_nodes()
            node_types = ["Position", "Skill", "Certification", "Publication"]

            for node_list, node_type in zip(nodes, node_types):
                await add_nodes_to_db(session, node_list, node_type)

            logger.info(f"{g}Nodes added to Neo4j")

    except Exception as e:
        logger.error(f"{r}Error running main function:{q} {e}")
    finally:
        await driver.close()
        logger.info(f"{g}Disconnected from Neo4j")

if __name__ == "__main__":
    pdf_paths = ["uploads/CV Nguyen Duy Minh - LLM_Resume_NguyenDuyMinh-TopCV.vn.pdf"]
    asyncio.run(extractFromPDF(pdf_paths))
    asyncio.run(flexFixedFunction("jsontest.json"))

