import asyncio
import os
import pandas as pd
from enum import Enum, auto
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from neo4j import GraphDatabase
from typing import Annotated, Any, Dict, List, Optional, TypedDict
from langchain_core.runnables import RunnableConfig
from langchain_core.runnables.graph import MermaidDrawMethod
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langfuse.callback import CallbackHandler

from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph, START

from app.agents.config import AgentState, AgentDefaultStates
from app.agents.node import (
    Router,
    QueryAnalysis,
    SearchFixedFilter,
    SearchEmbedding,
    Reranker,
    AnalyzeCandidate,
    TechnicalReranker,
    TechnicalAnalysis,
    TASpecialist
)

load_dotenv()


class AgentNode(Enum):
    init_node = auto()
    router = auto()
    query_analysis_node = auto()
    search_fixed_filter = auto()
    search_embedding = auto()
    reranker_node = auto()
    analyze_candidate = auto()
    technical_reranker = auto()
    technical_analysis = auto()
    specialist = auto()

class AgentGraph:
    def __init__(self, llm: ChatOpenAI, model_embedding: OpenAIEmbeddings):
        self.graph = StateGraph(AgentState)
        self.graph.support_multiple_edges = True
        self.graph_nodes = AgentNode
        self.graph_saved_path = AgentDefaultStates.graph_saved_path

        self.graphdb = GraphDatabase.driver(
                        uri=os.getenv("NEO4J_URI"), 
                        database=os.getenv("NEO4J_DATABASE"),
                        auth=(os.getenv("NEO4J_USERNAME"),os.getenv("NEO4J_PASSWORD"))
                    )

        self.llm = llm
        self.llm.temperature = 0
        self.model_embedding = model_embedding

        self.compiled_graph = self._compile_graph()
        self._check_local_folder_exists
    
    def _compile_graph(self) -> CompiledGraph:
        # Add all nodes to graph
        self._add_graph_nodes()
        # Add edges to connect nodes
        self._add_graph_edges()
        return self.graph.compile()

    def _check_local_folder_exists(self):
        if not os.path.exists(self.code_execution_result_path):
            os.makedirs(self.code_execution_result_path)

    def _check_choice_router(self, state: AgentState):
        if state["choice_next_agents"] == "SEARCH_IN_DATABASE":
            if state["search_trial"] <= 1:
                return "SEARCH_IN_DATABASE"
            else:
                return "NOT_SEARCH_IN_DATABASE"
        else:
            return "NOT_SEARCH_IN_DATABASE"
    
    def _check_quantity_search(self, state: AgentState):
        return state["search_trial"]

    def _add_graph_nodes(self):

        # Add Query Analysis node
        self.graph.add_node(
            self.graph_nodes.router.name,
            Router(llm=self.llm).invoke,
        )

        # Add Query Analysis node
        self.graph.add_node(
            self.graph_nodes.query_analysis_node.name,
            QueryAnalysis(llm=self.llm).invoke,
        )
        # Add Search Fixed Filter node
        self.graph.add_node(
            self.graph_nodes.search_fixed_filter.name,
            SearchFixedFilter(graphdb=self.graphdb).invoke,
        )

        # Add Search Embedding node
        self.graph.add_node(
            self.graph_nodes.search_embedding.name,
            SearchEmbedding(model_embedding=self.model_embedding, graphdb=self.graphdb).invoke,
        )

        # Add Reranker node
        self.graph.add_node(
            self.graph_nodes.reranker_node.name,
            Reranker().invoke,
        )

        # Add Analyze Candidate node
        self.graph.add_node(
            self.graph_nodes.analyze_candidate.name,
            AnalyzeCandidate(graphdb=self.graphdb).invoke,
        )

        # Add Technical Reranker node
        self.graph.add_node(
            self.graph_nodes.technical_reranker.name,
            TechnicalReranker(llm=self.llm).invoke,
        )

        # Add Technical Analysis node
        self.graph.add_node(
            self.graph_nodes.technical_analysis.name,
            TechnicalAnalysis(llm=self.llm).invoke,
        )

        # Add TA Specialist node
        self.graph.add_node(
            self.graph_nodes.specialist.name,
            TASpecialist(llm=self.llm).invoke,
        )
    
    def _add_graph_edges(self):
        self.graph.add_edge(START, self.graph_nodes.router.name)

        self.graph.add_conditional_edges(
            self.graph_nodes.router.name,
            self._check_choice_router,
            {
                "SEARCH_IN_DATABASE": self.graph_nodes.query_analysis_node.name,
                "NOT_SEARCH_IN_DATABASE": self.graph_nodes.specialist.name,
            },
        )

        ### SEARCH_IN_DATABASE
        self.graph.add_edge(
            self.graph_nodes.query_analysis_node.name, 
            self.graph_nodes.search_fixed_filter.name
        )

        self.graph.add_edge(
            self.graph_nodes.search_fixed_filter.name, 
            self.graph_nodes.search_embedding.name
        )

        self.graph.add_edge(
            self.graph_nodes.search_embedding.name, 
            self.graph_nodes.reranker_node.name
        )

        self.graph.add_edge(
            self.graph_nodes.reranker_node.name, 
            self.graph_nodes.analyze_candidate.name
        )

        self.graph.add_edge(
            self.graph_nodes.analyze_candidate.name, 
            self.graph_nodes.technical_reranker.name
        )

        self.graph.add_edge(
            self.graph_nodes.technical_reranker.name, 
            self.graph_nodes.technical_analysis.name
        )

        self.graph.add_edge(
            self.graph_nodes.technical_analysis.name, 
            END
        )

        ### NOT_SEARCH_IN_DATABASE
        self.graph.add_edge(
            self.graph_nodes.specialist.name, 
            END
        )


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
    
    async def stream_events(self, inputs: dict, config: dict):
        inputs.update(**AgentDefaultStates().__dict__)
        async for event in self.compiled_graph.astream_events(inputs, config, version="v2"):
            kind = event["event"]
            print(f"{kind}: {event['name']}")
            print(event['data'])

    async def ainvoke(self, inputs: dict, config: dict) -> dict:
        inputs.update(**AgentDefaultStates().__dict__)
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, self.compiled_graph.invoke, inputs, config
        )



