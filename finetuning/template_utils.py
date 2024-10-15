from langchain_lamini import System, Human, Assistant, ChatTemplate
from langchain_core.prompts import PromptTemplate

def get_schema() -> str:
    return"""Node properties are the following:
    Person {ID: STRING, name: STRING, phone: STRING, dob: DATE, summary: STRING, location: STRING, portfolio: STRING}
    Publication {CATEGORY: STRING}
    Certification {CATEGORY: STRING}
    Education {NAME: STRING, Field: STRING}
    WorkPlace {NAME: STRING, domain_expertise: STRING, size: STRING}
    Skills {NAME: STRING, category: STRING}
    Position {NAME: STRING, description: STRING}

Relationship properties are the following:
    Achieve {CONFERENCE: STRING, Date: DATE}
    Study_at {DEGREE: STRING, start_year: INT, end_year: INT, grade: STRING, achievement: STRING}
    Worked_at {ID: STRING, duration: INT, role: STRING, start_date: DATE, end_date: DATE, responsibilities: STRING, achievements: STRING}
    Experience {ID: STRING, duration: INT, responsibilities: STRING, achievements: STRING}
    Relevant_to {no properties listed}
    Has {no properties listed}

The relationships are the following:
    (:Person)-[:Achieve]->(:Publication)
    (:Person)-[:Achieve]->(:Certification)
    (:Person)-[:Has]->(:Skills)
    (:Person)-[:Experience]->(:Position)
    (:Person)-[:Worked_at]->(:WorkPlace)
    (:Person)-[:Study_at]->(:Education)
    (:Certification)-[:Relevant_to]->(:Skills)
    (:Position)-[:Relevant_to]->(:Skills)"""


def make_question() -> PromptTemplate:
    template = ChatTemplate([
        System(content="You are an experienced Cypher developer and English-speaking recruiter and a helpful assistant designed to output JSON.\n"
               + "Consider the Neo4j graph database with the following schema:\n"
               + get_schema().replace("{", "{{").replace("}", "}}") + "\n"
               + "Write a Cypher query that would help you answer the following question:\n"),
        Human(content="{question}"),
        Assistant()
    ])
    return template
