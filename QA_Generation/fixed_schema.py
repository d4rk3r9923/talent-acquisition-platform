from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional
import uuid

'''
******************************
----CLASS FOR FIXED SCHEMA----
#*****************************
'''


# # Education Model
# class Education(BaseModel):
#     name: str = Field(..., description="Name of the education institution")
#     field: str = Field(..., description="Field of study")

# # WorkPlace Model
# class WorkPlace(BaseModel):
#     name: str = Field(..., description="Name of the workplace")
#     domain_expertise: str = Field(..., description="Domain expertise of the workplace")
#     size: Optional[str] = Field(description="Size of the workplace")

# Position Model
class Position(BaseModel):
    name: str = Field(..., description="Name of the position")

# Skills Model
class Skills(BaseModel):
    name: str = Field(..., description="Name of the skill")
    category: str = Field(..., description="Category of the skill")

class Certification(BaseModel):
    category: str = Field(..., description="Category of the certification")

class Degree(BaseModel):
    category: str = Field(..., description="Category of the Academic Degrees")
    
# Publication Model
class Publication(BaseModel):
    category: str = Field(..., description="Category of the publication")


#-----------------------------------------------------------------------------------------------------------


# # Education Model
# list_universites = [
#     Education(name="Hanoi University of Science and Technology", field="Technology"),
#     Education(name="University of Social Sciences and Humanities, Vietnam National University Hanoi", field="Social Sciences"),
#     Education(name="University of Languages and International Studies, Vietnam National University Hanoi", field="Language"),
#     Education(name="Ho Chi Minh City University of Technology", field="Technology"),
#     Education(name="Foreign Trade University", field="Economics"),
#     Education(name="University of Danang - University of Science and Technology", field="Technology"),
#     Education(name="Hanoi University", field="Language"),
#     Education(name="Ho Chi Minh City University of Social Sciences and Humanities", field="Social Sciences"),
#     Education(name="Ho Chi Minh City University of Foreign Languages and Information Technology", field="Language"),
#     Education(name="Ton Duc Thang University", field="Technology"),
#     Education(name="FPT University", field="Technology"),
#     Education(name="University of Economics Ho Chi Minh City", field="Economics"),
#     Education(name="Hue University of Foreign Languages", field="Language"),
#     Education(name="Vietnam Maritime University", field="Technology"),
#     Education(name="Can Tho University", field="Agriculture"),
#     Education(name="University of Information Technology, Vietnam National University Ho Chi Minh City", field="Technology"),
#     Education(name="Thuy Loi University", field="Water Resources Engineering"),
#     Education(name="Ho Chi Minh City University of Economics and Law", field="Economics, Law"),
#     Education(name="Hanoi University of Mining and Geology", field="Technology, Natural Resources"),
#     Education(name="University of Danang - University of Economics", field="Economics"),
#     Education(name="University of Foreign Language Studies, University of Danang", field="Language"),
#     Education(name="Posts and Telecommunications Institute of Technology", field="Technology"),
#     Education(name="Ho Chi Minh City University of Transport", field="Technology"),
#     Education(name="Hanoi University of Industry", field="Technology, Economics"),
#     Education(name="Hanoi University of Agriculture", field="Agriculture"),
#     Education(name="Banking University of Ho Chi Minh City", field="Economics, Banking"),
#     Education(name="Hanoi Medical University", field="Healthcare"),
#     Education(name="University of Medicine and Pharmacy at Ho Chi Minh City", field="Healthcare"),
#     Education(name="National Economics University", field="Economics"),
#     Education(name="Ho Chi Minh City Open University", field="Economics, Social Sciences, Technology"),
#     Education(name="Others University", field="others")
# ]


