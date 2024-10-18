import os
import openai 
import instructor
import asyncio
from pprint import pprint
from loguru import logger
from dotenv import load_dotenv
from typing import List

from app.utils.util import Color, read_content_pdf 
from app.preprocessing.schema import CandidateProfile

load_dotenv()

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
                "content": f"Get the information of this resume and write a short summary (all in english): \n {content}",
            },
        ],
        temperature=0, 
        response_model=CandidateProfile
    )

async def processing_pdf(path_pdf):
    logger.info(f"{Color.RED}Processing {path_pdf}{Color.RESET}")
    try:
        response = await extract(path_pdf)
        logger.info(f"{Color.RED}Extracting contents for {path_pdf}:{Color.RESET}  \n{response}")
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
