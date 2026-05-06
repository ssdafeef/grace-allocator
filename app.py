from flask import Flask, jsonify, Response, request
from flask_cors import CORS
from ortools.linear_solver import pywraplp
import pandas as pd
import time
from datetime import datetime, timezone
import csv
import io

app = Flask(__name__)
CORS(app)
latest_result = None
refugees_df = None
cities_df = None
grouped = None

# this is use to load LOAD DATA
# and also some bit of preprocesing


group_columns = [
    "primary_language",
    "skill_type",
    "education_level",
    "preferred_cost_level"
]


def reload_data():
    global refugees_df, cities_df, grouped

    refugees_df = pd.read_csv("synthetic_refugees_50k.csv")
    cities_df = pd.read_csv("synthetic_cities_50.csv")
    cities_df["job_demand"] = cities_df["job_demand"].apply(lambda x: x.split(","))

    grouped = refugees_df.groupby(group_columns).agg({
        "refugee_id": "count",
        "family_size": "mean",
        "trauma_level": "mean",
        "adaptability_index": "mean"
    }).reset_index()

    grouped = grouped.rename(columns={"refugee_id": "group_size"})
    print("Grouped clusters:", len(grouped))


reload_data()

# this is pre scenario we are basically assigninhg

SCENARIO_PRESETS = {
    "balanced": {
        "label": "Balanced",
        "description": "Default trade-off across integration, labor match, and capacity",
        "capacity_scale": 1.0,
        "weights": {
            "language": 0.25,
            "skill_match": 0.25,
            "education": 0.2,
            "cost_match": 0.1,
            "employment": 0.1,
            "adaptability": 0.05,
            "trauma_penalty": 0.01,
            "diaspora_support": 0.08,
            "integration_policy": 0.08,
            "unallocated_penalty": 0.03,
        },
    },
    "capacity_stress": {
        "label": "Capacity Stress",
        "description": "Simulates tighter city capacity limits",
        "capacity_scale": 0.85,
        "weights": {
            "language": 0.25,
            "skill_match": 0.25,
            "education": 0.2,
            "cost_match": 0.1,
            "employment": 0.1,
            "adaptability": 0.05,
            "trauma_penalty": 0.01,
            "diaspora_support": 0.08,
            "integration_policy": 0.08,
            "unallocated_penalty": 0.04,
        },
    },
    "jobs_priority": {
        "label": "Jobs Priority",
        "description": "Prioritizes labor-market fit and unemployment outcomes",
        "capacity_scale": 1.0,
        "weights": {
            "language": 0.18,
            "skill_match": 0.38,
            "education": 0.16,
            "cost_match": 0.06,
            "employment": 0.18,
            "adaptability": 0.06,
            "trauma_penalty": 0.01,
            "diaspora_support": 0.04,
            "integration_policy": 0.03,
            "unallocated_penalty": 0.03,
        },
    },
    "integration_priority": {
        "label": "Integration Priority",
        "description": "Prioritizes language/cost compatibility and adaptability",
        "capacity_scale": 1.0,
        "weights": {
            "language": 0.34,
            "skill_match": 0.2,
            "education": 0.14,
            "cost_match": 0.14,
            "employment": 0.08,
            "adaptability": 0.1,
            "trauma_penalty": 0.01,
            "diaspora_support": 0.14,
            "integration_policy": 0.2,
            "unallocated_penalty": 0.03,
        },
    },
}

DEFAULT_SCENARIO = "balanced"

# SCORE FUNCTION


def compute_score(group, city, weights):
    score = 0

    if group["primary_language"] == city["primary_language"]:
        score += weights["language"]

    if group["skill_type"] in city["job_demand"]:
        score += weights["skill_match"]

    edu_weights = {
        "None": 0.0,
        "Primary": 0.25,
        "Secondary": 0.5,
        "Bachelor": 0.75,
        "Master": 1.0
    }

    score += edu_weights.get(group["education_level"], 0) * weights["education"]

    if group["preferred_cost_level"] == city["cost_level"]:
        score += weights["cost_match"]

    score += (1 - float(city["unemployment_rate"])) * weights["employment"]
    score += float(group["adaptability_index"]) * weights["adaptability"]
    score += float(city["diaspora_support_index"]) * weights["diaspora_support"]
    score += float(city["integration_policy_score"]) * weights["integration_policy"]
    score -= float(group["trauma_level"]) * weights["trauma_penalty"]

    return max(score, 0)


