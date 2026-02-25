from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from src.web.api import build_app


def write_grades(path: Path) -> None:
    payload = [
        {
            "year_name": "Y1",
            "semesters": [
                {
                    "semester_name": "S1",
                    "semester_modules": [
                        {
                            "module_name": "M1",
                            "module_courses": [
                                {
                                    "course_name": "Course A",
                                    "course_grades_type": [
                                        {
                                            "grade_type": "Exam",
                                            "coefficient": 100.0,
                                            "grades": [{"grade": "15.0", "coef": "100"}],
                                        }
                                    ],
                                }
                            ],
                        }
                    ],
                }
            ],
        }
    ]
    path.write_text(json.dumps(payload), encoding="latin")


def test_api_grades_success(tmp_path: Path) -> None:
    grades_file = tmp_path / "new_grades.json"
    static_dir = tmp_path / "static"
    static_dir.mkdir(parents=True, exist_ok=True)
    write_grades(grades_file)

    client = TestClient(build_app(data_path=grades_file, static_dir=static_dir))
    response = client.get("/api/grades")

    assert response.status_code == 200
    body = response.json()
    assert "years" in body
    assert "flattened" in body
    assert len(body["flattened"]) == 1
    assert body["flattened"][0]["grade_numeric"] == 15.0


def test_api_grades_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.json"
    client = TestClient(build_app(data_path=missing, static_dir=tmp_path / "static"))

    response = client.get("/api/grades")

    assert response.status_code == 404


def test_api_grades_invalid_json(tmp_path: Path) -> None:
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{bad json", encoding="latin")
    client = TestClient(build_app(data_path=invalid, static_dir=tmp_path / "static"))

    response = client.get("/api/grades")

    assert response.status_code == 500


def test_api_meta_filters(tmp_path: Path) -> None:
    grades_file = tmp_path / "new_grades.json"
    write_grades(grades_file)
    client = TestClient(build_app(data_path=grades_file, static_dir=tmp_path / "static"))

    response = client.get("/api/meta")

    assert response.status_code == 200
    body = response.json()
    assert body["filters"]["years"] == ["Y1"]
    assert body["filters"]["semesters"] == ["S1"]
    assert body["filters"]["modules"] == ["M1"]