# list_workplaces = [
#     WorkPlace(name="Viettel Group", domain_expertise="Telecommunications", size="Large"),
#     WorkPlace(name="VinGroup", domain_expertise="Conglomerate", size="Large"),
#     WorkPlace(name="FPT Corporation", domain_expertise="Technology", size="Large"),
#     WorkPlace(name="FPT Software", domain_expertise="Technology", size="Large"),
#     WorkPlace(name="Bosch Global Software Technologies", domain_expertise="Technology", size="Large"),
#     WorkPlace(name="Masan Group", domain_expertise="Consumer Goods", size="Large"),
#     WorkPlace(name="Techcombank", domain_expertise="Banking", size="Large"),
#     WorkPlace(name="VinaPhone", domain_expertise="Telecommunications", size="Large"),
#     WorkPlace(name="PetroVietnam", domain_expertise="Energy", size="Large"),
#     WorkPlace(name="Vietnam Airlines", domain_expertise="Aviation", size="Large"),
#     WorkPlace(name="Saigon Newport Corporation", domain_expertise="Logistics", size="Large"),
#     WorkPlace(name="Vietcombank", domain_expertise="Banking", size="Large"),
#     WorkPlace(name="VNPT", domain_expertise="Telecommunications", size="Large"),
#     WorkPlace(name="Hoang Anh Gia Lai Group", domain_expertise="Real Estate", size="Large"),
#     WorkPlace(name="Vinamilk", domain_expertise="Dairy", size="Large"),
#     WorkPlace(name="BIDV", domain_expertise="Banking", size="Large"),
#     WorkPlace(name="Tiki", domain_expertise="E-commerce", size="Medium"),
#     WorkPlace(name="Shopee Vietnam", domain_expertise="E-commerce", size="Large"),
#     WorkPlace(name="The Gioi Di Dong", domain_expertise="Retail", size="Large"),
#     WorkPlace(name="Grab Vietnam", domain_expertise="Ride-hailing", size="Large"),
#     WorkPlace(name="Công ty Cổ phần Bán lẻ Kỹ thuật số FPT", domain_expertise="Retail", size="Large"),
#     WorkPlace(name="VNG Corporation", domain_expertise="Technology", size="Large"),
#     WorkPlace(name="Vietnam Posts and Telecommunications Group", domain_expertise="Telecommunications", size="Large"),
#     WorkPlace(name="Thaco Group", domain_expertise="Automobile", size="Large"),
#     WorkPlace(name="Hoa Phat Group", domain_expertise="Steel Manufacturing", size="Large"),
#     WorkPlace(name="TH True Milk", domain_expertise="Dairy", size="Medium"),
#     WorkPlace(name="PepsiCo Vietnam", domain_expertise="Beverages", size="Large"),
#     WorkPlace(name="Nestlé Vietnam", domain_expertise="Food and Beverage", size="Large"),
#     WorkPlace(name="Unilever Vietnam", domain_expertise="Consumer Goods", size="Large"),
#     WorkPlace(name="Samsung Vietnam", domain_expertise="Electronics", size="Large"),
#     WorkPlace(name="Intel Products Vietnam", domain_expertise="Technology", size="Large"),
#     WorkPlace(name="Deloitte Vietnam", domain_expertise="Consulting", size="Large"),
#     WorkPlace(name="PwC Vietnam", domain_expertise="Consulting", size="Large"),
#     WorkPlace(name="EY Vietnam", domain_expertise="Consulting", size="Large"),
#     WorkPlace(name="KPMG Vietnam", domain_expertise="Consulting", size="Large"),
#     WorkPlace(name="VietinBank", domain_expertise="Banking", size="Large"),
#     WorkPlace(name="MB Bank", domain_expertise="Banking", size="Large"),
#     WorkPlace(name="SSI Securities Corporation", domain_expertise="Finance", size="Medium"),
#     WorkPlace(name="Bao Viet Holdings", domain_expertise="Insurance", size="Large"),
#     WorkPlace(name="VinFast", domain_expertise="Automobile", size="Large"),
#     WorkPlace(name="Bitexco Group", domain_expertise="Real Estate", size="Large"),
#     WorkPlace(name="SABECO", domain_expertise="Beverages", size="Large"),
#     WorkPlace(name="Habeco", domain_expertise="Beverages", size="Large"),
#     WorkPlace(name="Coca-Cola Vietnam", domain_expertise="Beverages", size="Large"),
#     WorkPlace(name="Pfizer Vietnam", domain_expertise="Pharmaceutical", size="Large"),
#     WorkPlace(name="Abbott Laboratories Vietnam", domain_expertise="Pharmaceutical", size="Large"),
#     WorkPlace(name="Vietravel", domain_expertise="Tourism", size="Medium"),
#     WorkPlace(name="VinaCapital", domain_expertise="Finance", size="Medium"),
#     WorkPlace(name="Techno Park", domain_expertise="Technology", size="Medium"),
#     WorkPlace(name="Decathlon Vietnam", domain_expertise="Retail", size="Large"),
#     WorkPlace(name="Lotte Mart Vietnam", domain_expertise="Retail", size="Large"),
#     WorkPlace(name="Aeon Vietnam", domain_expertise="Retail", size="Large"),
#     WorkPlace(name="Big C Vietnam", domain_expertise="Retail", size="Large"),
#     WorkPlace(name="Metro Cash & Carry Vietnam", domain_expertise="Retail", size="Large"),
#     WorkPlace(name="Zalo", domain_expertise="Technology", size="Large"),
#     WorkPlace(name="Vietnam Esports", domain_expertise="Entertainment", size="Medium"),
#     WorkPlace(name="Momo", domain_expertise="Fintech", size="Large"),
#     WorkPlace(name="Sea Group Vietnam", domain_expertise="Technology", size="Large"),
#     WorkPlace(name="Lazada Vietnam", domain_expertise="E-commerce", size="Large"),
#     WorkPlace(name="FLC Group", domain_expertise="Real Estate", size="Large"),
#     WorkPlace(name="Sun Group", domain_expertise="Real Estate", size="Large"),
#     WorkPlace(name="Công ty Cổ phần Cơ điện lạnh REE", domain_expertise="Engineering", size="Large"),
#     WorkPlace(name="Viettel Post", domain_expertise="Logistics", size="Large"),
#     WorkPlace(name="Bach Hoa Xanh", domain_expertise="Retail", size="Large"),
#     WorkPlace(name="VPBank", domain_expertise="Banking", size="Large"),
#     WorkPlace(name="Vinaconex", domain_expertise="Construction", size="Large"),
#     WorkPlace(name="Sovico Group", domain_expertise="Finance", size="Large"),
#     WorkPlace(name="VIB Bank", domain_expertise="Banking", size="Large"),
#     WorkPlace(name="Vietnam Electricity (EVN)", domain_expertise="Energy", size="Large"),
#     WorkPlace(name="Doji Group", domain_expertise="Jewelry", size="Medium"),
#     WorkPlace(name="PNJ", domain_expertise="Jewelry", size="Large"),
#     WorkPlace(name="Dat Xanh Group", domain_expertise="Real Estate", size="Large"),
#     WorkPlace(name="Novaland", domain_expertise="Real Estate", size="Large"),
#     WorkPlace(name="KIDO Group", domain_expertise="Food and Beverage", size="Medium"),
#     WorkPlace(name="Vietnam Oil and Gas Group", domain_expertise="Energy", size="Large"),
#     WorkPlace(name="Vietsovpetro", domain_expertise="Oil and Gas", size="Large"),
#     WorkPlace(name="Saigon Co.op", domain_expertise="Retail", size="Large"),
#     WorkPlace(name="Kim Oanh Real Estate", domain_expertise="Real Estate", size="Medium"),
#     WorkPlace(name="TNR Holdings Vietnam", domain_expertise="Real Estate", size="Medium"),
#     WorkPlace(name="An Phat Holdings", domain_expertise="Plastic Manufacturing", size="Medium"),
#     WorkPlace(name="Sun Life Vietnam", domain_expertise="Insurance", size="Medium"),
#     WorkPlace(name="Manulife Vietnam", domain_expertise="Insurance", size="Large"),
#     WorkPlace(name="Prudential Vietnam", domain_expertise="Insurance", size="Large"),
#     WorkPlace(name="AIA Vietnam", domain_expertise="Insurance", size="Large"),
#     WorkPlace(name="PVcomBank", domain_expertise="Banking", size="Medium"),
#     WorkPlace(name="SCB Bank", domain_expertise="Banking", size="Medium"),
#     WorkPlace(name="Dong A Bank", domain_expertise="Banking", size="Medium"),
#     WorkPlace(name="Eximbank", domain_expertise="Banking", size="Medium"),
#     WorkPlace(name="OCB", domain_expertise="Banking", size="Medium"),
#     WorkPlace(name="TPBank", domain_expertise="Banking", size="Medium"),
#     WorkPlace(name="Viet A Bank", domain_expertise="Banking", size="Medium"),
#     WorkPlace(name="LienVietPostBank", domain_expertise="Banking", size="Large"),
#     WorkPlace(name="Others Company", domain_expertise="others", size="others")
# ]


