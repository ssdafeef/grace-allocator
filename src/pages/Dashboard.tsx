import { useState } from "react";
import { Activity, Users, Building2, Target, Clock, AlertTriangle } from "lucide-react";

interface CityAllocation {
  city: string;
  allocated_refugees: number;
  capacity: number;
}

interface OptimizationResult {
  original_refugees: number;
  grouped_clusters: number;
  cities: number;
  objective_value: number;
  total_allocated_refugees: number;
  unallocated_refugees: number;
  runtime_seconds: number;
  city_allocations: CityAllocation[];
}

const Dashboard = () => {
  const [data, setData] = useState<OptimizationResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const runOptimization = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await fetch("http://localhost:5000/optimize");
      if (!res.ok) throw new Error(`Server responded with ${res.status}`);
      const json: OptimizationResult = await res.json();
      setData(json);
    } catch (err: any) {
      setError(err.message || "Failed to connect to the optimization server.");
    } finally {
      setLoading(false);
    }
  };

  const coverage = data
    ? ((data.total_allocated_refugees / data.original_refugees) * 100).toFixed(1)
    : null;

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
      </header>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        {/* Error */}
        {error && (
          <div className="mb-6 flex items-center gap-3 rounded-lg border border-destructive/30 bg-destructive/10 px-4 py-3 text-sm text-destructive">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            {error}
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

            {/* City allocation table */}
            <div className="overflow-hidden rounded-xl border border-border bg-card">
              <div className="border-b border-border px-5 py-4">
                <h2 className="flex items-center gap-2 text-base font-semibold text-foreground">
                  <Building2 className="h-4 w-4 text-muted-foreground" />
                  City Allocations
                </h2>
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
                    {data.city_allocations.map((city) => {
                      const usage = ((city.allocated_refugees / city.capacity) * 100).toFixed(1);
                      return (
                        <tr key={city.city} className="border-b border-border last:border-0 transition-colors hover:bg-muted/30">
                          <td className="px-5 py-3 font-medium text-foreground">{city.city}</td>
                          <td className="px-5 py-3 text-right font-mono text-foreground">
                            {city.allocated_refugees.toLocaleString()}
                          </td>
                          <td className="px-5 py-3 text-right font-mono text-muted-foreground">
                            {city.capacity.toLocaleString()}
                          </td>
                          <td className="px-5 py-3 text-right">
                            <UsageBadge value={Number(usage)} />
                          </td>
                        </tr>
                      );
                    })}
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

export default Dashboard;