def parse_custom_weights_from_request(req):
    if req.args.get("custom_weights") != "true":
        return None

    try:
        return {
            "capacity_scale": float(req.args.get("capacity_scale", 1.0)),
            "weights": {
                "language": float(req.args.get("weight_language", 0.25)),
                "skill_match": float(req.args.get("weight_skill_match", 0.25)),
                "education": float(req.args.get("weight_education", 0.2)),
                "cost_match": float(req.args.get("weight_cost_match", 0.1)),
                "employment": float(req.args.get("weight_employment", 0.1)),
                "adaptability": float(req.args.get("weight_adaptability", 0.05)),
                "trauma_penalty": float(req.args.get("weight_trauma_penalty", 0.01)),
                "diaspora_support": float(req.args.get("weight_diaspora_support", 0.08)),
                "integration_policy": float(req.args.get("weight_integration_policy", 0.08)),
                "unallocated_penalty": float(req.args.get("weight_unallocated_penalty", 0.03)),
            }
        }
    except (ValueError, TypeError):
        return None

# now we start using Google or tools , the pwwraplp thingy

def get_status_label(status):
    if status == pywraplp.Solver.OPTIMAL:
        return "optimal"
    if status == pywraplp.Solver.FEASIBLE:
        return "feasible"
    return "infeasible"


def get_utilization_band(usage_percent):
    if usage_percent >= 90:
        return "critical"
    if usage_percent >= 70:
        return "high"
    return "normal"


def build_score_matrix(weights):
    num_groups = len(grouped)
    num_cities = len(cities_df)
    return [
        [compute_score(grouped.loc[i], cities_df.loc[j], weights) for j in range(num_cities)]
        for i in range(num_groups)
    ]


def run_greedy_baseline(scenario_config, score_matrix=None):
    baseline_start = time.time()
    num_groups = len(grouped)
    num_cities = len(cities_df)
    weights = scenario_config["weights"]
    capacity_scale = scenario_config["capacity_scale"]
    if score_matrix is None:
        score_matrix = build_score_matrix(weights)

    city_capacity = [float(cities_df.loc[j, "capacity"]) * capacity_scale for j in range(num_cities)]
    remaining_capacity = city_capacity.copy()
    city_allocated = [0.0 for _ in range(num_cities)]

    total_score = 0.0
    total_allocated = 0.0
    unallocated_penalty = float(weights.get("unallocated_penalty", 0.0))

    for i in range(num_groups):
        group = grouped.loc[i]
        remaining_group = float(group["group_size"])
        family_size = max(float(group["family_size"]), 1e-6)

        city_rankings = [(score_matrix[i][j], j) for j in range(num_cities)]
        city_rankings.sort(key=lambda row: row[0], reverse=True)

        for score, j in city_rankings:
            if remaining_group <= 0:
                break

            if remaining_capacity[j] <= 0:
                continue

            max_assignable = remaining_capacity[j] / family_size
            assigned = min(remaining_group, max_assignable)

            if assigned <= 0:
                continue

            remaining_group -= assigned
            remaining_capacity[j] -= assigned * family_size
            city_allocated[j] += assigned
            total_allocated += assigned
            total_score += score * assigned

        if remaining_group > 0:
            total_score -= unallocated_penalty * remaining_group

    allocations = []
    for j in range(num_cities):
        allocated = city_allocated[j]
        capacity = city_capacity[j]
        usage_percent = round((allocated / capacity) * 100, 1) if capacity > 0 else 0.0

        allocations.append({
            "city": cities_df.loc[j, "city_name"],
            "allocated_refugees": int(round(allocated)),
            "capacity": int(capacity),
            "usage_percent": usage_percent,
            "utilization_band": get_utilization_band(usage_percent)
        })

    baseline_coverage = (total_allocated / len(refugees_df)) * 100 if len(refugees_df) > 0 else 0
    baseline_runtime = round(time.time() - baseline_start, 4)

    return {
        "method": "greedy_best_match",
        "objective_value": round(total_score, 2),
        "total_allocated_refugees": int(round(total_allocated)),
        "unallocated_refugees": int(len(refugees_df) - round(total_allocated)),
        "coverage_percent": round(baseline_coverage, 1),
        "score_per_allocated": round(total_score / total_allocated, 4) if total_allocated > 0 else 0.0,
        "runtime_seconds": baseline_runtime,
        "city_allocations": allocations
    }


