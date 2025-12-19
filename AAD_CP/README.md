# Biconnected Components (BCC) - Algorithm Analysis Project

A comprehensive analysis and comparison of five algorithms for finding Biconnected Components in undirected graphs, including performance benchmarking, cache analysis, and visualization.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Algorithms Implemented](#algorithms-implemented)
- [Project Structure](#project-structure)
- [Installation & Setup](#installation--setup)
- [Quick Start](#quick-start)
- [Detailed Usage Guide](#detailed-usage-guide)
- [Dataset Information](#dataset-information)
- [Performance Analysis](#performance-analysis)
- [Generated Outputs](#generated-outputs)
- [Visualization](#visualization)
- [Technical Details](#technical-details)
- [Results Summary](#results-summary)

---

## 🎯 Overview

This project implements and compares five different algorithms for finding Biconnected Components (BCCs) and Articulation Points in undirected graphs. The analysis includes:

- **Execution time comparison** across 82 test cases
- **Memory usage analysis** using Valgrind
- **Cache performance metrics** using Cachegrind
- **Hardware performance counters** using perf
- **Comprehensive visualizations** comparing all algorithms
- **Parallel performance analysis** for multi-threaded algorithms

---

## 🔬 Algorithms Implemented

### 1. **p1 - Tarjan's Algorithm** (Sequential)
- **File**: `codes/p1.cpp`
- **Description**: Classic DFS-based algorithm using discovery times and low values
- **Time Complexity**: O(V + E)
- **Space Complexity**: O(V + E)
- **Best For**: General-purpose BCC detection, reliable baseline

### 2. **p2 - Tarjan-Vishkin Algorithm** (Parallel-inspired)
- **File**: `codes/p2.cpp`
- **Description**: Tree-based parallel algorithm adapted for sequential execution
- **Time Complexity**: O(V + E)
- **Space Complexity**: O(V + E)
- **Best For**: Graphs with tree-like structure

### 3. **p3 - Slota-Madduri Parallel Algorithm** ⚡
- **File**: `codes/p3.cpp`
- **Description**: OpenMP-based parallel algorithm processing disconnected components concurrently
- **Time Complexity**: O(V + E)
- **Space Complexity**: O(V + E)
- **Parallelization**: Uses OpenMP for multi-core processing
- **Best For**: Large graphs with multiple disconnected components
- **Threads**: Configurable via `OMP_NUM_THREADS` environment variable

### 4. **p4 - Naive Algorithm** (Brute Force)
- **File**: `codes/p4.cpp`
- **Description**: Edge removal approach checking connectivity after each edge removal
- **Time Complexity**: O(E × (V + E))
- **Space Complexity**: O(V + E)
- **Best For**: Small graphs, educational comparison baseline

### 5. **p5 - Chain Decomposition Algorithm**
- **File**: `codes/p5.cpp`
- **Description**: Efficient algorithm using chain decomposition techniques
- **Time Complexity**: O(V + E)
- **Space Complexity**: O(V)
- **Best For**: Most efficient on dense graphs, lowest instruction count

---

## 📁 Project Structure

```
AAD_CP/
├── codes/                          # Algorithm implementations
│   ├── p1.cpp                      # Tarjan's Algorithm
│   ├── p2.cpp                      # Tarjan-Vishkin
│   ├── p3.cpp                      # Slota-Madduri Parallel
│   ├── p4.cpp                      # Naive Algorithm
│   └── p5.cpp                      # Chain Decomposition
│
├── dataset/                        # Test datasets (82 files)
│   ├── dense/                      # Dense graphs (10 files)
│   ├── sparse/                     # Sparse graphs (20 files)
│   ├── large/                      # Large graphs (10 files)
│   ├── small/                      # Small graphs (10 files)
│   ├── tree_like/                  # Tree-like graphs (10 files)
│   ├── highly_connected/           # Highly connected graphs (10 files)
│   └── real_world/                 # Real-world datasets (12 files)
│
├── outputs/                        # Algorithm outputs (auto-generated)
│   ├── p1/                         # p1 outputs by category
│   │   ├── dense/
│   │   ├── sparse/
│   │   └── ...
│   ├── p2/
│   ├── p3/
│   ├── p5/
│   ├── p1_results.csv              # p1 timing results
│   ├── p2_results.csv              # p2 timing results
│   ├── p3_results.csv              # p3 timing results
│   └── p5_results.csv              # p5 timing results
│
├── graphs/                         # Generated visualizations
│   ├── comparison_overall.png      # Overall performance comparison
│   ├── comparison_dense.png        # Category-specific comparisons
│   ├── comparison_time_vs_size.png # Time vs graph size
│   ├── cache_instructions.png      # Cache instruction comparison
│   ├── cache_l1_misses.png         # L1 cache miss comparison
│   ├── memory_overall.png          # Memory usage comparison
│   └── ...
│
├── scripts/                        # Analysis and visualization scripts
│   ├── create_performance_graphs.py    # Generate performance graphs
│   ├── create_memory_cache_graphs.py   # Generate cache/memory graphs
│   ├── parse_cachegrind.py             # Parse cachegrind output
│   ├── visualize_all.py                # Generate input dataset graphs
│   └── run_cachegrind_analysis.sh      # Run cachegrind on all algorithms
│
├── run_p1_only.py                  # Run p1 on all test cases
├── run_p2_only.py                  # Run p2 on all test cases
├── run_p3_only.py                  # Run p3 on all test cases
├── run_p5_only.py                  # Run p5 on all test cases
│
├── performance_metrics.txt         # Detailed performance metrics
├── cache_analysis_report.txt       # Cache performance report
├── cachegrind_p1.out              # Cachegrind output files
├── cachegrind_p2.out
├── cachegrind_p3.out
├── cachegrind_p4.out
└── cachegrind_p5.out
```

---

## 🚀 Installation & Setup

### Prerequisites

```bash
# Required packages (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install -y \
    g++ \
    valgrind \
    python3 \
    python3-pip \
    libomp-dev

# Python dependencies
pip3 install pandas matplotlib numpy
```

### Compilation

All algorithms are automatically compiled by the run scripts, but you can manually compile:

```bash
cd codes/

# Compile individual algorithms
g++ -std=c++17 -O2 -o p1 p1.cpp
g++ -std=c++17 -O2 -o p2 p2.cpp
g++ -std=c++17 -O2 -fopenmp -o p3 p3.cpp  # Requires OpenMP
g++ -std=c++17 -O2 -o p4 p4.cpp
g++ -std=c++17 -O2 -o p5 p5.cpp
```

---

## ⚡ Quick Start

### Run Complete Analysis (All Algorithms)

```bash
# 1. Run all algorithms on all test cases (takes ~5-10 minutes)
python run_p1_only.py
python run_p2_only.py
python run_p3_only.py
python run_p5_only.py

# 2. Run cache analysis (takes ~2-3 minutes)
cd scripts/
bash run_cachegrind_analysis.sh
python parse_cachegrind.py

# 3. Generate all visualizations
python create_performance_graphs.py
python create_memory_cache_graphs.py
python visualize_all.py

# 4. View results
cd ../graphs/
# Open PNG files to see comparison graphs
```

---

## 📖 Detailed Usage Guide

### 1. Running Individual Algorithms

Each algorithm can be run on all 82 test cases using dedicated Python scripts:

#### **Run p1 (Tarjan's Algorithm)**
```bash
python run_p1_only.py
```
**Output:**
- Creates `outputs/p1/` directory with subdirectories for each category
- Each test output saved in corresponding category folder
- Generates `outputs/p1_results.csv` with timing data
- Console shows progress: `[n/82] Processing category/file ... ✓ 0.003s`

**CSV Format:**
```
algorithm,category,file,n,m,time,exitcode,output
p1,dense,dense/dense_01.txt,10,31,0.001234,0,/path/to/output
```

#### **Run p2 (Tarjan-Vishkin)**
```bash
python run_p2_only.py
```
**Output:** Same structure as p1, outputs in `outputs/p2/`

#### **Run p3 (Slota-Madduri Parallel)** ⚡
```bash
# Run with default number of threads (system max)
python run_p3_only.py

# Run with specific number of threads
OMP_NUM_THREADS=4 python run_p3_only.py
OMP_NUM_THREADS=8 python run_p3_only.py
OMP_NUM_THREADS=16 python run_p3_only.py
```

**Testing Thread Performance:**
```bash
# Test single dataset with different thread counts
cd codes/
for threads in 1 4 8 16; do
    echo "=== $threads threads ==="
    OMP_NUM_THREADS=$threads ./p3 < ../dataset/large/large_01.txt | grep "Execution Time"
done
```

**Output:** Same structure, outputs in `outputs/p3/`

#### **Run p5 (Chain Decomposition)**
```bash
python run_p5_only.py
```
**Output:** Same structure, outputs in `outputs/p5/`

### 2. Running Single Test Case

```bash
cd codes/

# Run on specific test file
./p1 < ../dataset/dense/dense_08.txt

# Run on custom input
./p1 < custom_graph.txt

# Redirect output to file
./p1 < ../dataset/sparse/sparse_01.txt > output.txt
```

**Input Format:**
```
# Comments (optional, lines starting with #)
<num_vertices> <num_edges>
<vertex_u> <vertex_v>
<vertex_u> <vertex_v>
...
```

**Example:**
```
# Small triangle graph
3 3
0 1
1 2
2 0
```

### 3. Cache Performance Analysis

#### **Run Cachegrind Analysis**
```bash
cd scripts/
bash run_cachegrind_analysis.sh
```

This script:
1. Runs `valgrind --tool=cachegrind` on each algorithm
2. Uses `dense_08.txt` as the benchmark test case
3. Generates `cachegrind_p*.out` files in project root
4. Takes ~2-3 minutes to complete

**Manual Cachegrind Run:**
```bash
cd codes/

# Run cachegrind on specific algorithm
valgrind --tool=cachegrind \
         --branch-sim=yes \
         --cache-sim=yes \
         --cachegrind-out-file=../cachegrind_p1.out \
         ./p1 < ../dataset/dense/dense_08.txt
```

#### **Parse Cachegrind Results**
```bash
cd scripts/
python parse_cachegrind.py
```

**Output:**
- Generates `cache_analysis_report.txt` in project root
- Shows metrics for all algorithms:
  - Instructions executed (Ir)
  - L1 instruction cache misses (I1mr)
  - L1 data cache misses (D1mr)
  - Branch mispredictions (Bcm)
  - Miss rates and comparisons

**Sample Output:**
```
Algorithm: p1 (Tarjan's Algorithm)
Instructions (Ir):                    23,090,194
L1 I-cache misses:                        2,882
L1 D-cache misses:                       62,195
Branch mispredictions:                   64,650 (3.85%)
```

### 4. Memory Usage Analysis

Memory metrics are collected during algorithm execution using `/usr/bin/time -v`:

```bash
# Automatically collected when running via run_p*_only.py scripts
python run_p1_only.py  # Memory data included in outputs
```

**Manual Memory Analysis:**
```bash
/usr/bin/time -v ./codes/p1 < dataset/large/large_01.txt 2>&1 | grep "Maximum resident"
```

---

## 📊 Performance Analysis

### Generating Performance Comparison Graphs

#### **Create Performance Graphs**
```bash
cd scripts/
python create_performance_graphs.py
```

**Generated Graphs:**
1. **Category-wise comparisons:**
   - `comparison_dense.png` - Performance on dense graphs
   - `comparison_sparse.png` - Performance on sparse graphs
   - `comparison_large.png` - Performance on large graphs
   - `comparison_small.png` - Performance on small graphs
   - `comparison_tree_like.png` - Performance on tree-like graphs
   - `comparison_highly_connected.png` - Performance on highly connected graphs
   - `comparison_real_world.png` - Performance on real-world datasets

2. **Overall comparisons:**
   - `comparison_overall.png` - Average performance across all categories
   - `comparison_time_vs_size.png` - Scatter plot of execution time vs graph size

**Graph Features:**
- Bar charts with error bars (standard deviation)
- Color-coded algorithms:
  - 🔵 Blue: p1 (Tarjan's)
  - 🟠 Orange: p2 (Tarjan-Vishkin)
  - 🟣 Purple: p3 (Slota-Madduri)
  - 🔴 Red: p4 (Naive)
  - 🟢 Green: p5 (Chain Decomposition)
- Execution time labels on bars
- Sorted by performance (fastest to slowest)

#### **Create Cache & Memory Graphs**
```bash
cd scripts/
python create_memory_cache_graphs.py
```

**Generated Graphs:**
1. **Cache Performance:**
   - `cache_instructions.png` - Instruction count comparison
   - `cache_l1_misses.png` - L1 cache miss comparison
   - `cache_branch_mispredicts.png` - Branch misprediction comparison
   - `cache_combined_normalized.png` - Normalized combined metrics

2. **Memory Usage:**
   - `memory_overall.png` - Overall memory usage comparison
   - `memory_large.png` - Memory usage on large graphs

**Console Output:**
```
Memory Usage and Cache Performance Graph Generator
======================================================================
✓ Parsed memory data: 12 entries across 4 algorithms

Generating memory comparison graphs...
  ✓ large                -> memory_large.png
  ✓ Overall memory comparison -> memory_overall.png

Generating cache comparison graphs...
  ✓ L1 cache misses -> cache_l1_misses.png
  ✓ Branch mispredicts -> cache_branch_mispredicts.png
  ✓ Instructions executed -> cache_instructions.png
```

---

## 📈 Visualization

### Visualize Input Datasets

Generate visual representations of input graphs:

```bash
cd scripts/
python visualize_all.py
```

**Output:**
- Creates subdirectories in `graphs/` for each category
- Generates PNG visualizations for each dataset
- Shows graph structure with nodes and edges
- Highlights biconnected components in different colors

**Generated Structure:**
```
graphs/
├── dense/
│   ├── dense_01.png
│   ├── dense_02.png
│   └── ...
├── sparse/
├── large/
└── ...
```

**Visualization Features:**
- Color-coded biconnected components
- Node labels showing vertex IDs
- Edge visualization
- Spring layout for better readability
- Legend showing component colors

---

## 📦 Dataset Information

### Dataset Categories (82 Total Files)

#### 1. **Dense Graphs** (10 files)
- **Location:** `dataset/dense/`
- **Characteristics:** High edge-to-vertex ratio (≥70% of maximum possible edges)
- **Files:** `dense_01.txt` to `dense_10.txt`
- **Vertices:** 8-25
- **Edges:** 23-165
- **Best Algorithm:** p5 (Chain Decomposition)

#### 2. **Sparse Graphs** (20 files)
- **Location:** `dataset/sparse/`
- **Characteristics:** Low edge-to-vertex ratio (~1-3 edges per vertex)
- **Files:** `sparse_01.txt` to `sparse_20.txt`
- **Vertices:** 15-50
- **Edges:** 20-75
- **Best Algorithm:** p1 or p5

#### 3. **Large Graphs** (10 files)
- **Location:** `dataset/large/`
- **Characteristics:** High vertex count (500-1000 vertices)
- **Files:** `large_01.txt` to `large_10.txt`
- **Vertices:** 500-1000
- **Edges:** 700-1500
- **Best Algorithm:** p5 or p3 (parallel)

#### 4. **Small Graphs** (10 files)
- **Location:** `dataset/small/`
- **Characteristics:** Low vertex count (5-15 vertices)
- **Files:** `small_01.txt` to `small_10.txt`
- **Vertices:** 5-15
- **Edges:** 8-35
- **Best Algorithm:** Any (negligible differences)

#### 5. **Tree-like Graphs** (10 files)
- **Location:** `dataset/tree_like/`
- **Characteristics:** Minimal cycles, tree-like structure
- **Files:** `tree_like_01.txt` to `tree_like_10.txt`
- **Vertices:** 20-100
- **Edges:** ~V-1 to V+5
- **Best Algorithm:** p2 (Tarjan-Vishkin) or p5

#### 6. **Highly Connected Graphs** (10 files)
- **Location:** `dataset/highly_connected/`
- **Characteristics:** Near-complete graphs, very dense
- **Files:** `highly_connected_01.txt` to `highly_connected_10.txt`
- **Vertices:** 5-25
- **Edges:** 10-120
- **Best Algorithm:** p5

#### 7. **Real-world Datasets** (12 files)
- **Location:** `dataset/real_world/`
- **Characteristics:** Social networks, collaboration networks
- **Files:**
  - `facebook.txt` - Facebook social network
  - `eredos.txt` - Erdős collaboration network
  - `gemsec_Deezer_hr.txt` - Deezer social network (Croatia)
  - `gemsec_Deezer_hu.txt` - Deezer social network (Hungary)
  - `gemsec_Deezer_ro.txt` - Deezer social network (Romania)
  - `gemsec_facebook_artist.txt` - Facebook artist pages
  - `gemsec_facebook_athletes.txt` - Facebook athlete pages
  - `gemsec_facebook_company.txt` - Facebook company pages
  - `gemsec_facebook_government.txt` - Facebook government pages
- **Vertices:** 1,000-50,000
- **Edges:** 5,000-200,000
- **Best Algorithm:** p3 (parallel) or p5

---

## 📋 Generated Outputs

### 1. CSV Results Files

**Location:** `outputs/`

**Files:**
- `p1_results.csv` - Tarjan's algorithm results
- `p2_results.csv` - Tarjan-Vishkin results
- `p3_results.csv` - Slota-Madduri results
- `p5_results.csv` - Chain Decomposition results

**CSV Schema:**
```csv
algorithm,category,file,n,m,time,exitcode,output
p1,dense,dense/dense_01.txt,10,31,0.001234,0,/path/to/output.txt
```

**Columns:**
- `algorithm`: Algorithm identifier (p1/p2/p3/p5)
- `category`: Dataset category (dense/sparse/large/small/tree_like/highly_connected/real_world)
- `file`: Relative path to test file
- `n`: Number of vertices
- `m`: Number of edges
- `time`: Execution time in seconds
- `exitcode`: Process exit code (0 = success)
- `output`: Path to detailed output file

### 2. Algorithm Output Files

**Location:** `outputs/p*/category/`

**Format:**
```
--- [Algorithm Name] Results ---
Total Biconnected Components (BCCs) found: X
BCC 1 (Triangle 1): {(u, v), (v, w), (w, u)}
BCC 2 (Bridge): {(a, b)}
...

Articulation Points (Cut Vertices): 0 3 5 7
```

### 3. Cache Analysis Report

**Location:** `cache_analysis_report.txt`

**Contents:**
- Detailed metrics for each algorithm
- Instruction counts (Ir)
- Cache miss statistics (L1, LL)
- Branch prediction metrics
- Comparative rankings
- Performance insights

### 4. Performance Metrics

**Location:** `performance_metrics.txt`

**Contents:**
- Memory usage (kbytes, peak resident set size)
- CPU time (user + system)
- Page faults
- Context switches
- Collected using `/usr/bin/time -v`

---

## 🔧 Technical Details

### Algorithm Complexity Comparison

| Algorithm | Time Complexity | Space Complexity | Parallelizable | Best Use Case |
|-----------|----------------|------------------|----------------|---------------|
| p1 (Tarjan's) | O(V + E) | O(V + E) | No | General purpose |
| p2 (Tarjan-Vishkin) | O(V + E) | O(V + E) | Yes (sequential impl.) | Tree-like graphs |
| p3 (Slota-Madduri) | O(V + E) | O(V + E) | **Yes (OpenMP)** | Large graphs, multiple components |
| p4 (Naive) | O(E × (V + E)) | O(V + E) | No | Educational only |
| p5 (Chain Decomp.) | O(V + E) | O(V) | No | Dense graphs |

### OpenMP Configuration (p3)

**Environment Variables:**
```bash
# Set number of threads
export OMP_NUM_THREADS=8

# Set thread affinity
export OMP_PROC_BIND=true

# Set scheduling policy
export OMP_SCHEDULE="dynamic"
```

**Testing Scalability:**
```bash
#!/bin/bash
# Test p3 with different thread counts
for threads in 1 2 4 8 16; do
    echo "Testing with $threads threads:"
    OMP_NUM_THREADS=$threads time ./codes/p3 < dataset/real_world/facebook.txt
    echo ""
done
```

### Cachegrind Metrics Explained

| Metric | Description | Lower is Better |
|--------|-------------|-----------------|
| **Ir** | Instructions executed | ✓ |
| **I1mr** | L1 instruction cache misses | ✓ |
| **ILmr** | Last-level instruction cache misses | ✓ |
| **Dr** | Data reads | ✓ |
| **D1mr** | L1 data read cache misses | ✓ |
| **DLmr** | Last-level data read cache misses | ✓ |
| **Dw** | Data writes | ✓ |
| **D1mw** | L1 data write cache misses | ✓ |
| **DLmw** | Last-level data write cache misses | ✓ |
| **Bc** | Conditional branches | ✓ |
| **Bcm** | Conditional branch mispredictions | ✓ |

---

## 📊 Results Summary

### Performance Rankings (Average across all datasets)

**Fastest (Lowest execution time):**
1. 🥇 **p5** (Chain Decomposition) - Most efficient overall
2. 🥈 **p1** (Tarjan's Algorithm) - Reliable baseline
3. 🥉 **p3** (Slota-Madduri) - Best for parallel workloads
4. **p2** (Tarjan-Vishkin) - Good for tree-like structures
5. **p4** (Naive) - Educational baseline only

**Most Efficient (Lowest instructions):**
1. 🥇 **p5** - ~14M instructions
2. 🥈 **p3** - ~2.5M instructions (with parallelization overhead)
3. 🥉 **p1** - ~23M instructions
4. **p2** - ~35M instructions
5. **p4** - ~113M instructions

**Best Cache Performance:**
1. 🥇 **p2** - Lowest L1 cache misses (~54K)
2. 🥈 **p3** - ~20K L1 misses
3. 🥉 **p1** - ~65K L1 misses
4. **p5** - ~110K L1 misses
5. **p4** - ~1.4M L1 misses

**Memory Efficiency:**
1. 🥇 **p4** - 3.6 MB (but slow)
2. 🥈 **p1** - 3.86 MB
3. 🥉 **p2** - 3.90 MB
4. **p5** - 6.08 MB

### Key Insights

✅ **p5 (Chain Decomposition)** is the winner for most use cases:
- Fastest execution time
- Lowest instruction count
- Efficient on dense graphs

✅ **p3 (Slota-Madduri)** excels with parallelization:
- Best for large graphs with multiple components
- Scales with thread count
- Ideal for multi-core systems

✅ **p1 (Tarjan's)** is the most reliable:
- Consistent performance
- Good all-around baseline
- Well-tested algorithm

❌ **p4 (Naive)** should not be used in production:
- 7.9x slower than p5
- Very high cache miss rate
- Only useful for educational purposes

---

## 🔗 Common Commands Cheat Sheet

```bash
# ======================
# COMPILATION
# ======================
cd codes/
g++ -std=c++17 -O2 -o p1 p1.cpp
g++ -std=c++17 -O2 -fopenmp -o p3 p3.cpp

# ======================
# RUN SINGLE TEST
# ======================
./codes/p1 < dataset/dense/dense_08.txt
OMP_NUM_THREADS=8 ./codes/p3 < dataset/large/large_01.txt

# ======================
# RUN ALL TESTS
# ======================
python run_p1_only.py
python run_p2_only.py
python run_p3_only.py
python run_p5_only.py

# ======================
# CACHE ANALYSIS
# ======================
cd scripts/
bash run_cachegrind_analysis.sh
python parse_cachegrind.py

# ======================
# GENERATE GRAPHS
# ======================
cd scripts/
python create_performance_graphs.py
python create_memory_cache_graphs.py
python visualize_all.py

# ======================
# VIEW RESULTS
# ======================
cat cache_analysis_report.txt
cat performance_metrics.txt
cat outputs/p1_results.csv
```

---

## 📝 Citation

If you use this project in your research, please cite:

```
Biconnected Components Algorithm Analysis
Advanced Algorithm Design Course Project
[Year]
```

---

## 👥 Contributors

- Implementation and analysis of all five BCC algorithms
- Comprehensive performance benchmarking framework
- Visualization and reporting tools

---

## 📄 License

This project is for educational purposes as part of the Advanced Algorithm Design course.

---

## 🐛 Troubleshooting

### Common Issues

**Issue:** `p3: command not found`
```bash
# Solution: Compile with OpenMP flag
cd codes/
g++ -std=c++17 -O2 -fopenmp -o p3 p3.cpp
```

**Issue:** `cachegrind: command not found`
```bash
# Solution: Install valgrind
sudo apt-get install valgrind
```

**Issue:** Python module not found
```bash
# Solution: Install dependencies
pip3 install pandas matplotlib numpy
```

**Issue:** Graphs not showing p3 data
```bash
# Solution: Run p3 and regenerate graphs
python run_p3_only.py
cd scripts/
python create_performance_graphs.py
```

**Issue:** No OpenMP support
```bash
# Solution: Install OpenMP development package
sudo apt-get install libomp-dev
```

---

## 📚 Additional Resources

- **Tarjan's Algorithm Paper**: Tarjan, R. E. (1972). "Depth-first search and linear graph algorithms"
- **OpenMP Documentation**: https://www.openmp.org/
- **Valgrind/Cachegrind**: https://valgrind.org/docs/manual/cg-manual.html
- **Graph Theory Basics**: Introduction to Graph Theory by Douglas B. West

---

**Last Updated:** December 2025
**Version:** 1.0
