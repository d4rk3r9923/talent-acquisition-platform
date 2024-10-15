# PART 2 – Now that we have the formatted data, we will upload the file to Together AI to be finetuned
from langchain_lamini import ChatLamini, ChatTemplate, System, Human, Assistant
import lamini
lamini.api_key = "b1a1082334df151265156ef4a168352dff52db8e3064fa8d079f22b9051aeaf3"


message = [
    System(content="You are a helpful assistant."),
    Human(content="{input}"),
    Assistant()]

# Invoke the LLM with the formatted input

while True:
    template = ChatTemplate(message)
    llm = template | ChatLamini()

    user = input("User: ")
    if user == "q":
        break
    bot = ''
    print("AI: ", end="", flush=True)
    for chunk in llm.stream({"input": user}):
        print(chunk, end="", flush=True)
        bot += chunk
    print()
    message.insert(-2, Human(content=user))
    message.insert(-2, Assistant(content=bot))

from pprint import pprint
pprint(message)