list_degrees=[
    Degree(category='High School Diploma'),
    Degree(category='Associate Degree'),
    Degree(category='Bachelor Degree'),
    Degree(category='Master Degree'),
    Degree(category='Doctorate'),
]

list_positions = [
    Position(name="AI Engineer"),
    Position(name="Software Engineer"),
    Position(name="Data Scientist"),
    Position(name="DevOps"),
    Position(name="Project Lead"),
    Position(name="Marketing"),
    Position(name="Human Resources"),
    Position(name="Financial Officer"),
    Position(name="Graphic Designer"),
    Position(name="Sales"),
    Position(name="Operations"),
    Position(name="Customer Support"),
    Position(name="Business Analyst"),
    Position(name="Accountant"),
    Position(name="Mechanical Engineer"),
    Position(name="Product Developer"),
    Position(name="IT Support"),
    Position(name="Supply Chain"),
    Position(name="Legal Advisor"),
    Position(name="Environmental Engineer"),
    Position(name="Medical Doctor"),
    Position(name="UX Designer"),
    Position(name="Electrical Engineer"),
    Position(name="Logistics Coordinator"),
    Position(name="Web Developer"),
    Position(name="Clinical Researcher"),
    Position(name="Content Writer"),
    Position(name="Data Analyst"),
    Position(name="Public Relations"),
    Position(name="System Administrator"),
    Position(name="Architect"),
    Position(name="Civil Engineer"),
    Position(name="Health and Safety"),
    Position(name="Graphic Illustrator"),
    Position(name="Food Scientist"),
    Position(name="Biotechnologist"),
    Position(name="Software Tester"),
    Position(name="Economist"),
    Position(name="Cybersecurity Analyst"),
    Position(name="Pharmacist"),
    Position(name="Chemist"),
    Position(name="Construction Worker"),
    Position(name="Tour Guide"),
    Position(name="Fitness Instructor"),
    Position(name="Nutritionist"),
    Position(name="Research Scientist"),
    Position(name="Fashion Designer"),
    Position(name="Interior Designer"),
    Position(name="Real Estate Agent"),
    Position(name="Copywriter"),
    Position(name="Other Positions")
]



