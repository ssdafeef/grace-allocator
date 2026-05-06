import argparse
import json
from urllib.error import URLError, HTTPError
from urllib.request import urlopen

import matplotlib.pyplot as plt


def fetch_result_from_api(base_url: str, scenario: str) -> dict:
	url = f"{base_url.rstrip('/')}/optimize?scenario={scenario}"
	with urlopen(url, timeout=20) as response:
		return json.loads(response.read().decode("utf-8"))


def fetch_result_locally(scenario: str) -> dict:
	from app import run_optimization

	return run_optimization(scenario_name=scenario)


def get_result(scenario: str, base_url: str) -> dict:
	try:
		return fetch_result_from_api(base_url=base_url, scenario=scenario)
	except (URLError, HTTPError, TimeoutError):
		# Fallback if API is not running: execute optimization in-process.
		return fetch_result_locally(scenario=scenario)


def build_series(result: dict, top_n: int):
	baseline = result.get("baseline", {})
	baseline_allocs = baseline.get("city_allocations", [])
	model_allocs = result.get("city_allocations", [])

	baseline_map = {row["city"]: row["allocated_refugees"] for row in baseline_allocs}
	model_map = {row["city"]: row["allocated_refugees"] for row in model_allocs}

	merged = []
	for city in model_map:
		model_value = int(model_map.get(city, 0))
		baseline_value = int(baseline_map.get(city, 0))
		merged.append(
			{
				"city": city,
				"model": model_value,
				"baseline": baseline_value,
				"delta": model_value - baseline_value,
				"abs_delta": abs(model_value - baseline_value),
			}
		)

	merged.sort(key=lambda row: row["abs_delta"], reverse=True)
	top = merged[:top_n]

	cities = [row["city"] for row in top]
	model_values = [row["model"] for row in top]
	baseline_values = [row["baseline"] for row in top]
	deltas = [row["delta"] for row in top]

	return cities, model_values, baseline_values, deltas


def plot_model_vs_baseline(result: dict, top_n: int):
	cities, model_values, baseline_values, deltas = build_series(result=result, top_n=top_n)

	if not cities:
		raise ValueError("No city allocation data found in optimization output.")

	x = list(range(len(cities)))

	fig, (ax1, ax2) = plt.subplots(
		nrows=2,
		ncols=1,
		figsize=(14, 9),
		sharex=True,
		gridspec_kw={"height_ratios": [3, 1]},
	)

	ax1.plot(x, model_values, marker="o", linewidth=2.3, color="#0f766e", label="Model")
	ax1.plot(x, baseline_values, marker="s", linewidth=2.0, color="#9a3412", label="Baseline")
	ax1.fill_between(x, model_values, baseline_values, color="#0ea5e9", alpha=0.12)
	ax1.set_ylabel("Allocated Refugees")
	ax1.grid(alpha=0.25, linestyle="--", linewidth=0.7)
	ax1.legend(loc="upper right")

	scenario_label = result.get("scenario_label", result.get("scenario", "Unknown Scenario"))
	ax1.set_title(
		f"Model vs Baseline Allocation by City ({scenario_label})\nTop {len(cities)} Cities by Absolute Difference",
		pad=14,
	)

	delta_colors = ["#059669" if d >= 0 else "#dc2626" for d in deltas]
	ax2.bar(x, deltas, color=delta_colors, alpha=0.85)
	ax2.axhline(0, color="#475569", linewidth=1)
	ax2.set_ylabel("Delta")
	ax2.set_xlabel("City")
	ax2.grid(axis="y", alpha=0.2, linestyle="--", linewidth=0.6)

	plt.xticks(x, cities, rotation=45, ha="right")
	plt.tight_layout()
	plt.show()


def main():
	parser = argparse.ArgumentParser(description="Plot model-vs-baseline allocation differences.")
	parser.add_argument("--scenario", default="balanced", help="Scenario name (default: balanced)")
	parser.add_argument("--top-n", type=int, default=12, help="Number of cities to show (default: 12)")
	parser.add_argument(
		"--api-url",
		default="http://localhost:5000",
		help="Optimization API base URL (default: http://localhost:5000)",
	)
	args = parser.parse_args()

	result = get_result(scenario=args.scenario, base_url=args.api_url)
	plot_model_vs_baseline(result=result, top_n=max(1, args.top_n))


if __name__ == "__main__":
	main()
