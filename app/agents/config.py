import json
from dataclasses import dataclass
from typing import Any, List, TypedDict, Optional

# fixed (filter)
# "role": "Job title or role",
# "skill": "Specific skills",
# "certification": "Category of certifications",
# "education_degree": "Educational Degree",

entity_types = {
    #filter
    "age": "Candidate's age, e.g., 'under 40 years old', 'between 25 and 35 years old'",
    "years_of_experience": "Total years of professional experience, e.g., '10+ years', 'at least 3 years'",

    #partial filter
    "education_name": "Educational Name, e.g., 'FPT University'",
    "workplace_name": "Work Place Name, e.g., 'Bosch",
 
    #embedding
    "summary": "Summarize user query as the individual’s background by highlighting their education, work experience, industry focus, and specialized expertise (only 1 sentences and do not mention any number)",
    "location": "Following format: City, Country (e.g., Hanoi, Vietnam or San Francisco, USA)",

    #non-fixed
    "specialization": "Area of specialization within a field, e.g., 'backend development', 'natural language processing'",
    "industry": "Specific industry experience, e.g., 'hedge fund', 'digital transformation in tech'",
    "leadership_experience": "Experience in leadership roles, e.g., 'some leadership experience', 'managed remote teams'",
    "project": "Specific projects or achievements, e.g., 'launched mobile apps with over 100,000 users'",
    "team_experience": "Experience working with teams, e.g., 'worked with cross-functional teams'",
    "other": "Any other relevant details not covered above",
}

class AgentState(TypedDict):
    user_question: str
    entity_types: str
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
    num_retry: int
    max_retry: int

@dataclass
class AgentDefaultStates:
    graph_saved_path: str = "images/MainGraph.png"
    code_execution_result_path: str = "local_files/"
    entity_types: str = json.dumps(entity_types, indent=2)
    num_retry: int = 0
    max_retry: int = 3