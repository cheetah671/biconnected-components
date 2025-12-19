#!/usr/bin/env python3
"""Generate memory usage and cache performance comparison graphs"""
import re
import subprocess
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GRAPHS_DIR = ROOT / 'graphs'

# Algorithm metadata
ALGO_NAMES = {
    'p1': "Tarjan's Algorithm",
    'p2': 'Tarjan-Vishkin',
    'p3': 'Slota-Madduri Parallel',
    'p4': 'Naive Algorithm',
    'p5': 'Chain Decomposition'
}

ALGO_COLORS = {
    'p1': '#1f77b4',
    'p2': '#ff7f0e',
    'p3': '#9467bd',
    'p4': '#d62728',
    'p5': '#2ca02c'
}

def parse_performance_metrics():
    """Parse performance_metrics.txt to extract memory usage data."""
    metrics_file = ROOT / 'performance_metrics.txt'
    
    if not metrics_file.exists():
        print(f"Error: {metrics_file} not found!")
        return None
    
    data = []
    current_algo = None
    current_test = None
    
    with open(metrics_file, 'r') as f:
        content = f.read()
    
    # Split by algorithm sections
    algo_sections = re.split(r'Algorithm: (p\d)', content)
    
    for i in range(1, len(algo_sections), 2):
        algo = algo_sections[i]
        section = algo_sections[i + 1]
        
        # Find all test entries in this section
        test_blocks = re.split(r'Test: (\w+)', section)
        
        for j in range(1, len(test_blocks), 2):
            test_name = test_blocks[j]
            test_data = test_blocks[j + 1]
            
            # Extract memory usage (in kbytes)
            mem_match = re.search(r'Maximum resident set size \(kbytes\): (\d+)', test_data)
            
            if mem_match:
                memory_kb = int(mem_match.group(1))
                memory_mb = memory_kb / 1024.0
                
                # Determine category from test name
                category = None
                if test_name.startswith('dense'):
                    category = 'dense'
                elif test_name.startswith('sparse'):
                    category = 'sparse'
                elif test_name.startswith('small'):
                    category = 'small'
                elif test_name.startswith('large'):
                    category = 'large'
                elif test_name.startswith('tree'):
                    category = 'tree_like'
                elif test_name.startswith('highly'):
                    category = 'highly_connected'
                elif 'road' in test_name or 'com' in test_name or 'wiki' in test_name or 'soc' in test_name or 'web' in test_name:
                    category = 'real_world'
                
                if category:
                    data.append({
                        'algorithm': algo,
                        'test': test_name,
                        'category': category,
                        'memory_kb': memory_kb,
                        'memory_mb': memory_mb
                    })
    
    if not data:
        print("No memory data found!")
        return None
    
    df = pd.DataFrame(data)
    print(f"✓ Parsed memory data: {len(df)} entries across {len(df['algorithm'].unique())} algorithms")
    return df

def parse_cachegrind_for_test(test_path):
    """Parse cachegrind output for a specific test file by running cachegrind on it."""
    cache_data = []
    
    # Run cachegrind for each algorithm on this test
    for algo in ['p1', 'p2', 'p3', 'p4', 'p5']:
        exe = ROOT / 'codes' / algo
        if not exe.exists():
            continue
            
        temp_out = ROOT / f'temp_cachegrind_{algo}.out'
        
        try:
            # Run cachegrind
            subprocess.run(
                ['valgrind', '--tool=cachegrind', '--branch-sim=yes', '--cache-sim=yes',
                 f'--cachegrind-out-file={temp_out}', str(exe)],
                stdin=open(test_path, 'r'),
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=60
            )
            
            # Parse the output
            result = subprocess.run(
                ['cg_annotate', str(temp_out)],
                capture_output=True,
                text=True,
                check=True
            )
            
            output = result.stdout + result.stderr
            
            # Find PROGRAM TOTALS line
            for line in output.split('\n'):
                if 'PROGRAM TOTALS' in line:
                    numbers = []
                    tokens = line.split()
                    for i, token in enumerate(tokens):
                        token = token.replace(',', '')
                        if token.isdigit():
                            if i + 1 < len(tokens) and tokens[i + 1].startswith('(') and tokens[i + 1].endswith('%)'):
                                numbers.append(int(token))
                    
                    if len(numbers) >= 11:
                        cache_data.append({
                            'algorithm': algo,
                            'instructions': numbers[0],
                            'l1_i_misses': numbers[1],
                            'l1_d_misses': numbers[4],
                            'l1_total_misses': numbers[1] + numbers[4],
                            'branches': numbers[9],
                            'branch_mispredicts': numbers[10]
                        })
                    break
            
            # Clean up temp file
            if temp_out.exists():
                temp_out.unlink()
                
        except Exception as e:
            print(f"    Warning: Could not analyze {algo}: {e}")
            if temp_out.exists():
                temp_out.unlink()
    
    return cache_data

