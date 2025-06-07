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
    """
    Extract the number of years from the table.
    This function counts the number of rows in the table that have the class "master",
    which indicates a year row. It returns the count of such rows.

    @param table: The BeautifulSoup table object containing the grades.
    @return: The number of years found in the table.
    """
    return len(table.find_all("tr", class_=YEAR_ROW_CLASS))


def extract_grades(cell_text):
    """
    Extract grades from a cell text.
    This function processes the cell text to extract individual grades,
    their values, and weights. It handles cases where grades are separated by " - "
    and where weights are enclosed in parentheses.

    @param cell_text: The text content of the cell containing grades.
    @return: A list of dictionaries, each containing a grade value and its weight.
    """
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
    """
    Extract course part information from a row.

    @param row: The row containing the course part information.
    @return: A dictionary representing the course part with its name, weight, and grades.
    """
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
    """
    Extract course information from a row.

    @param row: The row containing the course information.
    @return: A dictionary representing the course with its name, coefficient, resit, and course parts.
    """
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
    """
    Extract the number of courses from the module rows.
    This function counts the number of course rows in the provided module rows,
    excluding rows that do not contain course information.

    @param module_rows: The list of rows for the module containing the courses.
    @return: The number of courses in the module.
    """
    return sum(1 for row in module_rows if row.find(class_=COURSE_ROW_CLASS))


def extract_course_from_rows(module_rows, i):
    """
    Extract a course from the module rows.
    This function extracts the course information, course parts, and grades
    from the provided module rows based on the index of the course.

    @param module_rows: The list of rows for the module containing the courses.
    @param i: The index of the course to extract.
    @return: A dictionary representing the course with its parts and grades.
    """
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
    """
    Extract module information from a row.

    @param row: The row containing the module information.
    @return: A dictionary representing the module with its name.
    """
    return {"name": row.find(class_=NAME_COLUMN_CLASS).get_text(strip=True)}


def extract_module_number_from_rows(semester_rows):
    """
    Extract the number of modules from the semester rows.
    This function counts the number of module rows in the provided semester rows,
    excluding semester rows and special titles like "Semestre Académique".

    @param semester_rows: The list of rows for the semester containing the modules.
    @return: The number of modules in the semester.
    """
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
    """Extract a module from the semester rows.
    This function extracts the module information, courses, and course parts
    from the provided semester rows based on the index of the module.

    @param semester_rows: The list of rows for the semester containing the modules.
    @param i: The index of the module to extract.
    @return: A dictionary representing the module with its courses and course parts.
    """
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
    """
    Extract semester information from a row.

    @param row: The row containing the semester information.
    @return: A dictionary representing the semester with its name.
    """
    return {"name": row.find(class_=NAME_COLUMN_CLASS).get_text(strip=True)}


def is_real_semester_row(row):
    """
    Check if the row is a real semester row.

    @param row: The row to check.
    @return: True if the row is a real semester row, False otherwise.
    """
    """True semester = 'Semestre X' (X number), not 'Semestre Académique' or anything else."""
    libelle = row.find(class_=NAME_COLUMN_CLASS)
    if not libelle:
        return False
    text = libelle.get_text(strip=True)
    # Doit contenir exactement 'Semestre' suivi d'un nombre
    return re.match(r"^Semestre\s+\d+", text)


def extract_semester_from_rows(year_rows, i):
    """
    Extract a semester from the year rows.
    This function extracts the semester information, modules, courses, and course parts
    from the provided year rows based on the index of the semester.

    @param year_rows: The list of rows for the year containing the semesters.
    @param i: The index of the semester to extract.
    @return: A dictionary representing the semester with its modules, courses, and course parts.
    """
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
    """
    Extract year information from a row.

    @param row: The row containing the year information.
    @return: A dictionary representing the year with its name.
    """
    return {"name": row.find(class_=NAME_COLUMN_CLASS).get_text(strip=True)}


def extract_year_from_rows(table_rows, i):
    """
    Extract a year from the table rows.
    This function extracts the year information, semesters, modules, courses, and course parts
    from the provided table rows based on the index of the year.

    @param table_rows: The list of table rows containing the grades.
    @param i: The index of the year to extract.
    @return: A dictionary representing the year with its semesters, modules, courses, and course parts.
    """
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


def extract_all_years_from_html(html_file):
    """Extract all years from the HTML file.
    This function reads the HTML file, parses it with BeautifulSoup,
    and extracts the years, semesters, modules, courses, and course parts.

    @param html_file: The path to the HTML file containing the grades.
    @return: A list of dictionaries, each representing a year with its semesters, modules, courses, and course parts.
    """
    html_dom = open(html_file, "r", encoding="latin").read()
    if not html_dom:
        return []
    soup = BeautifulSoup(html_dom, "html.parser")
    table = soup.find("table", id="table_note")
    if not table:
        return []
    table_rows = table.find_all("tr")
    years = []
    for i in range(extract_years_count(table)):
        year = extract_year_from_rows(table_rows, i)
        if year:
            years.append(year)
    return years


if __name__ == "__main__":
    with open("src/data/last_dom.txt", "r", encoding="latin") as f:
        html = f.read()
    data = extract_all_years_from_html(html)
    # print(json.dumps(data, indent=2, ensure_ascii=False))
    with open("src/data/notes.json", "w", encoding="latin") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
