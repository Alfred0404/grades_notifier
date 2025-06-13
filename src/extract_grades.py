import re
import logging
from setup_logging import setup_logging
from bs4 import BeautifulSoup
from utils import load_env_variables

setup_logging()
load_env_variables()

logger = logging.getLogger(__name__)

def extract_rows(html_content):
    """Extract rows from the HTML content of the grades page.

    @param html_content: The HTML content of the grades page.
    @return: A list of BeautifulSoup row elements.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    tbody = soup.find("tbody")
    return tbody.find_all("tr")


def parse_rows(rows):
    """Parse the rows of grades and organize them into a structured format.

    @param rows: A list of BeautifulSoup row elements containing grades data.
    @return: A dictionary containing the structured grades data.
    """
    result = {"years": []}
    current_year = None
    current_semester = None
    current_module = None
    current_course = None

    for row in rows:
        cells = row.find_all("td")
        if not cells:
            continue

        libelle = cells[0].get_text(strip=True)
        ponderation = cells[1].get_text(strip=True)
        coefficient = cells[2].get_text(strip=True)
        note = cells[3].get_text(strip=True)

        classes = row.get("class", [])

        if "master" in classes and "slave" not in classes:
            current_year = {"year_name": libelle, "semesters": []}
            result["years"].append(current_year)
            # logging.info(f"Processing year: {libelle}")

        elif "slave" in classes and re.search(
            r"semestre\s*\d+", libelle, re.IGNORECASE
        ):
            semester_name = libelle.split("/")[0].strip().lower()
            current_semester = {"semester_name": semester_name, "semester_modules": []}
            current_year["semesters"].append(current_semester)
            # logging.info(f"Processing semester: {semester_name}")

        elif not ponderation and not coefficient and not note:
            current_module = {"module_name": libelle, "module_courses": []}
            current_semester["semester_modules"].append(current_module)
            # logging.info(f"Processing module: {libelle}")

        elif ponderation and not coefficient and not note:
            try:
                float_ponderation = float(ponderation.replace(",", "."))
                current_course = {
                    "course_name": libelle,
                    "course_ponderation": float_ponderation,
                    "course_grades_type": [],
                }
                current_module["module_courses"].append(current_course)
                # logging.info(f"Processing course: {libelle}")
            except ValueError:
                # logger.warning(f"Ignoring invalid ponderation: {ponderation}")
                continue

        elif coefficient and note:
            grade_entries = extract_grades(note)
            float_coef = extract_float(coefficient)
            if float_coef is None:
                continue
            current_course["course_grades_type"].append(
                {
                    "grade_type": libelle,
                    "coefficient": float_coef,
                    "grades": grade_entries,
                }
            )

    return result


def extract_grades(note):
    """Extract grade entries from a note string.

    @param note: The note string containing grade information.
    @return: A list of dictionaries containing grade values and coefficients.
    """
    grade_entries = []
    if "(" in note and ")" in note:
        parts = note.split(" - ")
        for part in parts:
            match = re.match(r"([\d.,]+)\s*\((\d+%)\)", part.strip())
            if match:
                try:
                    grade_value = match.group(1).replace(",", ".")
                    grade_coef = match.group(2).replace("%", "")
                    grade_entries.append({"grade": grade_value, "coef": grade_coef})
                except ValueError:
                    logger.warning(f"Invalid grade or coef in part: {part}")
                    continue
    else:
        try:
            grade_value = note.replace(",", ".")
            grade_entries.append({"grade": grade_value, "coef": 100.0})
        except ValueError:
            logger.warning(f"Invalid single grade: {note}")
            pass
    return grade_entries


def extract_float(text):
    """Extract a float value from a string, removing any percentage signs.

    @param text: The string containing the float value.
    @return: The float value, or None if conversion fails.
    """
    try:
        return float(text.replace("%", ""))
    except ValueError:
        logger.warning(f"Invalid float string: {text}")
        return None
