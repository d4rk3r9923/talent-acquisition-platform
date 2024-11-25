from dataclasses import dataclass
from typing import Annotated, List, TypedDict, Optional
from langgraph.graph.message import AnyMessage, add_messages


class AgentState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]

    # user_question: str
    conversation_history: list
    choice_next_agents: str
    analyze_criteria: str
    role: List[str]
    skill: List[str]
    certification: List[str]
    education_degree: List[str]
    age: Optional[str]
    years_of_experience: Optional[str]
    education_name: Optional[str]
    workplace_name: Optional[str]
    summary: Optional[str] 
    location: Optional[str] 
    specialization: Optional[str]
    industry: Optional[str]
    leadership_experience: Optional[str]
    project: Optional[str]
    team_experience: Optional[str]
    other: Optional[str]

    filter_results: dict
    embedding_results: dict
    top_reranker_results: dict
    full_information: str

    technical_reranker_output: str
    final_response: str
    last_response: str

@dataclass
class AgentDefaultStates:
    graph_saved_path: str = "images/MainGraph.png"
    code_execution_result_path: str = "local_files/"
    technical_reranker_output: str = ""
