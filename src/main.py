from scrap import get_dom
from get_diff import get_diffs
from extract_notes import *
from send_ntfy_msg import send_ntfy_msg
import json


def print_diff_details(diff_json, notes_json):
    diff_details = ""
    for change_type, changes in diff_json.items():
        for path, value in changes.items():
            # Ex: root[0]['semesters'][1]['modules'][1]['courses'][4]['courseParts'][1]['grades'][0]
            # On extrait les indices
            import re

            indices = [int(x) for x in re.findall(r"\[(\d+)\]", path)]
            # On navigue dans le json
            year = notes_json[indices[0]]
            semester = year["semesters"][indices[1]]
            module = semester["modules"][indices[2]]
            course = module["courses"][indices[3]]
            course_part = course["courseParts"][indices[4]]
            grade = course_part["grades"][indices[5]]
            print(
                f"Changement détecté :\n"
                f"  Année : {year['name']}\n"
                f"  Semestre : {semester['name']}\n"
                f"  Module : {module['name']}\n"
                f"  Matière : {course['name']}\n"
                f"  Partie : {course_part['name']}\n"
                f"  Note : {grade['value']} (poids {grade['weight']})"
            )

            diff_details += (
                f"  Matière : {course['name']}\n"
                f"  Type : {course_part['name']}\n"
                f"  Note : {grade['value']} (coef {grade['weight']})\n\n"
            )

            return diff_details


def compare_and_upgrade_grades(old_grades_path, current_grades_path, data):
    # Get the differences between the old and new notes
    diffs = get_diffs(old_grades_path, current_grades_path)

    # Print the differences
    if diffs:
        # Update the old notes file with the new notes
        save_json(data, old_grades_path)
        # Charger le nouveau JSON pour navigation
        notes_json = load_json(current_grades_path)
        diff_details = print_diff_details(diffs, notes_json)

        # Send a notification with the differences
        send_ntfy_msg(
            "NotesUpdate", f"Changements détectés dans les notes :\n{diff_details}"
        )

    else:
        print("No differences found.")


def load_json(path):
    """
    Load JSON data from the specified file path.
    """
    with open(path, "r", encoding="latin") as f:
        return json.load(f)


def save_json(data, path):
    """
    Save the given data to a JSON file at the specified path.
    """
    with open(path, "w", encoding="latin") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


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
    with open(current_grades_path, "w", encoding="latin") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    compare_and_upgrade_grades(old_grades_path, current_grades_path, data)


if __name__ == "__main__":
    main()
