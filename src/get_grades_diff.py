import json
import re
from deepdiff import DeepDiff
from utils import load_json
import logging
from setup_logging import setup_logging
setup_logging()
logger = logging.getLogger(__name__)


def get_diffs(old_file="src/data/notes_old.json", new_file="src/data/notes.json"):
    """
    Compare two JSON files and return the differences.

    @param old_file: Path to the old JSON file.
    @param new_file: Path to the new JSON file.
    @return: A dictionary containing the differences between the two JSON files.
    """
    old_notes = load_json(old_file)

    if old_notes is None:
        raise ValueError(f"Could not load old notes from {old_file}")
    new_notes = load_json(new_file)

    if new_notes is None:
        raise ValueError(f"Could not load new notes from {new_file}")

    diff = DeepDiff(old_notes, new_notes, ignore_order=True)
    logger.info(f"Differences found: {json.dumps(diff, indent=2, ensure_ascii=False)}")
    return diff


def parse_diff_details(diff_json, notes_json):
    """
    Print the details of the differences found in the notes.

    @param diff_json: The JSON object containing the differences.
    @param notes_json: The JSON object containing the current notes.
    @return: A list of formatted strings detailing the differences.
    """
    diff_details = []
    for change_type, changes in diff_json.items():
        for path, value in changes.items():
            try:
                # Ex: root[0]['semesters'][1]['modules'][1]['courses'][4]['courseParts'][1]['grades'][0]
                indices = [int(x) for x in re.findall(r"\[(\d+)\]", path)]

                year = notes_json[indices[0]]
                semester = year["semesters"][indices[1]]
                module = semester["semester_modules"][indices[2]]
                course = module["module_courses"][indices[3]]
                course_part = course["course_grades_type"][indices[4]]
                grade_obj = course_part["grades"][indices[5]]

                diff_details.append(
                    f"{course['course_name']} | {course_part['grade_type']} | {grade_obj['grade']} | {grade_obj['coef']}%"
                )
                logger.info(diff_details[-1])

            except (IndexError, KeyError, ValueError) as e:
                logger.error(f"Error processing path '{path}': {e}")
                continue

    return diff_details


if __name__ == "__main__":
    diffs = get_diffs("src/data/notes_old.json", "src/data/notes.json")
    logger.info(json.dumps(diffs, indent=2, ensure_ascii=False))
