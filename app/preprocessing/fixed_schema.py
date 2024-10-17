from pydantic import BaseModel, Field
from enum import Enum
from typing import List, Optional


'''
******************************
----CLASS FOR FIXED SCHEMA----
#*****************************
'''


# Education Model
class Education(BaseModel):
    name: str = Field(..., description="Name of the education institution")
    field: str = Field(..., description="Field of study")

# WorkPlace Model
class WorkPlace(BaseModel):
    name: str = Field(..., description="Name of the workplace")
    domain_expertise: str = Field(..., description="Domain expertise of the workplace")
    size: Optional[str] = Field(description="Size of the workplace")

# Position Model
class Position(BaseModel):
    name: str = Field(..., description="Name of the position")
    description: str = Field(..., description="Description of the position")

# Skills Model
class Skills(BaseModel):
    name: str = Field(..., description="Name of the skill")
    category: str = Field(..., description="Category of the skill")

class Certification(BaseModel):
    category: str = Field(..., description="Category of the certification")

# Publication Model
class Publication(BaseModel):
    category: str = Field(..., description="Category of the publication")


#-----------------------------------------------------------------------------------------------------------


# Education Model
list_universites = [
    Education(name="Hanoi University of Science and Technology", field="Technology"),
    Education(name="University of Social Sciences and Humanities, Vietnam National University Hanoi", field="Social Sciences"),
    Education(name="University of Languages and International Studies, Vietnam National University Hanoi", field="Language"),
    Education(name="Ho Chi Minh City University of Technology", field="Technology"),
    Education(name="Foreign Trade University", field="Economics"),
    Education(name="University of Danang - University of Science and Technology", field="Technology"),
    Education(name="Hanoi University", field="Language"),
    Education(name="Ho Chi Minh City University of Social Sciences and Humanities", field="Social Sciences"),
    Education(name="Ho Chi Minh City University of Foreign Languages and Information Technology", field="Language"),
    Education(name="Ton Duc Thang University", field="Technology"),
    Education(name="FPT University", field="Technology"),
    Education(name="University of Economics Ho Chi Minh City", field="Economics"),
    Education(name="Hue University of Foreign Languages", field="Language"),
    Education(name="Vietnam Maritime University", field="Technology"),
    Education(name="Can Tho University", field="Agriculture"),
    Education(name="University of Information Technology, Vietnam National University Ho Chi Minh City", field="Technology"),
    Education(name="Thuy Loi University", field="Water Resources Engineering"),
    Education(name="Ho Chi Minh City University of Economics and Law", field="Economics, Law"),
    Education(name="Hanoi University of Mining and Geology", field="Technology, Natural Resources"),
    Education(name="University of Danang - University of Economics", field="Economics"),
    Education(name="University of Foreign Language Studies, University of Danang", field="Language"),
    Education(name="Posts and Telecommunications Institute of Technology", field="Technology"),
    Education(name="Ho Chi Minh City University of Transport", field="Technology"),
    Education(name="Hanoi University of Industry", field="Technology, Economics"),
    Education(name="Hanoi University of Agriculture", field="Agriculture"),
    Education(name="Banking University of Ho Chi Minh City", field="Economics, Banking"),
    Education(name="Hanoi Medical University", field="Healthcare"),
    Education(name="University of Medicine and Pharmacy at Ho Chi Minh City", field="Healthcare"),
    Education(name="National Economics University", field="Economics"),
    Education(name="Ho Chi Minh City Open University", field="Economics, Social Sciences, Technology"),
    Education(name="Others University", field="others")
]


