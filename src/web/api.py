from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException, Response
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

BASE_DIR = Path(__file__).resolve().parents[2]
DEFAULT_DATA_PATH = BASE_DIR / "src" / "data" / "new_grades.json"
DEFAULT_STATIC_DIR = Path(__file__).resolve().parent / "static"


def _parse_grades_file(data_path: Path) -> list[dict[str, Any]]:
    if not data_path.exists():
        raise HTTPException(
            status_code=404,
            detail={"message": f"Grades file not found: {data_path.as_posix()}"},
        )

    try:
        with data_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
    except json.JSONDecodeError as exc:
        raise HTTPException(
            status_code=500,
            detail={"message": "Invalid JSON in grades file", "error": str(exc)},
        ) from exc
    except OSError as exc:
        raise HTTPException(
            status_code=500,
            detail={"message": "Failed to read grades file", "error": str(exc)},
        ) from exc

    if not isinstance(payload, list):
        raise HTTPException(
            status_code=500,
            detail={
                "message": "Unexpected grades payload shape: expected top-level list"
            },
        )

    return payload


def _to_float(value: Any) -> float | None:
    if value is None:
        return None

    try:
        numeric = float(str(value).replace(",", ".").strip())
    except ValueError:
        return None

    if 0 <= numeric <= 20:
        return numeric
    return None


def flatten_grades(years: list[dict[str, Any]]) -> list[dict[str, Any]]:
    flattened: list[dict[str, Any]] = []

    for year in years:
        year_name = year.get("year_name", "")
        for semester in year.get("semesters", []):
            semester_name = semester.get("semester_name", "")
            for module in semester.get("semester_modules", []):
                module_name = module.get("module_name", "")
                for course in module.get("module_courses", []):
                    course_name = course.get("course_name", "")
                    for grade_type in course.get("course_grades_type", []):
                        type_name = grade_type.get("grade_type", "")
                        type_coefficient = grade_type.get("coefficient")
                        grades = grade_type.get("grades", [])

                        if not grades:
                            flattened.append(
                                {
                                    "year": year_name,
                                    "semester": semester_name,
                                    "module": module_name,
                                    "course": course_name,
                                    "grade_type": type_name,
                                    "grade_value": None,
                                    "grade_numeric": None,
                                    "grade_coef": None,
                                    "type_coefficient": type_coefficient,
                                    "status": "pending",
                                }
                            )
                            continue

                        for entry in grades:
                            raw_grade = entry.get("grade")
                            numeric_grade = _to_float(raw_grade)
                            status = (
                                "numeric" if numeric_grade is not None else "status"
                            )
                            flattened.append(
                                {
                                    "year": year_name,
                                    "semester": semester_name,
                                    "module": module_name,
                                    "course": course_name,
                                    "grade_type": type_name,
                                    "grade_value": raw_grade,
                                    "grade_numeric": numeric_grade,
                                    "grade_coef": entry.get("coef"),
                                    "type_coefficient": type_coefficient,
                                    "status": status,
                                }
                            )

    return flattened


def build_app(
    data_path: Path = DEFAULT_DATA_PATH,
    static_dir: Path = DEFAULT_STATIC_DIR,
) -> FastAPI:
    app = FastAPI(title="Grades Notifier UI API", version="1.0.0")

    @app.get("/api/grades")
    def get_grades() -> dict[str, Any]:
        years = _parse_grades_file(data_path)
        return {"years": years, "flattened": flatten_grades(years)}

    @app.get("/api/meta")
    def get_meta() -> dict[str, Any]:
        years = _parse_grades_file(data_path)
        flattened = flatten_grades(years)

        if data_path.exists():
            last_updated = datetime.fromtimestamp(
                data_path.stat().st_mtime,
                tz=timezone.utc,
            ).isoformat()
        else:
            last_updated = None

        return {
            "last_updated": last_updated,
            "filters": {
                "years": sorted({row["year"] for row in flattened if row["year"]}),
                "semesters": sorted(
                    {row["semester"] for row in flattened if row["semester"]}
                ),
                "modules": sorted(
                    {row["module"] for row in flattened if row["module"]}
                ),
            },
        }

    assets_dir = static_dir / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", response_model=None)
    def serve_spa(full_path: str) -> Response:
        if full_path.startswith("api"):
            return JSONResponse(status_code=404, content={"detail": "Not Found"})

        index_path = static_dir / "index.html"
        if index_path.exists():
            return FileResponse(index_path)

        return JSONResponse(
            status_code=200,
            content={
                "message": "Frontend build not found. Build the React app with `npm --prefix frontend run build`."
            },
        )

    return app


app = build_app()
