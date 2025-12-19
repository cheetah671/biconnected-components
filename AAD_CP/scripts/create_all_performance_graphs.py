#!/usr/bin/env python3
"""Generate performance graphs for all algorithms (p1, p2, p4, p5)"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent))

from create_performance_graphs import create_performance_graphs

def main():
    algorithms = ['p1', 'p2', 'p4', 'p5']
    
    print("="*70)
    print("GENERATING PERFORMANCE GRAPHS FOR ALL ALGORITHMS")
    print("="*70)
    
    success_count = 0
    failed = []
    
    for algo in algorithms:
        print(f"\n{'='*70}")
        print(f"Processing {algo.upper()}...")
        print(f"{'='*70}")
        
        if create_performance_graphs(algo):
            success_count += 1
        else:
            failed.append(algo)
    
    print(f"\n{'='*70}")
    print("FINAL SUMMARY")
    print(f"{'='*70}")
    print(f"✓ Successfully generated graphs for: {success_count}/{len(algorithms)} algorithms")
    if failed:
        print(f"✗ Failed for: {', '.join(failed)}")
        print(f"   (Run the corresponding run_<algo>_only.py script first)")
    print(f"{'='*70}\n")

if __name__ == '__main__':
    main()
