import json
from enum import Enum

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from loguru import logger
from typing import Optional, TypedDict
from pydantic import BaseModel, Field

from app.agents.config import AgentState
from app.agents.prompt import EXTRACT_ENTITY_PROMPT, EXTRACT_FIXED_ENTITY_PROMPT
from app.preprocessing.schema import (
    Analyze_PositionName,
    PositionName, 
    DegreeCategory, 
    SkillName,
    CertificationCategory,
    PublicationCategory,
)

entity_types = {
    # Filter
    # "role": "Job title or role",
    # "skill": "Specific skills",
    # "certification": "Category of certifications",
    # "education_degree": "Educational Degree",
    "age": "Candidate's age in the format <number, >number, or =number, e.g., '<30', '>20' or '=25'",
    "years_of_experience": "Total years of professional experience in the format <number, >number, or =number,, e.g., '=5', '>3'",

    #Partial filter
    "education_name": "Educational Name, e.g., 'FPT University'",
    "workplace_name": "Work Place Name, e.g., 'Bosch",

    #Embedding
    "summary": "Summarize user query as the individual’s background by highlighting their education, work experience, industry focus, and specialized expertise (only 1 sentences and do not mention any number)",
    "location": "Following format: City, Country (e.g., Hanoi, Vietnam or San Francisco, USA)",

    #Non-fixed
    "specialization": "Area of specialization within a field, e.g., 'backend development', 'natural language processing'",
    "industry": "Specific industry experience, e.g., 'hedge fund', 'digital transformation in tech'",
    "leadership_experience": "Experience in leadership roles, e.g., 'some leadership experience', 'managed remote teams'",
    "project": "Specific projects or achievements, e.g., 'launched mobile apps with over 100,000 users'",
    "team_experience": "Experience working with teams, e.g., 'worked with cross-functional teams'",
    "other": "Any other relevant details not covered above",
}

class FixedEntity(BaseModel):
    role: Optional[list[Analyze_PositionName]] = Field(None, description="Job title or role")
    skill: Optional[list[SkillName]] = Field(None, description="Specific skills")
    certification: Optional[list[CertificationCategory]]= Field(None, description="Category of certifications")
    education_degree: Optional[list[DegreeCategory]] = Field(None, description="Educational Degree")


class QueryAnalysis(Runnable):
    def __init__(self, llm: ChatOllama) -> None:
        super().__init__()
        self.llm = llm
        self.template = PromptTemplate.from_template(
            EXTRACT_ENTITY_PROMPT,
        )

    def _generate_prompt(self, state: AgentState):
        extract_prompt = self.template.format(
            entity_types=json.dumps(entity_types),
        )
        extract_fixed_prompt = EXTRACT_FIXED_ENTITY_PROMPT

        return extract_prompt, extract_fixed_prompt
    
    def _transform_entity_dict(self, entity_dict):
        transformed_dict = {}
        
        for key, values in entity_dict.items():
            if values is None:
                # If values is None, set the result for this key to None
                transformed_dict[key] = []
            # elif len(values) == 1:
            #     # If there's only one item, use its value directly
            #     transformed_dict[key] = values[0].value
            else:
                # If there are multiple items, create a list of their values
                transformed_dict[key] = [value.value for value in values]
        
        return transformed_dict

    # TODOS: Async llm invoke
    def invoke(self, state: AgentState) -> dict:
        extract_prompt, extract_fixed_prompt = self._generate_prompt(state)
        llm = self.llm.with_structured_output(schema=TypedDict, method="json_mode")
        fixed_llm = self.llm.with_structured_output(schema=FixedEntity, method="json_schema")

        entity = llm.invoke(
            input=[
                {"role":"system", "content": extract_prompt},
                {"role":"user", "content": state['conversation_history'][-1]['content']}
            ]
        )
        
        logger.debug(f"QueryAnalysis - Extract entity: \n{entity}")
        
        fixed_entity = fixed_llm.invoke(
            input=[
                {"role":"system", "content": extract_fixed_prompt},
                {"role":"user", "content": state['conversation_history'][-1]['content']}
            ]
        )

        fixed_entity = fixed_entity.model_dump()
        dict_fixed_entity = self._transform_entity_dict(fixed_entity)

        logger.debug(f"QueryAnalysis - Extract fixed entity: \n{dict_fixed_entity}")

        return {
            "analyze_criteria": dict_fixed_entity | entity,
            "role": dict_fixed_entity["role"],
            "skill": dict_fixed_entity["skill"],
            "certification": dict_fixed_entity["certification"],
            "education_degree": dict_fixed_entity["education_degree"],
            "age": entity.get("age", ""),
            "years_of_experience": entity.get("years_of_experience", ""),
            "education_name": entity.get("education_name", ""),
            "workplace_name": entity.get("workplace_name", ""),
            "summary": entity.get("summary", ""),
            "location": entity.get("location", ""),
            "specialization": entity.get("specialization", ""),
            "industry": entity.get("industry", ""),
            "leadership_experience": entity.get("leadership_experience", ""),
            "project": entity.get("project", ""),
            "team_experience": entity.get("team_experience", ""),
            "other": entity.get("other", "")
        }
