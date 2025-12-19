# Biconnected Components Dataset Overview

## Project Structure

```
dataset/
├── sparse/              # 10 sparse graphs (low edge density)
├── dense/               # 10 dense graphs (high edge density)
├── small/               # 10 small graphs (≤15 vertices)
├── large/               # 10 large graphs (≥100 vertices)
├── tree_like/           # 10 tree-like graphs (minimal cycles)
├── highly_connected/    # 10 highly connected graphs
└── real_world/          # Real-world graphs (user-provided)
```

**Total: 60 generated test cases** + space for real-world graphs

---

## File Format

All graph files follow this format:

```
# Description of the graph
num_vertices num_edges
u1 v1
u2 v2
...
```

- **Vertices are 0-indexed** (ranging from 0 to num_vertices-1)
- Each edge is represented as `u v` where u and v are vertex IDs
- Graphs are **undirected**
- No self-loops or duplicate edges

---

## Dataset Categories

### 1. Sparse Graphs (`sparse/`)
- **Edge Ratio**: ~1.5-2.5× number of vertices
- **Characteristics**: Many articulation points, many bridges
- **Files**: `sparse_01.txt` to `sparse_10.txt`
- **Use Case**: Testing algorithms on graphs with low connectivity

| File | Vertices | Edges | Description |
|------|----------|-------|-------------|
| sparse_01 | 10 | 12 | Small sparse graph |
| sparse_02 | 20 | 25 | Medium sparse graph with articulation points |
| sparse_03 | 30 | 40 | Sparse graph with multiple components |
| sparse_04 | 50 | 65 | Larger sparse graph |
| sparse_05 | 15 | 18 | Sparse graph - mostly linear |
| sparse_06 | 25 | 35 | Sparse graph with bridges |
| sparse_07 | 40 | 55 | Sparse graph - scattered connections |
| sparse_08 | 35 | 50 | Sparse graph with isolated biconnected components |
| sparse_09 | 60 | 80 | Large sparse graph |
| sparse_10 | 45 | 60 | Sparse graph with articulation point chains |

### 2. Dense Graphs (`dense/`)
- **Edge Ratio**: >50% of maximum possible edges
- **Characteristics**: Fewer articulation points, larger biconnected components
- **Files**: `dense_01.txt` to `dense_10.txt`
- **Use Case**: Testing algorithms on highly connected graphs

| File | Vertices | Approx Edges | Density |
|------|----------|--------------|---------|
| dense_01 | 10 | 31 | 70% |
| dense_02 | 15 | 68 | 65% |
| dense_03 | 12 | 52 | 80% |
| dense_04 | 20 | 114 | 60% |
| dense_05 | 8 | 23 | 85% |
| dense_06 | 18 | 107 | 70% |
| dense_07 | 14 | 68 | 75% |
| dense_08 | 16 | 81 | 68% |
| dense_09 | 22 | 142 | 62% |
| dense_10 | 25 | 165 | 55% |

### 3. Small Graphs (`small/`)
- **Vertices**: ≤15
- **Characteristics**: Hand-crafted cases for verification
- **Files**: `small_01.txt` to `small_10.txt`
- **Use Case**: Manual verification, debugging, edge cases

**Notable Test Cases:**
- **small_01**: Triangle path - 2 articulation points
- **small_02**: Square - biconnected
- **small_03**: Linear chain - many articulation points
- **small_04**: Triangle with tail
- **small_05**: Triangle with branch
- **small_06**: Pentagon with diagonals
- **small_07**: Two separate squares (disconnected)
- **small_08**: Hexagon with chords
- **small_09**: Simple path - all articulation points
- **small_10**: Four triangles - disconnected

### 4. Large Graphs (`large/`)
- **Vertices**: ≥100
- **Characteristics**: Performance testing, scalability
- **Files**: `large_01.txt` to `large_10.txt`
- **Use Case**: Stress testing, performance benchmarking

| File | Vertices | Edges | Type |
|------|----------|-------|------|
| large_01 | 100 | 150 | Sparse |
| large_02 | 200 | 300 | Sparse |
| large_03 | 150 | 400 | Medium |
| large_04 | 300 | 500 | Sparse |
| large_05 | 120 | 350 | Medium-sparse |
| large_06 | 250 | 600 | Dense |
| large_07 | 180 | 270 | Sparse |
| large_08 | 400 | 700 | Medium |
| large_09 | 500 | 800 | Sparse |
| large_10 | 350 | 1000 | Dense |

### 5. Tree-like Graphs (`tree_like/`)
- **Characteristics**: Trees or graphs with minimal cycles
- **Files**: `tree_01.txt` to `tree_10.txt`
- **Use Case**: Testing algorithms on acyclic/near-acyclic structures

