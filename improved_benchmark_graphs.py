import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from math import pi
from app import run_optimization, reload_data, SCENARIO_PRESETS

import seaborn as sns
plt.style.use('default')
sns.set_style("whitegrid")
sns.set_palette("husl")
plt.rcParams.update({
    'figure.dpi': 300, 
    'savefig.dpi': 300,
    'font.size': 12,
    'axes.titlesize': 16,
    'axes.labelsize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 12
})

def collect_benchmarks(scenarios):
    reload_data()
    data = []
    for scenario in scenarios:
        if scenario not in SCENARIO_PRESETS:
            continue
        result = run_optimization(scenario)
        baseline = result["baseline"]
        comparison = result["model_comparison"]
        data.append({
            'scenario': scenario.title(),
            'baseline_runtime': baseline['runtime_seconds'],
            'baseline_coverage': baseline['coverage_percent'],
            'baseline_score': baseline['score_per_allocated'],
            'model_runtime': result['runtime_seconds'],
            'model_coverage': result['coverage_percent'],
            'model_score': result['score_per_allocated'],
            'uplift_pct': comparison.get('objective_uplift_percent', 0),
            'alloc_reduction': comparison.get('unallocated_reduction', 0),
            'overlap_pct': comparison.get('allocation_overlap_percent', 0),
            'cities_changed': comparison.get('cities_with_different_allocations', 0)
        })
    return pd.DataFrame(data)

def plot1_grouped_bars(df):
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    # Runtime comparison
    x = np.arange(len(df))
    width = 0.35
    axes[0,0].bar(x - width/2, df['baseline_runtime'], width, label='Greedy Baseline', color='orange', alpha=0.8)
    axes[0,0].bar(x + width/2, df['model_runtime'], width, label='LP Model', color='teal', alpha=0.8)
    axes[0,0].set_title('Runtime Comparison')
    axes[0,0].set_xticks(x)
    axes[0,0].set_xticklabels(df['scenario'], rotation=45)
    axes[0,0].legend()
    
    # Coverage
    axes[0,1].bar(x - width/2, df['baseline_coverage'], width, label='Baseline', color='orange')
    axes[0,1].bar(x + width/2, df['model_coverage'], width, label='Model', color='teal')
    axes[0,1].set_title('Coverage %')
    axes[0,1].set_xticks(x)
    axes[0,1].set_xticklabels(df['scenario'], rotation=45)
    axes[0,1].legend()
    
    # Score per refugee
    axes[1,0].bar(x - width/2, df['baseline_score'], width, label='Baseline', color='orange')
    axes[1,0].bar(x + width/2, df['model_score'], width, label='Model', color='teal')
    axes[1,0].set_title('Score per Allocated Refugee')
    axes[1,0].set_xticks(x)
    axes[1,0].set_xticklabels(df['scenario'], rotation=45)
    axes[1,0].legend()
    
    # Uplift
    axes[1,1].bar(df['scenario'], df['uplift_pct'], color='green', alpha=0.7)
    axes[1,1].set_title('Objective Uplift % vs Baseline')
    axes[1,1].tick_params(axis='x', rotation=45)
    
    plt.suptitle('Grace Allocator: Multi-Metric Comparison Across Scenarios', fontsize=18, y=0.98)
    plt.tight_layout()
    plt.savefig('paper_plot_1_grouped_bars.png', bbox_inches='tight', dpi=300)
    plt.close()
    print('📊 Saved: paper_plot_1_grouped_bars.png')

def plot2_line_trends(df):
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    scenarios = df['scenario']
    
    # Runtime trend
    axes[0,0].plot(scenarios, df['baseline_runtime'], 'o-', label='Baseline', linewidth=3, markersize=8)
    axes[0,0].plot(scenarios, df['model_runtime'], 's-', label='Model', linewidth=3, markersize=8)
    axes[0,0].set_title('Runtime Trend', fontweight='bold')
    axes[0,0].tick_params(axis='x', rotation=45)
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    
    # Coverage trend
    axes[0,1].plot(scenarios, df['baseline_coverage'], 'o-', label='Baseline', linewidth=3)
    axes[0,1].plot(scenarios, df['model_coverage'], 's-', label='Model', linewidth=3)
    axes[0,1].set_title('Coverage Trend', fontweight='bold')
    axes[0,1].tick_params(axis='x', rotation=45)
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.3)
    
    # Score trend
    axes[1,0].plot(scenarios, df['baseline_score'], 'o-', label='Baseline', linewidth=3)
    axes[1,0].plot(scenarios, df['model_score'], 's-', label='Model', linewidth=3)
    axes[1,0].set_title('Score/Refugee Trend', fontweight='bold')
    axes[1,0].tick_params(axis='x', rotation=45)
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.3)
    
    # Uplift trend
    axes[1,1].plot(scenarios, df['uplift_pct'], 'D-', color='green', linewidth=3, markersize=8)
    axes[1,1].set_title('Uplift % Trend', fontweight='bold')
    axes[1,1].tick_params(axis='x', rotation=45)
    axes[1,1].grid(True, alpha=0.3)
    
    plt.suptitle('Grace Allocator: Performance Trends Across Scenarios', fontsize=18)
    plt.tight_layout()
    plt.savefig('paper_plot_2_lines.png', bbox_inches='tight', dpi=300)
    plt.close()
    print('📈 Saved: paper_plot_2_lines.png')

