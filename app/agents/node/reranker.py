import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
from langchain_core.runnables import Runnable
from loguru import logger

from app.agents.config import AgentState
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

load_dotenv()

class Reranker(Runnable):
    def __init__(self) -> None:
        super().__init__()
    
    def _reciprocal_rank_fusion(self, filter_results, embedding_results, k=40):
        # Assign ranks for embedding_results
        a_rank = {key: rank + 1 for rank, key in enumerate(embedding_results.keys())}

        # Rank items in filter results based on score
        b_rank = {}
        current_rank = 1
        sorted_b = sorted(filter_results.items(), key=lambda x: -x[1])  # Sort by score descending
        for i, (key, score) in enumerate(sorted_b):
            if i > 0 and score != sorted_b[i - 1][1]:
                current_rank = i + 1  # Update rank to the current position
            b_rank[key] = current_rank

        # Combine rankings using RRF
        rrf_scores = {}
        all_keys = set(filter_results.keys()).union(set(embedding_results.keys()))
        for key in all_keys:
            rank_a = a_rank.get(key, float('inf'))  # Use infinity for missing ranks
            rank_b = b_rank.get(key, float('inf'))
            rrf_score = 1 / (k + rank_a) + 1 / (k + rank_b)
            rrf_scores[key] = rrf_score

        # Sort the combined results by RRF score descending
        combined_sorted = dict(sorted(rrf_scores.items(), key=lambda x: -x[1]))
        # Get the first 5 items
        top = dict(list(combined_sorted.items())[:6])

        return top
    
    def invoke(self, state: AgentState) -> dict:
        reranker_results = self._reciprocal_rank_fusion(state['filter_results'], state['embedding_results'])

        logger.info(f"Reranker Ranking: \n{reranker_results}")
        return {
            "top_reranker_results": reranker_results
        }
