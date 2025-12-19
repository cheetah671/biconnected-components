/*
 * Slota-Madduri Parallel BCC Algorithm
 * Based on Tarjan's algorithm with OpenMP parallelization
 * Parallelizes processing of disconnected components
 */

#include <iostream>
#include <vector>
#include <stack>
#include <algorithm>
#include <set>
#include <sstream>
#include <string>
#include <chrono>
#include <omp.h>

using namespace std;

// Global variables
int V; // Number of vertices
vector<vector<int>> adj; // Adjacency list

// Per-component DFS variables (thread-local)
struct ComponentData {
    stack<pair<int, int>> edgeStack;
    vector<int> disc, low, parent;
    vector<bool> visited;
    int discoveryTime;
    int bccCount;
    set<int> articulationPoints;
    vector<vector<pair<int, int>>> bccList;
    
    ComponentData(int V) : disc(V), low(V), parent(V, -1), visited(V, false), 
                           discoveryTime(0), bccCount(0) {}
};

// Global results
set<int> allArticulationPoints;
vector<vector<pair<int, int>>> allBCCs;
omp_lock_t results_lock;

/**
 * DFS for finding BCCs (Tarjan's algorithm)
 */
void dfsBCC(int u, ComponentData& data) {
    data.disc[u] = data.low[u] = ++data.discoveryTime;
    data.visited[u] = true;
    int children = 0;

    for (int v : adj[u]) {
        // Push edge to stack
        if (!data.visited[v]) {
            data.edgeStack.push({u, v});
        }
        else if (v != data.parent[u] && data.disc[v] < data.disc[u]) {
            data.edgeStack.push({u, v});
        }

        if (!data.visited[v]) {
            children++;
            data.parent[v] = u;
            dfsBCC(v, data);

            data.low[u] = min(data.low[u], data.low[v]);

            // Check if u is articulation point and extract BCC
            if (data.low[v] >= data.disc[u]) {
                if (data.parent[u] != -1) {
                    data.articulationPoints.insert(u);
                }
                
                data.bccCount++;
                vector<pair<int, int>> currentBCC;
                pair<int, int> edge;
                do {
                    edge = data.edgeStack.top();
                    data.edgeStack.pop();
                    currentBCC.push_back(edge);
                } while (edge.first != u || edge.second != v);
                data.bccList.push_back(currentBCC);
            }
        } 
        else if (v != data.parent[u]) {
            data.low[u] = min(data.low[u], data.disc[v]);
        }
    }

    // Root articulation point check
    if (data.parent[u] == -1 && children > 1) {
        data.articulationPoints.insert(u);
    }
}

/**
 * Find connected components
 */
vector<vector<int>> findConnectedComponents() {
    vector<vector<int>> components;
    vector<bool> compVisited(V, false);
    
    for (int i = 0; i < V; i++) {
        if (!compVisited[i]) {
            vector<int> component;
            vector<int> stack;
            stack.push_back(i);
            compVisited[i] = true;
            
            while (!stack.empty()) {
                int u = stack.back();
                stack.pop_back();
                component.push_back(u);
                
                for (int v : adj[u]) {
                    if (!compVisited[v]) {
                        compVisited[v] = true;
                        stack.push_back(v);
                    }
                }
            }
            
            components.push_back(component);
        }
    }
    
    return components;
}

/**
 * Process a single connected component
 */
void processComponent(const vector<int>& component) {
    ComponentData data(V);
    
    // Find BCCs in this component
    for (int vertex : component) {
        if (!data.visited[vertex]) {
            dfsBCC(vertex, data);
            
            // Handle remaining edges
            if (!data.edgeStack.empty()) {
                vector<pair<int, int>> bcc;
                while (!data.edgeStack.empty()) {
                    bcc.push_back(data.edgeStack.top());
                    data.edgeStack.pop();
                }
                data.bccList.push_back(bcc);
            }
        }
    }
    
    // Merge results into global data (thread-safe)
    omp_set_lock(&results_lock);
    allBCCs.insert(allBCCs.end(), data.bccList.begin(), data.bccList.end());
    allArticulationPoints.insert(data.articulationPoints.begin(), 
                                  data.articulationPoints.end());
    omp_unset_lock(&results_lock);
}

/**
 * Main function to find BCCs with parallelization
 */
void findBCCs() {
    // Find connected components
    vector<vector<int>> components = findConnectedComponents();
    
    // Process components in parallel (Slota-Madduri parallelization strategy)
    // Each component can be processed independently
    #pragma omp parallel for schedule(dynamic) if(components.size() > 1)
    for (size_t i = 0; i < components.size(); i++) {
        processComponent(components[i]);
    }
}

void addEdge(int u, int v) {
    adj[u].push_back(v);
    adj[v].push_back(u);
}

int main() {
    // Initialize OpenMP
    omp_init_lock(&results_lock);
    int num_threads = omp_get_max_threads();
    omp_set_num_threads(num_threads);
    
    // Read number of vertices and edges
    int E;
    string line;
    
    // Skip comment lines and read V, E
    while (getline(cin, line)) {
        if (line.empty() || line[0] == '#') continue;
        stringstream ss(line);
        if (ss >> V >> E) break;
    }
    
    adj.resize(V);
    
    // Read edges, skipping comments
    for (int i = 0; i < E; ++i) {
        int u, v;
        while (getline(cin, line)) {
            if (line.empty() || line[0] == '#') continue;
            stringstream ss(line);
            if (ss >> u >> v) {
                addEdge(u, v);
                break;
            }
        }
    }
    
    // Find BCCs
    auto start = chrono::high_resolution_clock::now();
    findBCCs();
    auto end = chrono::high_resolution_clock::now();
    double elapsed = chrono::duration<double>(end - start).count();
    
    // Print results
    cout << "\n--- Slota-Madduri Parallel Algorithm Results (using " << num_threads << " threads) ---" << endl;
    cout << "Execution Time: " << elapsed << " seconds" << endl;
    cout << "Total Biconnected Components (BCCs) found: " << allBCCs.size() << endl;
    
    int idx = 1;
    for (const auto& bcc : allBCCs) {
        cout << "BCC " << idx << " (Triangle " << idx << "): {";
        for (size_t i = 0; i < bcc.size(); ++i) {
            if (i > 0) cout << ", ";
            cout << "(" << bcc[i].first << ", " << bcc[i].second << ")";
        }
        cout << "}" << endl;
        idx++;
    }
    
    cout << "\nArticulation Points found: " << allArticulationPoints.size() << endl;
    if (!allArticulationPoints.empty()) {
        cout << "Points: {";
        bool first = true;
        for (int ap : allArticulationPoints) {
            if (!first) cout << ", ";
            cout << ap;
            first = false;
        }
        cout << "}" << endl;
    }
    
    // Cleanup
    omp_destroy_lock(&results_lock);
    
    return 0;
}