list_skills = [
    Skills(name="Java", category="Technology"),
    Skills(name="Python", category="Technology"),
    Skills(name="JavaScript", category="Technology"),
    Skills(name="C++", category="Technology"),
    Skills(name="Ruby", category="Technology"),
    Skills(name="SQL", category="Technology"),
    Skills(name="Git", category="Technology"),
    Skills(name="Docker", category="Technology"),
    Skills(name="Kubernetes", category="Technology"),
    Skills(name="Machine Learning", category="Technology"),
    Skills(name="Data Analysis", category="Technology"),
    Skills(name="Cloud Computing", category="Technology"),
    Skills(name="HTML", category="Technology"),
    Skills(name="CSS", category="Technology"),
    Skills(name="React", category="Technology"),
    Skills(name="Node.js", category="Technology"),
    Skills(name="Agile Methodologies", category="Project Management"),
    Skills(name="Scrum", category="Project Management"),
    Skills(name="Kanban", category="Project Management"),
    Skills(name="Leadership", category="Business"),
    Skills(name="Communication", category="Business"),
    Skills(name="Teamwork", category="Business"),
    Skills(name="Critical Thinking", category="Business"),
    Skills(name="Problem Solving", category="Business"),
    Skills(name="Negotiation", category="Business"),
    Skills(name="Financial Analysis", category="Finance"),
    Skills(name="Market Research", category="Marketing"),
    Skills(name="SEO", category="Marketing"),
    Skills(name="Content Marketing", category="Marketing"),
    Skills(name="Social Media Management", category="Marketing"),
    Skills(name="Public Speaking", category="Communication"),
    Skills(name="Emotional Intelligence", category="Soft Skills"),
    Skills(name="Customer Service", category="Business"),
    Skills(name="Time Management", category="Business"),
    Skills(name="Data Visualization", category="Technology"),
    Skills(name="Microsoft Excel", category="Technology"),
    Skills(name="Tableau", category="Technology"),
    Skills(name="Power BI", category="Technology"),
    Skills(name="Project Management Software", category="Project Management"),
    Skills(name="Research Skills", category="Research"),
    Skills(name="Presentation Skills", category="Communication"),
    Skills(name="Networking", category="Business"),
    Skills(name="User Experience Design", category="Design"),
    Skills(name="Graphic Design", category="Design"),
    Skills(name="Video Editing", category="Media Production"),
    Skills(name="Photography", category="Media Production"),
    Skills(name="Content Creation", category="Media Production"),
    Skills(name="Interpersonal Skills", category="Soft Skills"),
    Skills(name="Adaptability", category="Soft Skills"),
    Skills(name="Technical Writing", category="Communication"),
    Skills(name="Regulatory Knowledge", category="Legal"),
    Skills(name="Risk Management", category="Finance"),
    Skills(name="Sales Techniques", category="Sales"),
    Skills(name="Inventory Management", category="Logistics"),
    Skills(name="Supply Chain Management", category="Logistics"),
    Skills(name="Quality Assurance", category="Technology"),
    Skills(name="Research and Development", category="Research"),
    Skills(name="Crisis Management", category="Business"),
    Skills(name="Coaching", category="Soft Skills"),
    Skills(name="Strategic Planning", category="Business"),
    Skills(name="Community Engagement", category="Social Work"),
    Skills(name="Nutritional Counseling", category="Health"),
    Skills(name="Environmental Compliance", category="Environmental"),
    Skills(name="Urban Planning", category="Planning"),
    Skills(name="Language Proficiency", category="Communication"),
    Skills(name="Digital Marketing", category="Marketing"),
    Skills(name="Client Relationship Management", category="Business"),
    Skills(name="Trade Knowledge", category="Finance"),
    Skills(name="Health and Safety Regulations", category="Safety"),
    Skills(name="Technical Support", category="IT Support"),
    Skills(name="Behavioral Analysis", category="Psychology"),
    Skills(name="Artificial Intelligence", category="Technology"),
    Skills(name="Cloud Security", category="Technology"),
    Skills(name="Networking Protocols", category="Technology"),
    Skills(name="Database Management", category="Technology"),
    Skills(name="Agile Coaching", category="Project Management"),
    Skills(name="Time Series Analysis", category="Data Science"),
    Skills(name="Blockchain Technology", category="Technology"),
    Skills(name="User Research", category="Design"),
    Skills(name="Usability Testing", category="Design"),
    Skills(name="Change Management", category="Business"),
    Skills(name="Negotiation Tactics", category="Business"),
    Skills(name="Forensic Accounting", category="Finance"),
    Skills(name="Cryptography", category="Technology"),
    Skills(name="Social Work Ethics", category="Social Work"),
    Skills(name="Conflict Resolution", category="Soft Skills"),
    Skills(name="Cross-Cultural Communication", category="Communication"),
    Skills(name="Sales Forecasting", category="Sales"),
    Skills(name="Lead Generation", category="Sales"),
    Skills(name="Technical SEO", category="Marketing"),
    Skills(name="Content Strategy", category="Marketing"),
    Skills(name="User Interface Design", category="Design"),
    Skills(name="Health Policy Analysis", category="Health"),
    Skills(name="Laboratory Techniques", category="Science"),
    Skills(name="Regulatory Affairs", category="Legal"),
    Skills(name="Mental Health Counseling", category="Health"),
    Skills(name="Pharmaceutical Knowledge", category="Health"),
    Skills(name="Event Coordination", category="Event Management"),
    Skills(name="Sustainability Practices", category="Environmental"),
    Skills(name="Cultural Competency", category="Social Work"),
    Skills(name="Instructional Design", category="Education"),
    Skills(name="Software Development Life Cycle", category="Technology"),
    Skills(name="Data Mining", category="Data Science"),
    Skills(name="Simulation Modeling", category="Engineering"),
    Skills(name="Graph Theory", category="Mathematics"),
    Skills(name="Test Automation", category="Technology"),
    Skills(name="Localization", category="Translation"),
    Skills(name="Risk Assessment", category="Finance"),
    Skills(name="Quantitative Analysis", category="Finance"),
    Skills(name="Inventory Control", category="Logistics"),
    Skills(name="Construction Management", category="Engineering"),
    Skills(name="Strategic Sourcing", category="Supply Chain"),
    Skills(name="Ethical Hacking", category="Cybersecurity"),
    Skills(name="Mobile App Development", category="Technology"),
    Skills(name="Content Management Systems", category="Technology"),
    Skills(name="Other Skills", category="Others")
]