def plot3_scatter_matrix(df):
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
    
    # Runtime vs Coverage
    scatter1 = ax1.scatter(df['baseline_runtime'], df['baseline_coverage'], s=200, alpha=0.7, label='Baseline', color='orange')
    scatter2 = ax1.scatter(df['model_runtime'], df['model_coverage'], s=200, alpha=0.7, label='Model', color='teal')
    ax1.set_xlabel('Runtime (s)')
    ax1.set_ylabel('Coverage (%)')
    ax1.set_title('Runtime vs Coverage Pareto')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Uplift vs Overlap
    scatter = ax2.scatter(df['overlap_pct'], df['uplift_pct'], s=df['cities_changed']*20 + 100, 
                          c=df['cities_changed'], cmap='viridis', alpha=0.8)
    ax2.set_xlabel('Overlap %')
    ax2.set_ylabel('Uplift %')
    ax2.set_title('Stability vs Improvement (size = cities changed)')
    plt.colorbar(scatter, ax=ax2)
    ax2.grid(True, alpha=0.3)
    
    # Reduction vs Uplift
    ax3.scatter(df['uplift_pct'], df['alloc_reduction'], s=150, alpha=0.8, color='purple')
    ax3.set_xlabel('Uplift %')
    ax3.set_ylabel('Unallocated Reduction')
    ax3.set_title('Efficiency Gains')
    ax3.grid(True, alpha=0.3)
    
    plt.suptitle('Grace Allocator: Scatter Analysis', fontsize=18)
    plt.tight_layout()
    plt.savefig('paper_plot_3_scatter.png', bbox_inches='tight', dpi=300)
    plt.close()
    print('🔍 Saved: paper_plot_3_scatter.png')

def plot4_radar_summary(df):
    # Radar chart for average model advantages
    categories = ['Runtime\\nRatio', 'Coverage\\nGain', 'Score\\nGain', 'Uplift\\n%', 'Overlap\\n%']
    N = len(categories)
    
    runtime_ratio = df['model_runtime'].mean() / df['baseline_runtime'].mean()
    coverage_gain = df['model_coverage'].mean() / df['baseline_coverage'].mean()
    score_gain = df['model_score'].mean() / df['baseline_score'].mean()
    uplift_norm = df['uplift_pct'].mean() / 100 + 1
    overlap = df['overlap_pct'].mean() / 100
    
    values = [runtime_ratio, coverage_gain, score_gain, uplift_norm, overlap]
    angles = np.linspace(0, 2 * pi, N, endpoint=False).tolist()
    values = values + values[:1]
    angles = angles + angles[:1]
    
    fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(projection='polar'))
    ax.plot(angles, values, 'o-', linewidth=3, markersize=10, color='darkblue', label='Model vs Baseline')
    ax.fill(angles, values, alpha=0.25, color='darkblue')
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    ax.set_ylim(0, max(2, max(values)*1.1))
    ax.set_title('Model Performance Profile (Normalized Advantages)', size=18, pad=20, fontweight='bold')
    ax.grid(True)
    
    plt.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
    plt.tight_layout()
    plt.savefig('paper_plot_4_radar.png', bbox_inches='tight', dpi=300)
    plt.close()
    print('📏 Saved: paper_plot_4_radar.png')

def plot5_heatmap(df):
    # Heatmap of key metrics
    metrics_df = df[['scenario', 'baseline_coverage', 'model_coverage', 'uplift_pct', 'overlap_pct']].set_index('scenario')
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(metrics_df.T, annot=True, fmt='.1f', cmap='RdYlGn', center=50, ax=ax,
                cbar_kws={'label': 'Value'})
    ax.set_title('Performance Heatmap Across Scenarios', fontsize=16, fontweight='bold')
    plt.tight_layout()
    plt.savefig('paper_plot_5_heatmap.png', bbox_inches='tight', dpi=300)
    plt.close()
    print('🔥 Saved: paper_plot_5_heatmap.png')

def main():
    parser = argparse.ArgumentParser(description='Advanced benchmark graphs for Grace Allocator research paper.')
    parser.add_argument('--scenarios', nargs='+', default=list(SCENARIO_PRESETS.keys()))
    args = parser.parse_args()
    
    print('🔄 Computing benchmarks for:', args.scenarios)
    df = collect_benchmarks(args.scenarios)
    print(df)
    
    print('\n📊 Generating 5 research-quality plots:')
    plot1_grouped_bars(df)
    plot2_line_trends(df)
    plot3_scatter_matrix(df)
    plot4_radar_summary(df)
    plot5_heatmap(df)
    
    print('\n✅ ALL PLOTS SAVED! Perfect for research paper screenshots:')
    print('- paper_plot_1_grouped_bars.png')
    print('- paper_plot_2_lines.png') 
    print('- paper_plot_3_scatter.png')
    print('- paper_plot_4_radar.png')
    print('- paper_plot_5_heatmap.png')

if __name__ == '__main__':
    main()
