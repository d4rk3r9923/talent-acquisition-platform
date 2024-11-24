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
from enum import Enum
import json

load_dotenv()

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value  # Serialize the Enum as its value (string)
        return super().default(obj)
    

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
    response = response.model_dump()
    return {"categories": response["categories"]}

def map_generate_QA(state: State):
    return [
        Send("generate_QA", {"category": category, 
                             "n_pair": state["n_pair"]}) for category in state["categories"]
    ]


async def generate_QA(state: State):
    answers = await generate_A_chain.ainvoke({"n_pair": state["n_pair"], "category": state["category"]})
    answers = answers.model_dump()
    answers = answers["answers"]

    questions = await generate_Q_chain.ainvoke({"answers": answers})
    questions = questions.model_dump()
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
    async for event in model.astream({"n_pair": 20, "n_category":30}, config=config):
        print(event.keys())
        if event.get("generate_category"):
            save_results("categories", event["generate_category"]["categories"])

        if event.get("generate_QA"):
            save_results("results", event["generate_QA"]["pairs"])


def save_results(name, data):
    with jsonlines.open(f"results/{name}.jsonl", "a") as writer:
        writer.write_all(json.loads(json.dumps(data, cls=CustomEncoder, ensure_ascii=False, indent=4)))


def save_image(model):
    with open("saved_image.png", "wb") as file:
        file.write(model.get_graph().draw_mermaid_png())


if __name__=="__main__":
    if not os.path.exists("results"):
        os.makedirs("results")

    from langchain_core.rate_limiters import InMemoryRateLimiter

    rate_limiter = InMemoryRateLimiter(
        requests_per_second=0.5,  # <-- Super slow! We can only make a request once every 10 seconds!!
        check_every_n_seconds=0.1,  # Wake up every 100 ms to check whether allowed to make a request,
        max_bucket_size=1000,  # Controls the maximum burst size.
    )

    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.0,
        max_tokens=None,
        timeout=None,
        max_retries=3,
        rate_limiter=rate_limiter,
        )

    inital_chain = categories_template() | llm.with_structured_output(Categories, method="json_schema")
    generate_Q_chain = generate_Q_template() | llm.with_structured_output(Questions, method="json_schema")
    generate_A_chain = generate_A_template() | llm.with_structured_output(Answers, method="json_schema")


    model_graph = model()
    save_image(model_graph)
    asyncio.run(inference(model_graph))
