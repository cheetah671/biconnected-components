#!/usr/bin/env python3
"""
Parse cachegrind output files and generate comprehensive hardware performance report
"""

import re
import subprocess
from datetime import datetime
from pathlib import Path

def parse_cachegrind_output(filename):
    """Extract metrics from cachegrind output file"""
    try:
        # Resolve path relative to script location
        script_dir = Path(__file__).resolve().parent
        root_dir = script_dir.parent
        cachegrind_file = root_dir / filename
        
        # Run cg_annotate and get output
        result = subprocess.run(
            ['cg_annotate', str(cachegrind_file)],
            capture_output=True,
            text=True,
            check=True
        )
        
        output = result.stdout + result.stderr
        
        # Find the PROGRAM TOTALS line
        for line in output.split('\n'):
            if 'PROGRAM TOTALS' in line:
                # Remove commas and extract all numbers (ignoring percentages)
                # Format: number (percentage%) number (percentage%) ... PROGRAM TOTALS
                numbers = []
                tokens = line.split()
                for i, token in enumerate(tokens):
                    # Remove commas
                    token = token.replace(',', '')
                    # Check if it's a pure number (not a percentage)
                    if token.isdigit():
                        # Make sure next token is a percentage (validation)
                        if i + 1 < len(tokens) and tokens[i + 1].startswith('(') and tokens[i + 1].endswith('%)'):
                            numbers.append(int(token))
                
                if len(numbers) >= 11:
                    return {
                        'Ir': numbers[0],    # Instructions
                        'I1mr': numbers[1],  # L1 I-cache misses
                        'ILmr': numbers[2],  # LL I-cache misses
                        'Dr': numbers[3],    # Data reads
                        'D1mr': numbers[4],  # L1 D-cache read misses
                        'DLmr': numbers[5],  # LL D-cache read misses
                        'Dw': numbers[6],    # Data writes
                        'D1mw': numbers[7],  # L1 D-cache write misses
                        'DLmw': numbers[8],  # LL D-cache write misses
                        'Bc': numbers[9],    # Branches
                        'Bcm': numbers[10],  # Branch mispredicts
                    }
                    
    except Exception as e:
        print(f"Error parsing {filename}: {e}")
    
    return None

def format_number(num):
    """Format number with thousands separator"""
    return f"{num:,}"

def calculate_miss_rate(misses, total):
    """Calculate miss rate as percentage"""
    if total == 0:
        return 0.0
    return (misses / total) * 100

