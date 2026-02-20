<script setup lang="ts">
import { ref, computed, watch, onMounted } from "vue";
import Button from "primevue/button";
import InputText from "primevue/inputtext";
import Select from "primevue/select";
import Skeleton from "primevue/skeleton";
import Message from "primevue/message";
import type {
  FlattenedGrade,
  GradesResponse,
  MetaResponse,
  ThemeName,
} from "./types";
import { filterRows } from "./lib/filter";
import { getGradeColor } from "./lib/gradeColor";
import { initTheme, applyTheme } from "./lib/theme";

// ─── Theme ───────────────────────────────────────────────────────────────────
const theme = ref<ThemeName>(initTheme());
const isDark = computed(() => theme.value === "dark");

function toggleTheme() {
  const next: ThemeName = isDark.value ? "light" : "dark";
  theme.value = next;
  applyTheme(next);
}

// ─── Data ────────────────────────────────────────────────────────────────────
const rows = ref<FlattenedGrade[]>([]);
const meta = ref<MetaResponse | null>(null);
const loading = ref(true);
const fetchError = ref<string | null>(null);

onMounted(async () => {
  try {
    const [gradesRes, metaRes] = await Promise.all([
      fetch("/api/grades"),
      fetch("/api/meta"),
    ]);
    if (!gradesRes.ok) throw new Error(`Grades API: ${gradesRes.status}`);
    if (!metaRes.ok) throw new Error(`Meta API: ${metaRes.status}`);
    const gradesJson: GradesResponse = await gradesRes.json();
    const metaJson: MetaResponse = await metaRes.json();
    rows.value = gradesJson.flattened ?? [];
    meta.value = metaJson;
  } catch (e) {
    fetchError.value = (e as Error).message;
  } finally {
    loading.value = false;
  }
});

// ─── Filters ─────────────────────────────────────────────────────────────────
const searchInput = ref("");
const searchDebounced = ref("");
const yearFilter = ref<string | null>(null);
const semFilter = ref<string | null>(null);
const modFilter = ref<string | null>(null);

let debounceTimer: ReturnType<typeof setTimeout>;
watch(searchInput, (val) => {
  clearTimeout(debounceTimer);
  debounceTimer = setTimeout(() => {
    searchDebounced.value = val;
  }, 250);
});

const hasFilters = computed(
  () =>
    searchDebounced.value.length > 0 ||
    !!yearFilter.value ||
    !!semFilter.value ||
    !!modFilter.value,
);

function resetFilters() {
  searchInput.value = "";
  searchDebounced.value = "";
  yearFilter.value = null;
  semFilter.value = null;
  modFilter.value = null;
}

// ─── Derived data ─────────────────────────────────────────────────────────────
type CourseRow = {
  course: string;
  gradesByType: Record<string, FlattenedGrade>;
};
type ModuleGroup = { moduleName: string; courses: CourseRow[] };

const filtered = computed(() =>
  filterRows(rows.value, {
    search: searchDebounced.value,
    year: yearFilter.value ?? "",
    semester: semFilter.value ?? "",
    module: modFilter.value ?? "",
  }),
);

const gradeTypes = computed(() => {
  const types = new Set<string>();
  for (const r of filtered.value) types.add(r.grade_type);
  return [...types].sort();
});

const moduleGroups = computed((): ModuleGroup[] => {
  const modMap = new Map<string, Map<string, Record<string, FlattenedGrade>>>();
  for (const row of filtered.value) {
    if (!modMap.has(row.module)) modMap.set(row.module, new Map());
    const courseMap = modMap.get(row.module)!;
    if (!courseMap.has(row.course)) courseMap.set(row.course, {});
    courseMap.get(row.course)![row.grade_type] = row;
  }
  return [...modMap.entries()].map(([moduleName, courseMap]) => ({
    moduleName,
    courses: [...courseMap.entries()].map(([course, gradesByType]) => ({
      course,
      gradesByType,
    })),
  }));
});

