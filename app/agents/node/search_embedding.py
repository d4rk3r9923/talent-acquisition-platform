import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_core.runnables import Runnable
from loguru import logger

from app.agents.config import AgentState
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

class SearchEmbedding(Runnable):
    def __init__(self, graphdb: GraphDatabase, model_embedding: OpenAIEmbeddings) -> None:
        super().__init__()
        self.model_embedding = model_embedding
        self.graphdb = graphdb

    def _sort_vector_nodes(self, data: dict) -> str:
        user_quesion = data["conversation_history"][-1]["content"]
        print(user_quesion)
        embedding = {
            "summary": self.model_embedding.embed_query(data["summary"]) if data["summary"] else self.model_embedding.embed_query(user_quesion),
            "location": self.model_embedding.embed_query(data["location"]) if data["location"] else ""        
        }

        query = "MATCH (p:Person)\n"
        query += f"WHERE p.id in {list(data['filter_results'].keys())}\n"

        # Cosine similarity for summary
        if embedding["summary"]:
            query += (
                "WITH p, "
                "reduce(dot_product = 0.0, i IN range(0, size(p.embedding_summary)-1) | "
                f"dot_product + (p.embedding_summary[i] * {embedding['summary']}[i])) AS dot_product, "
                "reduce(norm_p = 0.0, x IN p.embedding_summary | norm_p + x^2) AS norm_p, "
                f"reduce(norm_summary = 0.0, y IN {embedding['summary']} | norm_summary + y^2) AS norm_summary\n"
                "WITH p, dot_product / (sqrt(norm_p) * sqrt(norm_summary)) AS summary_similarity\n"
            )

        # Cosine similarity for location (if available)
        if embedding["location"]:
            query += (
                "WITH p, summary_similarity, "
                "reduce(dot_product_loc = 0.0, i IN range(0, size(p.embedding_location)-1) | "
                f"dot_product_loc + (p.embedding_location[i] * {embedding['location']}[i])) AS dot_product_loc, "
                "reduce(norm_p_loc = 0.0, x IN p.embedding_location | norm_p_loc + x^2) AS norm_p_loc, "
                f"reduce(norm_location = 0.0, y IN {embedding['location']} | norm_location + y^2) AS norm_location\n"
                "WITH p, summary_similarity, "
                "dot_product_loc / (sqrt(norm_p_loc) * sqrt(norm_location)) AS location_similarity\n"
                "WHERE location_similarity > 0.5\n"
            )

        # Sorting and returning
        query += (
            "ORDER BY summary_similarity DESC\n"
            "RETURN p.id as id, summary_similarity"
        )
        return query
    
    
    def invoke(self, state: AgentState) -> dict:
        data = {
            "summary": state['summary'],
            "location": state['location'],
            "filter_results": state['filter_results'],
            "conversation_history": state['conversation_history']
        }

        with self.graphdb.session(database=os.getenv("NEO4J_DATABASE")) as session:
            query = self._sort_vector_nodes(data)
            embedding_results = session.run(query)
            embedding_results = {record['id']: record['summary_similarity'] for record in embedding_results}
            
            logger.info(f"Embedding Ranking: \n{embedding_results}")

        self.graphdb.close()

        return {
            "embedding_results": embedding_results,
        }
