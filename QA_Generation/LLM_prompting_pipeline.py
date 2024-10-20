import operator
from typing_extensions import TypedDict
from langgraph.constants import Send
from langgraph.graph import StateGraph, START, END
from langchain_together import ChatTogether
from typing import Annotated, TypedDict, List
from template_utils import categories_template, map_categories_template, get_schema, generate_QA_template
from langchain_openai import AzureChatOpenAI
from parse_utils import Categories, Pairs
import jsonlines
import os
import asyncio
import time

os.environ["TOGETHER_API_KEY"] = "80f6eb25e6e817651c95012f6f92a9a4cfc33a7352e996ee46ca65fa4d7ce051"

class State(TypedDict):
    schema: str
    categories: Annotated[List, operator.add]
    category: str
    final_categories: List
    QA_pairs: Annotated[List, operator.add]
    times: int
    n_category: int
    n_pair: int


async def generate_category(state: State):
    response = await inital_chain.ainvoke({"schema": state["schema"], "n_category": state["n_category"]})
    return {"categories": response["categories"]}


def map_categories(state: State):
    return [
        Send("generate_category", {"schema": state["schema"], "n_category": state["n_category"]}) for _ in range(state["times"])
    ]


async def final_category(state: State):
    response = await map_chain.ainvoke({"categories": state["categories"], "n_category": state["n_category"] * 2})
    return {"final_categories": response["categories"]}


def map_generate_QA(state: State):
    return [
        Send("generate_QA", {"category": category, 
                             "n_pair": state["n_pair"], 
                             "schema": state["schema"]}) for category in state["final_categories"]
    ]


async def generate_QA(state: State):
    response = await generate_QA_chain.ainvoke({"category": state["category"], 
                                                "n_pair": state["n_pair"], 
                                                "schema": state["schema"]})
    return {"QA_pairs": response["question_cypher_pairs"]}


def model():
    graph_builder = StateGraph(State)
    graph_builder.add_node("generate_category", generate_category)
    graph_builder.add_node("final_category", final_category)
    graph_builder.add_node("generate_QA", generate_QA)
    graph_builder.add_conditional_edges(START, map_categories, ["generate_category"])
    graph_builder.add_edge("generate_category", "final_category")
    graph_builder.add_conditional_edges("final_category", map_generate_QA, ["generate_QA"])
    graph_builder.add_edge("generate_QA", END)
    graph = graph_builder.compile()
    return graph


async def inference(model):
    async for event in model.astream({"schema": get_schema(), "times": 5, "n_pair": 40, "n_category":12}):
        await asyncio.sleep(3)
        time.sleep(3)
        print(event.keys())
        if event.get("final_category"):
            save_results("categories", event["final_category"]["final_categories"])

        if event.get("generate_QA"):
            save_results("results", event["generate_QA"]["QA_pairs"])


def save_results(name, data):
    with jsonlines.open(f"results/{name}.jsonl", "a") as writer:
        writer.write_all(data)


def save_image(model):
    with open("saved_image.png", "wb") as file:
        file.write(model.get_graph().draw_mermaid_png())


if __name__=="__main__":
    if not os.path.exists("results"):
        os.makedirs("results")

    llm = ChatTogether(
        model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        temperature=0.0,
        max_tokens=None,
        timeout=None,
        max_retries=5,
        # other params...
    )

    inital_chain = categories_template() | llm.with_structured_output(Categories)
    map_chain = map_categories_template() | llm.with_structured_output(Categories)
    generate_QA_chain = generate_QA_template() | llm.with_structured_output(Pairs)

    model_graph = model()
    save_image(model_graph)
    asyncio.run(inference(model_graph))
