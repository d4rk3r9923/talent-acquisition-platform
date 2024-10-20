from langchain_core.prompts import ChatPromptTemplate

def get_schema() -> str:
    return"""// Node Properties
Node Properties are the following:
    Person {ID: STRING, name: STRING, phone: STRING, dob: DATE, summary: STRING, location: STRING, portfolio: STRING}
    Publication {TITLE: STRING, CATEGORY: STRING, conference_name: STRING, date: DATE}
    Certification {NAME: STRING, CATEGORY: STRING}
    Education {UNIVERSITY: STRING, DEGREE: STRING, start_year: INT, end_year: INT, achievement: STRING}
    WorkPlace {NAME: STRING, domain_expertise: STRING, size: STRING}
    Skills {NAME: STRING, category: STRING}
    Position {NAME: STRING, description: STRING}

// Relationship Properties
Relationship Properties are the following:
    Achieve {CONFERENCE: STRING, date: DATE}
    Study_at {DEGREE: STRING, start_year: INT, end_year: INT, achievement: STRING}
    Worked_at {ID: STRING, duration: INT, role: STRING, start_date: DATE, end_date: DATE, responsibilities: STRING, achievements: STRING}
    Experience {ID: STRING, duration: INT, responsibilities: STRING, achievements: STRING}
    Relevant_to {no properties listed}
    Has {no properties listed}

// Relationships
The relationships are the following:
    (:Person)-[:Achieve]->(:Publication)
    (:Person)-[:Achieve]->(:Certification)
    (:Person)-[:Has]->(:Skills)
    (:Person)-[:Experience]->(:Position)
    (:Person)-[:Worked_at]->(:WorkPlace)
    (:Person)-[:Study_at]->(:Education)
    (:Certification)-[:Relevant_to]->(:Skills)
    (:Position)-[:Relevant_to]->(:Skills)
"""


def categories_template() -> ChatPromptTemplate:
    template = ChatPromptTemplate.from_messages([
        ("system","You are an experienced and useful Python and Neo4j/Cypher developer and you are helpful assistant designed to output JSON. "
                  "I have a knowledge graph for which I would like to generate interesting questions that span "
                  "{n_category} categories (or types) about the graph.\n"
                  "Here is the graph schema:\n\n"
                  "{schema}"),
        ("human", "Please suggest {n_category} distinct categories together with their short descriptions and do not contain example. "
                  "The suggested category should encompass different aspects of one node, two or three more nodes, relationships, and paths.")
         ])
    return template


def map_categories_template() -> ChatPromptTemplate:
    template = ChatPromptTemplate.from_messages([
        ("system", "You are an experienced recruiter and you have a knowledge graph for which you would like to generate "
                   "interesting questions of {n_category} categories. Moreover, you are helpful assistant designed to output JSON.\n"
                   "Here are some candidate categories:\n\n"
                   "{categories}."),    
        ("human", "You should merge similar categories (descriptions) and remove the duplicated categories (descriptions). "
                  "Finally, give me a short description of each category.")
    ])
    return template


def generate_QA_template() -> ChatPromptTemplate:
    from langchain.prompts import ChatPromptTemplate

    template = ChatPromptTemplate.from_messages([
        ("system", 
            "You are an experienced Cypher developer and English-speaking recruiter, and a helpful assistant "
            "designed to output JSON."
        ),
        ("human", 
            "Generate {n_pair} questions and their corresponding Cypher statements about the Neo4j graph "
            "database with the following schema:\n\n"
            "{schema}\n\n"
            "The questions should cover {category} and should be phrased in a natural conversational "
            "manner. Make the questions diverse and interesting. Make sure to use the latest Cypher "
            "version and that all the queries are working Cypher queries for the provided graph. You "
            "may add values for the node attributes as needed. Do not add any comments, do not label "
            "or number the questions.\n\n"
            "Here are some examples of the Question-Cypher pairs to be generated:\n\n"
            "\"question\": \"What are all the publications that An has achieved?\"\n"
            "\"cypher\": \"MATCH (p:Person {{name: \"An\"}})-[:Achieve]->(pub:Publication) "
            "RETURN p.name AS PersonName, pub.CATEGORY AS PublicationCategory\"\n\n"
            "\"question\": \"What skills are relevant to Software Engineer?\"\n"
            "\"cypher\": \"MATCH (pos:Position {{NAME: \"Software Engineer\"}})-[:Relevant_to]->(s:Skills) "
            "RETURN pos.NAME AS PositionName, s.NAME AS SkillName, s.category AS SkillCategory\"\n\n"
            "Now it's your turn to generate {n_pair} question and Cypher pairs that are different from the examples."
        )
    ])
    return template
