#!/usr/bin/env python3
"""Generate visualizations for all dataset files."""
import sys
import os
from pathlib import Path

# Import the visualization function
sys.path.insert(0, str(Path(__file__).parent))
from visualize_graph import visualize_graph

ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / 'dataset'
GRAPHS_DIR = ROOT / 'graphs'

def main():
    GRAPHS_DIR.mkdir(exist_ok=True)
    
    files = []
    for category in sorted(DATASET_DIR.iterdir()):
        if not category.is_dir():
            continue
        for f in sorted(category.glob('*.txt')):
            files.append((category.name, f))
    
    print(f"Found {len(files)} graph files to visualize\n")
    
    success = 0
    failed = 0
    
    for category, fpath in files:
        try:
            print(f"[{category}] {fpath.name}...")
            out_dir = GRAPHS_DIR / category
            visualize_graph(str(fpath), str(out_dir))
            success += 1
        except Exception as e:
            print(f"  ✗ Failed: {e}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"Visualization complete!")
    print(f"  Success: {success}")
    print(f"  Failed: {failed}")
    print(f"  Output: {GRAPHS_DIR}")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
