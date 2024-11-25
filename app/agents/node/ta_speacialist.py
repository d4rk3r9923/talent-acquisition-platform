from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from loguru import logger

from app.agents.config import AgentState
from app.agents.prompt import SPECIALIST

class TASpecialist(Runnable):
    def __init__(self, llm: ChatOpenAI) -> None:
        super().__init__()
        self.llm = ChatOpenAI(temperature=0,streaming=True)
        # Streaming in this node
        self.llm.streaming = True 
        self.template = PromptTemplate.from_template(
            SPECIALIST,
        )

    def _generate_prompt(self, state: AgentState):
        prompt = self.template.format(
            top_candidate=state["full_information"],
            top_3_candidates=state["technical_reranker_output"],
        )
        return prompt

    def invoke(self, state: AgentState) -> dict:
        prompt = self._generate_prompt(state)
        response = self.llm.invoke(
            input=[
                {"role":"system", "content": prompt}
            ] + state['conversation_history']
        )
        logger.info(f"Speacialist: \n{prompt}")

        return {
            "final_response": response.content
        }

