#include <iostream>
#include <vector>
#include <stack>
#include <algorithm>
#include <set> // Using set to store BCCs and APs (for sorting and uniqueness)
#include <sstream>
#include <string>

using namespace std;

// Using 'int' for V, adjust if V is large
const int MAX_V = 100005; // Max vertices

vector<int> adj[MAX_V];
int disc[MAX_V]; // Discovery time
int low[MAX_V];  // Low-link value
int timer;
stack<pair<int, int>> edgeStack;

// --- Modified Data Structures ---
// Stores the biconnected components
vector<set<pair<int, int>>> bccs; 
// Stores the articulation points
set<int> articulationPoints; 
bool visited[MAX_V];

// Helper function to add an edge
void addEdge(int u, int v) {
    adj[u].push_back(v);
    adj[v].push_back(u);
}

/**
 * @brief The main DFS function for finding BCCs and Articulation Points.
 * @param u The current vertex being visited.
 * @param p The parent vertex in the DFS tree (-1 for root).
 */
void findBCC(int u, int p = -1) {
    visited[u] = true;
    disc[u] = low[u] = ++timer;
    int childCount = 0; // Track children for root AP check

    for (int v : adj[u]) {
        if (v == p) {
            continue; // Don't go back to the parent
        }

        if (visited[v]) {
            // This is a back-edge
            low[u] = min(low[u], disc[v]);
            // Push back-edges onto the stack only if v was visited before u
            if (disc[v] < disc[u]) {
                edgeStack.push({u, v});
            }
        } else {
            // This is a tree-edge (v is a child of u)
            childCount++;
            edgeStack.push({u, v});
            findBCC(v, u);

            // On callback, update low-link of u
            low[u] = min(low[u], low[v]);

            // --- Articulation Point Check ---
            // 1. Non-root case: if low[v] >= disc[u], u is an AP
            if (p != -1 && low[v] >= disc[u]) {
                articulationPoints.insert(u);
            }

            // --- BCC Pop Logic ---
            if (low[v] >= disc[u]) {
                set<pair<int, int>> currentBCC;
                pair<int, int> edge;
                
                do {
                    edge = edgeStack.top();
                    edgeStack.pop();
                    // Store edges in a canonical way (min, max)
                    currentBCC.insert({min(edge.first, edge.second), max(edge.first, edge.second)});
                } while (edge.first != u || edge.second != v); // Pop until (u,v)

                bccs.push_back(currentBCC);
            }
        }
    }
    
    // 2. Root case: if p is -1 (root) and childCount > 1, root is an AP
    if (p == -1 && childCount > 1) {
        articulationPoints.insert(u);
    }
}

int main() {
    int V, E;
    
    // Skip comment lines and read V E
    string line;
    while (getline(cin, line)) {
        if (line.empty() || line[0] == '#') continue;
        stringstream ss(line);
        if (ss >> V >> E) break;
    }

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

    // Initialize
    timer = 0;
    for (int i = 0; i < V; ++i) {
        disc[i] = low[i] = -1;
        visited[i] = false;
    }

    // Run the BCC algorithm from all unvisited nodes
    for (int i = 0; i < V; ++i) {
        if (!visited[i]) {
            findBCC(i); // Call with default p = -1
            
            // Any remaining edges on the stack form a BCC
            if (!edgeStack.empty()) {
                set<pair<int, int>> currentBCC;
                while(!edgeStack.empty()) {
                    pair<int, int> edge = edgeStack.top();
                    edgeStack.pop();
                    currentBCC.insert({min(edge.first, edge.second), max(edge.first, edge.second)});
                }
                bccs.push_back(currentBCC);
            }
        }
    }

    // --- Formatted Output ---
    cout << "\n--- Chain decomposition algorithm's results ---" << endl;

    // 1. Total Count
    cout << "Total Biconnected Components (BCCs) found: " << bccs.size() << endl;

    // 2. BCC List
    for (int i = 0; i < bccs.size(); ++i) {
        const auto& bcc = bccs[i];
        int bccIndex = i + 1;
        int edgeCount = bcc.size();
        
        string type;
        if (edgeCount == 1) {
            type = "Bridge";
        } else {
            // Matches image format "(Triangle X)"
            type = "Triangle " + to_string(bccIndex); 
        }

        cout << "BCC " << bccIndex << " (" << type << "): {";

        bool firstEdge = true;
        for (const auto& edge : bcc) {
            if (!firstEdge) {
                cout << ", ";
            }
            cout << "(" << edge.first << ", " << edge.second << ")";
            firstEdge = false;
        }
        cout << "}" << endl;
    }

    // 3. Articulation Points
    cout << "\nArticulation Points (Cut Vertices): ";
    for (int ap : articulationPoints) { // Set prints in sorted order
        cout << ap << " ";
    }
    cout << endl;

    return 0;
}