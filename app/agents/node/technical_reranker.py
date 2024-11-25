import json
from enum import Enum

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from loguru import logger
from typing import Optional, TypedDict
from pydantic import BaseModel, Field

from app.agents.config import AgentState
from app.agents.prompt import CHAIN_OF_THOUGHT_RERANKER

class TechnicalReranker(Runnable):
    def __init__(self, llm: ChatOpenAI) -> None:
        super().__init__()
        self.llm = llm
        self.template = PromptTemplate.from_template(
            CHAIN_OF_THOUGHT_RERANKER,
        )

    def _generate_prompt(self, state: AgentState):
        prompt = self.template.format(
            evaluation_criteria=state["analyze_criteria"],
            top_candidate=state["full_information"],
        )
        return prompt

    def invoke(self, state: AgentState) -> dict:
        prompt = self._generate_prompt(state)
        response = self.llm.invoke(
            input=[
                {"role":"user", "content": prompt}
            ]
        )
        logger.info(f"Technical Reranker: \n{response.content}")
        return {
            "technical_reranker_output": response.content
        }

