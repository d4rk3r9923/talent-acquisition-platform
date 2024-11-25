from enum import Enum

from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from loguru import logger

from app.agents.config import AgentState
from app.agents.prompt import TECHNICAL_ANALYST

class TechnicalAnalysis(Runnable):
    def __init__(self, llm: ChatOpenAI) -> None:
        super().__init__()
        self.llm = llm
        self.template = PromptTemplate.from_template(
            TECHNICAL_ANALYST,
        )

    def _generate_prompt(self, state: AgentState):
        prompt = self.template.format(
            evaluation_criteria=state["analyze_criteria"].pop('summary', None),
            top_candidate=state["full_information"],
            top_3_candidates=state["technical_reranker_output"],
        )
        return prompt

    def invoke(self, state: AgentState) -> dict:
        prompt = self._generate_prompt(state)
        response = self.llm.invoke(
            input=[
                {"role":"user", "content": prompt}
            ]
        )
        logger.info(f"Technical Analysis: \n{response.content}")
        return {
            "final_response": response.content
        }

