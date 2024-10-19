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
    """Extracts text from a PDF and appends embedded links next to the associated words, preserving new lines."""
    text = ""
    
    # Open the PDF file
    with fitz.open(file_path) as doc:
        # Loop through all pages
        for page_num in range(doc.page_count):
            page = doc.load_page(page_num)  # Get the page
            blocks = page.get_text("blocks")  # Extract text in blocks (preserves newlines)
            words = page.get_text("words")  # List of (x0, y0, x1, y1, "word")
            
            # Extract links
            links = page.get_links()
            linked_word_positions = {}  # Store positions of linked words
            used_links = set()  # Track used links to avoid repetition
            
            for link in links:
                rect = fitz.Rect(link["from"])  # Get the rectangle area for the link
                link_uri = link.get("uri", "No link found")  # Get the link URI
                
                # Find the closest word(s) within the link rectangle
                for word in words:
                    word_rect = fitz.Rect(word[:4])  # Create a rectangle for each word
                    if rect.intersects(word_rect):  # Check if word is in the link's rectangle
                        if link_uri not in used_links:  # Ensure link is only appended once
                            linked_word_positions[word[4]] = link_uri  # Associate word with link
                            used_links.add(link_uri)  # Mark link as used

            # Loop through each block of text
            for block in blocks:
                block_text = block[4]  # Extract the text content of the block
                block_lines = block_text.split('\n')  # Split block into lines
                
                for line in block_lines:
                    line_words = line.split(' ')  # Split line into words
                    for word in line_words:
                        if word in linked_word_positions:
                            # Append the link in parentheses next to the word
                            text += f'{word} ({linked_word_positions[word]}) '
                        else:
                            text += word + ' '  # Regular word without a link
                    text += '\n'  # Add new line at the end of each line of text
            
            text += "\n\n"  # Separate pages with a newline
    
    return text


def create_enum_from_objects(object_list, enum_name):
    # Get the first attribute name from the first object
    first_attribute = list(object_list[0].__dict__.keys())[0]

    unique_values = {getattr(obj, first_attribute) for obj in object_list}

    # return Enum(enum_name, { value.upper().replace(' ','_'): value for value in unique_values})
    return Enum(enum_name, { str(uuid.uuid5(uuid.NAMESPACE_DNS, value)): value for value in unique_values})

 