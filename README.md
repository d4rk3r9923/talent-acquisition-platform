# Note

## LLM_prompting_pipeline_v1.py

No async using ChatFirework

## LLM_prompting_pipeline.py

Async using AzureChatOpenAI

Should change to ChatTogether

```python
from langchain_together import ChatTogether

llm = ChatTogether(
    model="meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
    temperature=0.0,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    # other params...
)
