from langchain_openai.chat_models import AzureChatOpenAI
from langchain_ollama import ChatOllama
from llama_cpp.llama_speculative import LlamaPromptLookupDecoding
from llama_cpp import Llama
import multiprocessing

# azure_chat_openai_4 = AzureChatOpenAI(
#     ....
#     temperature=0,
#     max_tokens=4000,
#     top_p=0.95,
#     model_kwargs={"seed": 12},
# )


ChatOllama_llama = ChatOllama(
    model="llama3.1",
    temperature=0,
    # num_predict=512
)

# This model only for extract resume in preprocessing step.
ChatLlamacpp_llama = Llama(
    model_path="/Users/thanhnguyen/Documents/Developer/models/llm/SanctumAI-meta-llama-3-8b-instruct.Q8_0.gguf",
    n_gpu_layers=100,
    n_batch=5000,
    n_threads=multiprocessing.cpu_count() - 3,
    n_ctx=5000,
    draft_model=LlamaPromptLookupDecoding(num_pred_tokens=10),  # (1)!
    logits_all=True,
    verbose=True
)