list_workplaces = [
    WorkPlace(name="Viettel Group", domain_expertise="Telecommunications", size="Large"),
    WorkPlace(name="VinGroup", domain_expertise="Conglomerate", size="Large"),
    WorkPlace(name="FPT Corporation", domain_expertise="Technology", size="Large"),
    WorkPlace(name="FPT Software", domain_expertise="Technology", size="Large"),
    WorkPlace(name="Bosch Global Software Technologies", domain_expertise="Technology", size="Large"),
    WorkPlace(name="Masan Group", domain_expertise="Consumer Goods", size="Large"),
    WorkPlace(name="Techcombank", domain_expertise="Banking", size="Large"),
    WorkPlace(name="VinaPhone", domain_expertise="Telecommunications", size="Large"),
    WorkPlace(name="PetroVietnam", domain_expertise="Energy", size="Large"),
    WorkPlace(name="Vietnam Airlines", domain_expertise="Aviation", size="Large"),
    WorkPlace(name="Saigon Newport Corporation", domain_expertise="Logistics", size="Large"),
    WorkPlace(name="Vietcombank", domain_expertise="Banking", size="Large"),
    WorkPlace(name="VNPT", domain_expertise="Telecommunications", size="Large"),
    WorkPlace(name="Hoang Anh Gia Lai Group", domain_expertise="Real Estate", size="Large"),
    WorkPlace(name="Vinamilk", domain_expertise="Dairy", size="Large"),
    WorkPlace(name="BIDV", domain_expertise="Banking", size="Large"),
    WorkPlace(name="Tiki", domain_expertise="E-commerce", size="Medium"),
    WorkPlace(name="Shopee Vietnam", domain_expertise="E-commerce", size="Large"),
    WorkPlace(name="The Gioi Di Dong", domain_expertise="Retail", size="Large"),
    WorkPlace(name="Grab Vietnam", domain_expertise="Ride-hailing", size="Large"),
    WorkPlace(name="Công ty Cổ phần Bán lẻ Kỹ thuật số FPT", domain_expertise="Retail", size="Large"),
    WorkPlace(name="VNG Corporation", domain_expertise="Technology", size="Large"),
    WorkPlace(name="Vietnam Posts and Telecommunications Group", domain_expertise="Telecommunications", size="Large"),
    WorkPlace(name="Thaco Group", domain_expertise="Automobile", size="Large"),
    WorkPlace(name="Hoa Phat Group", domain_expertise="Steel Manufacturing", size="Large"),
    WorkPlace(name="TH True Milk", domain_expertise="Dairy", size="Medium"),
    WorkPlace(name="PepsiCo Vietnam", domain_expertise="Beverages", size="Large"),
    WorkPlace(name="Nestlé Vietnam", domain_expertise="Food and Beverage", size="Large"),
    WorkPlace(name="Unilever Vietnam", domain_expertise="Consumer Goods", size="Large"),
    WorkPlace(name="Samsung Vietnam", domain_expertise="Electronics", size="Large"),
    WorkPlace(name="Intel Products Vietnam", domain_expertise="Technology", size="Large"),
    WorkPlace(name="Deloitte Vietnam", domain_expertise="Consulting", size="Large"),
    WorkPlace(name="PwC Vietnam", domain_expertise="Consulting", size="Large"),
    WorkPlace(name="EY Vietnam", domain_expertise="Consulting", size="Large"),
    WorkPlace(name="KPMG Vietnam", domain_expertise="Consulting", size="Large"),
    WorkPlace(name="VietinBank", domain_expertise="Banking", size="Large"),
    WorkPlace(name="MB Bank", domain_expertise="Banking", size="Large"),
    WorkPlace(name="SSI Securities Corporation", domain_expertise="Finance", size="Medium"),
    WorkPlace(name="Bao Viet Holdings", domain_expertise="Insurance", size="Large"),
    WorkPlace(name="VinFast", domain_expertise="Automobile", size="Large"),
    WorkPlace(name="Bitexco Group", domain_expertise="Real Estate", size="Large"),
    WorkPlace(name="SABECO", domain_expertise="Beverages", size="Large"),
    WorkPlace(name="Habeco", domain_expertise="Beverages", size="Large"),
    WorkPlace(name="Coca-Cola Vietnam", domain_expertise="Beverages", size="Large"),
    WorkPlace(name="Pfizer Vietnam", domain_expertise="Pharmaceutical", size="Large"),
    WorkPlace(name="Abbott Laboratories Vietnam", domain_expertise="Pharmaceutical", size="Large"),
    WorkPlace(name="Vietravel", domain_expertise="Tourism", size="Medium"),
    WorkPlace(name="VinaCapital", domain_expertise="Finance", size="Medium"),
    WorkPlace(name="Techno Park", domain_expertise="Technology", size="Medium"),
    WorkPlace(name="Decathlon Vietnam", domain_expertise="Retail", size="Large"),
    WorkPlace(name="Lotte Mart Vietnam", domain_expertise="Retail", size="Large"),
    WorkPlace(name="Aeon Vietnam", domain_expertise="Retail", size="Large"),
    WorkPlace(name="Big C Vietnam", domain_expertise="Retail", size="Large"),
    WorkPlace(name="Metro Cash & Carry Vietnam", domain_expertise="Retail", size="Large"),
    WorkPlace(name="Zalo", domain_expertise="Technology", size="Large"),
    WorkPlace(name="Vietnam Esports", domain_expertise="Entertainment", size="Medium"),
    WorkPlace(name="Momo", domain_expertise="Fintech", size="Large"),
    WorkPlace(name="Sea Group Vietnam", domain_expertise="Technology", size="Large"),
    WorkPlace(name="Lazada Vietnam", domain_expertise="E-commerce", size="Large"),
    WorkPlace(name="FLC Group", domain_expertise="Real Estate", size="Large"),
    WorkPlace(name="Sun Group", domain_expertise="Real Estate", size="Large"),
    WorkPlace(name="Công ty Cổ phần Cơ điện lạnh REE", domain_expertise="Engineering", size="Large"),
    WorkPlace(name="Viettel Post", domain_expertise="Logistics", size="Large"),
    WorkPlace(name="Bach Hoa Xanh", domain_expertise="Retail", size="Large"),
    WorkPlace(name="VPBank", domain_expertise="Banking", size="Large"),
    WorkPlace(name="Vinaconex", domain_expertise="Construction", size="Large"),
    WorkPlace(name="Sovico Group", domain_expertise="Finance", size="Large"),
    WorkPlace(name="VIB Bank", domain_expertise="Banking", size="Large"),
    WorkPlace(name="Vietnam Electricity (EVN)", domain_expertise="Energy", size="Large"),
    WorkPlace(name="Doji Group", domain_expertise="Jewelry", size="Medium"),
    WorkPlace(name="PNJ", domain_expertise="Jewelry", size="Large"),
    WorkPlace(name="Dat Xanh Group", domain_expertise="Real Estate", size="Large"),
    WorkPlace(name="Novaland", domain_expertise="Real Estate", size="Large"),
    WorkPlace(name="KIDO Group", domain_expertise="Food and Beverage", size="Medium"),
    WorkPlace(name="Vietnam Oil and Gas Group", domain_expertise="Energy", size="Large"),
    WorkPlace(name="Vietsovpetro", domain_expertise="Oil and Gas", size="Large"),
    WorkPlace(name="Saigon Co.op", domain_expertise="Retail", size="Large"),
    WorkPlace(name="Kim Oanh Real Estate", domain_expertise="Real Estate", size="Medium"),
    WorkPlace(name="TNR Holdings Vietnam", domain_expertise="Real Estate", size="Medium"),
    WorkPlace(name="An Phat Holdings", domain_expertise="Plastic Manufacturing", size="Medium"),
    WorkPlace(name="Sun Life Vietnam", domain_expertise="Insurance", size="Medium"),
    WorkPlace(name="Manulife Vietnam", domain_expertise="Insurance", size="Large"),
    WorkPlace(name="Prudential Vietnam", domain_expertise="Insurance", size="Large"),
    WorkPlace(name="AIA Vietnam", domain_expertise="Insurance", size="Large"),
    WorkPlace(name="PVcomBank", domain_expertise="Banking", size="Medium"),
    WorkPlace(name="SCB Bank", domain_expertise="Banking", size="Medium"),
    WorkPlace(name="Dong A Bank", domain_expertise="Banking", size="Medium"),
    WorkPlace(name="Eximbank", domain_expertise="Banking", size="Medium"),
    WorkPlace(name="OCB", domain_expertise="Banking", size="Medium"),
    WorkPlace(name="TPBank", domain_expertise="Banking", size="Medium"),
    WorkPlace(name="Viet A Bank", domain_expertise="Banking", size="Medium"),
    WorkPlace(name="LienVietPostBank", domain_expertise="Banking", size="Large"),
    WorkPlace(name="Others Company", domain_expertise="others", size="others")
]


