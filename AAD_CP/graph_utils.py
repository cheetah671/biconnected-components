"""
Graph Reader and Utilities for Biconnected Components Dataset

This module provides helper functions to:
- Read graphs from the dataset
- Build adjacency lists
- Visualize graphs (optional)
- Compute basic graph properties
"""

import os
from typing import List, Tuple, Set, Dict
from collections import defaultdict

def read_graph(filename: str) -> Tuple[int, List[Tuple[int, int]], str]:
    """
    Read a graph from file
    
    Args:
        filename: Path to the graph file
        
    Returns:
        tuple: (num_vertices, edges_list, description)
    """
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Skip comment lines and extract description
    description = ""
    idx = 0
    while idx < len(lines) and lines[idx].strip().startswith('#'):
        description += lines[idx][1:].strip() + " "
        idx += 1
    
    # Read vertices and edges count
    n, m = map(int, lines[idx].split())
    
    # Read edges
    edges = []
    for i in range(idx + 1, min(idx + 1 + m, len(lines))):
        parts = lines[i].strip().split()
        if len(parts) >= 2:
            u, v = map(int, parts[:2])
            edges.append((u, v))
    
    return n, edges, description.strip()


def build_adjacency_list(n: int, edges: List[Tuple[int, int]]) -> List[List[int]]:
    """
    Build adjacency list representation
    
    Args:
        n: Number of vertices
        edges: List of edges as (u, v) tuples
        
    Returns:
        List of lists representing adjacency list
    """
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj


def build_edge_list(n: int, edges: List[Tuple[int, int]]) -> Set[Tuple[int, int]]:
    """
    Build a set of edges (normalized)
    
    Args:
        n: Number of vertices
        edges: List of edges as (u, v) tuples
        
    Returns:
        Set of edges with (min, max) ordering
    """
    edge_set = set()
    for u, v in edges:
        edge_set.add((min(u, v), max(u, v)))
    return edge_set


def get_graph_properties(n: int, edges: List[Tuple[int, int]]) -> Dict:
    """
    Compute basic graph properties
    
    Args:
        n: Number of vertices
        edges: List of edges
        
    Returns:
        Dictionary with graph properties
    """
    adj = build_adjacency_list(n, edges)
    
    properties = {
        'vertices': n,
        'edges': len(edges),
        'density': 2 * len(edges) / (n * (n - 1)) if n > 1 else 0,
        'avg_degree': 2 * len(edges) / n if n > 0 else 0,
        'max_degree': max([len(adj[i]) for i in range(n)]) if n > 0 else 0,
        'min_degree': min([len(adj[i]) for i in range(n)]) if n > 0 else 0,
    }
    
    # Check connectivity using DFS
    if n > 0:
        visited = [False] * n
        
        def dfs(v):
            visited[v] = True
            for u in adj[v]:
                if not visited[u]:
                    dfs(u)
        
        dfs(0)
        properties['is_connected'] = all(visited)
        properties['num_components'] = sum(1 for i in range(n) if not visited[i]) + 1 if not all(visited) else 1
    else:
        properties['is_connected'] = True
        properties['num_components'] = 0
    
    return properties


def print_graph_info(filename: str):
    """
    Print detailed information about a graph
    
    Args:
        filename: Path to graph file
    """
    n, edges, description = read_graph(filename)
    properties = get_graph_properties(n, edges)
    
    print(f"File: {os.path.basename(filename)}")
    print(f"Description: {description}")
    print(f"Vertices: {properties['vertices']}")
    print(f"Edges: {properties['edges']}")
    print(f"Density: {properties['density']:.4f}")
    print(f"Avg Degree: {properties['avg_degree']:.2f}")
    print(f"Degree Range: [{properties['min_degree']}, {properties['max_degree']}]")
    print(f"Connected: {properties['is_connected']}")
    if not properties['is_connected']:
        print(f"Components: {properties['num_components']}")
    print()


def list_all_graphs(dataset_dir: str = "dataset"):
    """
    List all graphs in the dataset with their properties
    
    Args:
        dataset_dir: Path to dataset directory
    """
    categories = ['sparse', 'dense', 'small', 'large', 'tree_like', 'highly_connected', 'real_world']
    
    for category in categories:
        category_path = os.path.join(dataset_dir, category)
        if not os.path.exists(category_path):
            continue
            
        print(f"\n{'=' * 60}")
        print(f"Category: {category.upper()}")
        print('=' * 60)
        
        files = sorted([f for f in os.listdir(category_path) if f.endswith('.txt')])
        
        if not files:
            print("No graph files found.")
            continue
        
        for filename in files:
            filepath = os.path.join(category_path, filename)
            print_graph_info(filepath)


def visualize_graph(n: int, edges: List[Tuple[int, int]], title: str = "Graph"):
    """
    Visualize a graph using matplotlib (requires matplotlib and networkx)
    
    Args:
        n: Number of vertices
        edges: List of edges
        title: Title for the plot
    """
    try:
        import matplotlib.pyplot as plt
        import networkx as nx
    except ImportError:
        print("Error: matplotlib and networkx are required for visualization")
        print("Install with: pip install matplotlib networkx")
        return
    
    # Create NetworkX graph
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges)
    
    # Create figure
    plt.figure(figsize=(10, 8))
    
    # Choose layout based on graph size
    if n <= 20:
        pos = nx.spring_layout(G, k=1, iterations=50)
    else:
        pos = nx.spring_layout(G, k=0.5, iterations=30)
    
    # Draw graph
    nx.draw(G, pos, 
            node_color='lightblue',
            node_size=500 if n <= 50 else 200,
            with_labels=True if n <= 30 else False,
            font_size=10,
            font_weight='bold',
            edge_color='gray',
            width=2)
    
    plt.title(title)
    plt.axis('off')
    plt.tight_layout()
    plt.show()


def visualize_graph_file(filename: str):
    """
    Read and visualize a graph from file
    
    Args:
        filename: Path to graph file
    """
    n, edges, description = read_graph(filename)
    title = f"{os.path.basename(filename)}\n{description}"
    visualize_graph(n, edges, title)


def export_to_networkx(n: int, edges: List[Tuple[int, int]]):
    """
    Export graph to NetworkX format
    
    Args:
        n: Number of vertices
        edges: List of edges
        
    Returns:
        NetworkX Graph object
    """
    try:
        import networkx as nx
    except ImportError:
        print("Error: networkx is required")
        print("Install with: pip install networkx")
        return None
    
    G = nx.Graph()
    G.add_nodes_from(range(n))
    G.add_edges_from(edges)
    return G


# Example usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        # If filename provided, show that graph
        filename = sys.argv[1]
        if os.path.exists(filename):
            print_graph_info(filename)
            
            # Optionally visualize
            if len(sys.argv) > 2 and sys.argv[2] == '--visualize':
                visualize_graph_file(filename)
        else:
            print(f"File not found: {filename}")
    else:
        # List all graphs
        print("Biconnected Components Dataset - Graph Utilities")
        print("=" * 60)
        list_all_graphs()
        
        print("\n" + "=" * 60)
        print("Usage:")
        print("  python graph_utils.py <filename>           # Show graph info")
        print("  python graph_utils.py <filename> --visualize  # Show and visualize")
        print("  python graph_utils.py                      # List all graphs")
