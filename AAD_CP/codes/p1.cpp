#include <iostream>
#include <vector>
#include <stack>
#include <algorithm>
#include <set>
#include <sstream>
#include <string>

using namespace std;

// --- Global Variables (replaces class members) ---
int V; // Number of vertices
vector<vector<int>> adj; // Adjacency list

// Stores the edges currently on the stack
stack<pair<int, int>> edgeStack;

// --- DFS discovery arrays ---
vector<int> disc, low, parent;
vector<bool> visited;

// discoveryTime: A counter for discovery time
// bccCount: A counter for the number of BCCs found
int discoveryTime, bccCount; 

// --- BCC Storage ---
set<int> articulationPoints;
vector<vector<pair<int, int>>> bccList;


// --- Standalone Functions ---

/**
 * @brief The recursive DFS utility for finding BCCs
 * @param u The current vertex being visited
 */
void dfsBCC(int u) {
    // Initialize discovery time and low-link value for u
    disc[u] = low[u] = ++discoveryTime; 
    visited[u] = true;
    int children = 0; // Count of children in the DFS tree

    for (int v : adj[u]) {
        // Only push edge once: when we discover it (going from lower disc to higher disc)
        if (!visited[v]) {
            edgeStack.push({u, v});
        }
        else if (v != parent[u] && disc[v] < disc[u]) {
            // Back edge (and we only push it once, from higher to lower disc time)
            edgeStack.push({u, v});
        }

        if (!visited[v]) {
            children++;
            parent[v] = u;
            dfsBCC(v);

            low[u] = min(low[u], low[v]);

            if (low[v] >= disc[u]) {
                if (parent[u] != -1) { // Not the root
                    articulationPoints.insert(u);
                }
                
                bccCount++;
                vector<pair<int, int>> currentBCC;
                pair<int, int> edge;
                do {
                    edge = edgeStack.top();
                    edgeStack.pop();
                    currentBCC.push_back(edge);
                } while (edge.first != u || edge.second != v);
                bccList.push_back(currentBCC);
            }
        } 
        else if (v != parent[u]) {
            low[u] = min(low[u], disc[v]);
        }
    }

    if (parent[u] == -1 && children > 1) {
        articulationPoints.insert(u);
    }
}

/**
 * @brief Function to add an undirected edge
 */
void addEdge(int u, int v) {
    adj[u].push_back(v);
    adj[v].push_back(u);
}

/**
 * @brief Main function to find and print all BCCs
 */
void findBCCs() {
    for (int i = 0; i < V; ++i) {
        if (!visited[i]) {
            dfsBCC(i);
            if (!edgeStack.empty()) {
                bccCount++;
                vector<pair<int, int>> currentBCC;
                while (!edgeStack.empty()) {
                    currentBCC.push_back(edgeStack.top());
                    edgeStack.pop();
                }
                bccList.push_back(currentBCC);
            }
        }
    }
    
    // --- Print the results ---
    cout << "\n--- Tarjan's Algorithm Results ---" << endl;
    cout << "Total Biconnected Components (BCCs) found: " << bccCount << endl;
    for (int i = 0; i < bccList.size(); ++i) {
        cout << "BCC " << (i + 1);
        
        // Determine type: Bridge (1 edge) or Triangle/Component (multiple edges)
        if (bccList[i].size() == 1) {
            cout << " (Bridge): ";
        } else {
            cout << " (Triangle " << (i + 1) << "): ";
        }
        
        // Use set to avoid duplicate edges
        set<pair<int, int>> uniqueEdges;
        for (const auto& edge : bccList[i]) {
            int u = edge.first;
            int v = edge.second;
            uniqueEdges.insert({min(u, v), max(u, v)});
        }
        
        cout << "{";
        bool first = true;
        for (const auto& edge : uniqueEdges) {
            if (!first) cout << ", ";
            cout << "(" << edge.first << ", " << edge.second << ")";
            first = false;
        }
        cout << "}" << endl;
    }

    cout << "\nArticulation Points (Cut Vertices): ";
    if (articulationPoints.empty()) {
        cout << "None";
    } else {
        for (int ap : articulationPoints) {
            cout << ap << " ";
        }
    }
    cout << endl;
}

// --- Main execution ---
int main() {
    int E; // Number of edges
    
    // Skip comment lines (lines starting with #)
    string line;
    while (getline(cin, line)) {
        if (line.empty() || line[0] == '#') continue;
        stringstream ss(line);
        if (ss >> V >> E) break;
    }

    // --- Initialization (replaces constructor) ---
    discoveryTime = 0;
    bccCount = 0;
    adj.resize(V);
    disc.resize(V, 0);
    low.resize(V, 0);
    parent.resize(V, -1);
    visited.resize(V, false);
    // ---------------------------------------------

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

    // Run the algorithm
    findBCCs();

    return 0;
}