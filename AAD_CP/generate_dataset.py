"""
Dataset Generator for Biconnected Components Testing
Generates test cases for different types of graphs:
- Sparse graphs
- Dense graphs
- Small graphs
- Large graphs
- Tree-like graphs
- Highly connected graphs
"""

import random
import os
from typing import List, Tuple, Set

def ensure_dir(directory):
    """Create directory if it doesn't exist"""
    os.makedirs(directory, exist_ok=True)

def write_graph(filename: str, vertices: int, edges: List[Tuple[int, int]], description: str = ""):
    """
    Write graph to file in edge list format
    Format:
    # Description (if provided)
    num_vertices num_edges
    u1 v1
    u2 v2
    ...
    """
    with open(filename, 'w') as f:
        if description:
            f.write(f"# {description}\n")
        f.write(f"{vertices} {len(edges)}\n")
        for u, v in edges:
            f.write(f"{u} {v}\n")

def generate_sparse_graphs(output_dir: str):
    """Generate 10 sparse graphs (edge ratio ~1.5 to 2.5 times vertices)"""
    print("Generating sparse graphs...")
    
    test_cases = [
        (10, 12, "Small sparse graph"),
        (20, 25, "Medium sparse graph with articulation points"),
        (30, 40, "Sparse graph with multiple components"),
        (50, 65, "Larger sparse graph"),
        (15, 18, "Sparse graph - mostly linear"),
        (25, 35, "Sparse graph with bridges"),
        (40, 55, "Sparse graph - scattered connections"),
        (35, 50, "Sparse graph with isolated biconnected components"),
        (60, 80, "Large sparse graph"),
        (45, 60, "Sparse graph with articulation point chains"),
    ]
    
    for i, (n, target_edges, desc) in enumerate(test_cases, 1):
        edges = set()
        
        # Ensure connectivity (create a spanning tree)
        for v in range(1, n):
            u = random.randint(0, v - 1)
            edges.add((min(u, v), max(u, v)))
        
        # Add remaining edges randomly
        while len(edges) < target_edges:
            u = random.randint(0, n - 1)
            v = random.randint(0, n - 1)
            if u != v:
                edges.add((min(u, v), max(u, v)))
        
        filename = os.path.join(output_dir, f"sparse_{i:02d}.txt")
        write_graph(filename, n, list(edges), desc)
        print(f"  Created {filename}")

def generate_dense_graphs(output_dir: str):
    """Generate 10 dense graphs (edge ratio > 0.5 * n * (n-1) / 2)"""
    print("Generating dense graphs...")
    
    test_cases = [
        (10, 0.7, "Small dense graph"),
        (15, 0.65, "Dense graph with high connectivity"),
        (12, 0.8, "Very dense graph"),
        (20, 0.6, "Medium dense graph"),
        (8, 0.85, "Nearly complete graph"),
        (18, 0.7, "Dense graph - multiple biconnected components"),
        (14, 0.75, "Dense graph with redundant paths"),
        (16, 0.68, "Dense graph - highly connected"),
        (22, 0.62, "Larger dense graph"),
        (25, 0.55, "Large dense graph"),
    ]
    
    for i, (n, density, desc) in enumerate(test_cases, 1):
        max_edges = n * (n - 1) // 2
        target_edges = int(max_edges * density)
        
        edges = set()
        # Generate edges randomly until we reach target
        attempts = 0
        while len(edges) < target_edges and attempts < target_edges * 10:
            u = random.randint(0, n - 1)
            v = random.randint(0, n - 1)
            if u != v:
                edges.add((min(u, v), max(u, v)))
            attempts += 1
        
        filename = os.path.join(output_dir, f"dense_{i:02d}.txt")
        write_graph(filename, n, list(edges), desc)
        print(f"  Created {filename}")

def generate_small_graphs(output_dir: str):
    """Generate 10 small graphs (vertices <= 15)"""
    print("Generating small graphs...")
    
    test_cases = [
        (3, [(0, 1), (1, 2)], "Triangle path - 2 articulation points"),
        (4, [(0, 1), (1, 2), (2, 3), (3, 0)], "Square - biconnected"),
        (5, [(0, 1), (1, 2), (2, 3), (3, 4)], "Linear chain - many articulation points"),
        (6, [(0, 1), (1, 2), (2, 0), (2, 3), (3, 4), (4, 5)], "Triangle with tail"),
        (7, [(0, 1), (1, 2), (2, 0), (1, 3), (3, 4), (4, 5), (5, 6)], "Triangle with branch"),
        (5, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 0), (0, 2), (1, 3), (2, 4)], "Pentagon with diagonals"),
        (8, [(0, 1), (1, 2), (2, 3), (3, 0), (4, 5), (5, 6), (6, 7), (7, 4)], "Two separate squares"),
        (6, [(0, 1), (1, 2), (2, 3), (3, 4), (4, 5), (5, 0), (0, 3), (1, 4), (2, 5)], "Hexagon with chords"),
        (10, [(i, i+1) for i in range(9)], "Simple path - all articulation points"),
        (12, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (6, 7), (7, 8), (8, 6), (9, 10), (10, 11), (11, 9)], "Four triangles - disconnected"),
    ]
    
    for i, (n, edges, desc) in enumerate(test_cases, 1):
        filename = os.path.join(output_dir, f"small_{i:02d}.txt")
        write_graph(filename, n, edges, desc)
        print(f"  Created {filename}")

