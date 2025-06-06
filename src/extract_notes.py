import json
import re
from bs4 import BeautifulSoup

YEAR_ROW_CLASS = "master"
SEMESTER_AND_MODULE_ROW_CLASS = "item-ens"
SEMESTER_STRINGS = ["Semestre"]
SEMESTER_MISTAKE_STR = "Semestre Académique"
COURSE_ROW_CLASS = "item-fpc"
COURSE_PART_CLASS = "item-ev1"
NAME_COLUMN_CLASS = "libelle"
RESIT_COLUMN_CLASS = "rattrapage"
GRADE_COLUMN_CLASS = "note"
COURSE_COEFFICIENT_CLASS = "ponderation"
WEIGHT_COLUMN_CLASS = "coefficient"
SEMESTER_NUMBER = 2


def extract_years_count(table):
    return len(table.find_all("tr", class_=YEAR_ROW_CLASS))


def extract_grades(cell_text):
    grades = []
    for grade in cell_text.split(" - "):
        grade = grade.strip()
        if not grade:
            continue
        parts = grade.split(" ")
        grade_value = None
        grade_weight = 100.0
        if parts:
            try:
                grade_value = float(parts[0].replace(",", "."))
            except Exception:
                grade_value = None
        if len(parts) > 1:
            grade_weight = parts[1].replace("(", "").replace(")", "")
            try:
                grade_weight = float(grade_weight.replace(",", "."))
            except Exception:
                grade_weight = 100.0
        grades.append({"value": grade_value, "weight": grade_weight})
    return grades


def extract_course_part_from_row(row):
    name = row.find(class_=NAME_COLUMN_CLASS).get_text(strip=True)
    weight_cell = row.find(class_=WEIGHT_COLUMN_CLASS)
    weight = None
    if weight_cell:
        try:
            weight = float(weight_cell.get_text(strip=True).replace(",", "."))
        except Exception:
            weight = None
    grade_cell = row.find(class_=GRADE_COLUMN_CLASS)
    grades = extract_grades(grade_cell.get_text(strip=True)) if grade_cell else []
    return {"name": name, "weight": weight, "grades": grades, "average": 0}


def extract_course_information(row):
    name = row.find(class_=NAME_COLUMN_CLASS).get_text(strip=True)
    coefficient_cell = row.find(class_=COURSE_COEFFICIENT_CLASS)
    coefficient = None
    if coefficient_cell:
        try:
            coefficient = float(coefficient_cell.get_text(strip=True).replace(",", "."))
        except Exception:
            coefficient = None
    resit_cell = row.find(class_=RESIT_COLUMN_CLASS)
    resit = None
    if resit_cell:
        try:
            resit = float(resit_cell.get_text(strip=True).replace(",", "."))
        except Exception:
            resit = None
    return {"name": name, "coefficient": coefficient, "resit": resit, "courseParts": []}


def extract_course_number_from_rows(module_rows):
    return sum(1 for row in module_rows if row.find(class_=COURSE_ROW_CLASS))


def extract_course_from_rows(module_rows, i):
    course_rows = [row for row in module_rows if row.find(class_=COURSE_ROW_CLASS)]
    if i >= len(course_rows):
        return None
    course_row_index = module_rows.index(course_rows[i])
    next_course_row_index = (
        module_rows.index(course_rows[i + 1])
        if i + 1 < len(course_rows)
        else len(module_rows)
    )
    rows = module_rows[course_row_index:next_course_row_index]
    course = extract_course_information(rows[0])
    for row in rows[1:]:
        if row.find(class_=COURSE_PART_CLASS):
            course_part = extract_course_part_from_row(row)
            course["courseParts"].append(course_part)
    course["average"] = 0
    return course


def extract_module_information(row):
    return {"name": row.find(class_=NAME_COLUMN_CLASS).get_text(strip=True)}


def extract_module_number_from_rows(semester_rows):
    modules_rows = [
        row for row in semester_rows if row.find(class_=SEMESTER_AND_MODULE_ROW_CLASS)
    ]
    # Exclure les lignes qui sont des semestres (contenant "Semestre")
    modules_rows = [
        row
        for row in modules_rows
        if not any(s in row.get_text() for s in SEMESTER_STRINGS)
    ]
    return len(modules_rows)