def generate_report():
    """Generate comprehensive hardware performance report"""
    
    algorithms = [
        ('cachegrind_p1.out', 'p1 (Tarjan\'s Algorithm)'),
        ('cachegrind_p2.out', 'p2 (Tarjan-Vishkin)'),
        ('cachegrind_p3.out', 'p3 (Slota-Madduri Parallel)'),
        ('cachegrind_p4.out', 'p4 (Naive Algorithm)'),
        ('cachegrind_p5.out', 'p5 (Chain Decomposition)'),
    ]
    
    output = []
    output.append("=" * 70)
    output.append("Hardware Performance Analysis Report")
    output.append("=" * 70)
    output.append(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    output.append("")
    output.append("Test Graph: graphs/dense/dense_08.txt (16 vertices, 81 edges)")
    output.append("")
    output.append("Metrics Collected:")
    output.append("  Ir:   Instructions executed")
    output.append("  I1mr: L1 Instruction cache misses")
    output.append("  ILmr: Last Level Instruction cache misses")
    output.append("  Dr:   Data reads")
    output.append("  D1mr: L1 Data cache read misses")
    output.append("  DLmr: Last Level Data cache read misses")
    output.append("  Dw:   Data writes")
    output.append("  D1mw: L1 Data cache write misses")
    output.append("  DLmw: Last Level Data cache write misses")
    output.append("  Bc:   Conditional branches executed")
    output.append("  Bcm:  Conditional branch mispredictions")
    output.append("")
    
    # Parse all algorithms
    results = {}
    for filename, name in algorithms:
        metrics = parse_cachegrind_output(filename)
        if metrics:
            results[name] = metrics

    # If no cachegrind results were parsed, write a short report and exit gracefully
    if not results:
        script_dir = Path(__file__).resolve().parent
        root_dir = script_dir.parent
        report_file = root_dir / 'cache_analysis_report.txt'
        
        msg = ["No cachegrind results were found or all parse attempts failed.",
               "Please ensure the files 'cachegrind_p1.out', 'cachegrind_p2.out', 'cachegrind_p3.out',",
               "'cachegrind_p4.out', 'cachegrind_p5.out' exist and are readable by cg_annotate.",
               "You can (re)generate them using the run_cachegrind_analysis.sh script."]
        report = "\n".join(msg)
        with open(report_file, 'w') as f:
            f.write(report + "\n")
        print(report)
        print(f"Written minimal report to {report_file}")
        return
    
    # Display detailed metrics for each algorithm
    for name in [algo[1] for algo in algorithms]:
        if name not in results:
            continue
            
        m = results[name]
        output.append("=" * 70)
        output.append(f"Algorithm: {name}")
        output.append("=" * 70)
        output.append(f"{'Instructions (Ir):':<45} {format_number(m['Ir']):>20}")
        output.append(f"{'L1 I-Cache Misses (I1mr):':<45} {format_number(m['I1mr']):>20}")
        output.append(f"{'LL I-Cache Misses (ILmr):':<45} {format_number(m['ILmr']):>20}")
        output.append(f"{'Data Reads (Dr):':<45} {format_number(m['Dr']):>20}")
        output.append(f"{'L1 D-Cache Read Misses (D1mr):':<45} {format_number(m['D1mr']):>20}")
        output.append(f"{'LL D-Cache Read Misses (DLmr):':<45} {format_number(m['DLmr']):>20}")
        output.append(f"{'Data Writes (Dw):':<45} {format_number(m['Dw']):>20}")
        output.append(f"{'L1 D-Cache Write Misses (D1mw):':<45} {format_number(m['D1mw']):>20}")
        output.append(f"{'LL D-Cache Write Misses (DLmw):':<45} {format_number(m['DLmw']):>20}")
        output.append(f"{'Conditional Branches (Bc):':<45} {format_number(m['Bc']):>20}")
        output.append(f"{'Branch Mispredicts (Bcm):':<45} {format_number(m['Bcm']):>20}")
        output.append("")
        
        # Calculate and display miss rates
        i1_rate = calculate_miss_rate(m['I1mr'], m['Ir'])
        d1r_rate = calculate_miss_rate(m['D1mr'], m['Dr'])
        d1w_rate = calculate_miss_rate(m['D1mw'], m['Dw'])
        branch_rate = calculate_miss_rate(m['Bcm'], m['Bc'])
        
        output.append(f"{'L1 I-Cache Miss Rate:':<45} {i1_rate:>19.4f}%")
        output.append(f"{'L1 D-Cache Read Miss Rate:':<45} {d1r_rate:>19.4f}%")
        output.append(f"{'L1 D-Cache Write Miss Rate:':<45} {d1w_rate:>19.4f}%")
        output.append(f"{'Branch Mispredict Rate:':<45} {branch_rate:>19.4f}%")
        output.append("")
    
    # Comparative summary
    output.append("=" * 70)
    output.append("Comparative Summary")
    output.append("=" * 70)
    output.append("")
    
    # Sort by instruction count (only if we have parsed entries)
    sorted_algos = sorted(results.items(), key=lambda x: x[1]['Ir']) if results else []
    output.append("Instruction Count Ranking (Lower is Better):")
    if sorted_algos:
        baseline = sorted_algos[0][1]['Ir']
        for i, (name, metrics) in enumerate(sorted_algos, 1):
            slowdown = metrics['Ir'] / baseline if baseline != 0 else 0
            if i == 1:
                output.append(f"{i}. {name:<35} {format_number(metrics['Ir']):>15} instructions")
            else:
                output.append(f"{i}. {name:<35} {format_number(metrics['Ir']):>15} instructions ({slowdown:.2f}x)")
    else:
        output.append("  No instruction data available to rank algorithms.")
    output.append("")
    
    output.append("Branch Misprediction Count:")
    for name, metrics in sorted(results.items(), key=lambda x: x[1]['Bcm']):
        rate = calculate_miss_rate(metrics['Bcm'], metrics['Bc'])
        output.append(f"  {name:<35} {format_number(metrics['Bcm']):>12} ({rate:.2f}%)")
    output.append("")
    
    output.append("Cache Performance Summary:")
    for name, metrics in sorted(results.items(), key=lambda x: x[1]['D1mr'] + x[1]['I1mr']):
        total_l1_misses = metrics['D1mr'] + metrics['I1mr'] + metrics['D1mw']
        output.append(f"  {name:<35} {format_number(total_l1_misses):>12} total L1 misses")
    output.append("")
    
    output.append("Key Insights:")
    if sorted_algos:
        fastest = sorted_algos[0][0]
        slowest = sorted_algos[-1][0]
        slowdown = sorted_algos[-1][1]['Ir'] / sorted_algos[0][1]['Ir'] if sorted_algos[0][1]['Ir'] != 0 else 0
        output.append(f"  • {fastest} is the most efficient (lowest instruction count)")
        output.append(f"  • {slowest} executes {slowdown:.1f}x more instructions")
    else:
        output.append("  No instruction-based insights available.")

    output.append(f"  • Cache locality and branch prediction insights shown when data available.")

    # Find best/worst branch predictor if branch data exists
    try:
        branch_candidates = {k: v for k, v in results.items() if v.get('Bc', 0) > 0}
        if branch_candidates:
            best_branch = min(branch_candidates.items(), key=lambda x: calculate_miss_rate(x[1]['Bcm'], x[1]['Bc']))
            worst_branch = max(branch_candidates.items(), key=lambda x: calculate_miss_rate(x[1]['Bcm'], x[1]['Bc']))
            output.append(f"  • {best_branch[0]} has best branch prediction ({calculate_miss_rate(best_branch[1]['Bcm'], best_branch[1]['Bc']):.2f}% mispredict)")
            output.append(f"  • {worst_branch[0]} has most branch mispredicts ({calculate_miss_rate(worst_branch[1]['Bcm'], worst_branch[1]['Bc']):.2f}%)")
    except Exception:
        # If anything goes wrong, skip branch insights
        pass
    output.append("")
    
    # Save to file
    report_text = '\n'.join(output)
    script_dir = Path(__file__).resolve().parent
    root_dir = script_dir.parent
    report_file = root_dir / 'cache_analysis_report.txt'
    
    with open(report_file, 'w') as f:
        f.write(report_text)
    
    print(report_text)
    print(f"\nReport saved to: {report_file}")

if __name__ == '__main__':
    generate_report()
