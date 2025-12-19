#!/usr/bin/env python3
"""
Generate visualization for a specific graph file.
Usage: python3 visualize_graph.py <path_to_graph_file>
"""
import sys
import os
from pathlib import Path
import networkx as nx
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def read_graph_from_file(filepath):
    """Read graph from file, skipping comments."""
    G = nx.Graph()
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Skip comment lines and read V, E
    line_idx = 0
    while line_idx < len(lines):
        line = lines[line_idx].strip()
        if line and not line.startswith('#'):
            parts = line.split()
            if len(parts) >= 2:
                try:
                    V, E = int(parts[0]), int(parts[1])
                    line_idx += 1
                    break
                except:
                    pass
        line_idx += 1
    
    # Read edges
    for i in range(line_idx, len(lines)):
        line = lines[i].strip()
        if not line or line.startswith('#'):
            continue
        parts = line.split()
        if len(parts) >= 2:
            try:
                u, v = int(parts[0]), int(parts[1])
                G.add_edge(u, v)
            except:
                continue
    
    return G

def visualize_graph(filepath, output_dir=None):
    """Create visualization with articulation points and bridges highlighted."""
    G = read_graph_from_file(filepath)
    
    n_nodes = G.number_of_nodes()
    n_edges = G.number_of_edges()
    
    filename = Path(filepath).stem
    
    if output_dir is None:
        output_dir = Path(filepath).parent / 'visualizations'
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Graph: {filename}")
    print(f"  Vertices: {n_nodes}")
    print(f"  Edges: {n_edges}")
    
    # For very large graphs, create degree distribution instead
    if n_nodes > 1000:
        print(f"  Graph too large ({n_nodes} nodes), creating degree distribution plot...")
        plt.figure(figsize=(8, 6))
        degrees = [d for _, d in G.degree()]
        plt.hist(degrees, bins=50, edgecolor='black')
        plt.title(f'{filename} - Degree Distribution\n({n_nodes} vertices, {n_edges} edges)')
        plt.xlabel('Degree')
        plt.ylabel('Count')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        output_file = output_dir / f"{filename}_degree_dist.png"
        plt.savefig(output_file, dpi=150)
        plt.close()
        print(f"  ✓ Saved: {output_file}")
        return
    
    # Find articulation points and bridges
    aps = set(nx.articulation_points(G))
    bridges = set(nx.bridges(G))
    
    print(f"  Articulation Points: {len(aps)}")
    print(f"  Bridges: {len(bridges)}")
    
    # Create layout
    if n_nodes <= 50:
        pos = nx.spring_layout(G, seed=42, k=1, iterations=50)
        node_size = 300
        font_size = 10
    elif n_nodes <= 200:
        pos = nx.spring_layout(G, seed=42, k=0.5, iterations=30)
        node_size = 100
        font_size = 8
    else:
        pos = nx.spring_layout(G, seed=42, k=0.3, iterations=20)
        node_size = 50
        font_size = 6
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 10))
    
    # Draw nodes
    node_colors = ['red' if v in aps else 'lightblue' for v in G.nodes()]
    nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=node_size, ax=ax)
    
    # Draw edges
    regular_edges = [e for e in G.edges() if e not in bridges and (e[1], e[0]) not in bridges]
    bridge_edges = [e for e in G.edges() if e in bridges or (e[1], e[0]) in bridges]
    
    nx.draw_networkx_edges(G, pos, edgelist=regular_edges, alpha=0.5, width=1, ax=ax)
    if bridge_edges:
        nx.draw_networkx_edges(G, pos, edgelist=bridge_edges, edge_color='red', width=2, ax=ax)
    
    # Draw labels for small graphs
    if n_nodes <= 100:
        nx.draw_networkx_labels(G, pos, font_size=font_size, ax=ax)
    
    ax.set_title(f'{filename}\n{n_nodes} vertices, {n_edges} edges\n'
                 f'{len(aps)} articulation points (red nodes), {len(bridges)} bridges (red edges)',
                 fontsize=14, fontweight='bold')
    ax.axis('off')
    plt.tight_layout()
    
    output_file = output_dir / f"{filename}_visualization.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    plt.close()
    
    print(f"  ✓ Saved: {output_file}")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 visualize_graph.py <path_to_graph_file> [output_dir]")
        print("Example: python3 visualize_graph.py dataset/dense/dense_01.txt")
        sys.exit(1)
    
    filepath = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not os.path.exists(filepath):
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    
    visualize_graph(filepath, output_dir)
