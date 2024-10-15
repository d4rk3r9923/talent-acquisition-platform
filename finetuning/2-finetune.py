import jsonlines
from template_utils import make_question
import lamini
lamini.api_key = "b1a1082334df151265156ef4a168352dff52db8e3064fa8d079f22b9051aeaf3"


def get_default_finetune_args():
    return {
        "learning_rate": 0.0003,
        "max_steps": 60,
        "early_stopping": False,
        "load_best_model_at_end": False,
        "peft_args": {"r_value": 32},
    }

def load_training_data():
    with jsonlines.open("train_data/results.jsonl") as f:
        for line in f:
            yield {
                "input": make_question().invoke({"question": line["question"]}).to_string(),
                "output": line["cypher"] + "<|eot_id|>",
            }

llm = lamini.Lamini(model_name="meta-llama/Meta-Llama-3.1-8B-Instruct")

dataset = list(load_training_data())
finetune_args = get_default_finetune_args()

llm.train(
    data_or_dataset_id=dataset,
    finetune_args=finetune_args,
    is_public=False,  # For sharing
)