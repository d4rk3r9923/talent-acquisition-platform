import fitz
import uuid
from pydantic import BaseModel
from typing import ClassVar
from enum import Enum


class Color(BaseModel):
    # ANSI escape codes for red and reset
    RED: ClassVar[str] = "\033[91m"
    RESET: ClassVar[str] = "\033[0m"


async def read_content_pdf(file_path):
    # Open the PDF file
    document = fitz.open(file_path)
    
    # Iterate through pages and extract text
    pdf_text = ""
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        pdf_text += page.get_text()
    
    # Close the document
    document.close()
    
    return pdf_text


def create_enum_from_objects(object_list, enum_name):
    # Get the first attribute name from the first object
    first_attribute = list(object_list[0].__dict__.keys())[0]

    """Creates an Enum from a list of objects based on a specified attribute."""
    unique_values = {getattr(obj, first_attribute) for obj in object_list}

    # Create the Enum class dynamically
    return Enum(enum_name, { str(uuid.uuid5(uuid.NAMESPACE_DNS, value)): value for value in unique_values})