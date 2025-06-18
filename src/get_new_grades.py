from typing import List, Dict, Set
from utils import load_json


def find_new_grades(old_file: str, new_file: str) -> List[str]:
    """Compare deux fichiers JSON et retourne les nouvelles notes."""
    old_data = load_json(old_file)
    new_data = load_json(new_file)

    return compare_grades(old_data, new_data)


def compare_grades(old_data: List[Dict], new_data: List[Dict]) -> List[str]:
    """Compare deux structures de données et retourne les nouvelles notes."""
    old_grades = _extract_grades(old_data)
    new_grades = _extract_grades(new_data)

    return [
        {
            "title": f"{course.split("/")[0].strip()} - {grade_type}",
            "details": f"{value} - {coef}%",
        }
        for course, grade_type, value, coef in new_grades - old_grades
    ]


def _extract_grades(data: List[Dict]) -> Set[tuple]:
    """Extrait toutes les notes sous forme de tuples uniques."""
    grades = set()

    for year in data:
        for semester in year.get("semesters", []):
            for module in semester.get("semester_modules", []):
                for course in module.get("module_courses", []):
                    course_name = course.get("course_name", "")
                    for grade_type in course.get("course_grades_type", []):
                        type_name = grade_type.get("grade_type", "")
                        for grade in grade_type.get("grades", []):
                            value = grade.get("grade", "")
                            coef = grade.get("coef", "")

                            if value and value != "Validé":
                                grades.add((course_name, type_name, value, coef))

    return grades


if __name__ == "__main__":
    # Exemple d'utilisation
    old_file_path = "src/data/old_grades.json"
    new_file_path = "src/data/new_grades.json"

    nouvelles_notes = find_new_grades(old_file_path, new_file_path)

    for note in nouvelles_notes:
        print(note)
