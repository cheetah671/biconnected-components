#include <iostream>
#include <vector>
#include <set>
#include <queue> // For BFS, matching the Python code
#include <string>
#include <sstream>

using namespace std;

/**
 * @brief Helper function to count reachable nodes using BFS,
 * matching the Python _count_reachable_nodes function.
 * @param num_nodes Total number of nodes in the graph.
 * @param start_node The node to start the BFS from.
 * @param removed_vertex The vertex to ignore during traversal.
 * @param adj The adjacency list of the graph.
 * @return The total count of reachable nodes.
 */
int countReachableNodes(int num_nodes, int start_node, int removed_vertex, const vector<vector<int>>& adj) {
    if (start_node == removed_vertex) {
        return 0;
    }

    vector<bool> visited(num_nodes, false);
    queue<int> q;

    q.push(start_node);
    visited[start_node] = true;
    int count = 0;

    while (!q.empty()) {
        int u = q.front();
        q.pop();
        count++;

        for (int v : adj[u]) {
            if (v == removed_vertex || visited[v]) {
                continue;
            }
            visited[v] = true;
            q.push(v);
        }
    }
    return count;
}

/**
 * @brief Finds all articulation points using the naive O(V * (V+E)) method.
 * Matches the Python find_articulation_points_naive function.
 * @param num_nodes Total number of nodes in the graph.
 * @param adj The adjacency list of the graph.
 * @return A set of articulation point (cut vertex) IDs.
 */
set<int> findArticulationPointsNaive(int num_nodes, const vector<vector<int>>& adj) {
    if (num_nodes <= 2) {
        return set<int>(); // Return empty set
    }

    set<int> articulation_points;

    for (int v_to_remove = 0; v_to_remove < num_nodes; ++v_to_remove) {
        // Pick a valid start node from the remaining graph
        int start_node = -1;
        for (int i = 0; i < num_nodes; ++i) {
            if (i != v_to_remove) {
                start_node = i;
                break;
            }
        }

        if (start_node == -1) {
            continue; // Should only happen for V=1, which is handled
        }

        // Count how many nodes are reachable in the graph *without* v_to_remove
        int reachable_count = countReachableNodes(num_nodes, start_node, v_to_remove, adj);

        if (reachable_count < num_nodes - 1) {
            articulation_points.insert(v_to_remove);
        }
    }
    return articulation_points;
}

int main() {
    int num_nodes, num_edges;
    
    // Skip comment lines and read V E
    string line;
    while (getline(cin, line)) {
        if (line.empty() || line[0] == '#') continue;
        stringstream ss(line);
        if (ss >> num_nodes >> num_edges) break;
    }

    // Use vector<vector<int>> for adjacency list
    vector<vector<int>> adj_list(num_nodes);

    // Read edges, skipping comments
    for (int i = 0; i < num_edges; ++i) {
        int u, v;
        bool success = false;
        while (getline(cin, line)) {
            if (line.empty() || line[0] == '#') continue;
            stringstream ss(line);
            if (ss >> u >> v) {
                if (u >= num_nodes || v >= num_nodes || u < 0 || v < 0) {
                    cout << "Invalid edge: (" << u << ", " << v << "). Nodes must be between 0 and " << (num_nodes - 1) << "." << endl;
                    continue;
                }
                adj_list[u].push_back(v);
                adj_list[v].push_back(u);
                success = true;
                break;
            }
        }
        if (!success) {
            cerr << "Error reading edge " << i << endl;
            break;
        }
    }

    cout << "\n--- Graph Input Complete ---" << endl;
    cout << "Graph has " << num_nodes << " nodes." << endl;

    // --- Find Articulation Points ---
    set<int> aps = findArticulationPointsNaive(num_nodes, adj_list);

    // --- CHANGED OUTPUT FORMAT ---
    cout << "\n--- Naive Algorithm Results ---" << endl;
    
    cout << "Articulation Points: ";
    if (aps.empty()) {
        cout << "None";
    } else {
        cout << "{";
        bool first = true;
        for (int ap : aps) {
            if (!first) {
                cout << ", ";
            }
            cout << ap;
            first = false;
        }
        cout << "}";
    }
    cout << endl;

    cout << "Number of BCCs: Not computed by this naive algorithm." << endl;

    return 0;
}