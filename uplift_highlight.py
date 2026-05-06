import matplotlib.pyplot as plt
import numpy as np
from app import run_optimization, reload_data, SCENARIO_PRESETS

# Ultra-high quality single chart styling
plt.rcParams.update({
    'figure.figsize': (16, 12),
    'figure.dpi': 300,
    'savefig.dpi': 400,
    'font.size': 18,
    'axes.titlesize': 28,
    'axes.labelsize': 22,
    'xtick.labelsize': 16,
    'ytick.labelsize': 18,
    'legend.fontsize': 20,
    'axes.linewidth': 2.5,
    'grid.linewidth': 1.5
})

def get_uplift_data():
    reload_data()
    scenarios = ['balanced', 'capacity_stress', 'jobs_priority', 'integration_priority']
    uplift_values = []
    scenario_names = []
    
    print('Computing LP vs Greedy uplift across scenarios...')
    
    for scenario in scenarios:
        result = run_optimization(scenario)
        uplift = result['model_comparison'].get('objective_uplift_percent', 0)
        uplift_values.append(uplift)
        scenario_names.append(scenario.replace('_', ' ').title())
    
    return scenario_names, uplift_values

def create_uplift_master_chart():
    scenarios, uplifts = get_uplift_data()
    x = np.arange(len(scenarios))
    
    # Determine colors and create figure
    colors = ['#27ae60' if u > 0 else '#e74c3c' for u in uplifts]  # Green positive, Red negative
    
    fig, ax = plt.subplots(figsize=(16, 12))
    
    # Main bars with thick edges
    bars = ax.bar(x, uplifts, width=0.65, color=colors, alpha=0.92, 
                  edgecolor='black', linewidth=4, capsize=15)
    
    # Zero line
    ax.axhline(y=0, color='black', linewidth=4, alpha=0.8, zorder=0)
    
    # Massive value labels
    for i, (bar, uplift) in enumerate(zip(bars, uplifts)):
        height = bar.get_height()
        label_y = height * 1.05 if height > 0 else height * 0.95
        va = 'bottom' if height > 0 else 'top'
        label_color = 'darkgreen' if height > 0 else 'darkred'
        
        ax.text(bar.get_x() + bar.get_width()/2, label_y, f'{uplift:+.1f}%', 
                ha='center', va=va, fontsize=32, fontweight='bold', 
                color=label_color, fontfamily='serif',
                bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.9, edgecolor=label_color))
    
    # Styling
    ax.set_title('GRACE ALLOCATOR: LP OPTIMIZATION vs GREEDY BASELINE\\nObjective Function Uplift Percentage', 
                 fontsize=32, fontweight='bold', pad=40, color='#2c3e50')
    ax.set_xlabel('Scenarios', fontsize=24, fontweight='bold', labelpad=20)
    ax.set_ylabel('Objective Uplift (%)', fontsize=24, fontweight='bold', labelpad=25)
    
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, rotation=20, ha='right', fontsize=18)
    
    # Legend showing Greedy baseline = 0%
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='none', edgecolor='black', label='Greedy Baseline = 0% (reference)'),
        Patch(facecolor='none', label=f'LP Model Uplift: Mean = {np.mean(uplifts):+.1f}%')
    ]
    ax.legend(handles=legend_elements, loc='upper left', bbox_to_anchor=(0.02, 0.98), 
              fontsize=18, frameon=True, fancybox=True, shadow=True)
    
    # Enhanced grid
    ax.grid(True, axis='y', alpha=0.4, linestyle='-', linewidth=2)
    ax.set_axisbelow(True)
    
    # Tight layout with padding
    plt.tight_layout(pad=3.0)
    
    # Save with max quality
    plt.savefig('LP_vs_Greedy_Uplift_Highlight.png', bbox_inches='tight', 
                facecolor='white', edgecolor=None, dpi=400)
    plt.close()
    
    print('✅ UPLIFT HIGHLIGHT CHART SAVED!')
    print('📁 LP_vs_Greedy_Uplift_Highlight.png')
    print('🎨 16x12in @ 400 DPI - Paper Perfect!')
    print('📊 Mean uplift:', f'{np.mean(uplifts):+.1f}% across {len(scenarios)} scenarios')

if __name__ == '__main__':
    create_uplift_master_chart()
