import type { FlattenedGrade } from "../types";

export type GradeFilters = {
  search: string;
  year: string;
  semester: string;
  module: string;
};

export function filterRows(
  rows: FlattenedGrade[],
  filters: GradeFilters,
): FlattenedGrade[] {
  const search = filters.search.trim().toLowerCase();
  return rows.filter((row) => {
    const matchesSearch =
      search.length === 0 ||
      row.course.toLowerCase().includes(search) ||
      row.module.toLowerCase().includes(search) ||
      row.grade_type.toLowerCase().includes(search);
    const matchesYear = !filters.year || row.year === filters.year;
    const matchesSemester =
      !filters.semester || row.semester === filters.semester;
    const matchesModule = !filters.module || row.module === filters.module;
    return matchesSearch && matchesYear && matchesSemester && matchesModule;
  });
}
