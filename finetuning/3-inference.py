from langchain_lamini import ChatLamini, ChatTemplate, System, Human, Assistant
import lamini
from template_utils import make_question

lamini.api_key = "b1a1082334df151265156ef4a168352dff52db8e3064fa8d079f22b9051aeaf3"

llm = ChatLamini(model_name="742f78b6d04ed6a95f4135bdd2bfd1bd53a3436b90caa85ed5041d8fb9f5c2d5")

chain = make_question() | llm

# a = chain.invoke({"question": "What are the names of people who have studied at Stanford University?"})
# print(a)

for chunk in chain.invoke({"question": "What are the names of people who have studied at FPT University?"}):
    print(chunk, end="", flush=True)
print()