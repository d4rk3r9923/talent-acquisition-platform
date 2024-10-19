import fitz
import json
import uuid
from collections import defaultdict
from datetime import datetime
from pydantic import BaseModel
from typing import ClassVar
from enum import Enum


class Color(BaseModel):
    # ANSI escape codes for red and reset
    RED: ClassVar[str] = "\033[91m"
    GREEN: ClassVar[str] = "\033[92m"
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


def replace_nulls(data):
    if isinstance(data, dict):
        return {key: replace_nulls(value) for key, value in data.items()}
    elif isinstance(data, list):
        return [replace_nulls(item) for item in data]
    elif data is None:
        return ""
    else:
        return data


def calculate_duration(start_date, end_date):
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


def convert_to_years_months(total_years, total_months):
    """
    Convert the total duration in years and months to a readable string format.
    """
    if total_years > 0 and total_months > 0:
        return f"{total_years} year(s) {total_months} month(s)"
    elif total_years > 0:
        return f"{total_years} year(s)"
    else:
        return f"{total_months} month(s)"


def process_candidate_data(candidate_data):
    candidate_data = replace_nulls(candidate_data)
    for candidate in candidate_data:
        role_dict = defaultdict(
            lambda: {"duration": (0, 0), "responsibilities": [], "achievements": []}
        )

        # Ensure work_experience exists and is a list before iterating
        for work_exp in candidate.get("work_experience", []):
            if work_exp is None:
                continue  # Skip if work_experience is None

            role = work_exp["role"]
            start_date = work_exp.get("start_date")
            end_date = work_exp.get("end_date")

            # Check if the dates exist before processing
            if not start_date:
                continue  # Skip if start_date is missing

            # Calculate the duration for this work experience
            years, months = calculate_duration(start_date, end_date)

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
        candidate["positions"] = []
        for role, details in role_dict.items():
            duration_years, duration_months = details["duration"]
            candidate["positions"].append(
                {
                    "role": role,
                    "duration": convert_to_years_months(
                        duration_years, duration_months
                    ),
                    "responsibilities": list(set(details["responsibilities"])),
                    "achievements": list(set(details["achievements"])),
                }
            )

    return candidate_data
