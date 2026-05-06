import { useMemo, useState } from "react";
import { Activity, Users, Building2, Target, Clock, AlertTriangle, Search, Download, BarChart3, Sliders, ChevronDown, ChevronUp, Moon, Sun } from "lucide-react";
import { Bar, BarChart, CartesianGrid, XAxis, YAxis } from "recharts";
import { ChartContainer, ChartLegend, ChartLegendContent, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";
import { useTheme } from "@/context/ThemeContext";

interface CityAllocation {
  city: string;
  allocated_refugees: number;
  capacity: number;
  usage_percent?: number;
  utilization_band?: "normal" | "high" | "critical";
}

interface OptimizationResult {
  original_refugees: number;
  grouped_clusters: number;
  cities: number;
  objective_value: number;
  total_allocated_refugees: number;
  unallocated_refugees: number;
  runtime_seconds: number;
  coverage_percent?: number;
  score_per_allocated?: number;
  optimization_status?: "optimal" | "feasible" | "infeasible";
  generated_at?: string;
  scenario?: string;
  scenario_label?: string;
  scenario_description?: string;
  baseline?: {
    method: string;
    objective_value: number;
    total_allocated_refugees: number;
    unallocated_refugees: number;
    coverage_percent: number;
    score_per_allocated: number;
    runtime_seconds?: number;
    city_allocations: CityAllocation[];
  };
  model_comparison?: {
    baseline_method: string;
    objective_delta: number;
    objective_uplift_percent: number | null;
    allocated_delta: number;
    coverage_delta_points: number;
    unallocated_reduction: number;
    score_per_allocated_delta: number;
    runtime_delta_seconds?: number;
    total_city_reallocation?: number;
    cities_with_different_allocations?: number;
    max_city_shift?: number;
    allocation_overlap_percent?: number;
    winner: "model" | "baseline";
  };
  city_allocations: CityAllocation[];
}

type UsageFilter = "all" | "normal" | "high" | "critical";
type SortBy = "usage_desc" | "usage_asc" | "allocated_desc" | "capacity_desc" | "city_asc";
type ScenarioPreset = "balanced" | "capacity_stress" | "jobs_priority" | "integration_priority" | "custom";

const SCENARIO_OPTIONS: { value: ScenarioPreset; label: string }[] = [
  { value: "balanced", label: "Balanced" },
  { value: "capacity_stress", label: "Capacity Stress" },
  { value: "jobs_priority", label: "Jobs Priority" },
  { value: "integration_priority", label: "Integration Priority" },
  { value: "custom", label: "Custom Weights" },
];

const Dashboard = () => {
  const { isDark, toggleDarkMode } = useTheme();
  const [data, setData] = useState<OptimizationResult | null>(null);
  const [runHistory, setRunHistory] = useState<OptimizationResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [exportingCsv, setExportingCsv] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [usageFilter, setUsageFilter] = useState<UsageFilter>("all");
  const [sortBy, setSortBy] = useState<SortBy>("usage_desc");
  const [scenario, setScenario] = useState<ScenarioPreset>("balanced");
  const [showCustomWeights, setShowCustomWeights] = useState(false);
  const [customWeights, setCustomWeights] = useState({
    language: 0.25,
    skill_match: 0.25,
    education: 0.2,
    cost_match: 0.1,
    employment: 0.1,
    adaptability: 0.05,
    trauma_penalty: 0.01,
    diaspora_support: 0.08,
    integration_policy: 0.08,
    unallocated_penalty: 0.03,
  });
  const [capacityScale, setCapacityScale] = useState(1.0);

  const runOptimization = async () => {
    setLoading(true);
    setError(null);
    try {
      let url = `http://localhost:5000/optimize?scenario=${encodeURIComponent(scenario)}`;
      
      if (scenario === "custom") {
        url += `&custom_weights=true`;
        url += `&weight_language=${customWeights.language}`;
        url += `&weight_skill_match=${customWeights.skill_match}`;
        url += `&weight_education=${customWeights.education}`;
        url += `&weight_cost_match=${customWeights.cost_match}`;
        url += `&weight_employment=${customWeights.employment}`;
        url += `&weight_adaptability=${customWeights.adaptability}`;
        url += `&weight_trauma_penalty=${customWeights.trauma_penalty}`;
        url += `&weight_diaspora_support=${customWeights.diaspora_support}`;
        url += `&weight_integration_policy=${customWeights.integration_policy}`;
        url += `&weight_unallocated_penalty=${customWeights.unallocated_penalty}`;
        url += `&capacity_scale=${capacityScale}`;
      }
      
      const res = await fetch(url);
      if (!res.ok) throw new Error(`Server responded with ${res.status}`);
      const json: OptimizationResult = await res.json();
      setData(json);
      setRunHistory((prev) => [json, ...prev].slice(0, 2));
    } catch (err: any) {
      setError(err.message || "Failed to connect to the optimization server.");
    } finally {
      setLoading(false);
    }
  };

  const exportCsv = async () => {
    setExportingCsv(true);
    setError(null);

    try {
      let apiUrl = `http://localhost:5000/optimize/export.csv?scenario=${encodeURIComponent(scenario)}`;
      
      if (scenario === "custom") {
        apiUrl += `&custom_weights=true`;
        apiUrl += `&weight_language=${customWeights.language}`;
        apiUrl += `&weight_skill_match=${customWeights.skill_match}`;
        apiUrl += `&weight_education=${customWeights.education}`;
        apiUrl += `&weight_cost_match=${customWeights.cost_match}`;
        apiUrl += `&weight_employment=${customWeights.employment}`;
        apiUrl += `&weight_adaptability=${customWeights.adaptability}`;
        apiUrl += `&weight_trauma_penalty=${customWeights.trauma_penalty}`;
        apiUrl += `&weight_diaspora_support=${customWeights.diaspora_support}`;
        apiUrl += `&weight_integration_policy=${customWeights.integration_policy}`;
        apiUrl += `&weight_unallocated_penalty=${customWeights.unallocated_penalty}`;
        apiUrl += `&capacity_scale=${capacityScale}`;
      }
      
      const res = await fetch(apiUrl);
      if (!res.ok) throw new Error(`Server responded with ${res.status}`);

      const blob = await res.blob();
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url;
      link.download = `city_allocations_${new Date().toISOString().replace(/[:.]/g, "-")}.csv`;
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    } catch (err: any) {
      setError(err.message || "Failed to export CSV from the optimization server.");
    } finally {
      setExportingCsv(false);
    }
  };

  const allocations = useMemo(() => {
    if (!data) return [];

    return data.city_allocations.map((city) => {
      const safeCapacity = city.capacity || 0;
      const usagePercent =
        typeof city.usage_percent === "number"
          ? city.usage_percent
          : safeCapacity > 0
            ? Number(((city.allocated_refugees / safeCapacity) * 100).toFixed(1))
            : 0;

      const utilizationBand = city.utilization_band || getUtilizationBand(usagePercent);

      return {
        ...city,
        usage_percent: usagePercent,
        utilization_band: utilizationBand,
      };
    });
  }, [data]);

  const filteredSortedAllocations = useMemo(() => {
    const normalizedQuery = searchQuery.trim().toLowerCase();

    let rows = allocations.filter((city) => city.city.toLowerCase().includes(normalizedQuery));

    if (usageFilter !== "all") {
      rows = rows.filter((city) => city.utilization_band === usageFilter);
    }

    const sorted = [...rows];
    switch (sortBy) {
      case "usage_asc":
        sorted.sort((a, b) => (a.usage_percent ?? 0) - (b.usage_percent ?? 0));
        break;
      case "allocated_desc":
        sorted.sort((a, b) => b.allocated_refugees - a.allocated_refugees);
        break;
      case "capacity_desc":
        sorted.sort((a, b) => b.capacity - a.capacity);
        break;
      case "city_asc":
        sorted.sort((a, b) => a.city.localeCompare(b.city));
        break;
      case "usage_desc":
      default:
        sorted.sort((a, b) => (b.usage_percent ?? 0) - (a.usage_percent ?? 0));
        break;
    }

    return sorted;
  }, [allocations, searchQuery, usageFilter, sortBy]);

  const chartData = useMemo(
    () =>
      [...allocations]
        .sort((a, b) => (b.usage_percent ?? 0) - (a.usage_percent ?? 0))
        .slice(0, 10)
        .map((city) => ({
          city: city.city,
          usage_percent: city.usage_percent,
        })),
    [allocations],
  );

  const modelVsBaselineChartData = useMemo(() => {
    if (!data?.baseline) return [];

    const baselineCityMap = new Map(
      data.baseline.city_allocations.map((city) => [city.city, city.allocated_refugees]),
    );

    return data.city_allocations
      .map((city) => {
        const baselineAllocated = baselineCityMap.get(city.city) ?? 0;
        const modelAllocated = city.allocated_refugees;
        return {
          city: city.city,
          model_allocated: modelAllocated,
          baseline_allocated: baselineAllocated,
          absolute_shift: Math.abs(modelAllocated - baselineAllocated),
        };
      })
      .sort((a, b) => {
        if (b.absolute_shift !== a.absolute_shift) {
          return b.absolute_shift - a.absolute_shift;
        }
        return b.model_allocated - a.model_allocated;
      })
      .slice(0, 10);
  }, [data]);

  const coverageValue =
    data && data.original_refugees > 0 ? (data.total_allocated_refugees / data.original_refugees) * 100 : 0;
  const coverage = data
    ? coverageValue.toFixed(1)
    : null;

  const generatedAtLabel = data?.generated_at ? new Date(data.generated_at).toLocaleString() : "-";

  const currentRun = runHistory[0] ?? data;
  const previousRun = runHistory.length > 1 ? runHistory[1] : null;

  const comparison = useMemo(() => {
    if (!currentRun || !previousRun) return null;

    const currentCoverage =
      currentRun.original_refugees > 0
        ? (currentRun.total_allocated_refugees / currentRun.original_refugees) * 100
        : 0;
    const previousCoverage =
      previousRun.original_refugees > 0
        ? (previousRun.total_allocated_refugees / previousRun.original_refugees) * 100
        : 0;

    const previousCityMap = new Map(
      previousRun.city_allocations.map((city) => [city.city, city.allocated_refugees]),
    );

    const topCityDeltas = currentRun.city_allocations
      .map((city) => ({
        city: city.city,
        delta: city.allocated_refugees - (previousCityMap.get(city.city) ?? 0),
      }))
      .filter((item) => item.delta !== 0)
      .sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta))
      .slice(0, 5);

    return {
      allocatedDelta: currentRun.total_allocated_refugees - previousRun.total_allocated_refugees,
      unallocatedDelta: currentRun.unallocated_refugees - previousRun.unallocated_refugees,
      objectiveDelta: Number((currentRun.objective_value - previousRun.objective_value).toFixed(2)),
      runtimeDelta: Number((currentRun.runtime_seconds - previousRun.runtime_seconds).toFixed(2)),
      coverageDelta: Number((currentCoverage - previousCoverage).toFixed(1)),
      topCityDeltas,
    };
  }, [currentRun, previousRun]);

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <h1 className="text-2xl font-bold tracking-tight text-foreground sm:text-3xl">
                Refugee Allocation Optimization
              </h1>
              <p className="mt-1 text-sm text-muted-foreground">
                Policy decision-support system for optimal refugee distribution
              </p>
            </div>
            <div className="flex w-full flex-col gap-2 sm:w-auto sm:flex-row sm:items-center">
              <button
                onClick={toggleDarkMode}
                className="inline-flex items-center justify-center gap-2 rounded-lg border border-input bg-background px-3 py-2.5 text-sm font-medium text-foreground shadow-sm transition-all hover:bg-secondary focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
                title={isDark ? "Switch to light mode" : "Switch to dark mode"}
              >
                {isDark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              </button>

              <select
                value={scenario}
                onChange={(e) => {
                  const newScenario = e.target.value as ScenarioPreset;
                  setScenario(newScenario);
                  setShowCustomWeights(newScenario === "custom");
                }}
                className="h-10 rounded-lg border border-input bg-background px-3 text-sm"
              >
                {SCENARIO_OPTIONS.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>

              <button
                onClick={runOptimization}
                disabled={loading}
                className="inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-5 py-2.5 text-sm font-semibold text-primary-foreground shadow-sm transition-all hover:opacity-90 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:opacity-50"
              >
                {loading ? (
                  <>
                    <span className="h-4 w-4 animate-spin rounded-full border-2 border-primary-foreground border-t-transparent" />
                    Running…
                  </>
                ) : (
                  <>
                    <Activity className="h-4 w-4" />
                    Run Optimization
                  </>
                )}
              </button>
            </div>
          </div>

          {data && (
            <div className="mt-4 flex flex-wrap items-center gap-3 text-xs text-muted-foreground">
              <span className="rounded-md border border-border bg-muted/50 px-2 py-1">
                Status: <span className="font-semibold text-foreground">{data.optimization_status ?? "-"}</span>
              </span>
              <span className="rounded-md border border-border bg-muted/50 px-2 py-1">
                Scenario: <span className="font-semibold text-foreground">{data.scenario_label ?? data.scenario ?? "-"}</span>
              </span>
              <span>Generated: {generatedAtLabel}</span>
            </div>
          )}
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Error */}
        {error && (
          <div className="mb-6 flex items-center gap-3 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            {error}
          </div>
        )}

        {/* Custom Weights Panel */}
        {showCustomWeights && (
          <div className="mb-6 rounded-xl border border-border bg-card p-5">
            <button
              onClick={() => setShowCustomWeights(!showCustomWeights)}
              className="mb-4 flex w-full items-center justify-between text-left"
            >
              <div className="flex items-center gap-2">
                <Sliders className="h-4 w-4 text-muted-foreground" />
                <h2 className="text-base font-semibold text-foreground">Custom Weight Configuration</h2>
              </div>
              {showCustomWeights ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
            </button>

            <div className="space-y-4">
              <WeightSlider
                label="Language Match"
                description="Bonus when refugee's primary language matches city's language (higher = prioritize language compatibility)"
                value={customWeights.language}
                onChange={(val) => setCustomWeights({ ...customWeights, language: val })}
              />
              <WeightSlider
                label="Skill & Job Match"
                description="Bonus when refugee's skill matches city's job demand (higher = prioritize employment opportunities)"
                value={customWeights.skill_match}
                onChange={(val) => setCustomWeights({ ...customWeights, skill_match: val })}
              />
              <WeightSlider
                label="Education Level"
                description="Score scales with refugee education (None=0, Primary=0.25, Secondary=0.5, Bachelor=0.75, Master=1.0) × this weight"
                value={customWeights.education}
                onChange={(val) => setCustomWeights({ ...customWeights, education: val })}
              />
              <WeightSlider
                label="Cost of Living Match"
                description="Weight for matching refugee's preferred cost level with city's actual cost (rewards alignment, not high/low)"
                value={customWeights.cost_match}
                onChange={(val) => setCustomWeights({ ...customWeights, cost_match: val })}
              />
              <WeightSlider
                label="Employment Rate"
                description="Score increases with city's employment rate (1 - unemployment_rate) × this weight"
                value={customWeights.employment}
                onChange={(val) => setCustomWeights({ ...customWeights, employment: val })}
              />
              <WeightSlider
                label="Adaptability Index"
                description="Score increases with refugee's adaptability (0-1 scale) × this weight"
                value={customWeights.adaptability}
                onChange={(val) => setCustomWeights({ ...customWeights, adaptability: val })}
              />
              <WeightSlider
                label="Diaspora Support"
                description="Score increases with city's diaspora support index (higher = stronger existing support networks)"
                value={customWeights.diaspora_support}
                onChange={(val) => setCustomWeights({ ...customWeights, diaspora_support: val })}
              />
              <WeightSlider
                label="Integration Policy"
                description="Score increases with city's integration policy score (higher = stronger integration infrastructure)"
                value={customWeights.integration_policy}
                onChange={(val) => setCustomWeights({ ...customWeights, integration_policy: val })}
              />
              <WeightSlider
                label="Trauma Penalty"
                description="Score DECREASES with refugee trauma level (higher weight = stronger penalty for high trauma)"
                value={customWeights.trauma_penalty}
                onChange={(val) => setCustomWeights({ ...customWeights, trauma_penalty: val })}
                max={0.1}
              />
              <WeightSlider
                label="Unallocated Penalty"
                description="Objective penalty for each unallocated refugee (higher = stronger push to allocate everyone)"
                value={customWeights.unallocated_penalty}
                onChange={(val) => setCustomWeights({ ...customWeights, unallocated_penalty: val })}
                max={0.2}
              />
              
              <div className="pt-2">
                <WeightSlider
                  label="Capacity Scale"
                  description="Multiplier for city capacity limits (1.0 = full capacity, 0.8 = 80% capacity stress)"
                  value={capacityScale}
                  onChange={setCapacityScale}
                  min={0.5}
                  max={1.5}
                  step={0.05}
                />
              </div>

              <div className="flex items-center justify-between rounded-md border border-border bg-muted/20 p-3 text-sm">
                <span className="font-medium text-foreground">Total Weight Sum:</span>
                <span className="font-mono font-semibold text-foreground">
                  {Object.values(customWeights).reduce((a, b) => a + b, 0).toFixed(3)}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* Empty state */}
        {!data && !loading && !error && (
          <div className="flex flex-col items-center justify-center py-24 text-center">
            <div className="rounded-full bg-muted p-4">
              <Activity className="h-8 w-8 text-muted-foreground" />
            </div>
            <h2 className="mt-4 text-lg font-semibold text-foreground">No data yet</h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Click "Run Optimization" to fetch allocation results from the server.
            </p>
          </div>
        )}

        {/* Loading skeleton */}
        {loading && (
          <div className="space-y-6">
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="h-28 animate-pulse rounded-xl bg-muted" />
              ))}
            </div>
            <div className="h-16 animate-pulse rounded-xl bg-muted" />
            <div className="h-64 animate-pulse rounded-xl bg-muted" />
          </div>
        )}

        {/* Results */}
        {data && !loading && (
          <div className="space-y-6">
            {/* Stat cards */}
            <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-5">
              <StatCard
                icon={<Users className="h-5 w-5" />}
                label="Total Refugees"
                value={data.original_refugees.toLocaleString()}
              />
              <StatCard
                icon={<Users className="h-5 w-5" />}
                label="Total Allocated"
                value={data.total_allocated_refugees.toLocaleString()}
                accent
              />
              <StatCard
                icon={<AlertTriangle className="h-5 w-5" />}
                label="Unallocated"
                value={data.unallocated_refugees.toLocaleString()}
                warn={data.unallocated_refugees > 0}
              />
              <StatCard
                icon={<Target className="h-5 w-5" />}
                label="Objective Score"
                value={data.objective_value.toLocaleString(undefined, { maximumFractionDigits: 2 })}
              />
              <StatCard
                icon={<Clock className="h-5 w-5" />}
                label="Runtime"
                value={`${data.runtime_seconds.toFixed(2)}s`}
              />
            </div>

            {data.model_comparison && data.baseline && (
              <div className="rounded-xl border border-border bg-card p-5">
                <div className="mb-2 flex items-center justify-between gap-3">
                  <h2 className="text-base font-semibold text-foreground">Model vs Baseline</h2>
                  <span
                    className={`rounded-md px-2 py-1 text-xs font-semibold ${
                      data.model_comparison.winner === "model"
                        ? "bg-success/15 text-success"
                        : "bg-destructive/15 text-destructive"
                    }`}
                  >
                    {data.model_comparison.winner === "model" ? "Model wins" : "Baseline wins"}
                  </span>
                </div>

                <p className="mb-4 text-xs text-muted-foreground">
                  Baseline strategy: {data.model_comparison.baseline_method.replace(/_/g, " ")}
                </p>

                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
                  <DeltaCard
                    label="Objective Delta"
                    delta={data.model_comparison.objective_delta}
                    positiveIsGood
                    contextLabel="vs baseline"
                  />

                  <MetricCard
                    label="Objective Uplift"
                    value={
                      data.model_comparison.objective_uplift_percent === null
                        ? "N/A"
                        : `${formatSigned(data.model_comparison.objective_uplift_percent)}%`
                    }
                    tone={getDeltaClass(data.model_comparison.objective_uplift_percent ?? 0, true)}
                  />

                  <DeltaCard
                    label="Score/Allocated Delta"
                    delta={data.model_comparison.score_per_allocated_delta}
                    positiveIsGood
                    suffix=" pts"
                    contextLabel="vs baseline"
                  />
                  <MetricCard
                    label="Reassigned Refugees"
                    value={String(data.model_comparison.total_city_reallocation ?? 0)}
                  />
                  <MetricCard
                    label="Cities Changed"
                    value={String(data.model_comparison.cities_with_different_allocations ?? 0)}
                  />
                </div>

                <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
                  <div className="rounded-md border border-border bg-muted/20 p-3">
                    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Model score per allocated</p>
                    <p className="mt-1 font-mono text-lg font-semibold text-foreground">
                      {Number(data.score_per_allocated ?? 0).toFixed(4)}
                    </p>
                  </div>
                  <div className="rounded-md border border-border bg-muted/20 p-3">
                    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Baseline score per allocated</p>
                    <p className="mt-1 font-mono text-lg font-semibold text-foreground">
                      {Number(data.baseline.score_per_allocated ?? 0).toFixed(4)}
                    </p>
                  </div>
                  <div className="rounded-md border border-border bg-muted/20 p-3">
                    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Max city shift</p>
                    <p className="mt-1 font-mono text-lg font-semibold text-foreground">
                      {Number(data.model_comparison.max_city_shift ?? 0).toLocaleString()}
                    </p>
                  </div>
                  <div className="rounded-md border border-border bg-muted/20 p-3">
                    <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">Allocation overlap</p>
                    <p className="mt-1 font-mono text-lg font-semibold text-foreground">
                      {Number(data.model_comparison.allocation_overlap_percent ?? 0).toFixed(1)}%
                    </p>
                  </div>
                </div>

                <div className="mt-4 rounded-lg border border-border bg-muted/10 p-4">
                  <div className="mb-3 flex items-center justify-between gap-2">
                    <h3 className="text-sm font-semibold text-foreground">Top 10 City Allocation Differences</h3>
                    <span className="text-xs text-muted-foreground">Model vs baseline</span>
                  </div>

                  {modelVsBaselineChartData.length > 0 ? (
                    <ChartContainer
                      className="h-[340px] w-full"
                      config={{
                        model_allocated: {
                          label: "Model",
                          color: "hsl(var(--accent))",
                        },
                        baseline_allocated: {
                          label: "Baseline",
                          color: "hsl(var(--secondary-foreground))",
                        },
                      }}
                    >
                      <BarChart
                        data={modelVsBaselineChartData}
                        layout="vertical"
                        margin={{ top: 4, right: 16, bottom: 4, left: 8 }}
                      >
                        <CartesianGrid horizontal={false} />
                        <XAxis type="number" />
                        <YAxis dataKey="city" type="category" width={130} axisLine={false} tickLine={false} />
                        <ChartTooltip
                          cursor={false}
                          content={
                            <ChartTooltipContent
                              formatter={(value) => (
                                <span className="font-mono">{Number(value).toLocaleString()} people</span>
                              )}
                            />
                          }
                        />
                        <ChartLegend content={<ChartLegendContent />} />
                        <Bar
                          dataKey="model_allocated"
                          fill="var(--color-model_allocated)"
                          radius={4}
                          animationDuration={700}
                        />
                        <Bar
                          dataKey="baseline_allocated"
                          fill="var(--color-baseline_allocated)"
                          radius={4}
                          animationDuration={700}
                        />
                      </BarChart>
                    </ChartContainer>
                  ) : (
                    <p className="text-sm text-muted-foreground">No city-level data available for model and baseline comparison.</p>
                  )}
                </div>
              </div>
            )}

            {/* Coverage bar */}
            <div className="rounded-xl border border-border bg-card p-5">
              <div className="mb-2 flex items-center justify-between text-sm">
                <span className="font-medium text-foreground">Allocation Coverage</span>
                <span className="font-mono font-semibold text-accent">{coverage}%</span>
              </div>
              <div className="h-3 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-accent transition-all duration-700"
                  style={{ width: `${coverage}%` }}
                />
              </div>
              <p className="mt-2 text-xs text-muted-foreground">
                {data.total_allocated_refugees.toLocaleString()} of {data.original_refugees.toLocaleString()} refugees allocated across {data.cities} cities ({data.grouped_clusters} clusters)
              </p>
            </div>

            <div className="rounded-xl border border-border bg-card p-5">
              <div className="mb-4 flex items-center justify-between gap-3">
                <h2 className="text-base font-semibold text-foreground">Run Comparison (Last 2 Runs)</h2>
                <span className="text-xs text-muted-foreground">Run optimize again to update</span>
              </div>

              {currentRun && previousRun && (
                <p className="mb-4 text-xs text-muted-foreground">
                  Current: {currentRun.scenario_label ?? currentRun.scenario ?? "-"} vs Previous: {previousRun.scenario_label ?? previousRun.scenario ?? "-"}
                </p>
              )}

              {comparison ? (
                <>
                  <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-5">
                    <DeltaCard
                      label="Allocated"
                      delta={comparison.allocatedDelta}
                      positiveIsGood
                      suffix=" people"
                    />
                    <DeltaCard
                      label="Unallocated"
                      delta={comparison.unallocatedDelta}
                      positiveIsGood={false}
                      suffix=" people"
                    />
                    <DeltaCard
                      label="Objective"
                      delta={comparison.objectiveDelta}
                      positiveIsGood
                    />
                    <DeltaCard
                      label="Coverage"
                      delta={comparison.coverageDelta}
                      positiveIsGood
                      suffix=" pts"
                    />
                    <DeltaCard
                      label="Runtime"
                      delta={comparison.runtimeDelta}
                      positiveIsGood={false}
                      suffix=" s"
                    />
                  </div>

                  <div className="mt-4 rounded-lg border border-border bg-muted/20 p-3">
                    <p className="mb-2 text-xs font-medium uppercase tracking-wide text-muted-foreground">
                      Top City Allocation Changes
                    </p>
                    {comparison.topCityDeltas.length > 0 ? (
                      <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
                        {comparison.topCityDeltas.map((item) => (
                          <div key={item.city} className="flex items-center justify-between rounded-md bg-background px-3 py-2 text-sm">
                            <span className="font-medium text-foreground">{item.city}</span>
                            <span className={`font-mono font-semibold ${getDeltaClass(item.delta, true)}`}>
                              {formatSigned(item.delta)}
                            </span>
                          </div>
                        ))}
                      </div>
                    ) : (
                      <p className="text-sm text-muted-foreground">No city-level allocation changes between the last two runs.</p>
                    )}
                  </div>
                </>
              ) : (
                <p className="text-sm text-muted-foreground">
                  Run optimization at least twice to compare the latest result with the previous run.
                </p>
              )}
            </div>

            <div className="rounded-xl border border-border bg-card p-5">
              <div className="mb-4 flex items-center gap-2">
                <BarChart3 className="h-4 w-4 text-muted-foreground" />
                <h2 className="text-base font-semibold text-foreground">Top 10 City Utilization</h2>
              </div>

              <ChartContainer
                className="h-[320px] w-full"
                config={{
                  usage_percent: {
                    label: "Usage %",
                    color: "hsl(var(--accent))",
                  },
                }}
              >
                <BarChart data={chartData} layout="vertical" margin={{ top: 4, right: 16, bottom: 4, left: 8 }}>
                  <CartesianGrid horizontal={false} />
                  <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} />
                  <YAxis dataKey="city" type="category" width={120} axisLine={false} tickLine={false} />
                  <ChartTooltip
                    cursor={false}
                    content={
                      <ChartTooltipContent
                        formatter={(value) => <span className="font-mono">{Number(value).toFixed(1)}%</span>}
                      />
                    }
                  />
                  <Bar dataKey="usage_percent" fill="var(--color-usage_percent)" radius={4} />
                </BarChart>
              </ChartContainer>
            </div>

            {/* City allocation table */}
            <div className="overflow-hidden rounded-xl border border-border bg-card">
              <div className="border-b border-border px-5 py-4">
                <h2 className="flex items-center gap-2 text-base font-semibold text-foreground">
                  <Building2 className="h-4 w-4 text-muted-foreground" />
                  City Allocations
                </h2>
              </div>

              <div className="grid gap-3 border-b border-border px-5 py-4 sm:grid-cols-[1fr_auto_auto_auto] sm:items-center">
                <div className="relative">
                  <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
                  <input
                    value={searchQuery}
                    onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Search city"
                    className="h-10 w-full rounded-md border border-input bg-background pl-9 pr-3 text-sm outline-none transition focus:border-ring focus:ring-2 focus:ring-ring/30"
                  />
                </div>

                <select
                  value={usageFilter}
                  onChange={(e) => setUsageFilter(e.target.value as UsageFilter)}
                  className="h-10 rounded-md border border-input bg-background px-3 text-sm"
                >
                  <option value="all">All usage bands</option>
                  <option value="critical">Critical (≥90%)</option>
                  <option value="high">High (70–89.9%)</option>
                  <option value="normal">Normal (&lt;70%)</option>
                </select>

                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as SortBy)}
                  className="h-10 rounded-md border border-input bg-background px-3 text-sm"
                >
                  <option value="usage_desc">Sort: Usage (high → low)</option>
                  <option value="usage_asc">Sort: Usage (low → high)</option>
                  <option value="allocated_desc">Sort: Allocated (high → low)</option>
                  <option value="capacity_desc">Sort: Capacity (high → low)</option>
                  <option value="city_asc">Sort: City (A → Z)</option>
                </select>

                <button
                  onClick={exportCsv}
                  disabled={exportingCsv}
                  className="inline-flex h-10 items-center justify-center gap-2 rounded-md border border-border bg-background px-3 text-sm font-medium text-foreground transition hover:bg-muted disabled:opacity-50"
                >
                  {exportingCsv ? (
                    <>
                      <span className="h-4 w-4 animate-spin rounded-full border-2 border-foreground border-t-transparent" />
                      Exporting...
                    </>
                  ) : (
                    <>
                      <Download className="h-4 w-4" />
                      Export CSV
                    </>
                  )}
                </button>
              </div>

              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-border bg-muted/50">
                      <th className="px-5 py-3 text-left font-medium text-muted-foreground">City</th>
                      <th className="px-5 py-3 text-right font-medium text-muted-foreground">Allocated</th>
                      <th className="px-5 py-3 text-right font-medium text-muted-foreground">Capacity</th>
                      <th className="px-5 py-3 text-right font-medium text-muted-foreground">Usage %</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredSortedAllocations.map((city) => (
                      <tr key={city.city} className="border-b border-border last:border-0 transition-colors hover:bg-muted/30">
                        <td className="px-5 py-3 font-medium text-foreground">{city.city}</td>
                        <td className="px-5 py-3 text-right font-mono text-foreground">
                          {city.allocated_refugees.toLocaleString()}
                        </td>
                        <td className="px-5 py-3 text-right font-mono text-muted-foreground">
                          {city.capacity.toLocaleString()}
                        </td>
                        <td className="px-5 py-3 text-right">
                          <UsageBadge value={city.usage_percent ?? 0} />
                        </td>
                      </tr>
                    ))}

                    {filteredSortedAllocations.length === 0 && (
                      <tr>
                        <td colSpan={4} className="px-5 py-10 text-center text-sm text-muted-foreground">
                          No cities match the current filters.
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

function StatCard({
  icon,
  label,
  value,
  accent,
  warn,
}: {
  icon: React.ReactNode;
  label: string;
  value: string;
  accent?: boolean;
  warn?: boolean;
}) {
  return (
    <div className="rounded-xl border border-border bg-card p-5 shadow-sm">
      <div className="flex items-center gap-2 text-muted-foreground">
        {icon}
        <span className="text-xs font-medium uppercase tracking-wider">{label}</span>
      </div>
      <p
        className={`mt-2 text-2xl font-bold tracking-tight ${
          warn ? "text-destructive" : accent ? "text-accent" : "text-foreground"
        }`}
      >
        {value}
      </p>
    </div>
  );
}

function getUtilizationBand(value: number): "normal" | "high" | "critical" {
  if (value >= 90) return "critical";
  if (value >= 70) return "high";
  return "normal";
}

function getDeltaClass(value: number, positiveIsGood: boolean) {
  if (value === 0) return "text-muted-foreground";
  const good = positiveIsGood ? value > 0 : value < 0;
  return good ? "text-success" : "text-destructive";
}

function formatSigned(value: number) {
  if (Math.abs(value) < 1e-9) return "0";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toLocaleString()}`;
}

function DeltaCard({
  label,
  delta,
  positiveIsGood,
  suffix,
  contextLabel = "vs previous run",
}: {
  label: string;
  delta: number;
  positiveIsGood: boolean;
  suffix?: string;
  contextLabel?: string;
}) {
  return (
    <div className="rounded-md border border-border bg-muted/20 p-3">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className={`mt-1 font-mono text-lg font-semibold ${getDeltaClass(delta, positiveIsGood)}`}>
        {formatSigned(delta)}
        {suffix}
      </p>
      <p className="text-xs text-muted-foreground">{contextLabel}</p>
    </div>
  );
}

function MetricCard({ label, value, tone }: { label: string; value: string; tone?: string }) {
  return (
    <div className="rounded-md border border-border bg-muted/20 p-3">
      <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">{label}</p>
      <p className={`mt-1 font-mono text-lg font-semibold ${tone ?? "text-foreground"}`}>{value}</p>
      <p className="text-xs text-muted-foreground">vs baseline</p>
    </div>
  );
}

function UsageBadge({ value }: { value: number }) {
  let colorClass = "bg-success/15 text-success";
  if (value >= 90) colorClass = "bg-destructive/15 text-destructive";
  else if (value >= 70) colorClass = "bg-warning/15 text-warning";

  return (
    <span className={`inline-block rounded-md px-2 py-0.5 text-xs font-semibold font-mono ${colorClass}`}>
      {value}%
    </span>
  );
}

function WeightSlider({
  label,
  description,
  value,
  onChange,
  min = 0,
  max = 0.5,
  step = 0.01,
}: {
  label: string;
  description: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
}) {
  return (
    <div className="space-y-1.5">
      <div className="flex items-center justify-between">
        <label className="text-sm font-medium text-foreground">{label}</label>
        <span className="font-mono text-sm font-semibold text-accent">{value.toFixed(3)}</span>
      </div>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(parseFloat(e.target.value))}
        className="h-2 w-full cursor-pointer appearance-none rounded-lg bg-muted accent-accent"
      />
      <p className="text-xs text-muted-foreground">{description}</p>
    </div>
  );
}

export default Dashboard;
