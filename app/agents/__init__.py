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
        return state["choice_next_agents"] 

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
    #     "user_question": "I’m looking for someone who lived in hcmc and has managed teams of 5-10 people, has experience with Agile methodologies, and a strong understanding of DevOps practices in healthcare IT."
    # }

    inputs = {
        "conversation_history": [
            {   
                "role": "user", 
                "content": "who are you ?"
            },
#             {   "role": "assistant",
#                 "content": """- **Tran Anh Hoang**:  
#   + **Healthcare IT Experience**: Tran Anh Hoang has extensive experience in IT, particularly in ERP systems, which are often integral to healthcare IT environments. His background in developing and managing IT solutions for various companies aligns well with the healthcare sector's needs for efficient data management and operational workflows.  
#   + **Agile Methodologies and Team Management**: He has held leadership roles, including Project Lead, where he coordinated with consulting partners and managed user permissions, indicating familiarity with Agile practices. However, specific experience in Agile methodologies is not explicitly mentioned, which could be a gap. His experience in managing teams and overseeing operations suggests he is capable of leading teams of 5-10 people effectively.  

# - **Thái Thành Nguyên**:  
#   + **Healthcare IT Experience**: While Thái Thành Nguyên's experience is primarily in AI and NLP, his technical skills could be beneficial in healthcare IT, especially in developing intelligent systems for data processing and patient management. However, he lacks direct experience in healthcare IT, which may limit his immediate applicability in this sector.  
#   + **Agile Methodologies and Team Management**: His role as an AI Engineer involved collaborative projects, which may imply experience with Agile methodologies. However, there is no direct mention of managing teams, which is a critical aspect of the evaluation criteria. His technical skills are strong, but the lack of team management experience could be a significant gap for this role.  

# - **Shino Pham**:  
#   + **Healthcare IT Experience**: Shino Pham has significant experience in operations management, which is valuable in any IT context, including healthcare. However, his background does not specifically mention healthcare IT, which may limit his relevance to the role. His experience in enhancing team performance and strategic planning could be beneficial in a healthcare setting, but the lack of direct experience in healthcare IT is a notable gap.  
#   + **Agile Methodologies and Team Management**: He has managed teams of over 20 staff, demonstrating strong leadership capabilities. His experience in operations and business analysis suggests familiarity with Agile practices, although this is not explicitly stated. His operational focus and ability to drive efficiency are strengths, but the lack of specific Agile experience could be a concern.  

# **Final Comment:**  
# Based on the evaluation criteria, **Tran Anh Hoang** emerges as the best candidate due to his extensive experience in IT and ERP systems, which are crucial for healthcare IT. His leadership roles indicate a capacity to manage teams effectively, although he could benefit from more explicit Agile experience. **Thái Thành Nguyên** has strong technical skills in AI, which could complement healthcare IT but lacks direct experience in the sector and team management. **Shino Pham**, while experienced in operations, does not have a specific focus on healthcare IT and is located in the USA, which may not align with the role's requirements. Therefore, Tran Anh Hoang is the most suitable candidate for the position."""
#             },
#             {   
#                 "role": "user", 
#                 "content": "tell me more about thanh nguyen"
#             },
        ]
    }

    config={"callbacks": [langfuse_handler]}

    main_agent = AgentGraph(llm=chatOpenai_client, model_embedding=embedding_OpenAI)
    # main_agent.invoke(inputs, config)

    # Use asyncio to run the stream_events coroutine
    asyncio.run(main_agent.stream_events(inputs, config))
