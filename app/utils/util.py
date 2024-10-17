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
    
    pdf_content = ""
    
    for page_num in range(len(document)):
        page = document.load_page(page_num)
        
        # Extract page content as a dictionary
        page_dict = page.get_text("dict")
        
        # Iterate through blocks of text
        for block in page_dict["blocks"]:
            for line in block["lines"]:
                line_text = ""  # To store the text for each line
                for span in line["spans"]:
                    # Get the text of the word or phrase
                    text = span["text"]
                    
                    # Check if this span has a link associated with it
                    links = page.get_links()
                    for link in links:
                        # Compare the position of the link with the span's position
                        if 'uri' in link:
                            link_rect = fitz.Rect(link['from'])
                            text_rect = fitz.Rect(span['bbox'])
                            
                            # If the text is within the link's area, consider it a link
                            if link_rect.intersects(text_rect):
                                text += f"({link['uri']})"
                    
                    # Append the text (with or without link) to the line text
                    line_text += text
                
                # After processing a line, add it to pdf_content with a newline
                pdf_content += line_text + "\n"
    
    # Close the document
    document.close()
    
    return pdf_content


def create_enum_from_objects(object_list, enum_name):
    # Get the first attribute name from the first object
    first_attribute = list(object_list[0].__dict__.keys())[0]

    """Creates an Enum from a list of objects based on a specified attribute."""
    unique_values = {getattr(obj, first_attribute) for obj in object_list}

    # Create the Enum class dynamically
    # return Enum(enum_name, { value.upper().replace(' ','_'): value for value in unique_values})
    return Enum(enum_name, { str(uuid.uuid5(uuid.NAMESPACE_DNS, value)): value for value in unique_values})

 