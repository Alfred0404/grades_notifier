export type ThemeName = "light" | "dark";

export type FlattenedGrade = {
  year: string;
  semester: string;
  module: string;
  course: string;
  grade_type: string;
  grade_value: string | null;
  grade_numeric: number | null;
  grade_coef: string | null;
  type_coefficient: number | null;
  status: "numeric" | "status" | "pending";
};

export type GradesResponse = {
  years: unknown[];
  flattened: FlattenedGrade[];
};

export type MetaResponse = {
  last_updated: string | null;
  filters: {
    years: string[];
    semesters: string[];
    modules: string[];
  };
};
