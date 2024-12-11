import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_core.runnables import Runnable
from loguru import logger

from app.agents.config import AgentState
from langchain_openai import ChatOpenAI

load_dotenv()

class SearchFixedFilter(Runnable):
    def __init__(self, graphdb: GraphDatabase) -> None:
        super().__init__()
        self.graphdb = graphdb
    def _filter_fixed_nodes(self, data: dict) -> str:
        query = "MATCH (p:Person)\n"
        or_clauses = []
        and_clauses = []
        match_weights = []
        matched_filters = []  # To track matched filters

        # OR condition for roles, skills, certification, education_degree, education, and workplace
        if data.get('roles'):
            match_weights.append(
                f"CASE WHEN EXISTS {{ MATCH (p)-[:WORKED_AS]->(pos:Position) WHERE pos.name IN {data['roles']} }} THEN 4 ELSE 0 END"
            )
            matched_filters.append(
                f"CASE WHEN EXISTS {{ MATCH (p)-[:WORKED_AS]->(pos:Position) WHERE pos.name IN {data['roles']} }} THEN 'roles' ELSE NULL END"
            )

        if data.get('skills'):
            match_weights.append(
                f"REDUCE(total = 0, s IN {data['skills']} | total + CASE WHEN EXISTS {{ MATCH (p)-[:HAS]->(skill:Skill) WHERE skill.name = s }} THEN 2 ELSE 0 END)"
            )
            matched_filters.append(
                f"CASE WHEN REDUCE(total = 0, s IN {data['skills']} | total + CASE WHEN EXISTS {{ MATCH (p)-[:HAS]->(skill:Skill) WHERE skill.name = s }} THEN 1 ELSE 0 END) > 0 THEN 'skills' ELSE NULL END"
            )

        if data.get('certification'):
            match_weights.append(
                f"REDUCE(total = 0, s IN {data['certification']} | total + CASE WHEN EXISTS {{ MATCH (p)-[:EARNED]->(c:Certification) WHERE c.name = s }} THEN 1 ELSE 0 END)"
            )
            matched_filters.append(
                f"CASE WHEN REDUCE(total = 0, s IN {data['certification']} | total + CASE WHEN EXISTS {{ MATCH (p)-[:EARNED]->(c:Certification) WHERE c.name = s }} THEN 1 ELSE 0 END) > 0 THEN 'certification' ELSE NULL END"
            )

        if data.get('education_degree'):
            match_weights.append(
                f"CASE WHEN EXISTS {{ MATCH (p)-[:HOLDS]->(d:Degree) WHERE d.name IN {data['education_degree']} }} THEN 2 ELSE 0 END"
            )
            matched_filters.append(
                f"CASE WHEN EXISTS {{ MATCH (p)-[:HOLDS]->(d:Degree) WHERE d.name IN {data['education_degree']} }} THEN 'education_degree' ELSE NULL END"
            )

        if data.get('education_name'):
            edu_keyword = data['education_name'].split()
            edu_conditions = ["edu.name CONTAINS '" + " ".join(edu_keyword) + "'"] + [
                f"edu.name CONTAINS '{kw}'" for kw in edu_keyword
            ]
            match_weights.append(
                f"CASE WHEN EXISTS {{ MATCH (p)-[:STUDIED_AT]->(edu:Education) WHERE {' OR '.join(edu_conditions)} }} THEN 3 ELSE 0 END"
            )
            matched_filters.append(
                f"CASE WHEN EXISTS {{ MATCH (p)-[:STUDIED_AT]->(edu:Education) WHERE {' OR '.join(edu_conditions)} }} THEN 'education_name' ELSE NULL END"
            )

        if data.get('workplace_name'):
            work_keyword = data['workplace_name'].split()
            work_conditions = ["work.name CONTAINS '" + " ".join(work_keyword) + "'"] + [
                f"work.name CONTAINS '{kw}'" for kw in work_keyword
            ]
            match_weights.append(
                f"CASE WHEN EXISTS {{ MATCH (p)-[:WORKED_AT]->(work:Workplace) WHERE {' OR '.join(work_conditions)} }} THEN 3 ELSE 0 END"
            )
            matched_filters.append(
                f"CASE WHEN EXISTS {{ MATCH (p)-[:WORKED_AT]->(work:Workplace) WHERE {' OR '.join(work_conditions)} }} THEN 'workplace_name' ELSE NULL END"
            )

        # AND condition for age and years_of_experience
        if data.get('age'):
            and_clauses.append(
                "p.dob IS NOT NULL "
                "AND p.dob <> '' "
                "AND date(p.dob) IS NOT NULL "
                f"AND date().year - date(p.dob).year {data['age'].strip()}"
            )

        if data.get('years_of_experience'):
            query += (
                "MATCH (p)-[r:WORKED_AS]->()\n"
                "WITH p, sum(r.duration/12.0) AS total_yoe\n"
            )
            and_clauses.append(f"total_yoe {data['years_of_experience'].strip()}")

        # Combine conditions
        combined_clauses = []
        if or_clauses:
            combined_clauses.append("(" + " OR ".join(or_clauses) + ")")
        if and_clauses:
            combined_clauses.append("(" + " AND ".join(and_clauses) + ")")

        if combined_clauses:
            query += "WHERE " + " AND ".join(combined_clauses) + "\n"

        # Add match weights and matched filters for sorting
        match_score = " + ".join(match_weights)
        filter_matches = " + ',' + ".join(filter for filter in matched_filters)
        query += f"WITH p, ({match_score}) AS match_score, [{filter_matches}] AS matched_filters\n"
        query += "ORDER BY match_score DESC\n"
        query += "RETURN p.id AS id, match_score, matched_filters LIMIT 15"

        return query

    # def _filter_fixed_nodes(self, data: dict) -> str:
    #     query = "MATCH (p:Person)\n"
    #     or_clauses = []
    #     and_clauses = []
    #     match_weights = []

    #     # OR condition for roles, skills, certification, education_degree, education, and workplace
    #     if data.get('roles'):
    #         match_weights.append(
    #             f"CASE WHEN EXISTS {{ MATCH (p)-[:WORKED_AS]->(pos:Position) WHERE pos.name IN {data['roles']} }} THEN 4 ELSE 0 END"
    #         )

    #     if data.get('skills'):
    #         match_weights.append(
    #             f"REDUCE(total = 0, s IN {data['skills']} | total + CASE WHEN EXISTS {{ MATCH (p)-[:HAS]->(skill:Skill) WHERE skill.name = s }} THEN 2 ELSE 0 END)"
    #         )

    #     if data.get('certification'):
    #         match_weights.append(
    #             f"REDUCE(total = 0, s IN {data['certification']} | total + CASE WHEN EXISTS {{ MATCH (p)-[:EARNED]->(c:Certification) WHERE c.name = s }} THEN 1 ELSE 0 END)"
    #         )

    #     if data.get('education_degree'):
    #         match_weights.append(
    #             f"CASE WHEN EXISTS {{ MATCH (p)-[:HOLDS]->(d:Degree) WHERE d.name IN {data['education_degree']} }} THEN 2 ELSE 0 END"
    #         )

    #     if data.get('education_name'):
    #         edu_keyword = data['education_name'].split()
    #         edu_conditions = ["edu.name CONTAINS '" + " ".join(edu_keyword) + "'"] + [
    #             f"edu.name CONTAINS '{kw}'" for kw in edu_keyword
    #         ]
    #         match_weights.append(
    #             f"CASE WHEN EXISTS {{ MATCH (p)-[:STUDIED_AT]->(edu:Education) WHERE {' OR '.join(edu_conditions)} }} THEN 3 ELSE 0 END"
    #         )

    #     if data.get('workplace_name'):
    #         work_keyword = data['workplace_name'].split()
    #         work_conditions = ["work.name CONTAINS '" + " ".join(work_keyword) + "'"] + [
    #             f"work.name CONTAINS '{kw}'" for kw in work_keyword
    #         ]
    #         match_weights.append(
    #             f"CASE WHEN EXISTS {{ MATCH (p)-[:WORKED_AT]->(work:Workplace) WHERE {' OR '.join(work_conditions)} }} THEN 3 ELSE 0 END"
    #         )

    #     # AND condition for age and years_of_experience
    #     if data.get('age'):
    #         and_clauses.append(
    #             "p.dob IS NOT NULL "
    #             "AND p.dob <> '' "
    #             "AND date(p.dob) IS NOT NULL "
    #             f"AND date().year - date(p.dob).year {data['age'].strip()}"
    #         )

    #     if data.get('years_of_experience'):
    #         query += (
    #             "MATCH (p)-[r:WORKED_AS]->()\n"
    #             "WITH p, sum(r.duration) AS total_yoe\n"
    #         )
    #         and_clauses.append(f"total_yoe {data['years_of_experience'].strip()}")

    #     # Combine conditions
    #     combined_clauses = []
    #     if or_clauses:
    #         combined_clauses.append("(" + " OR ".join(or_clauses) + ")")
    #     if and_clauses:
    #         combined_clauses.append("(" + " AND ".join(and_clauses) + ")")

    #     if combined_clauses:
    #         query += "WHERE " + " AND ".join(combined_clauses) + "\n"

    #     # Add match weights for sorting
    #     match_score = " + ".join(match_weights)
    #     query += f"WITH p, ({match_score}) AS match_score\n"
    #     query += "ORDER BY match_score DESC\n"
    #     query += "RETURN p.id AS id, match_score LIMIT 15"

    #     return query


    def invoke(self, state: AgentState) -> dict:
        data = {
            "roles": state['role'],
            "skills": state['skill'],
            "certification": state['certification'],
            "education_degree": state['education_degree'],
            "age": state['age'],
            "years_of_experience": state['years_of_experience'],
            "workplace_name": state['workplace_name'],
            "education_name": state['education_name'],
        }

        logger.info(f"Filters applied:\nOR Condition: {', '.join([key for key in ['roles', 'skills', 'certification', 'education_degree', 'workplace_name', 'education_name'] if data.get(key)])}, \nAND Condition: {', '.join([key for key in ['age', 'years_of_experience'] if data.get(key)])}")


        with self.graphdb.session(database=os.getenv("NEO4J_DATABASE")) as session:
            query = self._filter_fixed_nodes(data)
            result = session.run(query)
            dict_result = {record['id']: record['match_score'] for record in result}
            
            logger.info(f"Cypher Query: \n{query}")
            logger.info(f"Filter Ranking: \n{dict_result}")

        self.graphdb.close()

        return {
            "filter_results": dict_result
        }
