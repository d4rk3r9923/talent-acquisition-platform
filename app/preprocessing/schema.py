from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import List, Optional

from app.references.util import create_enum_from_objects
from app.preprocessing.fixed_schema import (
    # list_universites, 
    # list_workplaces, 
    list_degrees,
    list_positions, 
    list_skills, 
    list_certifications, 
    list_publications
)

# Creating Enums from objects using your custom utility
# UniversityName = create_enum_from_objects(list_universites, enum_name='UniversityName')
# CompanyName = create_enum_from_objects(list_workplaces, enum_name='CompanyName')
PositionName = create_enum_from_objects(list_positions, enum_name='PositionName')
DegreeCategory = create_enum_from_objects(list_degrees, enum_name='DegreeCategory')
SkillName = create_enum_from_objects(list_skills, enum_name='SkillName')
CertificationCategory = create_enum_from_objects(list_certifications, enum_name='CertificationCategory')
PublicationCategory = create_enum_from_objects(list_publications, enum_name='PublicationCategory')

# Person Model
class Person(BaseModel):
    name: Optional[str] = Field(None, description="Full English name of the person")
    summary: Optional[str] = Field(None, description="Summarize the individual’s background by highlighting their education, work experience, industry focus, and specialized expertise (around 2 sentences and do not mention any number)")
    dob: Optional[str] = Field(None, description="Date of birth (Must following format: yyyy-mm-dd)")
    location: Optional[str] = Field(None, description="Following format: City, Country (e.g., Hanoi, Vietnam or San Francisco, USA) returning in English")
    portfolio: Optional[List[str]] = Field(None, description="URLs of personal portfolio or website (e.g., GitHub, LinkedIn, etc.)")


# WorkExperience Model
class WorkAt(BaseModel):
    work_place: str = Field(..., description="Name of the workplace in english name")
    role: PositionName = Field(None, description="Position name should match an entry in the list")
    start_date: Optional[str] = Field(None, description="Start date of the role (Must following format: yyyy-mm-dd)")
    end_date: Optional[str] = Field(None, description="End date of the role, if applicable (Must following format: yyyy-mm-dd)")
    responsibilities: Optional[List[str]] = Field(None, description="List of responsibilities")
    achievements: Optional[List[str]] = Field(None, description="List of achievements during this role")

# Skill Model
class Skill(BaseModel):
    name: SkillName

# Certification Model
class Certification(BaseModel):
    name: str = Field(None, description="Name of the certification")
    category: CertificationCategory = Field(None, description="Category of Certification")

# # Publication Model
# class Publication(BaseModel):
#     category: PublicationCategory = Field(None, description="Category of the publication")
#     conference_name: Optional[str] = Field(None, description="Name of the conference")
#     date: Optional[str] = Field(None, description="Date of the publication")

# Project Model
class Project(BaseModel):
    name: Optional[str] = Field(None, description="Name of Project")
    description: Optional[str] = Field(None, description="Provide an introduction and detailed description of the project, outlining its purpose and key elements.")

# EducationRelation Model
class StudyAt(BaseModel):
    name_education: Optional[str] = Field(..., description="Name of the education institution in english name")
    degree: DegreeCategory = Field(None, description="Degree attained by the person")
    # start_year: Optional[str] = Field(None, description="Start year of the education (Must following format: yyyy-mm-dd)")
    # end_year: Optional[str] = Field(None, description="End year of the education (Must following format: yyyy-mm-dd)")
    # achievement: Optional[str] = Field(None, description="Notable achievement during education")


class CandidateProfile(BaseModel):
    person: Person
    work_experience: Optional[List[WorkAt]] = Field(None, description="List of work experiences for each company")
    education: Optional[List[StudyAt]] = Field(None, description="List of information for each school/university")
    list_certification: Optional[List[Certification]]
    list_skill: Optional[List[Skill]]
    list_project: Optional[List[Project]]
    # publications: Optional[List[Publication]] = Field(None, description="List of publications")
