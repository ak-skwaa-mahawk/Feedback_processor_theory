#!/usr/bin/env python3
"""
Polygonal Validation Visualization
===================================
Generate publication-quality figures for validation study.

Part of: Feedback Processor Theory (Two Mile Solutions LLC)
Author: John Carroll
License: Open Collaborative License v1.0

Usage:
    python visualize_polygonal.py [--input FILE] [--output-dir DIR]
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pathlib import Path
import argparse
import seaborn as sns

# Set publication-quality style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


# ============================================================================
# MAIN VISUALIZATIONS
# ============================================================================

def create_coherence_plot(df: pd.DataFrame, output_path: Path):
    """Generate main coherence vs disruption plot."""
    
    # Compute mean coherence by polygon and disruption
    summary = df.groupby(['polygon', 'sides', 'disruption'])['coherence'].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot each polygon
    polygons = summary['polygon'].unique()
    colors = plt.cm.viridis(np.linspace(0.2, 0.9, len(polygons)))
    
    for polygon, color in zip(polygons, colors):
        subset = summary[summary['polygon'] == polygon]
        ax.plot(subset['disruption'] * 100, 
                subset['coherence'], 
                marker='o', 
                label=polygon, 
                linewidth=2.5,
                markersize=8,
                color=color)
    
    # Golden ratio threshold
    ax.axhline(y=0.618, color='crimson', linestyle='--', 
               label='Golden Ratio Threshold (φ)', linewidth=2.5, alpha=0.8)
    
    # Styling
    ax.set_xlabel('Byzantine Failure Rate (%)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Coherence (σ)', fontsize=13, fontweight='bold')
    ax.set_title('Polygonal Scaling: Coherence Under Byzantine Failures', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.legend(loc='lower left', fontsize=11, framealpha=0.95)
    ax.grid(True, alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_xlim(5, 55)
    ax.set_ylim(0.55, 0.95)
    
    # Add improvement annotation at 50%
    pentagon_50 = summary[(summary['polygon'] == 'Pentagon') & (summary['disruption'] == 0.5)]['coherence'].values[0]
    hendecagon_50 = summary[(summary['polygon'] == 'Hendecagon') & (summary['disruption'] == 0.5)]['coherence'].values[0]
    improvement = (hendecagon_50 - pentagon_50) / pentagon_50 * 100
    
    ax.annotate(f'+{improvement:.1f}%\nimprovement', 
                xy=(50, hendecagon_50), 
                xytext=(45, 0.82),
                arrowprops=dict(arrowstyle='->', color='black', lw=1.5),
                fontsize=11,
                bbox=dict(boxstyle='round,pad=0.5', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def create_recovery_time_plot(df: pd.DataFrame, output_path: Path):
    """Generate recovery time comparison."""
    
    summary = df.groupby(['polygon', 'sides', 'disruption'])['recovery_time'].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Filter to 50% disruption
    subset = summary[summary['disruption'] == 0.5]
    
    polygons = subset['polygon'].values
    recovery_times = subset['recovery_time'].values
    
    bars = ax.bar(polygons, recovery_times, color=plt.cm.plasma(np.linspace(0.3, 0.9, len(polygons))))
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.2f}s',
                ha='center', va='bottom', fontweight='bold', fontsize=11)
    
    ax.set_ylabel('Recovery Time (seconds)', fontsize=13, fontweight='bold')
    ax.set_title('Recovery Time at 50% Byzantine Failure', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.grid(True, axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def create_heatmap(df: pd.DataFrame, output_path: Path):
    """Generate heatmap of coherence across all configurations."""
    
    summary = df.groupby(['polygon', 'disruption'])['coherence'].mean().reset_index()
    pivot = summary.pivot(index='polygon', columns='disruption', values='coherence')
    
    # Rename columns for readability
    pivot.columns = [f'{int(c*100)}%' for c in pivot.columns]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    
    sns.heatmap(pivot, annot=True, fmt='.3f', cmap='RdYlGn', 
                vmin=0.6, vmax=0.95, cbar_kws={'label': 'Coherence (σ)'},
                linewidths=0.5, ax=ax)
    
    ax.set_title('Coherence Heatmap: Polygon × Disruption', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.set_xlabel('Byzantine Failure Rate', fontsize=13, fontweight='bold')
    ax.set_ylabel('Polygon Configuration', fontsize=13, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def create_binding_energy_plot(df: pd.DataFrame, output_path: Path):
    """Generate binding energy comparison."""
    
    summary = df.groupby(['polygon', 'sides', 'disruption'])['binding_energy'].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    polygons = summary['polygon'].unique()
    colors = plt.cm.cool(np.linspace(0.2, 0.9, len(polygons)))
    
    for polygon, color in zip(polygons, colors):
        subset = summary[summary['polygon'] == polygon]
        ax.plot(subset['disruption'] * 100, 
                subset['binding_energy'], 
                marker='s', 
                label=polygon, 
                linewidth=2.5,
                markersize=8,
                color=color)
    
    ax.set_xlabel('Byzantine Failure Rate (%)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Binding Energy (Δ)', fontsize=13, fontweight='bold')
    ax.set_title('Cooper Pair Binding Energy Under Disruption', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.legend(loc='lower left', fontsize=11, framealpha=0.95)
    ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def create_phase_transition_plot(df: pd.DataFrame, output_path: Path):
    """Generate phase transition diagram around golden ratio."""
    
    summary = df.groupby(['polygon', 'sides', 'disruption'])['coherence'].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Create scatter plot sized by polygon order
    for polygon in summary['polygon'].unique():
        subset = summary[summary['polygon'] == polygon]
        sides = subset['sides'].iloc[0]
        
        # Size proportional to sides
        size = (sides / 5) ** 2 * 100
        
        ax.scatter(subset['disruption'] * 100,
                  subset['coherence'],
                  s=size,
                  alpha=0.7,
                  label=f"{polygon} ({sides})",
                  edgecolors='black',
                  linewidth=1.5)
    
    # Phase transition boundary
    ax.axhline(y=0.618, color='red', linestyle='--', linewidth=3, 
               label='Phase Transition (φ)', alpha=0.8)
    
    # Shade regions
    ax.fill_between([0, 100], 0.618, 1.0, alpha=0.1, color='green', label='Supercoherent')
    ax.fill_between([0, 100], 0, 0.618, alpha=0.1, color='red', label='Normal State')
    
    ax.set_xlabel('Byzantine Failure Rate (%)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Coherence (σ)', fontsize=13, fontweight='bold')
    ax.set_title('Phase Transition: Golden Ratio Threshold', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.legend(loc='lower left', fontsize=10, framealpha=0.95, ncol=2)
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0.55, 0.95)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


def create_improvement_chart(df: pd.DataFrame, output_path: Path):
    """Generate improvement percentage chart."""
    
    summary = df.groupby(['polygon', 'sides', 'disruption'])['coherence'].mean().reset_index()
    
    # Calculate improvement relative to pentagon
    pentagon_baseline = summary[summary['polygon'] == 'Pentagon'].set_index('disruption')['coherence']
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
    disruptions = [0.10, 0.30, 0.50]
    x = np.arange(len(disruptions))
    width = 0.2
    
    polygons = ['Heptagon', 'Decagon', 'Hendecagon']
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c']
    
    for i, (polygon, color) in enumerate(zip(polygons, colors)):
        subset = summary[summary['polygon'] == polygon].set_index('disruption')['coherence']
        improvements = [(subset[d] - pentagon_baseline[d]) / pentagon_baseline[d] * 100 
                       for d in disruptions]
        
        ax.bar(x + i*width, improvements, width, label=polygon, color=color, alpha=0.8)
    
    ax.set_ylabel('Improvement vs Pentagon (%)', fontsize=13, fontweight='bold')
    ax.set_xlabel('Byzantine Failure Rate', fontsize=13, fontweight='bold')
    ax.set_title('Coherence Improvement: Higher Polygons vs Pentagon Baseline', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks(x + width)
    ax.set_xticklabels([f'{int(d*100)}%' for d in disruptions])
    ax.legend(fontsize=11, framealpha=0.95)
    ax.grid(True, axis='y', alpha=0.3)
    ax.axhline(y=0, color='black', linestyle='-', linewidth=1)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved: {output_path}")
    plt.close()


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description='Generate polygonal validation figures')
    parser.add_argument('--input', type=str, default='../data/results_10k_trials.csv',
                       help='Input CSV file')
    parser.add_argument('--output-dir', type=str, default='../../docs/figures',
                       help='Output directory for figures')
    
    args = parser.parse_args()
    
    # Load data
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"✗ Input file not found: {input_path}")
        print(f"  Run polygon_validation.py first to generate data")
        return
    
    print(f"\n{'='*60}")
    print(f"POLYGONAL VALIDATION VISUALIZATION")
    print(f"{'='*60}\n")
    print(f"Input: {input_path}")
    
    df = pd.read_csv(input_path)
    print(f"Loaded {len(df)} data points\n")
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {output_dir}\n")
    
    # Generate all figures
    print("Generating figures...\n")
    
    create_coherence_plot(df, output_dir / 'polygonal_scaling.png')
    create_recovery_time_plot(df, output_dir / 'recovery_time_comparison.png')
    create_heatmap(df, output_dir / 'coherence_heatmap.png')
    create_binding_energy_plot(df, output_dir / 'binding_energy.png')
    create_phase_transition_plot(df, output_dir / 'phase_transition.png')
    create_improvement_chart(df, output_dir / 'improvement_chart.png')
    
    print(f"\n{'='*60}")
    print(f"✓ ALL FIGURES GENERATED")
    print(f"{'='*60}")
    print(f"\nGenerated files:")
    for file in output_dir.glob('*.png'):
        print(f"  - {file.name}")
    print(f"\nNext steps:")
    print(f"  1. Review figures in {output_dir}")
    print(f"  2. Include in paper (Step 2)")
    print(f"  3. Use for GitHub README")
    print()


if __name__ == "__main__":
    main()