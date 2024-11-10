from typing import Annotated, TypedDict, List, Optional


class Category(TypedDict):
    """Category"""
    category: Annotated[str, ..., "The category is based on schema"]

class Categories(TypedDict):
    """List Categories"""
    categories: List[Category]

class Question(TypedDict):
    """Question"""
    question: Annotated[str, ..., "The human language question is based on JSON resume"]

class Questions(TypedDict):
    """List Questions"""
    questions: List[Question]

class Answer(TypedDict):
    """Resume JSON Format"""
    role: Annotated[Optional[List[str]], ..., "Job title or role"]
    skill: Annotated[Optional[List[str]], ..., "Specific skills"]
    certification: Annotated[Optional[List[str]], ..., "Category of certifications"]
    education_degree: Annotated[Optional[List[str]], ..., "Educational Degree"]

    age: Annotated[Optional[str], ..., "Candidate's age, e.g., '< 40', '>= 25', '= 20'"]
    years_of_experience: Annotated[Optional[str], ..., "Total years of professional experience, e.g., '< 2', '>= 8', '= 4'"]

    education_name: Annotated[Optional[str], ..., "Educational Name, e.g., 'FPT University'"]
    workplace_name: Annotated[Optional[str], ..., "Work Place Name, e.g., 'Bosch'"]

    summary: Annotated[Optional[str], ..., "Summarize user query as the individual’s background by highlighting their education, work experience, industry focus, and specialized expertise (only 1 sentence and do not mention any number)"]
    location: Annotated[Optional[str], ..., "Following format: City, Country (e.g., Hanoi, Vietnam or San Francisco, USA)"]

    specialization: Annotated[Optional[str], ..., "Area of specialization within a field, e.g., 'backend development', 'natural language processing'"]
    industry: Annotated[Optional[str], ..., "Specific industry experience, e.g., 'hedge fund', 'digital transformation in tech'"]
    leadership_experience: Annotated[Optional[str], ..., "Experience in leadership roles, e.g., 'some leadership experience', 'managed remote teams'"]
    project: Annotated[Optional[str], ..., "Specific projects or achievements, e.g., 'launched mobile apps with over 100,000 users'"]
    team_experience: Annotated[Optional[str], ..., "Experience working with teams, e.g., 'worked with cross-functional teams'"]
    other: Annotated[Optional[str], ..., "Any other relevant details not covered above"]


class Answers(TypedDict):
    """List Resume JSON Format"""
    answers: List[Answer]