def generate_large_graphs(output_dir: str):
    """Generate 10 large graphs (vertices ~1000)"""
    print("Generating large graphs...")
    
    test_cases = [
        (1000, 1500, "1000 vertices, sparse"),
        (1200, 1800, "1200 vertices, sparse"),
        (900, 2500, "900 vertices, medium density"),
        (1100, 2000, "1100 vertices, sparse"),
        (1000, 3000, "1000 vertices, medium-sparse"),
        (1300, 4000, "1300 vertices, denser"),
        (950, 1500, "950 vertices, sparse"),
        (1150, 3500, "1150 vertices, medium"),
        (1000, 2000, "1000 vertices, moderate"),
        (1250, 5000, "1250 vertices, dense"),
    ]
    
    for i, (n, target_edges, desc) in enumerate(test_cases, 1):
        edges = set()
        
        # Create connected components
        num_components = random.randint(1, 3)
        component_sizes = []
        remaining = n
        
        for _ in range(num_components - 1):
            size = random.randint(n // (num_components * 2), n // num_components)
            component_sizes.append(size)
            remaining -= size
        component_sizes.append(remaining)
        
        offset = 0
        for comp_size in component_sizes:
            # Create spanning tree for this component
            for v in range(offset + 1, offset + comp_size):
                u = random.randint(offset, v - 1)
                edges.add((min(u, v), max(u, v)))
            offset += comp_size
        
        # Add remaining edges
        while len(edges) < target_edges:
            u = random.randint(0, n - 1)
            v = random.randint(0, n - 1)
            if u != v:
                edges.add((min(u, v), max(u, v)))
        
        filename = os.path.join(output_dir, f"large_{i:02d}.txt")
        write_graph(filename, n, list(edges), desc)
        print(f"  Created {filename}")

def generate_tree_like_graphs(output_dir: str):
    """Generate 10 tree-like graphs (minimal cycles)"""
    print("Generating tree-like graphs...")
    
    # Test case 1: Perfect binary tree
    n = 15
    edges = []
    for i in range(n // 2):
        left = 2 * i + 1
        right = 2 * i + 2
        if left < n:
            edges.append((i, left))
        if right < n:
            edges.append((i, right))
    write_graph(os.path.join(output_dir, "tree_01.txt"), n, edges, "Perfect binary tree")
    
    # Test case 2: Linear tree (path)
    n = 20
    edges = [(i, i+1) for i in range(n-1)]
    write_graph(os.path.join(output_dir, "tree_02.txt"), n, edges, "Linear path - maximum articulation points")
    
    # Test case 3: Star graph
    n = 25
    edges = [(0, i) for i in range(1, n)]
    write_graph(os.path.join(output_dir, "tree_03.txt"), n, edges, "Star graph - center is articulation point")
    
    # Test case 4: Tree with one cycle
    n = 30
    edges = [(i, i+1) for i in range(n-1)]
    edges.append((0, n-1))  # Close the loop
    write_graph(os.path.join(output_dir, "tree_04.txt"), n, edges, "Cycle graph")
    
    # Test case 5: Balanced k-ary tree
    n = 31
    edges = []
    k = 3
    for i in range(n):
        for j in range(1, k+1):
            child = k * i + j
            if child < n:
                edges.append((i, child))
    write_graph(os.path.join(output_dir, "tree_05.txt"), n, edges, "Ternary tree")
    
    # Test case 6: Tree with multiple branches
    n = 40
    edges = [(0, i) for i in range(1, 5)]  # 4 main branches
    offset = 5
    for branch in range(1, 5):
        branch_size = 9
        for i in range(branch_size - 1):
            edges.append((offset + i, offset + i + 1))
        edges.append((branch, offset))
        offset += branch_size
    write_graph(os.path.join(output_dir, "tree_06.txt"), n, edges, "Star with branches")
    
    # Test case 7: Random tree
    n = 35
    edges = []
    for v in range(1, n):
        u = random.randint(0, v - 1)
        edges.append((u, v))
    write_graph(os.path.join(output_dir, "tree_07.txt"), n, edges, "Random tree")
    
    # Test case 8: Caterpillar tree
    n = 28
    backbone_size = 14
    edges = [(i, i+1) for i in range(backbone_size - 1)]
    for i in range(backbone_size):
        if backbone_size + i < n:
            edges.append((i, backbone_size + i))
    write_graph(os.path.join(output_dir, "tree_08.txt"), n, edges, "Caterpillar tree")
    
    # Test case 9: Tree with 2 cycles
    n = 25
    edges = [(i, i+1) for i in range(n-1)]
    edges.append((5, 10))  # Create a cycle
    edges.append((15, 20))  # Create another cycle
    write_graph(os.path.join(output_dir, "tree_09.txt"), n, edges, "Tree with two cycles")
    
    # Test case 10: Sparse tree-like with few extra edges
    n = 50
    edges = []
    for v in range(1, n):
        u = random.randint(max(0, v - 5), v - 1)
        edges.append((u, v))
    # Add a few random edges
    for _ in range(5):
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)
        if u != v:
            edges.append((min(u, v), max(u, v)))
    write_graph(os.path.join(output_dir, "tree_10.txt"), n, list(set(edges)), "Tree-like with few cycles")
    
    print("  Created all tree-like graphs")

def generate_highly_connected_graphs(output_dir: str):
    """Generate 10 highly connected graphs (multiple biconnected components)"""
    print("Generating highly connected graphs...")
    
    # Test case 1: Complete graph K5
    n = 5
    edges = [(i, j) for i in range(n) for j in range(i+1, n)]
    write_graph(os.path.join(output_dir, "highly_connected_01.txt"), n, edges, "Complete graph K5")
    
    # Test case 2: Complete graph K7
    n = 7
    edges = [(i, j) for i in range(n) for j in range(i+1, n)]
    write_graph(os.path.join(output_dir, "highly_connected_02.txt"), n, edges, "Complete graph K7")
    
    # Test case 3: Multiple complete subgraphs connected
    edges = []
    # K4
    for i in range(4):
        for j in range(i+1, 4):
            edges.append((i, j))
    # K5
    for i in range(4, 9):
        for j in range(i+1, 9):
            edges.append((i, j))
    # Connect them
    edges.append((3, 4))
    write_graph(os.path.join(output_dir, "highly_connected_03.txt"), 9, edges, "Two complete subgraphs connected by bridge")
    
    # Test case 4: Grid graph
    rows, cols = 5, 5
    n = rows * cols
    edges = []
    for i in range(rows):
        for j in range(cols):
            node = i * cols + j
            if j < cols - 1:
                edges.append((node, node + 1))
            if i < rows - 1:
                edges.append((node, node + cols))
    write_graph(os.path.join(output_dir, "highly_connected_04.txt"), n, edges, "5x5 grid graph")
    
    # Test case 5: Wheel graph
    n = 12
    edges = [(0, i) for i in range(1, n)]  # Center to all
    edges.extend([(i, i+1) for i in range(1, n-1)])  # Outer cycle
    edges.append((n-1, 1))
    write_graph(os.path.join(output_dir, "highly_connected_05.txt"), n, edges, "Wheel graph - W11")
    
    # Test case 6: Complete bipartite graph K3,4
    n = 7
    edges = [(i, j) for i in range(3) for j in range(3, 7)]
    write_graph(os.path.join(output_dir, "highly_connected_06.txt"), n, edges, "Complete bipartite K3,4")
    
    # Test case 7: Petersen graph
    n = 10
    edges = []
    # Outer pentagon
    for i in range(5):
        edges.append((i, (i+1) % 5))
    # Inner pentagram
    for i in range(5, 10):
        edges.append((i, 5 + (i-5+2) % 5))
    # Connect outer to inner
    for i in range(5):
        edges.append((i, i+5))
    write_graph(os.path.join(output_dir, "highly_connected_07.txt"), n, edges, "Petersen graph")
    
    # Test case 8: High density random graph
    n = 20
    edges = set()
    target = 120
    while len(edges) < target:
        u = random.randint(0, n - 1)
        v = random.randint(0, n - 1)
        if u != v:
            edges.add((min(u, v), max(u, v)))
    write_graph(os.path.join(output_dir, "highly_connected_08.txt"), n, list(edges), "Dense random graph")
    
    # Test case 9: Multiple triangles connected
    n = 15
    edges = []
    # 5 triangles
    for t in range(5):
        base = t * 3
        edges.extend([(base, base+1), (base+1, base+2), (base+2, base)])
    # Connect triangles
    for t in range(4):
        edges.append((t * 3 + 2, (t+1) * 3))
    write_graph(os.path.join(output_dir, "highly_connected_09.txt"), n, edges, "Chain of triangles")
    
    # Test case 10: Dense graph with guaranteed biconnected components
    n = 30
    edges = set()
    # Create 3 highly connected subgraphs
    for comp in range(3):
        start = comp * 10
        end = start + 10
        # Make each component dense
        for i in range(start, end):
            for j in range(i+1, end):
                if random.random() < 0.6:
                    edges.add((i, j))
    # Connect components with single edges (articulation points)
    edges.add((9, 10))
    edges.add((19, 20))
    
    write_graph(os.path.join(output_dir, "highly_connected_10.txt"), n, list(edges), "Three dense components connected")
    
    print("  Created all highly connected graphs")

def create_readme_files():
    """Create README files for each directory"""
    
    readme_content = {
        "sparse": """# Sparse Graphs
Graphs with relatively few edges compared to vertices (edge ratio ~1.5-2.5x vertices).
These graphs are likely to have many articulation points and bridges.

Format: Each file contains:
- Line 1: # Description
- Line 2: num_vertices num_edges
- Following lines: u v (edge from u to v)

Vertices are 0-indexed.
""",
        "dense": """# Dense Graphs
Graphs with many edges (edge ratio > 50% of maximum possible edges).
These graphs tend to have fewer articulation points and larger biconnected components.

Format: Each file contains:
- Line 1: # Description
- Line 2: num_vertices num_edges
- Following lines: u v (edge from u to v)

Vertices are 0-indexed.
""",
        "small": """# Small Graphs
Graphs with few vertices (≤ 15).
Useful for manual verification and debugging of algorithms.

Format: Each file contains:
- Line 1: # Description
- Line 2: num_vertices num_edges
- Following lines: u v (edge from u to v)

Vertices are 0-indexed.
""",
        "large": """# Large Graphs
Graphs with many vertices (≥ 100).
Used for performance testing and scalability analysis.

Format: Each file contains:
- Line 1: # Description
- Line 2: num_vertices num_edges
- Following lines: u v (edge from u to v)

Vertices are 0-indexed.
""",
        "tree_like": """# Tree-like Graphs
Graphs that are trees or have very few cycles.
Most edges in these graphs are bridges, and most vertices are articulation points.

Format: Each file contains:
- Line 1: # Description
- Line 2: num_vertices num_edges
- Following lines: u v (edge from u to v)

Vertices are 0-indexed.
""",
        "highly_connected": """# Highly Connected Graphs
Graphs with high connectivity and multiple redundant paths.
These include complete graphs, wheels, grids, and dense random graphs.

Format: Each file contains:
- Line 1: # Description
- Line 2: num_vertices num_edges
- Following lines: u v (edge from u to v)

Vertices are 0-indexed.
""",
        "real_world": """# Real World Graphs
This directory is reserved for real-world graph datasets.

Please add your real-world graphs here in the same format:
- Line 1: # Description
- Line 2: num_vertices num_edges
- Following lines: u v (edge from u to v)

Vertices should be 0-indexed.

Examples of real-world graphs:
- Social networks
- Road networks
- Citation networks
- Collaboration networks
- Web graphs
"""
    }
    
    base_dir = "dataset"
    for subdir, content in readme_content.items():
        filepath = os.path.join(base_dir, subdir, "README.md")
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Created {filepath}")

def main():
    """Generate all test cases"""
    print("=" * 60)
    print("Biconnected Components Dataset Generator")
    print("=" * 60)
    print()
    
    random.seed(42)  # For reproducibility
    
    base_dir = "dataset"
    
    # Generate all test cases
    generate_sparse_graphs(os.path.join(base_dir, "sparse"))
    generate_dense_graphs(os.path.join(base_dir, "dense"))
    generate_small_graphs(os.path.join(base_dir, "small"))
    generate_large_graphs(os.path.join(base_dir, "large"))
    generate_tree_like_graphs(os.path.join(base_dir, "tree_like"))
    generate_highly_connected_graphs(os.path.join(base_dir, "highly_connected"))
    
    print()
    print("Creating README files...")
    create_readme_files()
    
    print()
    print("=" * 60)
    print("Dataset generation complete!")
    print("=" * 60)
    print()
    print("Directory structure:")
    print("  dataset/")
    print("    ├── sparse/           (10 test cases)")
    print("    ├── dense/            (10 test cases)")
    print("    ├── small/            (10 test cases)")
    print("    ├── large/            (10 test cases)")
    print("    ├── tree_like/        (10 test cases)")
    print("    ├── highly_connected/ (10 test cases)")
    print("    └── real_world/       (add your graphs here)")
    print()
    print("Total: 60 generated test cases + space for real-world graphs")

if __name__ == "__main__":
    main()