def run_optimization(scenario_name=DEFAULT_SCENARIO, custom_config=None):
    start = time.time()

    if custom_config:
        scenario_key = "custom"
        scenario_config = {
            "label": "Custom Weights",
            "description": "User-defined weight configuration",
            "capacity_scale": custom_config.get("capacity_scale", 1.0),
            "weights": custom_config.get("weights", {})
        }
    else:
        scenario_key = scenario_name if scenario_name in SCENARIO_PRESETS else DEFAULT_SCENARIO
        scenario_config = SCENARIO_PRESETS[scenario_key]
    
    weights = scenario_config["weights"]
    capacity_scale = scenario_config["capacity_scale"]

    # LP model: use a dedicated linear solver and apply a lexicographic objective.
    # Phase 1 maximizes allocation coverage; Phase 2 maximizes weighted quality
    # while preserving the best coverage from Phase 1.
    solver = pywraplp.Solver.CreateSolver("GLOP") or pywraplp.Solver.CreateSolver("CBC")
    if solver is None:
        raise RuntimeError("Unable to initialize OR-Tools solver backend")
    solver.SetTimeLimit(180000)
# we are using glop for mainly the linear part aand for speed and better momory management while cbc
# is used for the integer part, but since we are doing a linear relaxation we can use glop for everything and get faster results
    num_groups = len(grouped)
    num_cities = len(cities_df)
    effective_capacity = [float(cities_df.loc[j, "capacity"]) * capacity_scale for j in range(num_cities)]
    score_matrix = build_score_matrix(weights)

    x = {}
    u = {}

    for i in range(num_groups):
        for j in range(num_cities):
            x[(i, j)] = solver.NumVar(
                0,
                float(grouped.loc[i, "group_size"]),
                f"x_{i}_{j}"
            )

    for i in range(num_groups):
        u[i] = solver.NumVar(
            0,
            float(grouped.loc[i, "group_size"]),
            f"u_{i}"
        )

    unallocated_penalty = float(weights.get("unallocated_penalty", 0.0))

    total_allocated_expr = solver.Sum(
        x[(i, j)]
        for i in range(num_groups)
        for j in range(num_cities)
    )

    weighted_quality_expr = solver.Sum(
        score_matrix[i][j] * x[(i, j)]
        for i in range(num_groups)
        for j in range(num_cities)
    ) - solver.Sum(unallocated_penalty * u[i] for i in range(num_groups))

    # Assign exactly each group via allocation + unallocated slack
    for i in range(num_groups):
        solver.Add(
            solver.Sum(x[(i, j)] for j in range(num_cities)) + u[i]
            == float(grouped.loc[i, "group_size"])
        )

    # Capacity constraint
    for j in range(num_cities):
        solver.Add(
            solver.Sum(
                float(grouped.loc[i, "family_size"]) * x[(i, j)]
                for i in range(num_groups)
            )
            <= float(effective_capacity[j])
        )

    # Phase 1: maximize allocated refugees (coverage-first policy).
    solver.Maximize(total_allocated_expr)
    phase1_status = solver.Solve()

    if phase1_status == pywraplp.Solver.OPTIMAL or phase1_status == pywraplp.Solver.FEASIBLE:
        max_allocated = total_allocated_expr.solution_value()
        solver.Add(total_allocated_expr >= max_allocated - 1e-6)
        solver.Maximize(weighted_quality_expr)
        status = solver.Solve()
    else:
        status = phase1_status

    solve_time = solver.WallTime()

    total_allocated = 0
    allocations = []
    status_label = get_status_label(status)

    if status == pywraplp.Solver.OPTIMAL or status == pywraplp.Solver.FEASIBLE:
        total_score = solver.Objective().Value()

        for j in range(num_cities):
            allocated = sum(
                x[(i, j)].solution_value()
                for i in range(num_groups)
            )

            total_allocated += allocated
            capacity = float(effective_capacity[j])
            usage_percent = round((allocated / capacity) * 100, 1) if capacity > 0 else 0.0

            allocations.append({
                "city": cities_df.loc[j, "city_name"],
                "allocated_refugees": int(round(allocated)),
                "capacity": int(capacity),
                "usage_percent": usage_percent,
                "utilization_band": get_utilization_band(usage_percent)
            })
    else:
        total_score = 0

    end = time.time()

    optimized_coverage = (total_allocated / len(refugees_df)) * 100 if len(refugees_df) > 0 else 0
    optimized_score_per_allocated = total_score / total_allocated if total_allocated > 0 else 0.0
    baseline_result = run_greedy_baseline(scenario_config, score_matrix=score_matrix)

    objective_delta = total_score - baseline_result["objective_value"]
    objective_uplift_percent = None
    if baseline_result["objective_value"] > 0:
        objective_uplift_percent = round((objective_delta / baseline_result["objective_value"]) * 100, 1)

    model_city_map = {city["city"]: city["allocated_refugees"] for city in allocations}
    baseline_city_map = {city["city"]: city["allocated_refugees"] for city in baseline_result["city_allocations"]}
    city_abs_diffs = [
        abs(model_city_map.get(city_name, 0) - baseline_city_map.get(city_name, 0))
        for city_name in model_city_map.keys()
    ]
    total_city_reallocation = int(round(sum(city_abs_diffs) / 2))
    cities_with_different_allocations = int(sum(1 for diff in city_abs_diffs if diff > 0))
    max_city_shift = int(max(city_abs_diffs) if city_abs_diffs else 0)
    allocation_overlap_percent = round(
        (1 - (sum(city_abs_diffs) / (2 * max(total_allocated, 1.0)))) * 100,
        1,
    )

    model_comparison = {
        "baseline_method": baseline_result["method"],
        "objective_delta": round(objective_delta, 2),
        "objective_uplift_percent": objective_uplift_percent,
        "allocated_delta": int(round(total_allocated) - baseline_result["total_allocated_refugees"]),
        "coverage_delta_points": round(optimized_coverage - baseline_result["coverage_percent"], 1),
        "unallocated_reduction": int(
            baseline_result["unallocated_refugees"] - (len(refugees_df) - round(total_allocated))
        ),
        "score_per_allocated_delta": round(
            optimized_score_per_allocated - baseline_result["score_per_allocated"], 4
        ),
        "runtime_delta_seconds": round((end - start) - baseline_result.get("runtime_seconds", 0), 4),
        "total_city_reallocation": total_city_reallocation,
        "cities_with_different_allocations": cities_with_different_allocations,
        "max_city_shift": max_city_shift,
        "allocation_overlap_percent": allocation_overlap_percent,
        "winner": "model" if objective_delta >= 0 else "baseline"
    }

    return {
        "original_refugees": int(len(refugees_df)),
        "grouped_clusters": int(num_groups),
        "cities": int(num_cities),
        "objective_value": round(total_score, 2),
        "total_allocated_refugees": int(round(total_allocated)),
        "unallocated_refugees": int(len(refugees_df) - round(total_allocated)),
        "solve_time_ms": int(solve_time),
        "runtime_seconds": round(end - start, 2),
        "optimization_status": status_label,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scenario": scenario_key,
        "scenario_label": scenario_config["label"],
        "scenario_description": scenario_config["description"],
        "weights": weights,
        "capacity_scale": capacity_scale,
        "coverage_percent": round(optimized_coverage, 1),
        "score_per_allocated": round(optimized_score_per_allocated, 4),
        "baseline": baseline_result,
        "model_comparison": model_comparison,
        "city_allocations": allocations
    }

