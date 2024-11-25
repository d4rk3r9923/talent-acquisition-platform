import json
from enum import Enum
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import Runnable
from langchain_openai import ChatOpenAI
from loguru import logger
from typing import Optional, TypedDict
from pydantic import BaseModel, Field

from app.agents.config import AgentState
from app.agents.prompt import ROUTER_PROMPT


class Router(Runnable):
    def __init__(self, llm: ChatOpenAI) -> None:
        super().__init__()
        self.llm = llm

    # TODOS: Async llm invoke
    def invoke(self, state: AgentState) -> dict:
        options = ['SEARCH_IN_DATABASE', 'NOT_SEARCH_IN_DATABASE']

        function_def = {
            "name": "route",
            "description": "Select the next role.",
            "parameters": {
                "title": "routeSchema",
                "type": "object",
                "properties": {
                    "action": {
                        "anyOf": [
                            {"enum": options},
                        ],
                    },
                },
                "required": ["action"],
            },
        }

        llm = self.llm.bind_tools(tools=[function_def], tool_choice="route")
        
        response = llm.invoke(
            input=[
                {"role":"system", "content": ROUTER_PROMPT}
            ] + state['conversation_history']
        )
        choice = response.tool_calls[0]['args']['action']

        logger.debug(state['conversation_history'])
        logger.debug(choice)

        return {
            "choice_next_agents": choice,
        }
