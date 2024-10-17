from pydantic import BaseModel, Field
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
    location: Optional[str] = Field(None, description="City, Country (e.g., Hanoi, Vietnam or San Francisco, USA)")
    portfolio: Optional[List[str]] = Field(None, description="URLs of personal portfolio or website (e.g., GitHub, LinkedIn, etc.)")

    def __str__(self):
        return (
            f"Person(\n"
            f"    name='{self.name}',\n"
            f"    summary='{self.summary}',\n"
            f"    phone='{self.phone}',\n"
            f"    dob='{self.dob}',\n"
            f"    location='{self.location}',\n"
            f"    portfolio={self.portfolio}\n"
            f")"
        )

# WorkExperience Model
class WorkExperience(BaseModel):
    work_place: CompanyName = Field(..., description="Workplace name should match an entry in the list")
    role: PositionName = Field(..., description="Position name should match an entry in the list")
    start_date: Optional[str] = Field(None, description="Start date of the role (format: yyyy-mm-dd)")
    end_date: Optional[str] = Field(None, description="End date of the role, if applicable (format: yyyy-mm-dd)")
    responsibilities: Optional[List[str]] = Field(None, description="List of responsibilities")
    achievements: Optional[List[str]] = Field(None, description="List of achievements during this role")

    def __str__(self):
        return (
            f"WorkExperience(\n"
            f"    work_place={self.work_place},\n"
            f"    role={self.role},\n"
            f"    start_date='{self.start_date}',\n"
            f"    end_date='{self.end_date}',\n"
            f"    responsibilities={self.responsibilities},\n"
            f"    achievements={self.achievements}\n"
            f")"
        )

# Certification Model
class Certification(BaseModel):
    name: str = Field(..., description="Name of the certification")
    category: CertificationCategory = Field(..., description="Category of Certification")

    def __str__(self):
        return (
            f"Certification(\n"
            f"    name='{self.name}',\n"
            f"    category={self.category}\n"
            f")"
        )

# Publication Model
class Publication(BaseModel):
    category: PublicationCategory = Field(..., description="Category of the publication")
    conference_name: Optional[str] = Field(None, description="Name of the conference")
    date: Optional[str] = Field(None, description="Date of the publication")

    def __str__(self):
        return (
            f"Publication(\n"
            f"    category={self.category},\n"
            f"    conference_name='{self.conference_name}',\n"
            f"    date='{self.date}'\n"
            f")"
        )

# EducationRelation Model
class StudyAt(BaseModel):
    university: UniversityName = Field(..., description="University name should match an entry in the list")
    degree: Optional[str] = Field(None, description="Degree attained by the person (e.g., High School, Bachelor, Masters, etc.)")
    start_year: Optional[str] = Field(None, description="Start year of the education (format: yyyy-mm-dd)")
    end_year: Optional[str] = Field(None, description="End year of the education (format: yyyy-mm-dd)")
    achievement: Optional[str] = Field(None, description="Notable achievement during education")

    def __str__(self):
        return (
            f"StudyAt(\n"
            f"    university={self.university},\n"
            f"    degree='{self.degree}',\n"
            f"    start_year='{self.start_year}',\n"
            f"    end_year='{self.end_year}',\n"
            f"    achievement='{self.achievement}'\n"
            f")"
        )


class CandidateProfile(BaseModel):
    person: Person
    work_experience: List[WorkExperience] = Field(..., description="List of work experiences for each company")
    education: List[StudyAt] = Field(..., description="List of information for each school/university")
    certification: Optional[List[Certification]] = Field(None, description="List of certifications")
    publications: Optional[List[Publication]] = Field(None, description="List of publications")

    def __str__(self):
        # Format each work experience with indentation
        work_experience_str = ",\n".join(f"    {str(exp)}" for exp in self.work_experience)
        education_str = ",\n".join(f"    {str(edu)}" for edu in self.education)
        certification_str = ",\n".join(f"    {str(cert)}" for cert in (self.certification or []))
        publications_str = ",\n".join(f"    {str(pub)}" for pub in (self.publications or []))

        return (
            f"CandidateProfile(\n"
            f"    person={self.person},\n"
            f"    work_experience=[\n{work_experience_str}\n    ],\n"
            f"    education=[\n{education_str}\n    ],\n"
            f"    certification=[\n{certification_str}\n    ],\n"
            f"    publications=[\n{publications_str}\n    ]\n"
            f")"
        )