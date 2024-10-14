from typing import Annotated, TypedDict, List


class Category(TypedDict):
    """Category"""
    category: Annotated[str, ..., "The category is based on schema"]
    description: Annotated[str, ..., "The brief and detailed description for category"]

class Categories(TypedDict):
    "List Categories"
    categories: List[Category]

class Pair(TypedDict):
    """Question and Cypher pair"""
    question: Annotated[str, ..., "The human language question is based on schema"]
    cypher: Annotated[str, ..., "The cypher query for question"]

class Pairs(TypedDict):
    "List Question and Cypher pairs"
    question_cypher_pairs: List[Pair]