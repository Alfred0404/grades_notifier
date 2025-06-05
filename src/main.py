from scrap import get_dom
from get_diff import get_diffs
from extract_notes import *
import json


def print_diff_details(diff_json, notes_json):
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


def main():
    """
    Main function to scrape the INSEEC website and get the differences in notes.
    """
    # Get the current DOM and save it to a file
    get_dom()

    # Extract notes from the saved DOM
    data = extract_all_years_from_html("src/last_dom.txt")

    # Save the extracted notes to a JSON file
    with open("src/notes.json", "w", encoding="latin") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Get the differences between the old and new notes
    diffs = get_diffs("src/notes_old.json", "src/notes.json")

    # Print the differences
    if diffs:
        # Update the old notes file with the new notes
        with open("src/notes_old.json", "w", encoding="latin") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        # Charger le nouveau JSON pour navigation
        with open("src/notes.json", "r", encoding="latin") as f:
            notes_json = json.load(f)
        print_diff_details(diffs, notes_json)

    else:
        print("No differences found.")


if __name__ == "__main__":
    main()
