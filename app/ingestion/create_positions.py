import json
from app.utils.util import process_candidate_data

if __name__ == "__main__":
    with open("./data/sample/sample.json") as f:
        candidate_data = json.load(f)
    candidate_data = process_candidate_data(candidate_data)
    json.dump(candidate_data, open("./data/sample/added_positions.json", "w"), indent=4)
    # print(json.dumps(process_candidate_data(candidate_data), indent=4))
