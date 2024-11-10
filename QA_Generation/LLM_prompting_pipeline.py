import operator
from typing_extensions import TypedDict
from langgraph.constants import Send
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from typing import Annotated, TypedDict, List
from template_utils import categories_template, generate_Q_template, generate_A_template
from parse_utils import Categories, Questions, Answers
import jsonlines
import os
import asyncio
from langfuse.callback import CallbackHandler
from dotenv import load_dotenv
load_dotenv()


os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")
langfuse_handler = CallbackHandler(
    secret_key=os.getenv("SECRET_KEY"),
    public_key=os.getenv("PUBLIC_KEY"),
    host="https://us.cloud.langfuse.com"
)

class State(TypedDict):
    categories: Annotated[List, operator.add]
    category: str
    pairs: Annotated[List, operator.add]
    n_category: int
    n_pair: int


async def generate_category(state: State):
    response = await inital_chain.ainvoke({"n_category": state["n_category"]})

    return {"categories": response["categories"]}

def map_generate_QA(state: State):
    return [
        Send("generate_QA", {"category": category, 
                             "n_pair": state["n_pair"]}) for category in state["categories"]
    ]


async def generate_QA(state: State):
    answers = await generate_A_chain.ainvoke({"n_pair": state["n_pair"], "category": state["category"]})
    answers = answers["answers"]

    questions = await generate_Q_chain.ainvoke({"answers": answers})
    questions = questions["questions"]
    

    return {"pairs": [{"question": questions[i]["question"], 
                       "answer": answers[i]} for i in range(min(len(questions), len(answers)))]}


def model():
    graph_builder = StateGraph(State)
    graph_builder.add_node("generate_category", generate_category)
    graph_builder.add_node("generate_QA", generate_QA)
    graph_builder.add_edge(START, "generate_category")
    graph_builder.add_conditional_edges("generate_category", map_generate_QA, ["generate_QA"])
    graph_builder.add_edge("generate_QA", END)
    graph = graph_builder.compile()
    return graph


async def inference(model):
    config={"callbacks": [langfuse_handler]}
    async for event in model.astream({"n_pair": 10, "n_category":50}, config=config):
        print(event.keys())
        if event.get("generate_category"):
            save_results("categories", event["generate_category"]["categories"])

        if event.get("generate_QA"):
            save_results("results", event["generate_QA"]["pairs"])


def save_results(name, data):
    with jsonlines.open(f"results/{name}.jsonl", "a") as writer:
        writer.write_all(data)


def save_image(model):
    with open("saved_image.png", "wb") as file:
        file.write(model.get_graph().draw_mermaid_png())


if __name__=="__main__":
    if not os.path.exists("results"):
        os.makedirs("results")

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.0,
        max_tokens=None,
        timeout=None,
        max_retries=3,
        )

    inital_chain = categories_template() | llm.with_structured_output(Categories)
    generate_Q_chain = generate_Q_template() | llm.with_structured_output(Questions)
    generate_A_chain = generate_A_template() | llm.with_structured_output(Answers)


    model_graph = model()
    save_image(model_graph)
    asyncio.run(inference(model_graph))
