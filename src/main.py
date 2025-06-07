from scraper import get_dom
from get_grades_diff import get_diffs
from extract_grades import *
from send_ntfy_msg import send_ntfy_msg
from utils import load_json, save_json
import re
import logging

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def print_diff_details(diff_json, notes_json):
    """
    Print the details of the differences found in the notes.

    @param diff_json: The JSON object containing the differences.
    @param notes_json: The JSON object containing the current notes.
    @return: A list of formatted strings detailing the differences.
    """
    diff_details = []
    for change_type, changes in diff_json.items():
        for path, value in changes.items():
            # Ex: root[0]['semesters'][1]['modules'][1]['courses'][4]['courseParts'][1]['grades'][0]
            # On extrait les indices
            try:
                indices = [int(x) for x in re.findall(r"\[(\d+)\]", path)]
                # On navigue dans le json
                year = notes_json[indices[0]]
                semester = year["semesters"][indices[1]]
                module = semester["modules"][indices[2]]
                course = module["courses"][indices[3]]
                course_part = course["courseParts"][indices[4]]
                grade = course_part["grades"][indices[5]]

                diff_details.append(
                    f"{course['name']} | {course_part['name']} | {grade['value']} | {grade['weight']}%"
                )
                # print(diff_details)
            except (IndexError, KeyError, ValueError) as e:
                logging.error(f"Error processing path '{path}': {e}")
                continue
    return diff_details


def compare_and_upgrade_grades(old_grades_path, current_grades_path, data):
    """
    Compare the old and new grades, update the old grades file if there are differences,
    and send a notification with the differences.

    @param old_grades_path: Path to the old grades JSON file.
    @param current_grades_path: Path to the current grades JSON file.
    @param data: The extracted grades data to save if differences are found.
    """
    # Get the differences between the old and new notes
    diffs = get_diffs(old_grades_path, current_grades_path)

    # Print the differences
    if diffs:
        # Update the old notes file with the new notes
        save_json(data, old_grades_path)
        logging.info("Differences found and old notes updated.\n")
        notes_json = load_json(current_grades_path)
        diff_details = print_diff_details(diffs, notes_json)

        # Send a notification with the differences
        for message in diff_details:
            send_ntfy_msg(topic="NotesUpdate", message=message)

    else:
        logging.info("No differences found.\n")


def main():
    last_dom_path = "src/data/last_dom.txt"
    old_grades_path = "src/data/notes_old.json"
    current_grades_path = "src/data/notes.json"

    # Get the current DOM and save it to a file
    get_dom(dom_file=last_dom_path)

    # Extract notes from the saved DOM
    data = extract_all_years_from_html(last_dom_path)

    # Save the extracted notes to a JSON file
    save_json(data, current_grades_path)

    compare_and_upgrade_grades(old_grades_path, current_grades_path, data)


if __name__ == "__main__":
    main()
