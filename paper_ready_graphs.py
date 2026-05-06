import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from math import pi
from app import run_optimization, reload_data, SCENARIO_PRESETS

# Setup publication-ready styling
plt.rcParams.update({
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'figure.figsize': (10, 8),
    'font.size': 12,
    'axes.titlesize': 16,
    'axes.labelsize': 14,
    'xtick.labelsize': 11,
    'ytick.labelsize': 11,
    'legend.fontsize': 12
})
sns.set_style("whitegrid")

def collect_data():
    reload_data()
    scenarios = ['balanced', 'capacity_stress', 'jobs_priority', 'integration_priority']
    data = []
    
    for scenario in scenarios:
        result = run_optimization(scenario)
        baseline = result["baseline"]
        comparison = result["model_comparison"]
        
        data.append({
            'Scenario': scenario.replace('_', ' ').title(),
            'Baseline Runtime (s)': round(baseline['runtime_seconds'], 2),
            'Model Runtime (s)': round(result['runtime_seconds'], 2),
            'Baseline Coverage (%)': round(baseline['coverage_percent'], 1),
            'Model Coverage (%)': round(result['coverage_percent'], 1),
            'Baseline Score/Refugee': round(baseline['score_per_allocated'], 3),
            'Model Score/Refugee': round(result['score_per_allocated'], 3),
            'Objective Uplift (%)': round(comparison.get('objective_uplift_percent', 0), 1),
            'Overlap (%)': round(comparison.get('allocation_overlap_percent', 0), 1),
            'Cities Changed': comparison.get('cities_with_different_allocations', 0)
        })
    return pd.DataFrame(data)

def plot_type_1_comprehensive_bars(df):
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    x = np.arange(len(df))
    width = 0.35
    
    # Runtime
    axes[0,0].bar(x - width/2, df['Baseline Runtime (s)'], width, label='Greedy Baseline', color='coral', alpha=0.8)
    axes[0,0].bar(x + width/2, df['Model Runtime (s)'], width, label='LP Model', color='darkcyan', alpha=0.8)
    axes[0,0].set_title('Runtime Comparison (seconds)')
    axes[0,0].set_xticks(x)
    axes[0,0].set_xticklabels(df['Scenario'], rotation=45, ha='right')
    axes[0,0].legend()
    
    # Coverage
    axes[0,1].bar(x - width/2, df['Baseline Coverage (%)'], width, label='Baseline', color='coral')
    axes[0,1].bar(x + width/2, df['Model Coverage (%)'], width, label='Model', color='darkcyan')
    axes[0,1].set_title('Coverage Percentage')
    axes[0,1].set_xticks(x)
    axes[0,1].set_xticklabels(df['Scenario'], rotation=45, ha='right')
    axes[0,1].legend()
    
    # Score per Refugee
    axes[1,0].bar(x - width/2, df['Baseline Score/Refugee'], width, label='Baseline', color='coral')
    axes[1,0].bar(x + width/2, df['Model Score/Refugee'], width, label='Model', color='darkcyan')
    axes[1,0].set_title('Score per Allocated Refugee')
    axes[1,0].set_xticks(x)
    axes[1,0].set_xticklabels(df['Scenario'], rotation=45, ha='right')
    axes[1,0].legend()
    
    # Uplift
    bars = axes[1,1].bar(df['Scenario'], df['Objective Uplift (%)'], color=['green' if v > 0 else 'red' for v in df['Objective Uplift (%)']], alpha=0.8)
    axes[1,1].set_title('Objective Uplift vs Baseline (%)')
    axes[1,1].tick_params(axis='x', rotation=45)
    
    # Value labels on uplift bars
    for bar, val in zip(bars, df['Objective Uplift (%)']):
        height = bar.get_height()
        axes[1,1].text(bar.get_x() + bar.get_width()/2., height + 0.2,
                     f'{val}%', ha='center', va='bottom', fontweight='bold')
    
    plt.suptitle('Grace Allocator: Algorithm Performance Comparison (4 Scenarios)', fontsize=20, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig('research_paper_figure_1.png', bbox_inches='tight')
    plt.close()
    print('✅ TYPE 1: research_paper_figure_1.png - Grouped Bar Charts')

def plot_type_2_line_charts(df):
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    
    scenarios = df['Scenario']
    
    # Runtime lines
    axes[0,0].plot(scenarios, df['Baseline Runtime (s)'], 'o-', linewidth=3, markersize=10, label='Greedy Baseline', color='coral')
    axes[0,0].plot(scenarios, df['Model Runtime (s)'], 's-', linewidth=3, markersize=10, label='LP Model', color='darkcyan')
    axes[0,0].set_title('Runtime Evolution', fontweight='bold')
    axes[0,0].tick_params(axis='x', rotation=45)
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.4)
    
    # Coverage lines
    axes[0,1].plot(scenarios, df['Baseline Coverage (%)'], 'o-', linewidth=3, label='Baseline', color='coral')
    axes[0,1].plot(scenarios, df['Model Coverage (%)'], 's-', linewidth=3, label='Model', color='darkcyan')
    axes[0,1].set_title('Coverage Evolution', fontweight='bold')
    axes[0,1].tick_params(axis='x', rotation=45)
    axes[0,1].legend()
    axes[0,1].grid(True, alpha=0.4)
    
    # Score lines
    axes[1,0].plot(scenarios, df['Baseline Score/Refugee'], 'o-', linewidth=3, label='Baseline', color='coral')
    axes[1,0].plot(scenarios, df['Model Score/Refugee'], 's-', linewidth=3, label='Model', color='darkcyan')
    axes[1,0].set_title('Score per Refugee Evolution', fontweight='bold')
    axes[1,0].tick_params(axis='x', rotation=45)
    axes[1,0].legend()
    axes[1,0].grid(True, alpha=0.4)
    
    # Uplift line
    axes[1,1].plot(scenarios, df['Objective Uplift (%)'], 'D-', linewidth=4, markersize=12, color='darkgreen', markerfacecolor='lightgreen')
    axes[1,1].fill_between(scenarios, df['Objective Uplift (%)'], alpha=0.3, color='green')
    axes[1,1].set_title('Model Improvement vs Baseline', fontweight='bold')
    axes[1,1].tick_params(axis='x', rotation=45)
    axes[1,1].grid(True, alpha=0.4)
    
    plt.suptitle('Grace Allocator: Performance Trends (4 Scenarios)', fontsize=20, fontweight='bold')
    plt.tight_layout()
    plt.savefig('research_paper_figure_2.png', bbox_inches='tight')
    plt.close()
    print('✅ TYPE 2: research_paper_figure_2.png - Line Charts')

