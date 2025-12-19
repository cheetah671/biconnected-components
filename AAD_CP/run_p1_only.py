#!/usr/bin/env python3
import os
import subprocess
import time
import csv
from pathlib import Path

# Config
ROOT = Path(__file__).resolve().parent
DATASET_DIR = ROOT / 'dataset'
CODES_DIR = ROOT / 'codes'
OUTPUT_DIR = ROOT / 'outputs'

os.makedirs(OUTPUT_DIR, exist_ok=True)

def compile_p1():
    exe = CODES_DIR / 'p1'
    src = CODES_DIR / 'p1.cpp'
    if exe.exists() and os.access(exe, os.X_OK):
        print("p1 executable already exists")
        return True
    if not src.exists():
        print(f"Source file {src} not found!")
        return False
    print(f"Compiling {src} -> {exe} ...")
    r = subprocess.run(['g++', str(src), '-O2', '-std=c++17', '-o', str(exe)], 
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"Compilation failed:")
        print(r.stderr)
        return False
    print("✓ Compilation successful")
    return True

def discover_dataset_files():
    files = []
    for category in sorted(DATASET_DIR.iterdir()):
        if not category.is_dir():
            continue
        for f in sorted(category.glob('*.txt')):
            files.append((category.name, f))
    return files

def run():
    # Compile p1
    if not compile_p1():
        print("Failed to compile p1. Exiting.")
        return

    files = discover_dataset_files()
    results = []
    
    print(f"\n{'='*60}")
    print(f"Running p1 on {len(files)} test files")
    print(f"{'='*60}\n")
    
    exe_path = CODES_DIR / 'p1'
    
    for idx, (category, fpath) in enumerate(files, 1):
        rel = fpath.relative_to(DATASET_DIR)
        print(f"[{idx}/{len(files)}] Processing {rel} ...", end=' ')
        
        # Read file to get n, m
        try:
            with open(fpath, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        parts = line.split()
                        if len(parts) >= 2:
                            n, m = int(parts[0]), int(parts[1])
                            break
        except:
            n, m = None, None

        # Create output subdir
        out_subdir = OUTPUT_DIR / 'p1' / category
        out_subdir.mkdir(parents=True, exist_ok=True)
        outfile = out_subdir / fpath.name

        # Run with redirected stdin from dataset file
        start = time.perf_counter()
        try:
            p = subprocess.run([str(exe_path)], stdin=open(fpath,'r'), 
                             stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
                             timeout=600)
            end = time.perf_counter()
            runtime = end - start
            out = p.stdout.decode('utf-8', errors='replace')
            with open(outfile, 'w') as fo:
                fo.write(out)
            print(f"✓ {runtime:.3f}s (exit: {p.returncode})")
            results.append({'algorithm': 'p1', 'category': category, 'file': str(rel), 
                          'n': n, 'm': m, 'time': runtime, 'exitcode': p.returncode, 
                          'output': str(outfile)})
        except subprocess.TimeoutExpired:
            print(f"✗ TIMEOUT (>600s)")
            with open(outfile, 'w') as fo:
                fo.write('TIMEOUT\n')
            results.append({'algorithm': 'p1', 'category': category, 'file': str(rel), 
                          'n': n, 'm': m, 'time': None, 'exitcode': 'timeout', 
                          'output': str(outfile)})
        except Exception as e:
            print(f"✗ ERROR: {e}")
            with open(outfile, 'w') as fo:
                fo.write('ERROR: '+str(e)+'\n')
            results.append({'algorithm': 'p1', 'category': category, 'file': str(rel), 
                          'n': n, 'm': m, 'time': None, 'exitcode': 'error', 
                          'output': str(outfile)})
    
    # Write results CSV
    csv_path = OUTPUT_DIR / 'p1_results.csv'
    with open(csv_path, 'w', newline='') as cf:
        writer = csv.DictWriter(cf, fieldnames=['algorithm','category','file','n','m','time','exitcode','output'])
        writer.writeheader()
        for r in results:
            writer.writerow(r)
    
    print(f"\n{'='*60}")
    print("p1 testing complete!")
    print(f"Results saved to: {csv_path}")
    print(f"Output files in: {OUTPUT_DIR / 'p1'}")
    print(f"{'='*60}\n")
    
    # Summary
    successful = sum(1 for r in results if r['exitcode'] == 0)
    timeouts = sum(1 for r in results if r['exitcode'] == 'timeout')
    errors = sum(1 for r in results if r['exitcode'] not in [0, 'timeout'])
    
    print(f"Summary: {successful} successful, {timeouts} timeouts, {errors} errors")

if __name__ == '__main__':
    run()