list_positions = [
    Position(name="AI Engineer", description="Creating algorithms, building advanced data processing techniques, and improving the robustness and performance of AI systems"),
    Position(name="Software Engineer", description="Develops and maintains software applications for various platforms."),
    Position(name="Data Scientist", description="Analyzes and interprets complex data to help organizations make informed decisions."),
    Position(name="Project Lead", description="Oversees project planning, execution, and completion, ensuring it meets objectives and timelines."),
    Position(name="Marketing Specialist", description="Develops strategies to promote products and services, driving brand awareness and sales."),
    Position(name="Human Resources Specialist", description="Handles recruitment, employee relations, and employee development strategies."),
    Position(name="Financial Officer", description="Oversees financial planning, risk management, and reporting for the organization."),
    Position(name="Graphic Designer", description="Creates visual content for branding, marketing, and user interface designs."),
    Position(name="Sales Representative", description="Responsible for selling products or services and building client relationships."),
    Position(name="Operations Lead", description="Ensures smooth daily operations and manages resources to optimize productivity."),
    Position(name="Customer Support Specialist", description="Assists customers by addressing their issues and providing information about products and services."),
    Position(name="Business Analyst", description="Analyzes business processes and systems, recommending improvements to enhance efficiency."),
    Position(name="Accountant", description="Handles financial records, tax filing, and prepares financial reports for the company."),
    Position(name="Mechanical Engineer", description="Designs and develops mechanical systems, machines, and tools for various industries."),
    Position(name="Product Developer", description="Leads product development from conception to launch, ensuring it meets market needs."),
    Position(name="IT Support Specialist", description="Provides technical assistance and support to employees or clients facing IT issues."),
    Position(name="Supply Chain Specialist", description="Manages the logistics, procurement, and distribution of goods within a supply chain."),
    Position(name="Legal Advisor", description="Provides legal advice and support to ensure the company's activities comply with the law."),
    Position(name="Environmental Engineer", description="Designs projects and implements solutions to reduce environmental impact."),
    Position(name="Medical Doctor", description="Provides medical diagnosis, treatment, and care for patients."),
    Position(name="UX Designer", description="Designs intuitive user experiences for digital products, ensuring ease of use."),
    Position(name="Electrical Engineer", description="Develops electrical systems and ensures their safety and efficiency."),
    Position(name="Human Resources Consultant", description="Advises on HR policies, talent management, and organizational structure."),
    Position(name="Logistics Coordinator", description="Organizes the storage and distribution of goods to ensure timely delivery."),
    Position(name="Web Developer", description="Builds and maintains websites, ensuring functionality and performance."),
    Position(name="Marketing Analyst", description="Analyzes market trends and data to help improve marketing strategies."),
    Position(name="Clinical Researcher", description="Conducts studies and trials to test the effectiveness of medical treatments."),
    Position(name="Content Writer", description="Writes and edits content for websites, blogs, marketing materials, and more."),
    Position(name="Data Analyst", description="Interprets data to help organizations make better business decisions."),
    Position(name="Public Relations Specialist", description="Manages communication between the company and the public."),
    Position(name="System Administrator", description="Manages and maintains an organization's IT infrastructure and systems."),
    Position(name="Architect", description="Designs buildings and structures, ensuring they are functional and aesthetically pleasing."),
    Position(name="Civil Engineer", description="Plans and oversees construction projects, ensuring structural integrity and safety."),
    Position(name="Health and Safety Specialist", description="Ensures workplace environments comply with health and safety regulations."),
    Position(name="Graphic Illustrator", description="Creates original illustrations for various projects, from marketing to entertainment."),
    Position(name="Food Scientist", description="Develops and improves food products and ensures their safety and quality."),
    Position(name="Biotechnologist", description="Applies biological processes to develop products for agriculture, medicine, and the environment."),
    Position(name="Software Tester", description="Tests software applications to ensure they are free of defects and meet requirements."),
    Position(name="Economist", description="Studies economic trends and advises on policies or strategies based on economic data."),
    Position(name="Photographer", description="Captures professional images for various purposes such as marketing, media, or art."),
    Position(name="Translator", description="Converts written or spoken material from one language to another."),
    Position(name="Urban Planner", description="Develops plans and programs for land use in urban areas to ensure sustainable growth."),
    Position(name="Cybersecurity Analyst", description="Protects an organization's IT systems and data from cyber threats."),
    Position(name="Pharmacist", description="Dispenses medications and advises on their proper use."),
    Position(name="Chemist", description="Conducts experiments and research to develop new chemicals or improve products."),
    Position(name="Construction Worker", description="Performs tasks on construction sites such as building, repairing, and installing structures."),
    Position(name="Videographer", description="Produces and edits video content for marketing, entertainment, or education."),
    Position(name="Tour Guide", description="Leads and educates visitors about the history, culture, or nature of a destination."),
    Position(name="Fitness Instructor", description="Provides fitness training and wellness guidance to clients or groups."),
    Position(name="Pilot", description="Operates aircraft for commercial, private, or cargo flights."),
    Position(name="Event Planner", description="Organizes and coordinates events such as conferences, weddings, and parties."),
    Position(name="Social Worker", description="Provides support and assistance to individuals or groups in need of social services."),
    Position(name="Nutritionist", description="Advises individuals or organizations on proper nutrition and healthy eating habits."),
    Position(name="Research Scientist", description="Conducts scientific studies to discover new information or develop new products."),
    Position(name="Fashion Designer", description="Creates clothing and accessory designs for consumers or fashion shows."),
    Position(name="Interior Designer", description="Designs indoor spaces to improve aesthetics, functionality, and comfort."),
    Position(name="Real Estate Agent", description="Assists clients in buying, selling, or renting properties."),
    Position(name="Copywriter", description="Writes persuasive text for advertising, marketing materials, and websites."),
    Position(name="Position Others", description="others")
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
    Skills(name="Skill Others", category="others")
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
    Certification(category="Legal Studies"),
    Certification(category="Quality Management"),
    Certification(category="Education and Training"),
    Certification(category="Digital Marketing"),
    Certification(category="Change Management"),
    Certification(category="Operations Management"),
    Certification(category="Social Work"),
    Certification(category="Graphic Design"),
    Certification(category="Public Relations"),
    Certification(category="Communication"),
    Certification(category="Entrepreneurship"),
    Certification(category="Real Estate"),
    Certification(category="Retail Management"),
    Certification(category="Sales"),
    Certification(category="E-commerce"),
    Certification(category="Content Creation"),
    Certification(category="Personal Development"),
    Certification(category="Logistics and Transportation"),
    Certification(category="Food Safety"),
    Certification(category="Risk Management"),
    Certification(category="Event Management"),
    Certification(category="Travel and Tourism"),
    Certification(category="Fashion and Design"),
    Certification(category="Construction Management"),
    Certification(category="Nonprofit Management"),
    Certification(category="Artificial Intelligence Ethics"),
    Certification(category="Telecommunications"),
    Certification(category="Behavioral Health"),
    Certification(category="Certification Others")
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
    Publication(category="Legal Studies"),
    Publication(category="Quality Management"),
    Publication(category="Education and Training"),
    Publication(category="Digital Marketing"),
    Publication(category="Change Management"),
    Publication(category="Operations Management"),
    Publication(category="Social Work"),
    Publication(category="Graphic Design"),
    Publication(category="Public Relations"),
    Publication(category="Communication"),
    Publication(category="Entrepreneurship"),
    Publication(category="Real Estate"),
    Publication(category="Retail Management"),
    Publication(category="Sales"),
    Publication(category="E-commerce"),
    Publication(category="Content Creation"),
    Publication(category="Personal Development"),
    Publication(category="Logistics and Transportation"),
    Publication(category="Food Safety"),
    Publication(category="Risk Management"),
    Publication(category="Event Management"),
    Publication(category="Travel and Tourism"),
    Publication(category="Fashion and Design"),
    Publication(category="Construction Management"),
    Publication(category="Nonprofit Management"),
    Publication(category="Artificial Intelligence Ethics"),
    Publication(category="Telecommunications"),
    Publication(category="Behavioral Health"),
    Publication(category="Publication Others")
]



