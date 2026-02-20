import { useEffect, useMemo, useState } from "react";
import "./index.css";
import type {
  FlattenedGrade,
  GradesResponse,
  MetaResponse,
  ThemeName,
} from "./types";
import { filterRows } from "./lib/filter";
import { getGradeColor } from "./lib/gradeColor";
import {
  applyTheme,
  getInitialThemeFromStorage,
  getStoredTheme,
  themeNames,
} from "./lib/theme";

type CourseRow = {
  key: string;
  module: string;
  course: string;
  gradesByType: Map<string, FlattenedGrade>;
};

type ModuleGroup = {
  moduleName: string;
  courses: CourseRow[];
};

function formatTimestamp(isoDate: string | null): string {
  if (!isoDate) {
    return "Unknown";
  }

  const parsed = new Date(isoDate);
  if (Number.isNaN(parsed.getTime())) {
    return "Unknown";
  }

  return parsed.toLocaleString();
}

export default function App() {
  const [theme, setTheme] = useState<ThemeName>(() =>
    getInitialThemeFromStorage(
      getStoredTheme(),
      window.matchMedia("(prefers-color-scheme: dark)").matches,
    ),
  );
  const [rows, setRows] = useState<FlattenedGrade[]>([]);
  const [meta, setMeta] = useState<MetaResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [search, setSearch] = useState("");
  const [year, setYear] = useState("");
  const [semester, setSemester] = useState("");
  const [moduleName, setModuleName] = useState("");
  const [collapsedModules, setCollapsedModules] = useState<Set<string>>(
    new Set(),
  );

  useEffect(() => {
    applyTheme(theme);
  }, [theme]);

  useEffect(() => {
    async function loadData() {
      try {
        setLoading(true);
        const [gradesRes, metaRes] = await Promise.all([
          fetch("/api/grades"),
          fetch("/api/meta"),
        ]);

        if (!gradesRes.ok) {
          throw new Error(`Grades API failed: ${gradesRes.status}`);
        }
        if (!metaRes.ok) {
          throw new Error(`Meta API failed: ${metaRes.status}`);
        }

        const gradesData = (await gradesRes.json()) as GradesResponse;
        const metaData = (await metaRes.json()) as MetaResponse;

        setRows(gradesData.flattened);
        setMeta(metaData);
        setError(null);
      } catch (err) {
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        setLoading(false);
      }
    }

    void loadData();
  }, []);

  const filteredRows = useMemo(
    () =>
      filterRows(rows, {
        search,
        year,
        semester,
        module: moduleName,
      }),
    [rows, search, year, semester, moduleName],
  );

  const { moduleGroups, gradeTypes } = useMemo(() => {
    const courseMap = new Map<string, CourseRow>();
    const gradeTypesSet = new Set<string>();

    for (const row of filteredRows) {
      const key = `${row.module}::${row.course}`;
      if (!courseMap.has(key)) {
        courseMap.set(key, {
          key,
          module: row.module,
          course: row.course,
          gradesByType: new Map(),
        });
      }

      const courseRow = courseMap.get(key)!;
      courseRow.gradesByType.set(row.grade_type, row);
      gradeTypesSet.add(row.grade_type);
    }

    const sortedGradeTypes = Array.from(gradeTypesSet).sort();
    const sortedCourseRows = Array.from(courseMap.values());

    // Group courses by module
    const moduleMap = new Map<string, CourseRow[]>();
    for (const courseRow of sortedCourseRows) {
      if (!moduleMap.has(courseRow.module)) {
        moduleMap.set(courseRow.module, []);
      }
      moduleMap.get(courseRow.module)!.push(courseRow);
    }

    const groups: ModuleGroup[] = Array.from(moduleMap.entries())
      .map(([moduleName, courses]) => ({
        moduleName,
        courses,
      }))
      .sort((a, b) => a.moduleName.localeCompare(b.moduleName));

    return { moduleGroups: groups, gradeTypes: sortedGradeTypes };
  }, [filteredRows]);

  const toggleModule = (moduleName: string) => {
    setCollapsedModules((prev) => {
      const next = new Set(prev);
      if (next.has(moduleName)) {
        next.delete(moduleName);
      } else {
        next.add(moduleName);
      }
      return next;
    });
  };

  return (
    <main className="min-h-screen bg-base px-4 py-6 md:px-8">
      <section className="mx-auto flex w-full max-w-7xl flex-col gap-4">
        <header className="card flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
          <div>
            <h1 className="text-2xl font-semibold">Grades Notifier UI</h1>
            <p className="text-sm text-subtext0">
              Last update: {formatTimestamp(meta?.last_updated ?? null)}
            </p>
          </div>

          <label className="flex items-center gap-2 text-sm">
            Theme
            <select
              value={theme}
              onChange={(event) => setTheme(event.target.value as ThemeName)}
              className="min-w-40"
            >
              {themeNames.map((option) => (
                <option key={option} value={option}>
                  {option}
                </option>
              ))}
            </select>
          </label>
        </header>

        <section className="card grid grid-cols-1 gap-3 md:grid-cols-4">
          <input
            placeholder="Search course/module/type"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
          />
          <select
            value={year}
            onChange={(event) => setYear(event.target.value)}
          >
            <option value="">All years</option>
            {meta?.filters.years.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
          <select
            value={semester}
            onChange={(event) => setSemester(event.target.value)}
          >
            <option value="">All semesters</option>
            {meta?.filters.semesters.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
          <select
            value={moduleName}
            onChange={(event) => setModuleName(event.target.value)}
          >
            <option value="">All modules</option>
            {meta?.filters.modules.map((value) => (
              <option key={value} value={value}>
                {value}
              </option>
            ))}
          </select>
        </section>

        {loading ? <p className="text-subtext0">Loading grades...</p> : null}
        {error ? (
          <p className="rounded-md bg-red-600/20 p-3 text-sm text-text">
            {error}
          </p>
        ) : null}

        {!loading && !error && moduleGroups.length === 0 ? (
          <p className="card text-subtext0">
            No grades match the current filters.
          </p>
        ) : null}

        {!loading && !error && moduleGroups.length > 0 ? (
          <div className="card overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr>
                  <th className="sticky left-0 bg-base p-3 text-left text-sm font-semibold uppercase tracking-wide text-subtext0">
                    Course
                  </th>
                  {gradeTypes.map((gradeType) => (
                    <th
                      key={gradeType}
                      className="min-w-32 p-3 text-center text-sm font-semibold uppercase tracking-wide text-subtext0"
                    >
                      {gradeType}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {moduleGroups.map((moduleGroup) => (
                  <>
                    <tr
                      key={`module-${moduleGroup.moduleName}`}
                      className="cursor-pointer bg-surface0 hover:bg-surface1"
                      onClick={() => toggleModule(moduleGroup.moduleName)}
                    >
                      <td
                        colSpan={1 + gradeTypes.length}
                        className="p-3 text-left font-bold text-text"
                      >
                        <div className="flex items-center gap-2">
                          <span
                            className={`module-arrow text-lg transition-transform duration-300 ${
                              collapsedModules.has(moduleGroup.moduleName)
                                ? "-rotate-90"
                                : ""
                            }`}
                          >
                            ▼
                          </span>
                          <span>{moduleGroup.moduleName}</span>
                        </div>
                      </td>
                    </tr>
                    {moduleGroup.courses.map((courseRow) => {
                      const isCollapsed = collapsedModules.has(
                        moduleGroup.moduleName,
                      );
                      return (
                        <tr
                          key={courseRow.key}
                          className="hover:bg-surface0/50"
                        >
                          <td className="sticky left-0 bg-base pl-12 overflow-hidden p-0">
                            <div
                              className={`font-medium transition-all duration-300 ease-in-out overflow-hidden ${
                                isCollapsed
                                  ? "max-h-0 opacity-0 py-0"
                                  : "max-h-16 opacity-100 py-3"
                              }`}
                            >
                              {courseRow.course}
                            </div>
                          </td>
                          {gradeTypes.map((gradeType) => {
                            const grade = courseRow.gradesByType.get(gradeType);
                            if (!grade) {
                              return (
                                <td
                                  key={gradeType}
                                  className="text-center text-subtext0 overflow-hidden p-0"
                                >
                                  <div
                                    className={`transition-all duration-300 ease-in-out overflow-hidden ${
                                      isCollapsed
                                        ? "max-h-0 opacity-0 py-0"
                                        : "max-h-16 opacity-100 py-3"
                                    }`}
                                  >
                                    —
                                  </div>
                                </td>
                              );
                            }

                            const color = getGradeColor(
                              grade.grade_numeric,
                              theme,
                            );
                            const displayValue =
                              grade.grade_value ??
                              (grade.status === "pending"
                                ? "Pending"
                                : "Status");

                            return (
                              <td
                                key={gradeType}
                                className="overflow-hidden p-0"
                              >
                                <div
                                  className={`transition-all duration-300 ease-in-out overflow-hidden ${
                                    isCollapsed
                                      ? "max-h-0 opacity-0 py-0"
                                      : "max-h-16 opacity-100 py-3"
                                  }`}
                                >
                                  <div
                                    className="rounded-lg p-2 text-center font-semibold"
                                    style={{
                                      backgroundColor: color.background,
                                      color: color.color,
                                    }}
                                    title={`Entry coef: ${grade.grade_coef ?? "-"} | Type coef: ${grade.type_coefficient ?? "-"}`}
                                  >
                                    {displayValue}
                                  </div>
                                </div>
                              </td>
                            );
                          })}
                        </tr>
                      );
                    })}
                  </>
                ))}
              </tbody>
            </table>
          </div>
        ) : null}
      </section>
    </main>
  );
}
