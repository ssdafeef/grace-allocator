import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import argparse
from app import run_optimization, reload_data, SCENARIO_PRESETS

plt.style.use('default')
plt.rcParams['figure.dpi'] = 300
plt.rcParams['savefig.dpi'] = 300
plt.rcParams['font.size'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10
plt.rcParams['legend.fontsize'] = 11

def collect_benchmarks(scenarios):
    reload_data()
    data = []
    for scenario in scenarios:
        if scenario not in SCENARIO_PRESETS:
            print(f"Skipping unknown scenario: {scenario}")
            continue
        result = run_optimization(scenario_name=scenario)
        baseline = result["baseline"]
        model = result
        comparison = result["model_comparison"]
        
        data.append({
            'scenario': scenario,
            'baseline_runtime': baseline['runtime_seconds'],
            'baseline_coverage': baseline['coverage_percent'],
            'baseline_score_per': baseline['score_per_allocated'],
            'baseline_allocated': baseline['total_allocated_refugees'],
            'model_runtime': model['runtime_seconds'],
            'model_coverage': model['coverage_percent'],
            'model_score_per': model['score_per_allocated'],
            'model_allocated': model['total_allocated_refugees'],
            'uplift_pct': comparison['objective_uplift_percent'] or 0.0,
            'unalloc_reduction': comparison['unallocated_reduction'],
            'alloc_overlap': comparison['allocation_overlap_percent'] or 0.0,
            'cities_changed': comparison['cities_with_different_allocations']
        })
    df = pd.DataFrame(data)
    return df

def plot_grouped_bar(df):
    # Average across scenarios for overall comparison
    avg_df = df.groupby('algorithm')[['runtime_seconds', 'coverage_percent', 'score_per_allocated', 'objective_uplift_percent']].mean().reset_index()
    
    x = np.arange(len(avg_df.columns[1:]))  # metrics
    width = 0.35
    
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.bar(x - width/2, avg_df.loc[avg_df['algorithm']=='baseline'].iloc[0,1:], width, label='Greedy Baseline', color='#9a3412', alpha=0.8)
    ax.bar(x + width/2, avg_df.loc[avg_df['algorithm']=='model'].iloc[0,1:], width, label='LP Optimization', color='#0f766e', alpha=0.8)
    
    ax.set_xlabel('Metrics')
    ax.set_ylabel('Value')
    ax.set_title('Grace Allocator: Greedy Baseline vs LP Optimization\\n(Averaged Across Scenarios)')
    ax.set_xticks(x)
    ax.set_xticklabels(['Runtime (s)', 'Coverage (%)', 'Score/Allocated', 'Objective Uplift (%)'])
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('benchmark_comparison_grouped.png', bbox_inches='tight')
    plt.close()
    print('Saved: benchmark_comparison_grouped.png')

def plot_scenario_lines(df):
    metrics = ['runtime_seconds', 'coverage_percent', 'score_per_allocated']
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    scenarios_order = sorted(df['scenario'].unique())
    
    for i, metric in enumerate(metrics):
        pivot = df.pivot(index='scenario', columns='algorithm', values=metric)
        pivot.plot(kind='line', ax=axes[i], marker='o', linewidth=2.5)
        axes[i].set_title(f'{metric.replace("_", " ").title()}')
        axes[i].set_xticklabels(scenarios_order, rotation=45)
        axes[i].grid(True, alpha=0.3)
        axes[i].legend(title='Algorithm')
    
    plt.suptitle('Performance Across Scenarios', fontsize=16)
    plt.tight_layout()
    plt.savefig('benchmark_scenario_lines.png', bbox_inches='tight')
    plt.close()
    print('Saved: benchmark_scenario_lines.png')

def plot_uplift_bar(df):
    model_df = df[df['algorithm']=='model']
    x = np.arange(len(model_df))
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(model_df['scenario'], model_df['objective_uplift_percent'], 
                  color=['#10b981' if v > 0 else '#ef4444' for v in model_df['objective_uplift_percent']],
                  alpha=0.8)
    ax.set_ylabel('Objective Uplift vs Baseline (%)')
    ax.set_title('Model Uplift Across Scenarios')
    ax.set_xticklabels(model_df['scenario'], rotation=45)
    ax.grid(True, alpha=0.3)
    
    # Add value labels
    for bar, val in zip(bars, model_df['objective_uplift_percent']):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, 
                f'{val:.1f}%', ha='center', va='bottom')
    
    plt.tight_layout()
    plt.savefig('benchmark_uplift.png', bbox_inches='tight')
    plt.close()
    print('Saved: benchmark_uplift.png')

def main():
    parser = argparse.ArgumentParser(description='Generate benchmark comparison graphs for Grace Allocator.')
    parser.add_argument('--scenarios', nargs='+', default=list(SCENARIO_PRESETS.keys()),
                        help='Scenarios to benchmark (default: all)')
    args = parser.parse_args()
    
    print('Running benchmarks for scenarios:', args.scenarios)
    df = collect_benchmarks(args.scenarios)
    
    plot_grouped_bar(df)
    plot_scenario_lines(df)
    plot_uplift_bar(df)
    
    print('\\nBenchmark graphs saved as PNGs. Ready for research paper screenshot!')
    print(df.head())

if __name__ == '__main__':
    main()
