import os
import json
import openai 
import instructor
import asyncio
from pprint import pprint
from loguru import logger
from dotenv import load_dotenv
from typing import List
from enum import Enum

from app.utils.util import Color, read_content_pdf 
from app.preprocessing.schema import CandidateProfile

load_dotenv()

# Custom JSON encoder for Enum
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value  # Serialize the Enum as its value (string)
        return super().default(obj)
    
# Async OpenAI
client = instructor.from_openai(
    openai.AsyncOpenAI(api_key=os.getenv('OPENAI_API_KEY')),
    mode=instructor.Mode.JSON,
)

async def extract(path_pdf):

    content = await read_content_pdf(path_pdf)
   
    return await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": f"Get the information of this resume and write a short summary (all in english regardless of Resume content's language below): \n\n {content}",
            },
        ],
        temperature=0, 
        response_model=CandidateProfile
    )

async def processing_pdf(path_pdf, json_list_path="data/sample/sample.json"):
    logger.info(f"{Color.RED}Processing {path_pdf}{Color.RESET}")
    try:
        response = await extract(path_pdf)
        candidate_profile_dict = response.model_dump()  # Get the candidate profile as a dict
        candidate_profile_json = json.dumps(candidate_profile_dict, cls=CustomEncoder, ensure_ascii=False, indent=4)
        logger.info(f"{Color.RED}Extracting contents for {path_pdf}:{Color.RESET}  \n{candidate_profile_json}")

        # Load the existing JSON list if the file exists, otherwise initialize an empty list
        try:
            with open(json_list_path, "r", encoding="utf-8") as json_file:
                json_list = json.load(json_file)
        except (FileNotFoundError, json.JSONDecodeError):
            json_list = []

        # Append the new profile (as a dictionary, not a string) to the existing list
        json_list.append(candidate_profile_dict)

        # Save the updated list back to the file in human-readable format
        with open(json_list_path, "w", encoding="utf-8") as json_file:
            json.dump(json_list, json_file, cls=CustomEncoder, ensure_ascii=False, indent=4)

        logger.info(f"{Color.RED}Added profile to {json_list_path}{Color.RESET}")

    except Exception as e:
        logger.error(f"{Color.RED}Error processing {path_pdf}:{Color.RESET} {str(e)}")



async def main(pdf_paths: List[str]):
    # Run tasks concurrently for each PDF
    tasks = [processing_pdf(path) for path in pdf_paths]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Example input list of PDF file paths
    pdf_paths = ["data/sample/ThanhNguyen.pdf"]
    
    asyncio.run(main(pdf_paths))
