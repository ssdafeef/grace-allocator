import matplotlib.pyplot as plt
import numpy as np
from app import run_optimization, reload_data, SCENARIO_PRESETS

# High-quality publication styling
plt.rcParams.update({
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'figure.figsize': (18, 14),
    'font.family': 'serif',
    'font.size': 13,
    'axes.titlesize': 20,
    'axes.labelsize': 16,
    'xtick.labelsize': 12,
    'ytick.labelsize': 12,
    'legend.fontsize': 14,
    'figure.titlesize': 24
})

def benchmark_all_scenarios():
    reload_data()
    scenarios = ['balanced', 'capacity_stress', 'jobs_priority', 'integration_priority']
    results = {}
    
    print('Benchmarking Greedy vs Optimization across scenarios...')
    
    for scenario in scenarios:
        print(f'  Running {scenario}...')
        result = run_optimization(scenario)
        baseline = result['baseline']
        comparison = result['model_comparison']
        
        results[scenario.replace('_', ' ').title()] = {
            'greedy_runtime': round(baseline['runtime_seconds'], 3),
            'opt_runtime': round(result['runtime_seconds'], 3),
            'greedy_coverage': round(baseline['coverage_percent'], 2),
            'opt_coverage': round(result['coverage_percent'], 2),
            'greedy_score': round(baseline['score_per_allocated'], 4),
            'opt_score': round(result['score_per_allocated'], 4),
            'uplift_pct': round(comparison.get('objective_uplift_percent', 0), 1),
            'coverage_gain_pts': round(result['coverage_percent'] - baseline['coverage_percent'], 2),
            'score_gain': round(result['score_per_allocated'] - baseline['score_per_allocated'], 4),
            'runtime_ratio': round(result['runtime_seconds'] / baseline['runtime_seconds'], 2) if baseline['runtime_seconds'] > 0 else 0,
            'unalloc_reduction': comparison.get('unallocated_reduction', 0)
        }
    
    return results