def parse_cachegrind_for_category(category_file):
    """Parse cachegrind output for a specific test file."""
    cachegrind_files = list(ROOT.glob('cachegrind_*.out'))
    
    cache_data = []
    
    for cg_file in cachegrind_files:
        algo = cg_file.stem.replace('cachegrind_', '')
        
        try:
            result = subprocess.run(
                ['cg_annotate', str(cg_file)],
                capture_output=True,
                text=True,
                check=True
            )
            
            output = result.stdout + result.stderr
            
            # Find PROGRAM TOTALS line
            for line in output.split('\n'):
                if 'PROGRAM TOTALS' in line:
                    # Remove commas and extract numbers
                    numbers = []
                    tokens = line.split()
                    for i, token in enumerate(tokens):
                        token = token.replace(',', '')
                        if token.isdigit():
                            if i + 1 < len(tokens) and tokens[i + 1].startswith('(') and tokens[i + 1].endswith('%)'):
                                numbers.append(int(token))
                    
                    if len(numbers) >= 11:
                        cache_data.append({
                            'algorithm': algo,
                            'instructions': numbers[0],
                            'l1_i_misses': numbers[1],
                            'l1_d_misses': numbers[4],
                            'l1_total_misses': numbers[1] + numbers[4],
                            'branches': numbers[9],
                            'branch_mispredicts': numbers[10]
                        })
                    break
        except Exception as e:
            print(f"Warning: Could not parse {cg_file}: {e}")
    
    return cache_data

