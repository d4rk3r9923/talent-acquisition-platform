from fixed_schema import PositionName, DegreeCategory, SkillName, CertificationCategory, PublicationCategory
from typing import List, Optional
from pydantic import BaseModel, Field
from typing_extensions import Annotated


class Category(BaseModel):
    """Category"""
    category: Annotated[str, Field(..., description="The generated category")]


class Categories(BaseModel):
    """List Categories"""
    categories: List[Category]


class Question(BaseModel):
    """Question"""
    question: Annotated[str, Field(..., description="The human language question is based on JSON resume")]


class Questions(BaseModel):
    """List Questions"""
    questions: List[Question]


class Answer(BaseModel):
    """Resume JSON Format"""
    role: Optional[List[PositionName]] = Field(None, description="Position name should match an entry in the list")
    skill: Optional[List[SkillName]] = Field(None, description="Skill name should match an entry in the list")
    certification: Optional[List[CertificationCategory]] = Field(None, description="Certifications Category should match an entry in the list")
    education_degree: Optional[List[DegreeCategory]] = Field(None, description="Educational Degree should match an entry in the list")
    
    age: Annotated[Optional[str], Field(None, description="Candidate's age, e.g., '< 40', '>= 25', '= 20'")]
    years_of_experience: Annotated[Optional[str], Field(None, description="Total years of professional experience, e.g., '< 2', '>= 8', '= 4'")]
    
    education_name: Annotated[Optional[str], Field(None, description="Educational Name, e.g., 'FPT University'")]
    workplace_name: Annotated[Optional[str], Field(None, description="Work Place Name, e.g., 'Bosch'")]
    
    summary: Annotated[Optional[str], Field(None, description="Summarize user query as the individual’s background by highlighting their education, work experience, industry focus, and specialized expertise (only 1 sentence and do not mention any number)")]
    location: Annotated[Optional[str], Field(None, description="Following format: City, Country (e.g., Hanoi, Vietnam or San Francisco, USA)")]
    
    specialization: Annotated[Optional[str], Field(None, description="Area of specialization within a field, e.g., 'backend development', 'natural language processing'")]
    industry: Annotated[Optional[str], Field(None, description="Specific industry experience, e.g., 'hedge fund', 'digital transformation in tech'")]
    leadership_experience: Annotated[Optional[str], Field(None, description="Experience in leadership roles, e.g., 'some leadership experience', 'managed remote teams'")]
    project: Annotated[Optional[str], Field(None, description="Specific projects or achievements, e.g., 'launched mobile apps with over 100,000 users'")]
    team_experience: Annotated[Optional[str], Field(None, description="Experience working with teams, e.g., 'worked with cross-functional teams'")]
    other: Annotated[Optional[str], Field(None, description="Any other relevant details not covered above")]


class Answers(BaseModel):
    """List Resume JSON Format"""
    answers: List[Answer]
