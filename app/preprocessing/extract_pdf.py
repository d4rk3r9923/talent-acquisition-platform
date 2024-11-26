import os
import json
import asyncio
import base64
import openai
from loguru import logger
from typing import List
from enum import Enum
from app.references.util import (
    Color, 
    read_content_pdf, 
    load_json_list,
    save_json_list,
    pdf_to_single_image , 
    postprocess_candidate_data
)
from app.preprocessing.schema import CandidateProfile
from app.references.client import chatOpenai_client, embedding_OpenAI


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

    llm = chatOpenai_client.with_structured_output(schema=CandidateProfile, method='json_schema', strict=False)

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
 
# # Process a single PDF and update JSON list
# async def processing_upload_pdf(
#         path_pdf: str, 
#         embedding=embedding_OpenAI, 
#     ):
#     try:
#         logger.info(f"{Color.RED}Processing {path_pdf}{Color.RESET}")

#         response = await extract(path_pdf)
#         candidate_profile_dict = response.model_dump()  # Get the candidate profile as a dict
#         candidate_profile_dict["person"]["path_pdf"] = path_pdf

#         # candidate_profile_json = json.dumps(candidate_profile_dict, cls=CustomEncoder, ensure_ascii=False, indent=4)
#         # logger.info(f"{Color.RED}Extracted contents for {path_pdf}: {Color.RESET} \n{candidate_profile_json}")

#         candidate_profile_dict["person"]["embedding_summary"] = await embedding.aembed_query(candidate_profile_dict["person"]["summary"])
#         candidate_profile_dict["person"]["embedding_location"] = await embedding.aembed_query(candidate_profile_dict["person"]["location"])
        
#         candidate_profile_dict = await postprocess_candidate_data(candidate_profile_dict)

#         return candidate_profile_dict

#     except Exception as e:
#         logger.error(f"{Color.RED}Error processing {path_pdf}: {Color.RESET} {str(e)}")
#         # Optionally, pass or continue depending on the desired behavior


# Process a single PDF and update JSON list
async def process_single_pdf(
        path_pdf: str, 
        json_list_path: str = "upload.json",
        embedding=embedding_OpenAI, 
    ):
    try:
        logger.info(f"{Color.RED}Processing {path_pdf}{Color.RESET}")

        response = await extract(path_pdf)
        candidate_profile_dict = response.model_dump()  # Get the candidate profile as a dict
        candidate_profile_dict["person"]["path_pdf"] = path_pdf

        # candidate_profile_json = json.dumps(candidate_profile_dict, cls=CustomEncoder, ensure_ascii=False, indent=4)
        # logger.info(f"{Color.RED}Extracted contents for {path_pdf}: {Color.RESET} \n{candidate_profile_json}")

        candidate_profile_dict["person"]["embedding_summary"] = await embedding.aembed_query(candidate_profile_dict["person"]["summary"])
        candidate_profile_dict["person"]["embedding_location"] = await embedding.aembed_query(candidate_profile_dict["person"]["location"])
        
        candidate_profile_dict = await postprocess_candidate_data(candidate_profile_dict)

        # Load, append, and save updated JSON list
        json_list = await load_json_list(json_list_path)
        json_list.append(candidate_profile_dict)
        await save_json_list(json_list, json_list_path, CustomEncoder)

    except Exception as e:
        logger.error(f"{Color.RED}Error processing {path_pdf}: {Color.RESET} {str(e)}")
        # Optionally, pass or continue depending on the desired behavior

async def process_pdfs_concurrently(pdf_paths: List[str]):
    tasks = [process_single_pdf(path) for path in pdf_paths]
    await asyncio.gather(*tasks)


# if __name__ == "__main__":
#     from tqdm.asyncio import tqdm_asyncio
#     import nest_asyncio
#     nest_asyncio.apply()

#     async def main():
#         list_pdf = os.listdir("data/Resume_IT")
#         first_100_pdf = list_pdf[39:50]

#         for i in tqdm_asyncio(range(0, len(first_100_pdf), 2), desc="Processing PDFs", unit="batch"):
#             three_pdf = first_100_pdf[i:i+2]
#             full_paths = [os.path.join("data/Resume_IT", pdf) for pdf in three_pdf]
#             await process_pdfs_concurrently(full_paths)

#     asyncio.run(main())