**Test Cases:**
- **tree_01**: Perfect binary tree (15 vertices)
- **tree_02**: Linear path - maximum articulation points (20 vertices)
- **tree_03**: Star graph - center is articulation point (25 vertices)
- **tree_04**: Cycle graph (30 vertices)
- **tree_05**: Ternary tree (31 vertices)
- **tree_06**: Star with branches (40 vertices)
- **tree_07**: Random tree (35 vertices)
- **tree_08**: Caterpillar tree (28 vertices)
- **tree_09**: Tree with two cycles (25 vertices)
- **tree_10**: Tree-like with few cycles (50 vertices)

### 6. Highly Connected Graphs (`highly_connected/`)
- **Characteristics**: Multiple redundant paths, high connectivity
- **Files**: `highly_connected_01.txt` to `highly_connected_10.txt`
- **Use Case**: Testing on graphs with few/no articulation points

**Special Graphs:**
- **highly_connected_01**: Complete graph K5
- **highly_connected_02**: Complete graph K7
- **highly_connected_03**: Two complete subgraphs connected by bridge
- **highly_connected_04**: 5×5 grid graph
- **highly_connected_05**: Wheel graph W11
- **highly_connected_06**: Complete bipartite K3,4
- **highly_connected_07**: Petersen graph
- **highly_connected_08**: Dense random graph (20 vertices)
- **highly_connected_09**: Chain of triangles
- **highly_connected_10**: Three dense components connected

### 7. Real World Graphs (`real_world/`)
- **Purpose**: Add your own real-world network datasets
- **Examples**: Social networks, road networks, citation networks, etc.
- **Format**: Follow the same format as other datasets

---

## Using the Dataset

### Reading a Graph (Python)

```python
def read_graph(filename):
    """Read a graph from file"""
    with open(filename, 'r') as f:
        lines = f.readlines()
    
    # Skip comments
    idx = 0
    while lines[idx].startswith('#'):
        idx += 1
    
    # Read vertices and edges count
    n, m = map(int, lines[idx].split())
    
    # Read edges
    edges = []
    for i in range(idx + 1, idx + 1 + m):
        u, v = map(int, lines[i].split())
        edges.append((u, v))
    
    return n, edges

# Example usage
n, edges = read_graph('dataset/small/small_01.txt')
print(f"Vertices: {n}, Edges: {len(edges)}")
```

### Building Adjacency List

```python
def build_adj_list(n, edges):
    """Build adjacency list from edges"""
    adj = [[] for _ in range(n)]
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    return adj
```

---

## Testing Your Algorithms

### Suggested Test Strategy

1. **Start with Small Graphs**: Use `small/` directory for debugging
2. **Verify Edge Cases**: Test tree-like graphs for articulation points
3. **Test Connectivity**: Use highly_connected graphs
4. **Performance Testing**: Use large graphs
5. **Comprehensive Testing**: Run on all categories

### What to Verify

For biconnected components algorithms, verify:
- ✓ Correct identification of articulation points
- ✓ Correct identification of bridges
- ✓ Correct grouping of edges into biconnected components
- ✓ Handling of disconnected graphs
- ✓ Handling of isolated vertices
- ✓ Performance on large graphs

---

## Regenerating the Dataset

To regenerate the entire dataset:

```bash
python3 generate_dataset.py
```

The script uses `random.seed(42)` for reproducibility, so you'll get the same graphs each time.

---

## Expected Properties

### Sparse Graphs
- Many articulation points
- Many bridges
- Multiple small biconnected components

### Dense Graphs
- Few articulation points
- Few/no bridges
- Large biconnected components

### Tree-like Graphs
- Almost all edges are bridges
- Almost all internal vertices are articulation points
- Each edge forms its own biconnected component

### Highly Connected Graphs
- Few/no articulation points
- No bridges (except for specific test cases)
- One or few large biconnected components

---

## Adding Real-World Graphs

To add your own graphs to `real_world/`:

1. Convert your graph to the format:
   ```
   # Description
   num_vertices num_edges
   u1 v1
   u2 v2
   ...
   ```

2. Ensure vertices are 0-indexed

3. Place the file in `dataset/real_world/`

**Suggested Real-World Datasets:**
- Karate Club Network
- Dolphins Social Network
- Les Misérables Character Network
- Email Networks
- Collaboration Networks
- Road Networks

---

## Statistics Summary

| Category | Files | Total Vertices | Total Edges | Avg V/file | Avg E/file |
|----------|-------|----------------|-------------|------------|------------|
| Sparse | 10 | 330 | 450 | 33 | 45 |
| Dense | 10 | 155 | ~900 | 15.5 | ~90 |
| Small | 10 | 73 | 90 | 7.3 | 9 |
| Large | 10 | 2,450 | 4,870 | 245 | 487 |
| Tree-like | 10 | 319 | ~318 | 31.9 | ~31.8 |
| Highly Connected | 10 | 152 | ~600 | 15.2 | ~60 |
| **Total** | **60** | **~3,479** | **~7,228** | - | - |

---

## License

This dataset is generated for academic purposes. Feel free to use and modify for your project.

---

## Contact

For issues or questions about the dataset, please refer to the project documentation.
