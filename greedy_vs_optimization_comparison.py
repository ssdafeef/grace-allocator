import matplotlib.pyplot as plt
import numpy as np
from app import run_optimization, reload_data, SCENARIO_PRESETS

plt.rcParams['figure.figsize'] = (14, 10)
plt.rcParams['font.size'] = 14
plt.rcParams['axes.titlesize'] = 18
plt.rcParams['axes.labelsize'] = 16
plt.rcParams['xtick.labelsize'] = 12
plt.rcParams['ytick.labelsize'] = 12
plt.rcParams['legend.fontsize'] = 14

def run_benchmarks():
    reload_data()
    scenarios = ['balanced', 'capacity_stress', 'jobs_priority', 'integration_priority']
    
    greedy_runtimes = []
    opt_runtimes = []
    greedy_coverage = []
    opt_coverage = []
    greedy_score = []
    opt_score = []
    uplift = []
    scenario_labels = []
    
    for scenario in scenarios:
        print(f'Running {scenario}...')
        result = run_optimization(scenario)
        baseline = result['baseline']
        
        greedy_runtimes.append(baseline['runtime_seconds'])
        opt_runtimes.append(result['runtime_seconds'])
        greedy_coverage.append(baseline['coverage_percent'])
        opt_coverage.append(result['coverage_percent'])
        greedy_score.append(baseline['score_per_allocated'])
        opt_score.append(result['score_per_allocated'])
        uplift.append(result['model_comparison'].get('objective_uplift_percent', 0))
        scenario_labels.append(scenario.replace('_', ' ').title())
    
    return {
        'scenarios': scenario_labels,
        'greedy_runtime': np.array(greedy_runtimes),
        'opt_runtime': np.array(opt_runtimes),
        'greedy_coverage': np.array(greedy_coverage),
        'opt_coverage': np.array(opt_coverage),
        'greedy_score': np.array(greedy_score),
        'opt_score': np.array(opt_score),
        'uplift': np.array(uplift)
    }

def create_master_comparison(data):
    fig = plt.figure(figsize=(20, 16))
    
    # 2x2 grid of subplots
    ax1 = plt.subplot(2, 2, 1)
    x = np.arange(len(data['scenarios']))
    width = 0.35
    
    ax1.bar(x - width/2, data['greedy_runtime'], width, label='Greedy Baseline', color='#ff6b35', alpha=0.9, edgecolor='darkred')
    ax1.bar(x + width/2, data['opt_runtime'], width, label='LP Optimization', color='#4ecdc4', alpha=0.9, edgecolor='darkcyan')
    ax1.set_title('Runtime Comparison', fontweight='bold', fontsize=20)
    ax1.set_ylabel('Time (seconds)')
    ax1.set_xticks(x)
    ax1.set_xticklabels(data['scenarios'], rotation=45, ha='right')
    ax1.legend(fontsize=14)
    ax1.grid(axis='y', alpha=0.3)
    
    ax2 = plt.subplot(2, 2, 2)
    ax2.bar(x - width/2, data['greedy_coverage'], width, label='Greedy Baseline', color='#ff6b35', alpha=0.9)
    ax2.bar(x + width/2, data['opt_coverage'], width, label='LP Optimization', color='#4ecdc4', alpha=0.9)
    ax2.set_title('Coverage Comparison', fontweight='bold', fontsize=20)
    ax2.set_ylabel('Coverage (%)')
    ax2.set_xticks(x)
    ax2.set_xticklabels(data['scenarios'], rotation=45, ha='right')
    ax2.legend(fontsize=14)
    ax2.grid(axis='y', alpha=0.3)
    
    ax3 = plt.subplot(2, 2, 3)
    ax3.bar(x - width/2, data['greedy_score'], width, label='Greedy Baseline', color='#ff6b35', alpha=0.9)
    ax3.bar(x + width/2, data['opt_score'], width, label='LP Optimization', color='#4ecdc4', alpha=0.9)
    ax3.set_title('Score per Refugee', fontweight='bold', fontsize=20)
    ax3.set_ylabel('Score')
    ax3.set_xticks(x)
    ax3.set_xticklabels(data['scenarios'], rotation=45, ha='right')
    ax3.legend(fontsize=14)
    ax3.grid(axis='y', alpha=0.3)
    
    # Uplift subplot with value labels
    ax4 = plt.subplot(2, 2, 4)
    colors = ['darkgreen' if u > 0 else 'darkred' for u in data['uplift']]
    bars = ax4.bar(data['scenarios'], data['uplift'], color=colors, alpha=0.9, edgecolor='black', linewidth=2)
    ax4.set_title('LP Model Uplift vs Greedy Baseline', fontweight='bold', fontsize=20)
    ax4.set_ylabel('Improvement (%)')
    ax4.axhline(y=0, color='black', linestyle='-', alpha=0.5)
    ax4.tick_params(axis='x', rotation=45)
    ax4.grid(axis='y', alpha=0.3)
    
    # Add value labels on bars
    for bar, value in zip(bars, data['uplift']):
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., height + (0.5 if height > 0 else -1),
                f'{value:+.1f}%', ha='center', va='bottom' if height > 0 else 'top',
                fontweight='bold', fontsize=13)
    
    plt.suptitle('Grace Allocator: GREEDY BASELINE vs LP OPTIMIZATION MODEL\\nFull Performance Comparison (4 Scenarios)', 
                 fontsize=24, fontweight='bold', y=0.98)
    plt.tight_layout()
    plt.savefig('greedy_vs_optimization_master.png', dpi=300, bbox_inches='tight')
    plt.close()
    print('✅ SAVED: greedy_vs_optimization_master.png - Master comparison figure!')

if __name__ == '__main__':
    print('Computing Greedy vs Optimization benchmarks...')
    data = run_benchmarks()
    create_master_comparison(data)
    print('\\n🎯 MASTER COMPARISON GRAPH READY!')
    print('📁 File: greedy_vs_optimization_master.png')
    print('📏 Size: High-res (300 DPI) publication quality')
    print('✅ Perfect single-screenshot for research paper!')
