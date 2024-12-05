import os
from openai import OpenAI
from dotenv import load_dotenv 
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_ollama import ChatOllama
from langchain_openai.chat_models import AzureChatOpenAI

load_dotenv()

openai_client = OpenAI()

# chatAzure_client = AzureChatOpenAI(
#     azure_endpoint=os.getenv("CHAT-GPT4-32K-API-BASE"),
#     api_key=os.getenv("CHAT-GPT4-32K-API-KEY"),
#     api_version=os.getenv("CHAT-GPT4-32K-API-VERSION", "2023-12-01-preview"),
#     azure_deployment=os.getenv("CHAT-GPT4-32K-DEPLOPMENT-NAME"),
#     temperature=0,
# )

chatOpenai_client = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0,
)

chatOllama_llama = ChatOllama(
    model="QueryExtractionLlama",
    temperature=0,
)

embedding_OpenAI = OpenAIEmbeddings(
    model="text-embedding-3-large",
)