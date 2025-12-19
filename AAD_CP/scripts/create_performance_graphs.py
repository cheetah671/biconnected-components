#!/usr/bin/env python3
"""Generate performance comparison graphs across all algorithms"""
import sys
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
    'p1': '#1f77b4',  # Blue
    'p2': '#ff7f0e',  # Orange
    'p3': '#9467bd',  # Purple
    'p4': '#d62728',  # Red
    'p5': '#2ca02c'   # Green
}

def load_all_results():
    """Load and combine results from all algorithms."""
    all_data = []
    
    for algo in ['p1', 'p2', 'p3', 'p4', 'p5']:
        csv_path = ROOT / 'outputs' / f'{algo}_results.csv'
        if csv_path.exists():
            df = pd.read_csv(csv_path)
            df = df[df['exitcode'] == 0].copy()  # Only successful runs
            df['algorithm'] = algo
            all_data.append(df)
            print(f"✓ Loaded {len(df)} results for {algo}")
        else:
            print(f"⚠ Warning: {csv_path} not found, skipping {algo}")
    
    if not all_data:
        print("Error: No results files found!")
        return None
    
    combined_df = pd.concat(all_data, ignore_index=True)
    print(f"\n✓ Total: {len(combined_df)} test results across {len(all_data)} algorithms")
    return combined_df

def create_category_comparison_graphs(df):
    """Create comparison graphs for each category showing all algorithms."""
    categories = sorted(df['category'].unique())
    
    print("\nGenerating comparison graphs for each category...")
    print("=" * 70)
    
    for category in categories:
        cat_df = df[df['category'] == category]
        
        # Get average time per algorithm for this category
        algo_stats = cat_df.groupby('algorithm')['time'].agg(['mean', 'std', 'count']).reset_index()
        algo_stats = algo_stats.sort_values('mean')
        
        plt.figure(figsize=(10, 6))
        
        x_pos = range(len(algo_stats))
        colors = [ALGO_COLORS.get(algo, '#808080') for algo in algo_stats['algorithm']]
        labels = [ALGO_NAMES.get(algo, algo) for algo in algo_stats['algorithm']]
        
        bars = plt.bar(x_pos, algo_stats['mean'], 
                      yerr=algo_stats['std'],
                      color=colors,
                      alpha=0.7, capsize=5, edgecolor='black', linewidth=1.5)
        
        # Add value labels on bars
        for i, (bar, mean_val) in enumerate(zip(bars, algo_stats['mean'])):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height,
                    f'{mean_val:.4f}s',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
        
        plt.xlabel('Algorithm', fontsize=12, fontweight='bold')
        plt.ylabel('Average Execution Time (seconds)', fontsize=12, fontweight='bold')
        plt.title(f'Performance Comparison: {category.upper()} Graphs', 
                 fontsize=14, fontweight='bold')
        plt.xticks(x_pos, labels, rotation=15, ha='right')
        plt.grid(True, axis='y', alpha=0.3, linestyle='--')
        plt.tight_layout()
        
        output_file = GRAPHS_DIR / f'comparison_{category}.png'
        plt.savefig(output_file, dpi=150, bbox_inches='tight')
        print(f"  ✓ {category:<20} -> {output_file.name}")
        plt.close()

