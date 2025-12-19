#!/usr/bin/env python3
import os
import subprocess
import time
import csv
import json
from pathlib import Path
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# Config
ROOT = Path(__file__).resolve().parents[1]
DATASET_DIR = ROOT / 'dataset'
CODES_DIR = ROOT / 'codes'
OUTPUT_DIR = ROOT / 'outputs'
GRAPHS_DIR = ROOT / 'graphs'
# Only include algorithms that are implemented
EXEC_NAMES = ['p1', 'p2', 'p4', 'p5']

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(GRAPHS_DIR, exist_ok=True)

def compile_if_needed(name: str):
    exe = CODES_DIR / name
    src = CODES_DIR / f"{name}.cpp"
    if exe.exists() and os.access(exe, os.X_OK):
        return True
    if not src.exists():
        print(f"Source file {src} not found, skipping compilation.")
        return False
    print(f"Compiling {src} -> {exe} ...")
    r = subprocess.run(['g++', str(src), '-O2', '-std=c++17', '-o', str(exe)], 
                       capture_output=True, text=True)
    if r.returncode != 0:
        print(f"Compilation failed for {name}:")
        print(r.stderr)
        return False
    return True

def discover_dataset_files():
    files = []
    for category in sorted(DATASET_DIR.iterdir()):
        if not category.is_dir():
            continue
        for f in sorted(category.glob('*.txt')):
            files.append((category.name, f))
    return files

def read_header_and_edges(path: Path):
    """Return (n, m, edges_generator)
       edges_generator yields (u,v) pairs (as ints)
       This function is robust to files that have header "n m" on first line or not.
    """
    f = open(path, 'r')
    first = f.readline().strip()
    parts = first.split()
    def gen_from_file(fp):
        for line in fp:
            line=line.strip()
            if not line: continue
            # skip comment lines
            if line.lstrip().startswith('#'): continue
            # replace commas
            line = line.replace(',', ' ')
            a = line.split()
            if len(a) < 2: continue
            try:
                u = int(a[0]); v = int(a[1])
            except:
                continue
            yield u, v

    # Try to detect header
    if len(parts) >= 2:
        try:
            n = int(parts[0]); m = int(parts[1])
            return n, m, gen_from_file(f)
        except:
            # not header, fallthrough
            pass
    # No header: rewind and produce edges
    f.seek(0)
    edges = list(gen_from_file(f))
    # infer n,m
    if edges:
        maxv = max(max(u,v) for u,v in edges)
        n = maxv + 1
        m = len(edges)
    else:
        n = 0; m = 0
    return n, m, iter(edges)

def build_graph_from_file(path: Path, limit_nodes_plot=2000):
    n, m, edges_gen = read_header_and_edges(path)
    G = nx.Graph()
    count = 0
    for u,v in edges_gen:
        G.add_edge(u, v)
        count += 1
    return n, m, G

def visualize_graph(category, fname, G: nx.Graph, out_dir: Path):
    # highlight articulation points and bridges
    n_nodes = G.number_of_nodes()
    basename = fname.stem
    out_dir.mkdir(parents=True, exist_ok=True)
    if n_nodes == 0:
        return
    if n_nodes > 2000:
        # For very large graphs, produce a summary plot (degree histogram) instead
        plt.figure(figsize=(6,4))
        degs = [d for _,d in G.degree()]
        plt.hist(degs, bins=50)
        plt.title(f'{basename} degree distribution (n={n_nodes})')
        plt.xlabel('degree'); plt.ylabel('count')
        plt.tight_layout()
        plt.savefig(out_dir / f"{basename}_degree_hist.png")
        plt.close()
        return

    aps = set(nx.articulation_points(G))
    br = set(nx.bridges(G))

    pos = nx.spring_layout(G, seed=42)
    plt.figure(figsize=(8,8))
    # draw nodes
    node_colors = ['red' if v in aps else 'skyblue' for v in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_size=50, node_color=node_colors)
    # draw edges: bridges in red
    regular_edges = [e for e in G.edges() if e not in br and (e[1],e[0]) not in br]
    nx.draw_networkx_edges(G, pos, edgelist=regular_edges, alpha=0.6, width=0.7)
    if br:
        nx.draw_networkx_edges(G, pos, edgelist=list(br), edge_color='red', width=1.0)
    plt.axis('off')
    plt.title(f'{basename} (n={n_nodes}, m={G.number_of_edges()})\nred=articulation points / bridges')
    plt.tight_layout()
    plt.savefig(out_dir / f"{basename}_articulation_bridges.png", dpi=150)
    plt.close()