if __name__ == "__main__":

    from langfuse.callback import CallbackHandler
    from app.references.client import chatOpenai_client, embedding_OpenAI

    langfuse_handler = CallbackHandler(
        secret_key="sk-lf-88194161-6bab-48a1-9dd6-28ba5af82847",
        public_key="pk-lf-8f26d208-2582-4aa4-ad3b-16c6e9bd37e9",
        host="https://us.cloud.langfuse.com"
    )

    # inputs = {
    #     "user_question": "software engineer work in FPT before and live in hcmc. a full-stack developer who has built large-scale e-commerce websites and knows about performance optimization."
    # }

    # inputs = {
    #     "user_question": "I need a software engineer living HCMC who specializes in backend development with Java, has experience in RESTful APIs, and knows their way around Kubernetes."
    # }

    # inputs = {
    #     "user_question": "I’m looking for a software engineer living HCMC and has managed teams of 5-10 people, has experience with Agile methodologies, and a strong understanding of DevOps practices in healthcare IT."
    # }

    inputs = {
        "conversation_history": [
            {   
                "role": "user", 
                "content": "who are you?"
            },
        ],
        "search_trial" : 0,
        "full_information": "",
        "technical_reranker_output": "",
    }

    config={"callbacks": [langfuse_handler]}

    main_agent = AgentGraph(llm=chatOpenai_client, model_embedding=embedding_OpenAI)
    # main_agent.invoke(inputs, config)

    # Use asyncio to run the stream_events coroutine
    asyncio.run(main_agent.stream_events(inputs, config))