# OPTIMIZATION ROUTE

@app.route("/optimize", methods=["GET"])
def optimize():
    global latest_result
    reload_data()
    scenario = request.args.get("scenario", DEFAULT_SCENARIO).strip().lower()
    custom_config = parse_custom_weights_from_request(request)

    latest_result = run_optimization(scenario, custom_config)
    return jsonify(latest_result)


@app.route("/optimize/export.csv", methods=["GET"])
def optimize_export_csv():
    global latest_result
    reload_data()

    fresh = request.args.get("fresh", "false").lower() == "true"
    scenario = request.args.get("scenario", DEFAULT_SCENARIO).strip().lower()
    custom_config = parse_custom_weights_from_request(request)

    requested_scenario = "custom" if custom_config else scenario
    custom_changed = (
        custom_config is not None
        and latest_result is not None
        and latest_result.get("scenario") == "custom"
        and (
            latest_result.get("weights") != custom_config.get("weights")
            or latest_result.get("capacity_scale") != custom_config.get("capacity_scale")
        )
    )

    if fresh or latest_result is None or latest_result.get("scenario") != requested_scenario or custom_changed:
        latest_result = run_optimization(scenario, custom_config)

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["city", "allocated_refugees", "capacity", "usage_percent", "utilization_band"])
    for city in latest_result["city_allocations"]:
        writer.writerow([
            city["city"],
            city["allocated_refugees"],
            city["capacity"],
            city["usage_percent"],
            city["utilization_band"],
        ])

    writer.writerow([])
    writer.writerow(["summary_metric", "value"])
    writer.writerow(["optimization_status", latest_result["optimization_status"]])
    writer.writerow(["scenario", latest_result.get("scenario", "")])
    writer.writerow(["scenario_label", latest_result.get("scenario_label", "")])
    writer.writerow(["capacity_scale", latest_result.get("capacity_scale", "")])
    writer.writerow(["generated_at", latest_result["generated_at"]])
    writer.writerow(["objective_value", latest_result["objective_value"]])
    writer.writerow(["total_allocated_refugees", latest_result["total_allocated_refugees"]])
    writer.writerow(["unallocated_refugees", latest_result["unallocated_refugees"]])
    writer.writerow(["runtime_seconds", latest_result["runtime_seconds"]])
    writer.writerow(["coverage_percent", latest_result.get("coverage_percent", "")])
    writer.writerow(["score_per_allocated", latest_result.get("score_per_allocated", "")])

    baseline = latest_result.get("baseline", {})
    comparison = latest_result.get("model_comparison", {})
    writer.writerow(["baseline_method", baseline.get("method", "")])
    writer.writerow(["baseline_objective_value", baseline.get("objective_value", "")])
    writer.writerow(["baseline_total_allocated_refugees", baseline.get("total_allocated_refugees", "")])
    writer.writerow(["baseline_unallocated_refugees", baseline.get("unallocated_refugees", "")])
    writer.writerow(["baseline_coverage_percent", baseline.get("coverage_percent", "")])
    writer.writerow(["baseline_runtime_seconds", baseline.get("runtime_seconds", "")])
    writer.writerow(["objective_uplift_percent", comparison.get("objective_uplift_percent", "")])
    writer.writerow(["coverage_delta_points", comparison.get("coverage_delta_points", "")])
    writer.writerow(["allocated_delta", comparison.get("allocated_delta", "")])
    writer.writerow(["unallocated_reduction", comparison.get("unallocated_reduction", "")])
    writer.writerow(["score_per_allocated_delta", comparison.get("score_per_allocated_delta", "")])
    writer.writerow(["runtime_delta_seconds", comparison.get("runtime_delta_seconds", "")])
    writer.writerow(["total_city_reallocation", comparison.get("total_city_reallocation", "")])
    writer.writerow(["cities_with_different_allocations", comparison.get("cities_with_different_allocations", "")])
    writer.writerow(["max_city_shift", comparison.get("max_city_shift", "")])
    writer.writerow(["allocation_overlap_percent", comparison.get("allocation_overlap_percent", "")])

    filename = f"city_allocations_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'}
    )


if __name__ == "__main__":
    app.run(debug=True)