// ─── Collapse ────────────────────────────────────────────────────────────────
const collapsedModules = ref(new Set<string>());

function toggleModule(mod: string) {
  const next = new Set(collapsedModules.value);
  if (next.has(mod)) next.delete(mod);
  else next.add(mod);
  collapsedModules.value = next;
}

const allOpen = computed(
  () => moduleGroups.value.length > 0 && collapsedModules.value.size === 0,
);

function expandAll() {
  collapsedModules.value = new Set();
}
function collapseAll() {
  collapsedModules.value = new Set(moduleGroups.value.map((g) => g.moduleName));
}

// ─── Averages ────────────────────────────────────────────────────────────────
const weightedAverage = computed(() => {
  const nums = filtered.value.filter(
    (r) => r.grade_numeric !== null && r.type_coefficient !== null,
  );
  if (nums.length === 0) return null;
  const totalW = nums.reduce((s, r) => s + r.type_coefficient!, 0);
  if (totalW === 0) return null;
  return (
    nums.reduce((s, r) => s + r.grade_numeric! * r.type_coefficient!, 0) /
    totalW
  );
});

function moduleAvg(group: ModuleGroup): number | null {
  const nums = group.courses.flatMap((c) =>
    Object.values(c.gradesByType).filter((r) => r.grade_numeric !== null),
  );
  if (nums.length === 0) return null;
  return nums.reduce((s, r) => s + r.grade_numeric!, 0) / nums.length;
}

// ─── Helpers ─────────────────────────────────────────────────────────────────
function displayGrade(g: FlattenedGrade): string {
  if (g.status === "pending") return "—";
  if (g.status === "status") return g.grade_value ?? "—";
  return g.grade_numeric !== null ? g.grade_numeric.toFixed(2) : "—";
}

function chipStyle(grade: number | null) {
  const c = getGradeColor(grade, isDark.value);
  return {
    backgroundColor: c.background,
    color: c.color,
  };
}

function highlight(text: string, query: string): string {
  if (!query.trim()) return text;
  const idx = text.toLowerCase().indexOf(query.toLowerCase());
  if (idx === -1) return text;
  return (
    text.slice(0, idx) +
    `<mark>${text.slice(idx, idx + query.length)}</mark>` +
    text.slice(idx + query.length)
  );
}
</script>

