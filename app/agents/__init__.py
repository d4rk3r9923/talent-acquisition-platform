import asyncio
import os
import pandas as pd
from enum import Enum, auto
from io import BytesIO
from PIL import Image
from typing import Annotated, Any, Dict, List, Optional, TypedDict
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.graph import MermaidDrawMethod
from langchain_openai import ChatOpenAI
from langfuse.callback import CallbackHandler

from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph, START

from app.agents.config import AgentState, AgentDefaultStates
from app.agents.node import (
    QueryAnalysis
)


class AgentNode(Enum):
    init_node = auto()
    query_analysis_node = auto()


class AgentGraph:
    def __init__(self, llm: ChatOpenAI):
        self.graph = StateGraph(AgentState)
        self.graph.support_multiple_edges = True
        self.graph_nodes = AgentNode
        self.graph_saved_path = AgentDefaultStates.graph_saved_path
        self.llm = llm

        self.llm.temperature = 0

        self.compiled_graph = self._compile_graph()
        self._check_local_folder_exists

    def _check_local_folder_exists(self):
        if not os.path.exists(self.code_execution_result_path):
            os.makedirs(self.code_execution_result_path)

    def _check_code_excecution_status(self, state: AgentState):
        if state["code_execution_error"]:
            return "failed"
        else:
            return "success"

    def _check_error_correction_max_retries(self, state: AgentState):
        if state["num_retry"] < state["max_retry"]:
            return "retry"
        else:
            return "max retries"

    def _add_graph_nodes(self):

        # Add Query Analysis node
        self.graph.add_node(
            self.graph_nodes.query_analysis_node.name,
            QueryAnalysis(llm=self.llm).invoke,
        )
    
    def _add_graph_edges(self):
        # Add edges: START -> Information Extractor
        self.graph.add_edge(START, self.graph_nodes.query_analysis_node.name)
    
        self.graph.add_edge(self.graph_nodes.query_analysis_node.name, END)

    def _compile_graph(self) -> CompiledGraph:
        # Add all nodes to graph
        self._add_graph_nodes()

        # Add edges to connect nodes
        self._add_graph_edges()

        return self.graph.compile()

    def visualize_graph(self):
        file = Image.open(
            BytesIO(
                self.compiled_graph.get_graph().draw_mermaid_png(
                    draw_method=MermaidDrawMethod.API,
                )
            )
        )
        file.save(self.graph_saved_path)
    
    def invoke(self, inputs: dict, config: dict) -> dict:
        inputs.update(**AgentDefaultStates().__dict__)
        output = self.compiled_graph.invoke(inputs, config=config)
        return output

    async def ainvoke(self, inputs: dict, config: dict) -> dict:
        inputs.update(**AgentDefaultStates().__dict__)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.compiled_graph.invoke, inputs, config
        )



if __name__ == "__main__":

    from langfuse.callback import CallbackHandler
    from app.references.client import chatOpenai_client

    langfuse_handler = CallbackHandler(
        secret_key="sk-lf-2775ace0-28e2-433a-b56c-650977ae6d11",
        public_key="pk-lf-a950fa09-aac1-49b0-a678-b0338878c047",
        host="https://us.cloud.langfuse.com"
    )

    inputs = {
        "user_question": "We need a candidate who has at least 3 years of experience in AI research, focusing on natural language processing and deep learning, with a few published papers in top-tier conferences. And they maybe from hcmc"
    }

    config={"callbacks": [langfuse_handler]}

    main_agent = AgentGraph(llm=chatOpenai_client)
    main_agent.invoke(inputs, config)