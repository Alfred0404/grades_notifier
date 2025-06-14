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
    Analyse les changements détectés et retourne une liste des nouvelles notes.
    """
    diff_details = []

    for change_type, changes in diff_json.items():
        logger.info(f"Processing change type: {change_type}")
        if change_type not in ["iterable_item_added", "values_changed"]:
            logger.info(f"Skipping change type: {change_type}")
            continue

        for path, value in changes.items():
            try:
                # Récupère les indices pour accéder à grade_type
                indices = [int(x) for x in re.findall(r"\[(\d+)\]", path)]
                if len(indices) < 5:
                    logger.warning(f"Path incomplet pour accéder à grade_type : {path}")
                    continue

                year = notes_json[indices[0]]
                semester = year["semesters"][indices[1]]
                module = semester["semester_modules"][indices[2]]
                course = module["module_courses"][indices[3]]
                grade_type = course["course_grades_type"][indices[4]]

                # Récupération directe de la note depuis `value`
                if change_type == "iterable_item_added":
                    new_grade = value
                elif change_type == "values_changed":
                    new_grade = value.get("new_value")
                else:
                    continue  # au cas où

                grade_str = (
                    f"Note {new_grade['grade']} - {new_grade['coef']}%"
                    if new_grade
                    else "Note inconnue"
                )

                diff_details.append(
                    {
                        "title": f"{course['course_name'].replace('/', '-').split('-')[0]} - {grade_type['grade_type']}",
                        "grade": grade_str,
                    }
                )
                logger.info(f"✅ Nouvelle note détectée : {diff_details[-1]}")

            except (IndexError, KeyError, ValueError, TypeError) as e:
                logger.error(f"❌ Erreur lors du traitement du path '{path}': {e}")
                continue

    return diff_details


if __name__ == "__main__":
    diffs = get_diffs("src/data/notes_old.json", "src/data/notes.json")
    logger.info(json.dumps(diffs, indent=2, ensure_ascii=False))