def plot_type_3_scatter_plots(df):
    fig, axes = plt.subplots(2, 2, figsize=(15, 12))
    
    # Pareto front: Runtime vs Coverage
    axes[0,0].scatter(df['Baseline Runtime (s)'], df['Baseline Coverage (%)'], s=300, alpha=0.7, label='Greedy Baseline', 
                      color='coral', edgecolors='darkred', linewidth=2)
    axes[0,0].scatter(df['Model Runtime (s)'], df['Model Coverage (%)'], s=300, alpha=0.7, label='LP Model', 
                      color='darkcyan', edgecolors='navy', linewidth=2)
    axes[0,0].set_xlabel('Runtime (s)')
    axes[0,0].set_ylabel('Coverage (%)')
    axes[0,0].set_title('Runtime-Coverage Pareto Front')
    axes[0,0].legend()
    axes[0,0].grid(True, alpha=0.3)
    
    # Uplift vs Stability
    sizes = df['Cities Changed'] * 30 + 200
    scatter = axes[0,1].scatter(df['Overlap (%)'], df['Objective Uplift (%)'], s=sizes, alpha=0.8,
                                c=df['Cities Changed'], cmap='plasma', edgecolors='black')
    axes[0,1].set_xlabel('Allocation Overlap (%)')
    axes[0,1].set_ylabel('Objective Uplift (%)')
    axes[0,1].set_title('Stability vs Improvement\\n(bubble size = cities changed)')
    plt.colorbar(scatter, ax=axes[0,1], label='Cities Changed')
    axes[0,1].grid(True, alpha=0.3)
    
    # Uplift vs Reduction
    axes[1,0].scatter(df['Objective Uplift (%)'], df['alloc_reduction'] / 1000, s=250, alpha=0.8, color='mediumpurple')
    axes[1,0].set_xlabel('Objective Uplift (%)')
    axes[1,0].set_ylabel('Unallocated Reduction (K)')
    axes[1,0].set_title('Efficiency Frontier')
    axes[1,0].grid(True, alpha=0.3)
    
    plt.suptitle('Grace Allocator: Advanced Visualization Suite', fontsize=20, fontweight='bold')
    plt.tight_layout()
    plt.savefig('research_paper_figure_3.png', bbox_inches='tight')
    plt.close()
    print('✅ TYPE 3: research_paper_figure_3.png - Scatter Plots')

def main():
    print('🚀 Generating RESEARCH PAPER-READY comparison graphs for Grace Allocator...')
    df = collect_data()
    print('\nData summary:')
    print(df[['Scenario', 'Objective Uplift (%)', 'Model Coverage (%)', 'Overlap (%)']])
    
    plot_type_1_comprehensive_bars(df)
    plot_type_2_line_charts(df)
    plot_type_3_scatter_plots(df)
    
    print('\n🎉 SUCCESS! 3 publication-ready figures generated:')
    print('   research_paper_figure_1.png  → Grouped bars (best for table comparison)')
    print('   research_paper_figure_2.png  → Line trends (best for scenario analysis)')
    print('   research_paper_figure_3.png  → Scatter plots (best for trade-offs)')
    print('\n📸 Open these PNGs for perfect research paper screenshots!')

if __name__ == '__main__':
    main()