def create_overall_comparison(df):
    """Create overall comparison graph across all categories."""
    plt.figure(figsize=(14, 7))
    
    categories = sorted(df['category'].unique())
    algorithms = sorted(df['algorithm'].unique())
    
    x = np.arange(len(categories))
    width = 0.8 / len(algorithms)
    
    for i, algo in enumerate(algorithms):
        algo_df = df[df['algorithm'] == algo]
        means = []
        stds = []
        
        for cat in categories:
            cat_data = algo_df[algo_df['category'] == cat]
            if len(cat_data) > 0:
                means.append(cat_data['time'].mean())
                stds.append(cat_data['time'].std())
            else:
                means.append(0)
                stds.append(0)
        
        offset = width * (i - len(algorithms)/2 + 0.5)
        plt.bar(x + offset, means, width, 
               label=ALGO_NAMES.get(algo, algo),
               color=ALGO_COLORS.get(algo, '#808080'),
               alpha=0.8, edgecolor='black', linewidth=1)
    
    plt.xlabel('Graph Category', fontsize=13, fontweight='bold')
    plt.ylabel('Average Execution Time (seconds)', fontsize=13, fontweight='bold')
    plt.title('Overall Performance Comparison: All Algorithms Across All Categories', 
             fontsize=15, fontweight='bold', pad=20)
    plt.xticks(x, [cat.replace('_', ' ').title() for cat in categories], 
              rotation=30, ha='right')
    plt.legend(loc='upper left', fontsize=11, framealpha=0.95)
    plt.grid(True, axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    output_file = GRAPHS_DIR / 'comparison_overall.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n  ✓ Overall comparison -> {output_file.name}")
    plt.close()

def create_time_vs_size_all_algos(df):
    """Create time vs size graph with all algorithms on same plot."""
    plt.figure(figsize=(12, 7))
    
    for algo in sorted(df['algorithm'].unique()):
        algo_df = df[df['algorithm'] == algo].sort_values('n')
        plt.scatter(algo_df['n'], algo_df['time'],
                   label=ALGO_NAMES.get(algo, algo),
                   color=ALGO_COLORS.get(algo, '#808080'),
                   alpha=0.6, s=50, edgecolors='black', linewidth=0.5)
    
    plt.xscale('log')
    plt.yscale('log')
    plt.xlabel('Number of Vertices (n)', fontsize=13, fontweight='bold')
    plt.ylabel('Execution Time (seconds)', fontsize=13, fontweight='bold')
    plt.title('Performance Comparison: Time vs Graph Size (All Algorithms)', 
             fontsize=15, fontweight='bold', pad=20)
    plt.legend(loc='upper left', fontsize=11, framealpha=0.95)
    plt.grid(True, alpha=0.3, linestyle='--', which='both')
    plt.tight_layout()
    
    output_file = GRAPHS_DIR / 'comparison_time_vs_size.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  ✓ Time vs Size -> {output_file.name}")
    plt.close()

def create_performance_summary_table(df):
    """Print summary statistics table."""
    print("\n" + "=" * 90)
    print("PERFORMANCE SUMMARY: AVERAGE TIME BY ALGORITHM AND CATEGORY")
    print("=" * 90)
    
    categories = sorted(df['category'].unique())
    algorithms = sorted(df['algorithm'].unique())
    
    # Header
    header = f"{'Category':<20}"
    for algo in algorithms:
        header += f"{ALGO_NAMES.get(algo, algo):<22}"
    print(header)
    print("-" * 90)
    
    # Data rows
    for cat in categories:
        row = f"{cat:<20}"
        for algo in algorithms:
            cat_algo_df = df[(df['category'] == cat) & (df['algorithm'] == algo)]
            if len(cat_algo_df) > 0:
                mean_time = cat_algo_df['time'].mean()
                row += f"{mean_time:<22.6f}"
            else:
                row += f"{'N/A':<22}"
        print(row)
    
    print("=" * 90)
    
    # Overall statistics
    print("\nOVERALL STATISTICS:")
    print("-" * 90)
    for algo in algorithms:
        algo_df = df[df['algorithm'] == algo]
        print(f"{ALGO_NAMES.get(algo, algo):<30} Mean: {algo_df['time'].mean():.6f}s  "
              f"Median: {algo_df['time'].median():.6f}s  Std: {algo_df['time'].std():.6f}s")
    print("=" * 90)

def parse_performance_metrics():
    """Parse performance_metrics.txt to extract memory usage for dense category."""
    metrics_file = ROOT / 'performance_metrics.txt'
    
    if not metrics_file.exists():
        print(f"Warning: {metrics_file} not found, skipping memory graphs")
        return None
    
    data = []
    
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
            
            # Only process dense category tests
            if not test_name.startswith('dense'):
                continue
            
            # Extract memory usage (in kbytes)
            mem_match = re.search(r'Maximum resident set size \(kbytes\): (\d+)', test_data)
            
            if mem_match:
                memory_kb = int(mem_match.group(1))
                memory_mb = memory_kb / 1024.0
                
                data.append({
                    'algorithm': algo,
                    'test': test_name,
                    'memory_mb': memory_mb
                })
    
    if not data:
        return None
    
    return pd.DataFrame(data)

def parse_cachegrind_data():
    """Parse cachegrind output files for cache metrics."""
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
    
    if not cache_data:
        return None
    
    return pd.DataFrame(cache_data)

def create_memory_graph_dense(memory_df):
    """Create memory usage graph for dense category."""
    if memory_df is None:
        return
    
    algo_stats = memory_df.groupby('algorithm')['memory_mb'].agg(['mean', 'std']).reset_index()
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
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.xlabel('Algorithm', fontsize=12, fontweight='bold')
    plt.ylabel('Memory Usage (MB)', fontsize=12, fontweight='bold')
    plt.title('Memory Usage Comparison: DENSE Graphs',
             fontsize=14, fontweight='bold')
    plt.xticks(x_pos, labels, rotation=15, ha='right')
    plt.grid(True, axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    output_file = GRAPHS_DIR / 'memory_dense.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  ✓ Memory (dense) -> {output_file.name}")
    plt.close()

def create_cache_graphs(cache_df):
    """Create cache performance graphs."""
    if cache_df is None:
        return
    
    algorithms = sorted(cache_df['algorithm'].unique())
    x_pos = range(len(algorithms))
    colors = [ALGO_COLORS.get(algo, '#808080') for algo in algorithms]
    labels = [ALGO_NAMES.get(algo, algo) for algo in algorithms]
    
    # Graph 1: L1 Cache Misses
    plt.figure(figsize=(10, 6))
    l1_misses = [cache_df[cache_df['algorithm'] == algo]['l1_total_misses'].values[0] for algo in algorithms]
    
    bars = plt.bar(x_pos, l1_misses, color=colors, alpha=0.7, 
                   edgecolor='black', linewidth=1.5)
    
    for bar, val in zip(bars, l1_misses):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{val:,}',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.xlabel('Algorithm', fontsize=12, fontweight='bold')
    plt.ylabel('L1 Cache Misses', fontsize=12, fontweight='bold')
    plt.title('L1 Cache Miss Comparison (dense_08.txt)',
             fontsize=14, fontweight='bold')
    plt.xticks(x_pos, labels, rotation=15, ha='right')
    plt.grid(True, axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    output_file = GRAPHS_DIR / 'cache_l1_misses_dense.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  ✓ L1 cache misses -> {output_file.name}")
    plt.close()
    
    # Graph 2: Instructions Executed
    plt.figure(figsize=(10, 6))
    instructions = [cache_df[cache_df['algorithm'] == algo]['instructions'].values[0] for algo in algorithms]
    
    bars = plt.bar(x_pos, instructions, color=colors, alpha=0.7,
                   edgecolor='black', linewidth=1.5)
    
    for bar, val in zip(bars, instructions):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{val/1e6:.1f}M',
                ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    plt.xlabel('Algorithm', fontsize=12, fontweight='bold')
    plt.ylabel('Instructions Executed', fontsize=12, fontweight='bold')
    plt.title('Instruction Count Comparison (dense_08.txt)',
             fontsize=14, fontweight='bold')
    plt.xticks(x_pos, labels, rotation=15, ha='right')
    plt.grid(True, axis='y', alpha=0.3, linestyle='--')
    plt.tight_layout()
    
    output_file = GRAPHS_DIR / 'cache_instructions_dense.png'
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"  ✓ Instructions -> {output_file.name}")
    plt.close()

def create_performance_graphs():
    """Main function to create all performance comparison graphs."""
    
    print("Performance Comparison Graph Generator")
    print("=" * 70)
    print("Loading results from all algorithms...")
    
    df = load_all_results()
    if df is None:
        return False
    
    GRAPHS_DIR.mkdir(exist_ok=True)
    
    print("\nCategories found:", sorted(df['category'].unique()))
    print("Algorithms found:", sorted(df['algorithm'].unique()))
    
    # Generate time-based graphs
    print("\n[TIME PERFORMANCE GRAPHS]")
    create_category_comparison_graphs(df)
    create_overall_comparison(df)
    create_time_vs_size_all_algos(df)
    create_performance_summary_table(df)
    
    # Generate memory graphs for dense category
    print("\n[MEMORY PERFORMANCE GRAPHS]")
    memory_df = parse_performance_metrics()
    if memory_df is not None:
        create_memory_graph_dense(memory_df)
    
    # Generate cache performance graphs
    print("\n[CACHE PERFORMANCE GRAPHS]")
    cache_df = parse_cachegrind_data()
    if cache_df is not None:
        create_cache_graphs(cache_df)
    
    print(f"\n✓ All graphs saved to: {GRAPHS_DIR}")
    print("\nGenerated files:")
    print("  Time performance:")
    print("    • comparison_<category>.png - Per-category algorithm comparison")
    print("    • comparison_overall.png - All algorithms across all categories")
    print("    • comparison_time_vs_size.png - Time vs graph size")
    print("  Memory performance:")
    print("    • memory_dense.png - Memory usage for dense graphs")
    print("  Cache performance:")
    print("    • cache_l1_misses_dense.png - L1 cache misses")
    print("    • cache_instructions_dense.png - Instructions executed")
    
    # Generate speedup vs threads graph for p3 (Slota-Madduri)
    create_p3_speedup_graph()
    
    return True

def create_p3_speedup_graph():
    """Generate speedup vs number of threads graph for p3 (Slota-Madduri)."""
    print("\n[P3 PARALLEL SPEEDUP ANALYSIS]")
    print("=" * 70)
    
    # Run p3 with different thread counts on a representative dataset
    import subprocess
    import time
    
    exe_path = ROOT / 'codes' / 'p3'
    test_file = ROOT / 'dataset' / 'real_world' / 'facebook.txt'
    
    if not exe_path.exists():
        print(f"⚠ p3 executable not found at {exe_path}, skipping speedup graph")
        return
    
    if not test_file.exists():
        print(f"⚠ Test file not found at {test_file}, skipping speedup graph")
        return
    
    thread_counts = [1, 2, 4, 8, 16]
    times = []
    
    print(f"Running p3 on {test_file.name} with different thread counts...")
    
    for threads in thread_counts:
        # Run 3 times and take average
        run_times = []
        for _ in range(3):
            env = {'OMP_NUM_THREADS': str(threads)}
            start = time.perf_counter()
            try:
                subprocess.run([str(exe_path)], 
                             stdin=open(test_file, 'r'),
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL,
                             env={**subprocess.os.environ, **env},
                             timeout=60)
                end = time.perf_counter()
                run_times.append(end - start)
            except:
                run_times.append(None)
        
        avg_time = sum(t for t in run_times if t) / len([t for t in run_times if t]) if any(run_times) else None
        times.append(avg_time)
        if avg_time:
            print(f"  {threads} threads: {avg_time:.6f}s")
    
    # Calculate speedup
    if times[0] and all(times):
        speedups = [times[0] / t for t in times]
        ideal_speedup = thread_counts
        
        # Create speedup graph
        plt.figure(figsize=(10, 6))
        plt.plot(thread_counts, speedups, 'o-', linewidth=2, markersize=8, 
                color='#9467bd', label='Actual Speedup')
        plt.plot(thread_counts, ideal_speedup, '--', linewidth=2, 
                color='#666666', label='Ideal Speedup')
        
        plt.xlabel('Number of Threads', fontsize=12, fontweight='bold')
        plt.ylabel('Speedup', fontsize=12, fontweight='bold')
        plt.title('Slota-Madduri Parallel Algorithm\nSpeedup vs Number of Threads', 
                 fontsize=14, fontweight='bold')
        plt.grid(True, alpha=0.3)
        plt.legend(fontsize=10)
        
        # Add efficiency annotation
        efficiency = (speedups[-1] / thread_counts[-1]) * 100
        plt.text(0.98, 0.02, f'Parallel Efficiency ({thread_counts[-1]} threads): {efficiency:.1f}%',
                transform=plt.gca().transAxes, ha='right', va='bottom',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
        
        plt.tight_layout()
        output_file = GRAPHS_DIR / 'p3_speedup_vs_threads.png'
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"  ✓ p3_speedup_vs_threads.png")
        print(f"  Speedup at {thread_counts[-1]} threads: {speedups[-1]:.2f}x")
        print(f"  Parallel efficiency: {efficiency:.1f}%")
    else:
        print("  ✗ Failed to collect timing data for speedup graph")


if __name__ == '__main__':
    success = create_performance_graphs()
    sys.exit(0 if success else 1)