def create_detailed_comparison(results):
    scenarios = list(results.keys())
    n_scenarios = len(scenarios)
    x = np.arange(n_scenarios)
    width = 0.25
    
    fig = plt.figure(figsize=(20, 16))
    
    # Top row: Primary metrics (Runtime, Coverage, Score)
    ax1 = plt.subplot2grid((3, 3), (0, 0), colspan=1, rowspan=1)
    ax1.bar(x - width, [results[s]['greedy_runtime'] for s in scenarios], width, 
            label='Greedy Baseline', color='#e74c3c', alpha=0.9, edgecolor='darkred', linewidth=1.5)
    ax1.bar(x, [results[s]['opt_runtime'] for s in scenarios], width, 
            label='LP Optimization', color='#3498db', alpha=0.9, edgecolor='navy', linewidth=1.5)
    ax1.set_title('Runtime (seconds)', fontweight='bold', pad=20)
    ax1.set_ylabel('Time')
    ax1.set_xticks(x)
    ax1.set_xticklabels(scenarios, rotation=45, ha='right')
    ax1.legend()
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    ax2 = plt.subplot2grid((3, 3), (0, 1), colspan=1, rowspan=1)
    ax2.bar(x - width, [results[s]['greedy_coverage'] for s in scenarios], width, 
            label='Greedy', color='#e74c3c', alpha=0.9)
    ax2.bar(x, [results[s]['opt_coverage'] for s in scenarios], width, 
            label='Optimization', color='#3498db', alpha=0.9)
    ax2.set_title('Coverage Percentage', fontweight='bold', pad=20)
    ax2.set_ylabel('Coverage (%)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(scenarios, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    ax3 = plt.subplot2grid((3, 3), (0, 2), colspan=1, rowspan=1)
    ax3.bar(x - width, [results[s]['greedy_score'] for s in scenarios], width, 
            label='Greedy', color='#e74c3c', alpha=0.9)
    ax3.bar(x, [results[s]['opt_score'] for s in scenarios], width, 
            label='Optimization', color='#3498db', alpha=0.9)
    ax3.set_title('Score per Refugee', fontweight='bold', pad=20)
    ax3.set_ylabel('Score')
    ax3.set_xticks(x)
    ax3.set_xticklabels(scenarios, rotation=45, ha='right')
    ax3.legend()
    ax3.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Middle row: Key gains/deltas
    ax4 = plt.subplot2grid((3, 3), (1, 0), colspan=1, rowspan=1)
    gains = [results[s]['coverage_gain_pts'] for s in scenarios]
    colors = ['green' if g > 0 else 'red' for g in gains]
    bars = ax4.bar(scenarios, gains, color=colors, alpha=0.9, edgecolor='black')
    ax4.set_title('Coverage Gain (points)', fontweight='bold', pad=20)
    ax4.set_ylabel('Gain')
    ax4.axhline(y=0, color='black', linewidth=2, alpha=0.7)
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(axis='y', alpha=0.3)
    
    # Value labels
    for bar, gain in zip(bars, gains):
        ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (0.1 if gain > 0 else -0.3),
                f'{gain:+.2f}', ha='center', va='bottom' if gain > 0 else 'top', 
                fontweight='bold', fontsize=12)
    
    ax5 = plt.subplot2grid((3, 3), (1, 1), colspan=1, rowspan=1)
    score_gains = [results[s]['score_gain'] for s in scenarios]
    colors = ['green' if g > 0 else 'red' for g in score_gains]
    bars = ax5.bar(scenarios, score_gains, color=colors, alpha=0.9, edgecolor='black')
    ax5.set_title('Score Gain per Refugee', fontweight='bold', pad=20)
    ax5.set_ylabel('Gain')
    ax5.axhline(y=0, color='black', linewidth=2, alpha=0.7)
    ax5.tick_params(axis='x', rotation=45)
    ax5.grid(axis='y', alpha=0.3)
    
    for bar, gain in zip(bars, score_gains):
        ax5.text(bar.get_x() + bar.get_width()/2, bar.get_height() + (0.0001 if gain > 0 else -0.0002),
                f'{gain:+.4f}', ha='center', va='bottom' if gain > 0 else 'top', fontweight='bold', fontsize=11)
    
    ax6 = plt.subplot2grid((3, 3), (1, 2), colspan=1, rowspan=1)
    bars = ax6.bar(scenarios, [results[s]['unalloc_reduction'] for s in scenarios], 
                   color='gold', alpha=0.9, edgecolor='darkgoldenrod')
    ax6.set_title('Unallocated Refugees Reduced', fontweight='bold', pad=20)
    ax6.set_ylabel('Count')
    ax6.tick_params(axis='x', rotation=45)
    ax6.grid(axis='y', alpha=0.3)
    
    # Bottom: Main event - Objective Uplift
    ax7 = plt.subplot2grid((3, 3), (2, 0), colspan=3, rowspan=1)
    colors = ['darkgreen' if u > 0 else 'darkred' for u in [results[s]['uplift_pct'] for s in scenarios]]
    bars = ax7.bar(scenarios, [results[s]['uplift_pct'] for s in scenarios], width=0.6, 
                   color=colors, alpha=0.95, edgecolor='black', linewidth=2.5)
    ax7.set_title('LP OPTIMIZATION vs GREEDY BASELINE: OBJECTIVE UPLIFT (%)', 
                  fontweight='bold', fontsize=22, pad=30, color='darkblue')
    ax7.set_ylabel('Improvement (%)', fontweight='bold')
    ax7.axhline(y=0, color='black', linewidth=3, alpha=0.8)
    ax7.tick_params(axis='x', rotation=45)
    ax7.grid(axis='y', alpha=0.4, linestyle='-', linewidth=1)
    
    # Large value labels on main uplift chart
    for bar, uplift in zip(bars, [results[s]['uplift_pct'] for s in scenarios]):
        height = bar.get_height()
        label_y = height + (2 if height > 0 else -3)
        va = 'bottom' if height > 0 else 'top'
        color = 'darkgreen' if height > 0 else 'darkred'
        ax7.text(bar.get_x() + bar.get_width()/2, label_y, f'{uplift:.1f}%', 
                ha='center', va=va, fontweight='bold', fontsize=18, color=color)
    
    ax7.legend(['Greedy Baseline = 0%', 'LP Model Uplift'], loc='upper left', fontsize=14)
    
    plt.suptitle('GRACE ALLOCATOR: COMPREHENSIVE GREEDY BASELINE vs LP OPTIMIZATION COMPARISON', 
                 fontsize=28, fontweight='bold', y=0.96, color='#2c3e50')
    
    plt.tight_layout()
    plt.savefig('detailed_greedy_vs_optimization.png', dpi=300, bbox_inches='tight', 
                facecolor='white', edgecolor='none')
    plt.close()
    
    print('✅ DETAILED MASTER COMPARISON SAVED: detailed_greedy_vs_optimization.png')

if __name__ == '__main__':
    results = benchmark_all_scenarios()
    create_detailed_comparison(results)
    print('\n' + '='*80)
    print('🎉 WELL-DETAILED GREEDY vs OPTIMIZATION COMPARISON READY!')
    print('📁 FILE: detailed_greedy_vs_optimization.png')
    print('📐 SIZE: 18x14 inches @ 300 DPI - Publication Perfect')
    print('🖼️  PERFECT SINGLE SCREENSHOT FOR RESEARCH PAPER')
    print('='*80)