<template>
  <div>
    <!-- ─── Header ─── -->
    <header class="app-header">
      <div class="header-inner">
        <div class="header-left">
          <span class="app-title">Grades</span>
          <span v-if="meta?.last_updated" class="last-updated">
            Updated {{ new Date(meta.last_updated).toLocaleString() }}
          </span>
          <span
            v-if="weightedAverage !== null"
            class="grade-chip avg-chip"
            :style="chipStyle(weightedAverage)"
          >
            Avg {{ weightedAverage.toFixed(2) }} / 20
          </span>
        </div>
        <Button
          :icon="isDark ? 'pi pi-moon' : 'pi pi-sun'"
          text
          rounded
          severity="secondary"
          :aria-label="isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          @click="toggleTheme"
        />
      </div>
    </header>

    <div class="app-body">
      <!-- ─── Filters ─── -->
      <div class="filter-bar">
        <div class="filter-search">
          <InputText
            v-model="searchInput"
            placeholder="Search courses…"
            fluid
          />
        </div>
        <Select
          v-model="yearFilter"
          :options="meta?.filters.years ?? []"
          placeholder="All years"
          show-clear
          class="filter-select"
        />
        <Select
          v-model="semFilter"
          :options="meta?.filters.semesters ?? []"
          placeholder="All semesters"
          show-clear
          class="filter-select"
        />
        <Select
          v-model="modFilter"
          :options="meta?.filters.modules ?? []"
          placeholder="All modules"
          show-clear
          class="filter-select filter-select--wide"
        />
        <Button
          v-if="hasFilters"
          v-tooltip.top="'Reset filters'"
          icon="pi pi-filter-slash"
          text
          rounded
          severity="secondary"
          aria-label="Reset filters"
          @click="resetFilters"
        />
      </div>

      <!-- ─── Toolbar row ─── -->
      <div v-if="!loading && moduleGroups.length > 1" class="toolbar-row">
        <span class="result-count">
          {{ filtered.length }} grade{{ filtered.length !== 1 ? "s" : "" }}
          &nbsp;·&nbsp;
          {{ moduleGroups.length }} module{{
            moduleGroups.length !== 1 ? "s" : ""
          }}
        </span>
        <button class="text-btn" @click="allOpen ? collapseAll() : expandAll()">
          {{ allOpen ? "Collapse all" : "Expand all" }}
        </button>
      </div>

      <!-- ─── Loading ─── -->
      <template v-if="loading">
        <Skeleton
          height="3.5rem"
          style="border-radius: 8px; margin-bottom: 0.5rem"
        />
        <Skeleton
          height="3.5rem"
          style="border-radius: 8px; margin-bottom: 0.5rem"
        />
        <Skeleton height="3.5rem" style="border-radius: 8px" />
      </template>

      <!-- ─── Error ─── -->
      <Message v-else-if="fetchError" severity="error" :closable="false">
        {{ fetchError }}
      </Message>

      <!-- ─── Empty ─── -->
      <Message
        v-else-if="!loading && moduleGroups.length === 0"
        severity="secondary"
        :closable="false"
      >
        No grades match the current filters.
      </Message>

      <!-- ─── Pivot table ─── -->
      <div v-else class="table-wrapper">
        <table class="grades-table">
          <thead>
            <tr>
              <th>Course</th>
              <th v-for="gt in gradeTypes" :key="gt" class="grade-col">
                {{ gt }}
              </th>
            </tr>
          </thead>
          <tbody>
            <template v-for="group in moduleGroups" :key="group.moduleName">
              <!-- Module header row -->
              <tr class="module-row" @click="toggleModule(group.moduleName)">
                <td :colspan="1 + gradeTypes.length">
                  <div class="cell-inner module-cell">
                    <i
                      class="pi pi-chevron-down module-arrow"
                      :class="{
                        'module-arrow--collapsed': collapsedModules.has(
                          group.moduleName,
                        ),
                      }"
                    />
                    <!-- eslint-disable-next-line vue/no-v-html -->
                    <span
                      v-html="highlight(group.moduleName, searchDebounced)"
                    />
                    <span class="module-badge">
                      {{ group.courses.length }}
                      course{{ group.courses.length !== 1 ? "s" : "" }}
                    </span>
                    <span
                      v-if="moduleAvg(group) !== null"
                      class="grade-chip"
                      :style="chipStyle(moduleAvg(group))"
                    >
                      {{ moduleAvg(group)!.toFixed(2) }}
                    </span>
                  </div>
                </td>
              </tr>

              <!-- Course rows -->
              <tr
                v-for="course in group.courses"
                :key="`${group.moduleName}::${course.course}`"
                class="course-row"
              >
                <!-- Course name -->
                <td>
                  <div
                    class="cell-inner"
                    :class="{
                      'cell-inner--hidden': collapsedModules.has(
                        group.moduleName,
                      ),
                    }"
                  >
                    <!-- eslint-disable-next-line vue/no-v-html -->
                    <span v-html="highlight(course.course, searchDebounced)" />
                  </div>
                </td>

                <!-- Grade cells -->
                <td v-for="gt in gradeTypes" :key="gt" class="grade-td">
                  <div
                    class="cell-inner cell-inner--center"
                    :class="{
                      'cell-inner--hidden': collapsedModules.has(
                        group.moduleName,
                      ),
                    }"
                  >
                    <span
                      v-if="course.gradesByType[gt]"
                      v-tooltip.top="{
                        value: `Entry coef: ${course.gradesByType[gt].grade_coef ?? '—'} | Type coef: ${course.gradesByType[gt].type_coefficient ?? '—'}`,
                        showDelay: 400,
                      }"
                      class="grade-chip"
                      :class="{
                        'grade-chip--pending':
                          course.gradesByType[gt].status === 'pending',
                      }"
                      :style="
                        course.gradesByType[gt].status === 'numeric'
                          ? chipStyle(course.gradesByType[gt].grade_numeric)
                          : {}
                      "
                    >
                      {{ displayGrade(course.gradesByType[gt]) }}
                    </span>
                    <span v-else class="no-grade">—</span>
                  </div>
                </td>
              </tr>
            </template>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* ─── Layout ─── */