def run():
    # compile executables if source exists
    compiled_exes = []
    for name in EXEC_NAMES:
        if compile_if_needed(name):
            compiled_exes.append(name)
    
    if not compiled_exes:
        print("No executables compiled successfully!")
        return

    files = discover_dataset_files()
    results = []

    # Run one algorithm at a time on full dataset
    for exe in compiled_exes:
        print(f"\n{'='*60}")
        print(f"Running algorithm: {exe}")
        print(f"{'='*60}\n")
        
        exe_path = CODES_DIR / exe
        
        for category, fpath in files:
            rel = fpath.relative_to(DATASET_DIR)
            print(f"  [{exe}] Processing {rel} ...")
            
            # prepare graph info (only once per file)
            n, m, G = None, None, None
            try:
                n, m, G = build_graph_from_file(fpath)
            except Exception as e:
                print(f'    Failed to build graph: {e}')

            # create output subdir
            out_subdir = OUTPUT_DIR / exe / category
            out_subdir.mkdir(parents=True, exist_ok=True)
            outfile = out_subdir / fpath.name

            # run with redirected stdin from dataset file
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
                print(f"    ✓ Completed in {runtime:.3f}s (exit code: {p.returncode})")
                results.append({'algorithm': exe, 'category': category, 'file': str(rel), 
                              'n': n, 'm': m, 'time': runtime, 'exitcode': p.returncode, 
                              'output': str(outfile)})
            except subprocess.TimeoutExpired:
                print(f"    ✗ TIMEOUT (>600s)")
                with open(outfile, 'w') as fo:
                    fo.write('TIMEOUT\n')
                results.append({'algorithm': exe, 'category': category, 'file': str(rel), 
                              'n': n, 'm': m, 'time': None, 'exitcode': 'timeout', 
                              'output': str(outfile)})
            except Exception as e:
                print(f"    ✗ ERROR: {e}")
                with open(outfile, 'w') as fo:
                    fo.write('ERROR: '+str(e)+'\n')
                results.append({'algorithm': exe, 'category': category, 'file': str(rel), 
                              'n': n, 'm': m, 'time': None, 'exitcode': 'error', 
                              'output': str(outfile)})
            
            # Save intermediate results after each test
            csv_path = OUTPUT_DIR / 'results.csv'
            with open(csv_path, 'w', newline='') as cf:
                writer = csv.DictWriter(cf, fieldnames=['algorithm','category','file','n','m','time','exitcode','output'])
                writer.writeheader()
                for r in results:
                    writer.writerow(r)
    
    # Produce visualizations once at the end
    print(f"\n{'='*60}")
    print("Generating visualizations...")
    print(f"{'='*60}\n")
    
    for category, fpath in files:
        try:
            n, m, G = build_graph_from_file(fpath)
            if G is not None:
                vis_out = GRAPHS_DIR / category
                visualize_graph(category, fpath, G, vis_out)
                print(f"  ✓ Visualized {fpath.name}")
        except Exception as e:
            print(f'  ✗ Visualization failed for {fpath.name}: {e}')

    # write final results CSV
    csv_path = OUTPUT_DIR / 'results.csv'
    with open(csv_path, 'w', newline='') as cf:
        writer = csv.DictWriter(cf, fieldnames=['algorithm','category','file','n','m','time','exitcode','output'])
        writer.writeheader()
        for r in results:
            writer.writerow(r)

    # performance plot: time vs n per algorithm
    print("\nGenerating performance plots...")
    try:
        import pandas as pd
        df = pd.read_csv(csv_path)
        df = df[df['time'].notna()]
        if not df.empty:
            plt.figure(figsize=(8,6))
            for alg, g in df.groupby('algorithm'):
                plt.scatter(g['n'], g['time'], label=alg, s=20)
            plt.xscale('log'); plt.yscale('log')
            plt.xlabel('number of vertices (n)'); plt.ylabel('time (s)'); plt.legend()
            plt.title('Time vs Graph Size')
            plt.tight_layout(); plt.savefig(GRAPHS_DIR / 'time_vs_size.png')
            plt.close()
            print("  ✓ Saved time_vs_size.png")
    except Exception as e:
        print(f'  ✗ Could not create performance plot: {e}')

    # save raw results json
    with open(OUTPUT_DIR / 'results.json', 'w') as jf:
        json.dump(results, jf, indent=2)
    
    print(f"\n{'='*60}")
    print("All tests complete!")
    print(f"Results saved to: {OUTPUT_DIR}")
    print(f"Visualizations saved to: {GRAPHS_DIR}")
    print(f"{'='*60}\n")

if __name__ == '__main__':
    run()
