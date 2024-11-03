import os
import json
import asyncio
import base64
import openai
from loguru import logger
from typing import List
from enum import Enum

from app.references.util import Color, read_content_pdf, pdf_to_single_image 
from app.preprocessing.schema import CandidateProfile
from app.references.client import chatOpenai_client

# client = openai.AsyncOpenAI()

# Custom JSON encoder for Enum
class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value  # Serialize the Enum as its value (string)
        return super().default(obj)


# Function to encode the image
async def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  

async def extract(path_pdf):
    content = await read_content_pdf(path_pdf)
    # image_url = await pdf_to_single_image(path_pdf)
    # base64_image = await encode_image(image_url)

    llm = chatOpenai_client.with_structured_output(schema=CandidateProfile, method='json_schema')

    response = await llm.ainvoke(
        input=[
            {
                "role": "system",
                "content": "Extract the information from the resume provided in English, regardless of Resume content's language"
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"<Resume Content>\n {content} <\Resume Content>\n\n \
                    Get the information of this resume, if content above is Vietnamese then you must translate to english"},
                    # {
                    #     "type": "image_url",
                    #     "image_url": {
                    #         "url": f"data:image/jpeg;base64,{base64_image}",
                    #     }
                    # },
                ],
            }
        ]
    )

    return response

    
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
    pdf_paths = ["data/Resume/0a95731d-d7e8-479a-a5a4-cf86346765a6.pdf"]
    
    asyncio.run(main(pdf_paths))
