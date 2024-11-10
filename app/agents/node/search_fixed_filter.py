# input: json dict (from agent state)
# output: list of ids -> to technical agent to analyze the candidates

import json
from enum import Enum

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from loguru import logger
from typing import Optional, TypedDict
from pydantic import BaseModel, Field


from app.agents.config import AgentState
from app.agents.prompts import EXTRACT_ENTITY_PROMPT, EXTRACT_FIXED_ENTITY_PROMPT
from app.preprocessing.schema import (
    PositionName, 
    DegreeCategory, 
    SkillName,
    CertificationCategory,
    PublicationCategory,
)

from neo4j import GraphDatabase





class SearchFixedFilter(Runnable):
    def __init__(self, llm: ChatOpenAI, state: AgentState) -> None:
        super().__init__()
        self.llm = llm
        self.graphdb = GraphDatabase.driver(uri=state['uri'], 
                                            database=state['database'],
                                            auth=(state['user'],state['password'])
                                        )
        

    def _filter_fixed_nodes(self, data):
        
        query = "MATCH (p:Person)\n"

        # Fixed filters
        if data['roles']:
            for role in data['roles']:
                query += f"MATCH (p)-[:WORKED_AS]->(:Position {{name: '{role}'}})\n"

        if data['skills']:
            for skill in data['skills']:
                query += f"MATCH (p)-[:HAS]->(:Skill {{name: '{skill}'}})\n"

        if data['certification']:
            for cert in data['certification']:
                query += f"MATCH (p)-[:EARNED]->(:Certification {{field: '{cert}'}})\n"

        if data['education_degree']:
            for degree in data['education_degree']:
                query += f"MATCH (p)-[:HOLDS]->(:Degree {{name: '{degree}'}})\n"

        # Filters
        if data['age']:
            query += (
                "WHERE p.dob IS NOT NULL AND p.dob <> '' "
                "AND date(p.dob) IS NOT NULL "
                "AND date().year - date(p.dob).year "
            )
            query += f"{data['age'].strip()}\n"

        if data['years_of_experience']:
            query += (
                "MATCH (p)-[r:WORKED_AS]->()\n"
                "WITH p, sum(r.duration) AS total_yoe\n"
                "WHERE total_yoe "
            )
            query += f"{data['years_of_experience'].strip()}\n"

        query += "RETURN DISTINCT(p) LIMIT 10"
        
        logger.info(f"Generated query:\n{query}")
        return query
        
    # TODOS: Async llm invoke
    def invoke(self, state: AgentState) -> dict:
        data = {
            "roles": state['role'],
            "skills": state['skill'],
            "certification": state['certification'],
            "education_degree": state['education_degree'],
            "age": state['age'],
            "years_of_experience": state['years_of_experience'],
        }
        with self.graphdb.session(database=state['database']) as session:
    
            query = self._filter_fixed_nodes(data)
            result = session.run(query)

            for record in result:
                logger.info(f"Found person node: {record['p']}")
        
        self.graphdb.close()