list_certifications = [
    Certification(category="Information Technology"),
    Certification(category="Data Science"),
    Certification(category="Cybersecurity"),
    Certification(category="Project Management"),
    Certification(category="Cloud Computing"),
    Certification(category="Software Development"),
    Certification(category="Artificial Intelligence"),
    Certification(category="Business Analysis"),
    Certification(category="Finance"),
    Certification(category="Marketing"),
    Certification(category="Human Resources"),
    Certification(category="Supply Chain Management"),
    Certification(category="Healthcare"),
    Certification(category="Environmental Management"),
    Certification(category="Quality Management"),
    Certification(category="Education and Training"),
    Certification(category="Digital Marketing"),
    Certification(category="Change Management"),
    Certification(category="Operations Management"),
    Certification(category="Social Work"),
    Certification(category="Graphic Design"),
    Certification(category="Real Estate"),
    Certification(category="Sales"),
    Certification(category="Content Creation"),
    Certification(category="Personal Development"),
    Certification(category="Logistics and Transportation"),
    Certification(category="Risk Management"),
    Certification(category="Event Management"),
    Certification(category="Travel and Tourism"),
    Certification(category="Construction Management"),
    Certification(category="Telecommunications"),
    Certification(category="Behavioral Health"),
]


list_publications = [
    Publication(category="Information Technology"),
    Publication(category="Data Science"),
    Publication(category="Cybersecurity"),
    Publication(category="Project Management"),
    Publication(category="Cloud Computing"),
    Publication(category="Software Development"),
    Publication(category="Artificial Intelligence"),
    Publication(category="Business Analysis"),
    Publication(category="Finance"),
    Publication(category="Marketing"),
    Publication(category="Human Resources"),
    Publication(category="Supply Chain Management"),
    Publication(category="Healthcare"),
    Publication(category="Environmental Management"),
    Publication(category="Quality Management"),
    Publication(category="Education and Training"),
    Publication(category="Digital Marketing"),
    Publication(category="Change Management"),
    Publication(category="Operations Management"),
    Publication(category="Social Work"),
    Publication(category="Graphic Design"),
    Publication(category="Real Estate"),
    Publication(category="Sales"),
    Publication(category="Content Creation"),
    Publication(category="Personal Development"),
    Publication(category="Logistics and Transportation"),
    Publication(category="Risk Management"),
    Publication(category="Event Management"),
    Publication(category="Travel and Tourism"),
    Publication(category="Construction Management"),
    Publication(category="Telecommunications"),
    Publication(category="Behavioral Health"),
]

def create_enum_from_objects(object_list, enum_name):
    # Get the first attribute name from the first object
    first_attribute = list(object_list[0].__dict__.keys())[0]

    unique_values = {getattr(obj, first_attribute) for obj in object_list}

    # return Enum(enum_name, { value.upper().replace(' ','_'): value for value in unique_values})
    return Enum(enum_name, { str(uuid.uuid5(uuid.NAMESPACE_DNS, value)): value for value in unique_values})

PositionName = create_enum_from_objects(list_positions, enum_name='PositionName')
DegreeCategory = create_enum_from_objects(list_degrees, enum_name='DegreeCategory')
SkillName = create_enum_from_objects(list_skills, enum_name='SkillName')
CertificationCategory = create_enum_from_objects(list_certifications, enum_name='CertificationCategory')
PublicationCategory = create_enum_from_objects(list_publications, enum_name='PublicationCategory')
