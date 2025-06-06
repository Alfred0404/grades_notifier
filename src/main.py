from scrap import get_dom
from get_diff import get_diffs
from extract_notes import *
from send_ntfy_msg import send_ntfy_msg
from utils import load_json, save_json
import json
import re


def print_diff_details(diff_json, notes_json):
    diff_details = []
    for change_type, changes in diff_json.items():
        for path, value in changes.items():
            # Ex: root[0]['semesters'][1]['modules'][1]['courses'][4]['courseParts'][1]['grades'][0]
            # On extrait les indices

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
            print(diff_details)

    return diff_details


def compare_and_upgrade_grades(old_grades_path, current_grades_path, data):
    # Get the differences between the old and new notes
    diffs = get_diffs(old_grades_path, current_grades_path)

    # Print the differences
    if diffs:
        # Update the old notes file with the new notes
        save_json(data, old_grades_path)
        notes_json = load_json(current_grades_path)
        diff_details = print_diff_details(diffs, notes_json)

        # Send a notification with the differences
        for message in diff_details:
            send_ntfy_msg(topic="NotesUpdate", message=message)

    else:
        print("No differences found.")


def main():
    """
    Main function to scrape the INSEEC website and get the differences in notes.
    """

    last_dom_path = "src/last_dom.txt"
    old_grades_path = "src/notes_old.json"
    current_grades_path = "src/notes.json"

    # Get the current DOM and save it to a file
    get_dom(dom_file=last_dom_path)

    # Extract notes from the saved DOM
    data = extract_all_years_from_html(last_dom_path)

    # Save the extracted notes to a JSON file
    save_json(data, current_grades_path)

    compare_and_upgrade_grades(old_grades_path, current_grades_path, data)


if __name__ == "__main__":
    main()
