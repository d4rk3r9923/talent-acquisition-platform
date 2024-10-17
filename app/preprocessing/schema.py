from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional

from app.utils.util import create_enum_from_objects
from app.preprocessing.fixed_schema import list_universites, list_workplaces, list_positions, list_skills, list_certifications, list_publications


UniversityName = create_enum_from_objects(list_universites, enum_name='UniversityName')
CompanyName = create_enum_from_objects(list_workplaces, enum_name='CompanyName')
PositionName = create_enum_from_objects(list_positions, enum_name='PositionName')
SkillName = create_enum_from_objects(list_skills, enum_name='SkillName')
CertificationCategory = create_enum_from_objects(list_certifications, enum_name='CertificationCategory')
PublicationCategory = create_enum_from_objects(list_publications, enum_name='PublicationCategory')


# Person Model
class Person(BaseModel):
    # id: str = Field(..., description="Unique identifier for the person")
    name: str = Field(description="Full Vietnamese name of the person")
    summary: str = Field(description="Write a short summary about the person")
    phone: Optional[str] = Field(None, description="Phone number")
    dob: Optional[str] = Field(None, description="Date of birth")
    location: Optional[str] = Field(None, description="only City, Country (e.g Hanoi, Vietnam or San Francisco, USA)")
    # portfolio: Optional[List[str]] = Field(None, description="Link to the person's portfolio")

class Certification(BaseModel):
    category: CertificationCategory 

# # Publication Model
# class Publication(BaseModel):
#     category: str = Field(..., description="Category of the publication")
#     conference: Optional[str] = Field(description="Conference where the publication was presented")
#     date: Optional[str] = Field(description="Date of the publication")

# # WorkExperience Model
# class WorkExperience(BaseModel):
#     id: str = Field(..., description="Unique identifier for the work experience")
#     role: str = Field(..., description="Role held by the person")
#     start_date: str = Field(..., description="Start date of the role")
#     end_date: Optional[str] = Field(description="End date of the role, if applicable")
#     responsibilities: List[str] = Field(..., description="List of responsibilities")
#     achievements: List[str] = Field(..., description="List of achievements during this role")

# # EducationRelation Model
# class StudyAt(BaseModel):
#     degree: str = Field(None, description="Degree attained by the person")
#     start_year: str = Field(None, description="Start year of the education")
#     end_year: Optional[str] = Field(description="End year of the education")
#     achievement: Optional[str] = Field(description="Notable achievement during education")

# # Achievements (Publication and Certification)
# class Achieve(BaseModel):
#     conference: Optional[str] = Field(description="Conference where achievement occurred")
#     date: Optional[str] = Field(description="Date of the achievement")

# # Person Relationships
# class WorkedAt(BaseModel):
#     work_experience: WorkExperience = Field(..., description="Work experience at a specific workplace")
#     workplace: WorkPlace = Field(..., description="Details of the workplace")

# class HasSkills(BaseModel):
#     skills: List[Skills] = Field(..., description="List of skills the person has")

# class AchievePublication(BaseModel):
#     publication: Publication = Field(..., description="Publication achieved by the person")
#     date: Optional[str] = Field(description="Date of the publication")

# class AchieveCertification(BaseModel):
#     certification: Certification = Field(..., description="Certification achieved by the person")

# class RelevantTo(BaseModel):
#     skills: Skills = Field(..., description="Relevant skills")
#     position: Position = Field(..., description="Relevant position")


class CandidateProfile(BaseModel):
    person: Person
    certification: List[Certification]
    # study: List[StudyAt]
    # work_experience: List[WorkedAt] = Field(..., description="List of work experiences and workplaces")
    # skills: HasSkills = Field(..., description="Skills the person possesses")
    # certifications: Optional[List[AchieveCertification]] = Field(description="List of certifications achieved")
    # publications: Optional[List[AchievePublication]] = Field(description="List of publications")
    # relevant_positions: Optional[List[RelevantTo]] = Field(description="Positions relevant to the person's skills")





