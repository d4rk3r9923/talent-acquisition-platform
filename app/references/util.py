import os
import fitz
import json
import uuid
import io
import pytesseract

from loguru import logger
from typing import ClassVar, Dict, List, Any
from datetime import datetime
from collections import defaultdict
from pydantic import BaseModel
from enum import Enum
from PIL import Image
from app.references.client import openai_client

class Color(BaseModel):
    # ANSI escape codes for red and reset
    RED: ClassVar[str] = "\033[91m"
    GREEN: ClassVar[str] = "\033[92m"
    RESET: ClassVar[str] = "\033[0m"


def get_embedding(text, 
                  model="text-embedding-3-small", 
                  client= openai_client,
    ):
   text = text.replace("\n", " ")
   return client.embeddings.create(input =[text], model=model).data[0].embedding


def create_enum_from_objects(object_list, enum_name):
    # Get the first attribute name from the first object
    first_attribute = list(object_list[0].__dict__.keys())[0]

    unique_values = {getattr(obj, first_attribute) for obj in object_list}

    # return Enum(enum_name, { value.upper().replace(' ','_'): value for value in unique_values})
    return Enum(enum_name, { str(uuid.uuid5(uuid.NAMESPACE_DNS, value)): value for value in unique_values})

  
# Helper function to load or initialize JSON list
async def load_json_list(json_list_path: str) -> List[dict]:
    try:
        with open(json_list_path, "r", encoding="utf-8") as json_file:
            return json.load(json_file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

# Helper function to save JSON list to file
async def save_json_list(json_list: List[dict], json_list_path: str, cls):
    with open(json_list_path, "w", encoding="utf-8") as json_file:
        json.dump(json_list, json_file, cls=cls, ensure_ascii=False, indent=4)
    # logger.info(f"{Color.RED}Updated JSON list saved to {json_list_path}{Color.RESET}")


async def read_content_pdf(file_path):
    # Open the PDF file
    document = fitz.open(file_path)
    
    # Try to extract text directly from PDF
    pdf_text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        page_text = page.get_text()
        
        if page_text.strip():  # If there is text on the page
            pdf_text += page_text
        else:
            # If no text found, fallback to OCR
            pix = page.get_pixmap()
            img = Image.open(io.BytesIO(pix.tobytes()))
            page_text = pytesseract.image_to_string(img)
            pdf_text += page_text + "\n"
    
    # Close the document
    document.close()
    return pdf_text
      

async def pdf_to_single_image(
        pdf_path, 
        output_image="output_image.png", 
        orientation="vertical",
        zoom=3,
):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    images = []
    
    # Render each page as an image with higher quality
    for page_number in range(pdf_document.page_count):
        page = pdf_document[page_number]
        # Apply scaling for higher resolution
        matrix = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=matrix)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)

    # Determine the dimensions for the combined image
    widths, heights = zip(*(img.size for img in images))

    if orientation == "vertical":
        total_width = max(widths)
        total_height = sum(heights)
        combined_image = Image.new("RGB", (total_width, total_height))
        y_offset = 0
        for img in images:
            combined_image.paste(img, (0, y_offset))
            y_offset += img.height
    else:
        total_width = sum(widths)
        total_height = max(heights)
        combined_image = Image.new("RGB", (total_width, total_height))
        x_offset = 0
        for img in images:
            combined_image.paste(img, (x_offset, 0))
            x_offset += img.width

    # Save the combined image
    combined_image.save(output_image)
    return f"{os.path.abspath(output_image)}"


async def replace_nulls(data: Any) -> Any:
    if isinstance(data, dict):
        return {key: await replace_nulls(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [await replace_nulls(item) for item in data]
    elif data is None:
        return ""
    else:
        return data


async def calculate_duration(start_date: str, end_date: str) -> (int, int):
    """
    Calculate the difference between start and end dates, returning the duration in years and months.
    """
    if not end_date:
        end_date = datetime.now().strftime("%Y-%m-%d")

    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    duration = end - start
    years, remainder = divmod(duration.days, 365)
    months = remainder // 30
    return years, months


async def convert_to_years_months(total_years: int, total_months: int) -> int:
    """
    Convert the total duration in years and months to an integer representing the total months.
    """
    total_duration_in_months = total_years * 12 + total_months
    return total_duration_in_months


async def postprocess_candidate_data(candidate_data: Dict[str, Any]) -> Dict[str, Any]:
    candidate_data = await replace_nulls(candidate_data)

    role_dict = defaultdict(
        lambda: {"duration": (0, 0), "responsibilities": [], "achievements": []}
    )

    # Ensure work_experience exists and is a list before iterating
    for work_exp in candidate_data.get("work_experience", []):
        if work_exp is None:
            continue  # Skip if work_experience is None

        role = work_exp["role"]
        start_date = work_exp.get("start_date")
        end_date = work_exp.get("end_date", "2025-01-01")

        # Check if the dates exist before processing
        if not start_date:
            continue  # Skip if start_date is missing

        # Calculate the duration for this work experience
        years, months = await calculate_duration(start_date, end_date)

        # Add up the duration
        total_years, total_months = role_dict[role]["duration"]
        new_total_years = total_years + years
        new_total_months = total_months + months

        if new_total_months >= 12:
            new_total_years += new_total_months // 12
            new_total_months = new_total_months % 12

        # Update role's responsibilities and achievements
        role_dict[role]["duration"] = (new_total_years, new_total_months)
        role_dict[role]["responsibilities"].extend(
            work_exp.get("responsibilities", [])
        )
        role_dict[role]["achievements"].extend(work_exp.get("achievements", []))

    # Process education, certification, and publications similarly
    candidate_data["positions"] = []
    for role, details in role_dict.items():
        duration_years, duration_months = details["duration"]
        candidate_data["positions"].append(
            {
                "role": role,
                "duration": await convert_to_years_months(duration_years, duration_months),
                "responsibilities": list(set(details["responsibilities"])),
                "achievements": list(set(details["achievements"])),
            }
        )

    return candidate_data
