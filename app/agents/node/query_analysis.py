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


class FixedEntity(BaseModel):
    role: Optional[list[PositionName]] = Field(None, description="Job title or role")
    skill: Optional[list[SkillName]] = Field(None, description="Specific skills")
    certification: Optional[list[CertificationCategory]]= Field(None, description="Category of certifications")
    education_degree: Optional[list[DegreeCategory]] = Field(None, description="Educational Degree")


class QueryAnalysis(Runnable):
    def __init__(self, llm: ChatOpenAI) -> None:
        super().__init__()
        self.llm = llm
        self.template = PromptTemplate.from_template(
            EXTRACT_ENTITY_PROMPT,
        )

    def _generate_prompt(self, state: AgentState):
        extract_prompt = self.template.format(
            entity_types=state["entity_types"],
        )
        extract_fixed_prompt = EXTRACT_FIXED_ENTITY_PROMPT

        return extract_prompt, extract_fixed_prompt
    
    def _transform_entity_dict(self, entity_dict):
        transformed_dict = {}
        
        for key, values in entity_dict.items():
            if values is None:
                # If values is None, set the result for this key to None
                transformed_dict[key] = None
            elif len(values) == 1:
                # If there's only one item, use its value directly
                transformed_dict[key] = values[0].value
            else:
                # If there are multiple items, create a list of their values
                transformed_dict[key] = [value.value for value in values]
        
        return transformed_dict

    def invoke(self, state: AgentState) -> dict:
        extract_prompt, extract_fixed_prompt = self._generate_prompt(state)
        llm = self.llm.with_structured_output(schema=TypedDict, method="json_mode")
        fixed_llm = self.llm.with_structured_output(schema=FixedEntity, method="json_schema")

        entity = llm.invoke(
            input=[
                {"role":"system", "content": extract_prompt},
                {"role":"user", "content": state['user_question']}
            ]
        )
        
        logger.debug(f"QueryAnalysis - Extract entity: \n{entity}")
        
        fixed_entity = fixed_llm.invoke(
            input=[
                {"role":"system", "content": extract_fixed_prompt},
                {"role":"user", "content": state['user_question']}
            ]
        )

        fixed_entity = fixed_entity.model_dump()
        dict_fixed_entity = self._transform_entity_dict(fixed_entity)

        logger.debug(f"QueryAnalysis - Extract fixed entity: \n{dict_fixed_entity}")

        return {
            "role": dict_fixed_entity["role"],
            "skill": dict_fixed_entity["skill"],
            "certification": dict_fixed_entity["certification"],
            "education_degree": dict_fixed_entity["education_degree"],
            "age": entity.get("age"),
            "years_of_experience": entity.get("years_of_experience"),
            "education_name": entity.get("education_name"),
            "workplace_name": entity.get("workplace_name"),
            "summary": entity.get("summary"),
            "location": entity.get("location"),
            "specialization": entity.get("specialization"),
            "industry": entity.get("industry"),
            "leadership_experience": entity.get("leadership_experience"),
            "project": entity.get("project"),
            "team_experience": entity.get("team_experience"),
            "other": entity.get("other")
        }