.header-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  max-width: 1200px;
  margin: 0 auto;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.app-title {
  font-size: 1.2rem;
  font-weight: 700;
  letter-spacing: -0.01em;
}

.last-updated {
  font-size: 0.72rem;
  color: var(--p-text-muted-color);
}

.avg-chip {
  font-size: 0.78rem;
}

.app-body {
  max-width: 1200px;
  margin: 0 auto;
  padding: 1.1rem 1.1rem 2rem;
}

/* ─── Filters ─── */
.filter-bar {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  flex-wrap: wrap;
  background: var(--p-surface-card);
  border: 1px solid var(--p-content-border-color);
  border-radius: 10px;
  padding: 0.8rem 1rem;
  margin-bottom: 0.75rem;
}

.filter-search {
  flex: 1 1 180px;
  min-width: 150px;
}

.filter-select {
  flex: 1 1 130px;
  min-width: 110px;
}

.filter-select--wide {
  flex: 1.5 1 180px;
}

/* ─── Toolbar ─── */
.toolbar-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.6rem;
  font-size: 0.78rem;
  color: var(--p-text-muted-color);
}

.result-count {
  flex: 1;
}

.text-btn {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--p-primary-color);
  font-size: 0.78rem;
  font-family: inherit;
  padding: 2px 4px;
}

.text-btn:hover {
  text-decoration: underline;
}

/* ─── Table wrapper ─── */
.table-wrapper {
  background: var(--p-surface-card);
  border: 1px solid var(--p-content-border-color);
  border-radius: 10px;
  overflow: hidden;
  overflow-x: auto;
}

/* ─── Grade table (global styles are in style.css) ─── */

/* ─── Module row ─── */
.module-cell {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
}

.module-arrow {
  font-size: 0.7rem;
  color: var(--p-text-muted-color);
  transition: transform 0.2s ease;
}

.module-arrow--collapsed {
  transform: rotate(-90deg);
}

.module-badge {
  font-size: 0.7rem;
  font-weight: 500;
  color: var(--p-text-muted-color);
  background: var(--p-surface-ground);
  border: 1px solid var(--p-content-border-color);
  border-radius: 20px;
  padding: 0.08rem 0.45rem;
}

/* ─── Cell collapse animation ─── */
.cell-inner {
  overflow: hidden;
  transition:
    max-height 0.22s ease,
    opacity 0.22s ease,
    padding 0.22s ease;
  max-height: 5rem;
  opacity: 1;
  padding: 0.55rem 0.85rem;
}

.cell-inner--hidden {
  max-height: 0 !important;
  opacity: 0;
  padding-top: 0;
  padding-bottom: 0;
}

.cell-inner--center {
  display: flex;
  justify-content: center;
}

/* ─── Grade chip ─── */
.grade-chip {
  display: inline-block;
  border-radius: 6px;
  padding: 0.2rem 0.55rem;
  font-weight: 600;
  font-size: 0.82rem;
  text-align: center;
  min-width: 3.2rem;
  white-space: nowrap;
}

.grade-chip--pending {
  opacity: 0.45;
  font-style: italic;
  font-weight: 400;
}

.no-grade {
  color: var(--p-text-muted-color);
  font-size: 0.85rem;
}

.grade-td {
  text-align: center;
}
</style>
