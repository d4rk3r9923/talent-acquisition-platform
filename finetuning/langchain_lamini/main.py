from typing import Any, Iterator, List, Mapping, Optional
from pydantic import Field
from langchain_core.outputs import GenerationChunk
from langchain_core.language_models.llms import LLM
from langchain_core.prompts import PromptTemplate
import lamini
from requests.exceptions import ConnectionError

class ChatLamini(LLM):
    """Base LLM abstract interface.

    It should take in a prompt and return a string."""
    
    model_name: Optional[str] = Field("meta-llama/Meta-Llama-3.1-8B-Instruct")
    max_new_tokens: Optional[int] = Field(150)


    def _call(self, prompt: str, stop: Optional[str] = None, **kwargs: Any) -> str:
        llm = lamini.Lamini(model_name=self.model_name)
        return llm.generate(prompt, max_new_tokens=self.max_new_tokens, **kwargs)
        
    def _stream(self, prompt: str, stop: Optional[List[str]] = None, **kwargs: Any) -> Iterator[GenerationChunk]:
        llm = lamini.StreamingCompletion()

        previous = "\n\n"
        for output in llm.create(prompt=prompt, model_name=self.model_name, max_new_tokens=self.max_new_tokens):
            if output:
                cur = output["outputs"][0]["output"]
            else:
                continue

            chunk = GenerationChunk(text=cur.removeprefix(previous))
            previous = cur
            yield chunk

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"model_name": self.model_name,
                "max_tokens": self.max_new_tokens}
    
    @property
    def _llm_type(self) -> str:
        return "lamini"


def System(content) -> str:
    """role: system"""
    return f"<|start_header_id|>system<|end_header_id|>{content}<|eot_id|>"
  
def Human(content) -> str:
    """role: user"""
    return f"<|start_header_id|>user<|end_header_id|>{content}<|eot_id|>"

def Assistant(content=None):
    """role: assistant"""
    if content:
        return f"<|start_header_id|>assistant<|end_header_id|>{content}<|eot_id|>"
    return "<|start_header_id|>assistant<|end_header_id|>"


def ChatTemplate(message: List):
    message = ["<|begin_of_text|>"] + message
    return PromptTemplate.from_template('\n'.join(message))