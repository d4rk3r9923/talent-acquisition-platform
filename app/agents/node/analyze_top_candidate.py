import os
import json
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_core.runnables import Runnable
from loguru import logger

from app.agents.config import AgentState

load_dotenv()

class AnalyzeCandidate(Runnable):
    def __init__(self, graphdb: GraphDatabase) -> None:
        super().__init__()
        self.graphdb = graphdb

    def _read_information_candidate(self, raw_result):
        transformed = {
            "person": {},
            "work_place": [],
            "experience": [],
            "education": [],
            "degree": [],
            "project": []
        }

        for record in raw_result:
            nodes = record["nodes"]
            relationships = record["relationships"]

            for node in nodes:
                if node.labels == {"Person"}:
                    transformed["person"] = {
                        "name": node.get("name"),
                        "summary": node.get("summary"),
                        "location": node.get("location"),
                        "age": 2024 - int(node.get("dob").split("-")[0]) if node.get("dob") else ""
                    }
                elif node.labels == {"Workplace"}:
                    workplace = {
                        "name": node.get('name')
                    }
                    transformed["work_place"].append(workplace)
                elif node.labels == {"Position"}:
                    position = {
                        "name": node.get("name"),
                        "duration": None,
                        "responsibilities": None,
                        "achievements": None
                    }
                    for rel in relationships:
                        if rel.end_node.element_id == node.element_id and rel.type == "WORKED_AS":
                            position["duration"] = str(round(rel.get("duration") / 12, 2)) + ' years'
                            
                            position["responsibilities"] = rel.get("responsibilities")
                            position["achievements"] = rel.get("achievements")
                    transformed["experience"].append(position)
                elif node.labels == {"Education"}:
                    education = {
                        "name": node.get("name")
                    }
                    transformed["education"].append(education)
                elif node.labels == {"Degree"}:
                    degree = {
                        "name": node.get("name")
                    }
                    transformed["degree"].append(degree)
                    
                elif node.labels == {"Project"}:
                    project = {
                        "name": node.get("name"),
                        "description": node.get("description")
                    }
                    transformed["project"].append(project)

        return transformed
    
    def invoke(self, state: AgentState) -> dict:

        top_candidate_ids = list(state['top_reranker_results'].keys())
        full_information = []

        with self.graphdb.session(database=os.getenv("NEO4J_DATABASE")) as session:
            for idx, target_id in enumerate(top_candidate_ids):
                result = session.run(f"""
                    MATCH info=(p:Person)-[r]->(n)
                    WHERE p.id = "{target_id}"
                    AND type(r) IN ['WORKED_AS', 'WORKED_AT', 'STUDIED_AT', 'DID', 'HOLDS']
                    RETURN info
                """)
            
                raw_result = []
                for record in result:
                    path = record["info"]
                    raw_result.append({
                        "nodes": path.nodes,
                        "relationships": path.relationships
                    })

                information = self._read_information_candidate(raw_result)
                full_information.append({f'Top {idx+1}': information})
        
        dict_information = json.dumps(full_information, indent=2, ensure_ascii=False)

        # logger.info(f"Top Candidate: \n {dict_information}")

        return {
            "full_information": dict_information
        }