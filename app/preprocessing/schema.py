from pydantic import BaseModel, Field, field_validator
from enum import Enum
from typing import List, Optional

from app.utils.util import create_enum_from_objects
from app.preprocessing.fixed_schema import (
    list_universites, 
    list_workplaces, 
    list_positions, 
    list_skills, 
    list_certifications, 
    list_publications
)

# Creating Enums from objects using your custom utility
UniversityName = create_enum_from_objects(list_universites, enum_name='UniversityName')
CompanyName = create_enum_from_objects(list_workplaces, enum_name='CompanyName')
PositionName = create_enum_from_objects(list_positions, enum_name='PositionName')
SkillName = create_enum_from_objects(list_skills, enum_name='SkillName')
CertificationCategory = create_enum_from_objects(list_certifications, enum_name='CertificationCategory')
PublicationCategory = create_enum_from_objects(list_publications, enum_name='PublicationCategory')

# Person Model
class Person(BaseModel):
    name: Optional[str] = Field(None, description="Full English name of the person")
    summary: Optional[str] = Field(None, description="Short summary about the person")
    phone: Optional[str] = Field(None, description="Phone number")
    dob: Optional[str] = Field(None, description="Date of birth (format: yyyy-mm-dd)")
    location: Optional[str] = Field(None, description="format: City, Country (e.g., Hanoi, Vietnam or San Francisco, USA)")
    portfolio: Optional[List[str]] = Field(None, description="URLs of personal portfolio or website (e.g., GitHub, LinkedIn, etc.)")


# WorkExperience Model
class WorkExperience(BaseModel):
    work_place: CompanyName = Field(None, description="Workplace name should match an entry in the list")
    role: PositionName = Field(None, description="Position name should match an entry in the list")
    start_date: Optional[str] = Field(None, description="Start date of the role (format: yyyy-mm-dd)")
    end_date: Optional[str] = Field(None, description="End date of the role, if applicable (format: yyyy-mm-dd)")
    responsibilities: Optional[List[str]] = Field(None, description="List of responsibilities")
    achievements: Optional[List[str]] = Field(None, description="List of achievements during this role")

    # # Validator to check if name is 'others' and assign a new generated name
    # @field_validator('work_place', mode='before', check_fields=False)
    # def generate_name_if_others(cls, v, values):
    #     if v == CompanyName.OTHERS_COMPANY:
    #         values['generated_company_name'] = cls.generate_new_company_name()
    #     return v

    # @staticmethod
    # def generate_new_skill():
    #     # Simulate a generated company name
    #     return "New Generated Company Name"


# Certification Model
class Certification(BaseModel):
    name: str = Field(None, description="Name of the certification")
    category: CertificationCategory = Field(None, description="Category of Certification")


# Publication Model
class Publication(BaseModel):
    category: PublicationCategory = Field(None, description="Category of the publication")
    conference_name: Optional[str] = Field(None, description="Name of the conference")
    date: Optional[str] = Field(None, description="Date of the publication")


# EducationRelation Model
class StudyAt(BaseModel):
    university: UniversityName = Field(None, description="University name should match an entry in the list")
    degree: Optional[str] = Field(None, description="Degree attained by the person (e.g., High School, Bachelor, Masters, etc.)")
    start_year: Optional[str] = Field(None, description="Start year of the education (format: yyyy-mm-dd)")
    end_year: Optional[str] = Field(None, description="End year of the education (format: yyyy-mm-dd)")
    achievement: Optional[str] = Field(None, description="Notable achievement during education")


class CandidateProfile(BaseModel):
    person: Person
    work_experience: Optional[List[WorkExperience]] = Field(None, description="List of work experiences for each company")
    education: Optional[List[StudyAt]] = Field(None, description="List of information for each school/university")
    certification: Optional[List[Certification]] = Field(None, description="List of certifications")
    publications: Optional[List[Publication]] = Field(None, description="List of publications")