def extract_module_from_rows(semester_rows, i):
    modules_rows = [
        row for row in semester_rows if row.find(class_=SEMESTER_AND_MODULE_ROW_CLASS)
    ]
    modules_rows = [
        row
        for row in modules_rows
        if not any(s in row.get_text() for s in SEMESTER_STRINGS)
    ]
    if i >= len(modules_rows):
        return None
    module_row_index = semester_rows.index(modules_rows[i])
    next_module_row_index = (
        semester_rows.index(modules_rows[i + 1])
        if i + 1 < len(modules_rows)
        else len(semester_rows)
    )
    module_rows = semester_rows[module_row_index:next_module_row_index]
    courses = []
    for j in range(extract_course_number_from_rows(module_rows)):
        course = extract_course_from_rows(module_rows, j)
        if course:
            courses.append(course)
    module = extract_module_information(module_rows[0])
    module["courses"] = courses
    module["average"] = 0
    return module


def extract_semester_information(row):
    return {"name": row.find(class_=NAME_COLUMN_CLASS).get_text(strip=True)}


def is_real_semester_row(row):
    """Vrai semestre = 'Semestre X' (X chiffre), pas 'Semestre Académique' ou autre."""
    libelle = row.find(class_=NAME_COLUMN_CLASS)
    if not libelle:
        return False
    text = libelle.get_text(strip=True)
    # Doit contenir exactement 'Semestre' suivi d'un nombre
    return re.match(r"^Semestre\s+\d+", text)


def extract_semester_from_rows(year_rows, i):
    # On sélectionne tous les vrais semestres (pas les modules, pas les intitulés spéciaux)
    semesters_and_module_rows = [
        row for row in year_rows if row.find(class_=SEMESTER_AND_MODULE_ROW_CLASS)
    ]
    semesters_rows = [
        row for row in semesters_and_module_rows if is_real_semester_row(row)
    ]
    # On ne garde que les deux premiers semestres de numéro différent
    seen = set()
    filtered_semesters = []
    for row in semesters_rows:
        libelle = row.find(class_=NAME_COLUMN_CLASS).get_text(strip=True)
        match = re.match(r"^Semestre\s+(\d+)", libelle)
        if match:
            num = match.group(1)
            if num not in seen:
                filtered_semesters.append(row)
                seen.add(num)
        if len(filtered_semesters) == 2:
            break
    if i >= len(filtered_semesters):
        return None
    semester_row_index = year_rows.index(filtered_semesters[i])
    next_semester_row_index = (
        year_rows.index(filtered_semesters[i + 1])
        if i + 1 < len(filtered_semesters)
        else len(year_rows)
    )
    semester_rows = year_rows[semester_row_index:next_semester_row_index]
    modules = []
    for j in range(extract_module_number_from_rows(semester_rows)):
        module = extract_module_from_rows(semester_rows, j)
        if module:
            modules.append(module)
    semester = extract_semester_information(semester_rows[0])
    semester["modules"] = modules
    return semester


def extract_year_information(row):
    return {"name": row.find(class_=NAME_COLUMN_CLASS).get_text(strip=True)}


def extract_year_from_rows(table_rows, i):
    years_rows = [row for row in table_rows if YEAR_ROW_CLASS in row.get("class", [])]
    if i >= len(years_rows):
        return None
    year_row_index = table_rows.index(years_rows[i])
    next_year_row_index = (
        table_rows.index(years_rows[i + 1])
        if i + 1 < len(years_rows)
        else len(table_rows)
    )
    year_rows = table_rows[year_row_index:next_year_row_index]
    semesters = []
    for j in range(SEMESTER_NUMBER):
        semester = extract_semester_from_rows(year_rows, j)
        if semester:
            semesters.append(semester)
    year = extract_year_information(year_rows[0])
    year["semesters"] = semesters
    return year


def remove_useless_parts_from_rows(table_rows):
    # En Python, on ne modifie pas le DOM, donc on ignore cette étape
    return table_rows


def extract_all_years_from_html(html_file):
    html_dom = open(html_file, "r", encoding="latin").read()
    if not html_dom:
        return []
    soup = BeautifulSoup(html_dom, "html.parser")
    table = soup.find("table", id="table_note")
    if not table:
        return []
    table_rows = table.find_all("tr")
    table_rows = remove_useless_parts_from_rows(table_rows)
    years = []
    for i in range(extract_years_count(table)):
        year = extract_year_from_rows(table_rows, i)
        if year:
            years.append(year)
    return years


if __name__ == "__main__":
    with open("src/last_dom.txt", "r", encoding="latin") as f:
        html = f.read()
    data = extract_all_years_from_html(html)
    # print(json.dumps(data, indent=2, ensure_ascii=False))
    with open("src/notes.json", "w", encoding="latin") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