def create_memory_comparison_graphs(df):
    """Create memory usage comparison graphs for each category."""
    categories = sorted(df['category'].unique())
    
    print("\nGenerating memory comparison graphs...")
    print("=" * 70)
    
    for category in categories:
        cat_df = df[df['category'] == category]
        
        # Average memory per algorithm
        algo_stats = cat_df.groupby('algorithm')['memory_mb'].agg(['mean', 'std', 'count']).reset_index()
        algo_stats = algo_stats.sort_values('mean')
        
        plt.figure(figsize=(10, 6))
        
        x_pos = range(len(algo_stats))
        colors = [ALGO_COLORS.get(algo, '#808080') for algo in algo_stats['algorithm']]
        labels = [ALGO_NAMES.get(algo, algo) for algo in algo_stats['algorithm']]
        
        bars = plt.bar(x_pos, algo_stats['mean'],
                      yerr=algo_stats['std'],
                      color=colors,
                      alpha=0.7, capsize=5, edgecolor='black', linewidth=1.5)
        
        # Add value labels
        for bar, mean_val in zip(bars, algo_stats['mean']):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{mean_val:.2f} MB',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        plt.xlabel('Algorithm', fontsize=12, fontweight='bold')
        plt.ylabel('Memory Usage (MB)', fontsize=12, fontweight='bold')
        plt.title(f'Memory Usage Comparison: {category.upper()} Graphs',
                 fontsize=14, fontweight='bold')
        plt.xticks(x_pos, labels, rotation=15, ha='right')
        plt.grid(True, axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        output_file = GRAPHS_DIR / f'memory_{category}.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"  ✓ {category:<20} -> {output_file.name}")
        plt.close()

def create_overall_memory_comparison(df):
    """Create overall memory comparison across all categories."""
    plt.figure(figsize=(14, 7))
    
    categories = sorted(df['category'].unique())
    algorithms = sorted(df['algorithm'].unique())
    
    x = np.arange(len(categories))
    width = 0.8 / len(algorithms)
    
    for i, algo in enumerate(algorithms):
        algo_df = df[df['algorithm'] == algo]
        means = []
        
        for cat in categories:
            cat_data = algo_df[algo_df['category'] == cat]
            if len(cat_data) > 0:
                means.append(cat_data['memory_mb'].mean())
            else:
                means.append(0)
        
        offset = width * (i - len(algorithms)/2 + 0.5)
        plt.bar(x + offset, means, width,
               label=ALGO_NAMES.get(algo, algo),
               color=ALGO_COLORS.get(algo, '#808080'),
               alpha=0.8, edgecolor='black', linewidth=1)
    
    plt.xlabel('Graph Category', fontsize=13, fontweight='bold')
    plt.ylabel('Average Memory Usage (MB)', fontsize=13, fontweight='bold')
    plt.title('Memory Usage Comparison: All Algorithms Across All Categories',
             fontsize=15, fontweight='bold', pad=20)
    plt.xticks(x, [cat.replace('_', ' ').title() for cat in categories],
              rotation=30, ha='right')
    plt.legend(loc='upper left', fontsize=11, framealpha=0.95)
    plt.grid(True, axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    output_file = GRAPHS_DIR / 'memory_overall.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n  ✓ Overall memory comparison -> {output_file.name}")
    plt.close()

def create_cache_comparison_graphs():
    """Create cache performance comparison graphs."""
    cache_data = parse_cachegrind_for_category(None)
    
    if not cache_data:
        print("No cache data available")
        return
    
    df = pd.DataFrame(cache_data)
    
    print("\nGenerating cache comparison graphs...")
    print("=" * 70)
    
    # Graph 1: L1 Cache Misses
    plt.figure(figsize=(10, 6))
    algorithms = sorted(df['algorithm'].unique())
    x_pos = range(len(algorithms))
    
    l1_misses = [df[df['algorithm'] == algo]['l1_total_misses'].values[0] for algo in algorithms]
    colors = [ALGO_COLORS.get(algo, '#808080') for algo in algorithms]
    labels = [ALGO_NAMES.get(algo, algo) for algo in algorithms]
    
    bars = plt.bar(x_pos, l1_misses, color=colors, alpha=0.7, 
                   edgecolor='black', linewidth=1.5)
    
    for bar, val in zip(bars, l1_misses):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:,}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.xlabel('Algorithm', fontsize=12, fontweight='bold')
    plt.ylabel('L1 Cache Misses', fontsize=12, fontweight='bold')
    plt.title('L1 Cache Miss Comparison (dense_08.txt test)',
             fontsize=14, fontweight='bold')
    plt.xticks(x_pos, labels, rotation=15, ha='right')
    plt.grid(True, axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    output_file = GRAPHS_DIR / 'cache_l1_misses.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  ✓ L1 cache misses -> {output_file.name}")
    plt.close()
    
    # Graph 2: Branch Mispredictions
    plt.figure(figsize=(10, 6))
    
    branch_misses = [df[df['algorithm'] == algo]['branch_mispredicts'].values[0] for algo in algorithms]
    
    bars = plt.bar(x_pos, branch_misses, color=colors, alpha=0.7,
                   edgecolor='black', linewidth=1.5)
    
    for bar, val in zip(bars, branch_misses):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:,}',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.xlabel('Algorithm', fontsize=12, fontweight='bold')
    plt.ylabel('Branch Mispredictions', fontsize=12, fontweight='bold')
    plt.title('Branch Misprediction Comparison (dense_08.txt test)',
             fontsize=14, fontweight='bold')
    plt.xticks(x_pos, labels, rotation=15, ha='right')
    plt.grid(True, axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    output_file = GRAPHS_DIR / 'cache_branch_mispredicts.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  ✓ Branch mispredicts -> {output_file.name}")
    plt.close()
    
    # Graph 3: Instructions Executed
    plt.figure(figsize=(10, 6))
    
    instructions = [df[df['algorithm'] == algo]['instructions'].values[0] for algo in algorithms]
    
    bars = plt.bar(x_pos, instructions, color=colors, alpha=0.7,
                   edgecolor='black', linewidth=1.5)
    
    for bar, val in zip(bars, instructions):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{val/1e6:.1f}M',
                ha='center', va='bottom', fontsize=9, fontweight='bold')
    
    plt.xlabel('Algorithm', fontsize=12, fontweight='bold')
    plt.ylabel('Instructions Executed', fontsize=12, fontweight='bold')
    plt.title('Instruction Count Comparison (dense_08.txt test)',
             fontsize=14, fontweight='bold')
    plt.xticks(x_pos, labels, rotation=15, ha='right')
    plt.grid(True, axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    output_file = GRAPHS_DIR / 'cache_instructions.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  ✓ Instructions executed -> {output_file.name}")
    plt.close()
    
    # Graph 4: Combined cache metrics (normalized)
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Normalize all metrics to 0-100 scale for comparison
    max_l1 = max(l1_misses)
    max_branch = max(branch_misses)
    max_instr = max(instructions)
    
    norm_l1 = [(m / max_l1) * 100 for m in l1_misses]
    norm_branch = [(m / max_branch) * 100 for m in branch_misses]
    norm_instr = [(m / max_instr) * 100 for m in instructions]
    
    x = np.arange(len(algorithms))
    width = 0.25
    
    ax.bar(x - width, norm_l1, width, label='L1 Cache Misses',
           color='#3498db', alpha=0.8, edgecolor='black')
    ax.bar(x, norm_branch, width, label='Branch Mispredicts',
           color='#e74c3c', alpha=0.8, edgecolor='black')
    ax.bar(x + width, norm_instr, width, label='Instructions',
           color='#2ecc71', alpha=0.8, edgecolor='black')
    
    ax.set_xlabel('Algorithm', fontsize=13, fontweight='bold')
    ax.set_ylabel('Normalized Performance (% of maximum)', fontsize=13, fontweight='bold')
    ax.set_title('Combined Cache Performance Metrics (Normalized)',
                 fontsize=15, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15, ha='right')
    ax.legend(fontsize=11, framealpha=0.95)
    ax.grid(True, axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    output_file = GRAPHS_DIR / 'cache_combined_normalized.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  ✓ Combined cache metrics -> {output_file.name}")
    plt.close()

def create_category_cache_graphs():
    """Create cache performance graphs for each category."""
    dataset_dir = ROOT / 'dataset'
    categories = {
        'dense': 'dense_08.txt',
        'sparse': 'sparse_08.txt',
        'small': 'small_08.txt',
        'large': 'large_01.txt',
        'tree_like': 'tree_like_08.txt',
        'highly_connected': 'highly_connected_08.txt'
    }
    
    print("\nGenerating per-category cache graphs...")
    print("=" * 70)
    
    for category, test_file in categories.items():
        test_path = dataset_dir / category / test_file
        if not test_path.exists():
            print(f"  ⚠ Skipping {category}: test file not found")
            continue
        
        print(f"  Analyzing {category}/{test_file}...")
        cache_data = parse_cachegrind_for_test(test_path)
        
        if not cache_data:
            print(f"    ✗ No data for {category}")
            continue
        
        df = pd.DataFrame(cache_data)
        algorithms = sorted(df['algorithm'].unique())
        
        # Branch Mispredictions graph for this category
        plt.figure(figsize=(10, 6))
        x_pos = range(len(algorithms))
        
        branch_misses = [df[df['algorithm'] == algo]['branch_mispredicts'].values[0] for algo in algorithms]
        colors = [ALGO_COLORS.get(algo, '#808080') for algo in algorithms]
        labels = [ALGO_NAMES.get(algo, algo) for algo in algorithms]
        
        bars = plt.bar(x_pos, branch_misses, color=colors, alpha=0.7,
                       edgecolor='black', linewidth=1.5)
        
        for bar, val in zip(bars, branch_misses):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{val:,}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        plt.xlabel('Algorithm', fontsize=12, fontweight='bold')
        plt.ylabel('Branch Mispredictions', fontsize=12, fontweight='bold')
        plt.title(f'Branch Misprediction Comparison: {category.upper()}',
                 fontsize=14, fontweight='bold')
        plt.xticks(x_pos, labels, rotation=15, ha='right')
        plt.grid(True, axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        output_file = GRAPHS_DIR / f'cache_branch_mispredicts_{category}.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"    ✓ {output_file.name}")
        plt.close()

def print_summary_tables(memory_df):
    """Print summary statistics."""
    print("\n" + "=" * 90)
    print("MEMORY USAGE SUMMARY (MB)")
    print("=" * 90)
    
    categories = sorted(memory_df['category'].unique())
    algorithms = sorted(memory_df['algorithm'].unique())
    
    header = f"{'Category':<20}"
    for algo in algorithms:
        header += f"{ALGO_NAMES.get(algo, algo):<22}"
    print(header)
    print("-" * 90)
    
    for cat in categories:
        row = f"{cat:<20}"
        for algo in algorithms:
            cat_algo_df = memory_df[(memory_df['category'] == cat) & (memory_df['algorithm'] == algo)]
            if len(cat_algo_df) > 0:
                mean_mem = cat_algo_df['memory_mb'].mean()
                row += f"{mean_mem:<22.2f}"
            else:
                row += f"{'N/A':<22}"
        print(row)
    
    print("=" * 90)

def main():
    """Main function."""
    print("Memory Usage and Cache Performance Graph Generator")
    print("=" * 70)
    
    GRAPHS_DIR.mkdir(exist_ok=True)
    
    # Parse and visualize memory data
    memory_df = parse_performance_metrics()
    if memory_df is not None:
        create_memory_comparison_graphs(memory_df)
        create_overall_memory_comparison(memory_df)
        print_summary_tables(memory_df)
    
    # Create cache performance graphs
    create_cache_comparison_graphs()
    
    # Create per-category cache graphs
    create_category_cache_graphs()
    
    print(f"\n✓ All graphs saved to: {GRAPHS_DIR}")
    print("\nGenerated files:")
    print("  Memory graphs:")
    print("    • memory_<category>.png - Per-category memory comparison")
    print("    • memory_overall.png - Overall memory comparison")
    print("  Cache graphs:")
    print("    • cache_l1_misses.png - L1 cache miss comparison")
    print("    • cache_branch_mispredicts.png - Branch misprediction comparison")
    print("    • cache_branch_mispredicts_<category>.png - Per-category branch mispredictions")
    print("    • cache_instructions.png - Instruction count comparison")
    print("    • cache_combined_normalized.png - Combined normalized metrics")

if __name__ == '__main__':
    main()
