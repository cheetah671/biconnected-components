/*
 * This is the C++ code you provided for a sequential simulation
 * of the Tarjan-Vishkin Algorithm (Algorithm 2).
 *
 * I have modified step4_buildAuxiliaryGraph and step5_assignEdges
 * to correctly handle non-tree edges and form the proper BCCs.
 */

#include <iostream>
#include <vector>
#include <queue>
#include <map>
#include <set>
#include <algorithm>
#include <chrono> // For timing
#include <sstream>
#include <string>

using namespace std;

// Global variables
int V = 0, E = 0;
vector<vector<int>> adj;
vector<pair<int,int>> edges;

// Algorithm data
vector<bool> inTree;
vector<int> parentv;
vector<vector<int>> treeAdj;
vector<int> preorder;
vector<int> preorderToVertex;
vector<int> numDescendants;
vector<int> low;
vector<int> high;
map<pair<int,int>, int> treeEdgeToId;
vector<int> uf_parent, uf_rank;
int uf_components = 0;
vector<int> edgeToBCC;
int numBCCs = 0;

// =============== Union-Find ===============
void uf_init(int n) {
    uf_parent.resize(n);
    uf_rank.assign(n, 0);
    for (int i = 0; i < n; i++) uf_parent[i] = i;
    uf_components = n;
}
int uf_find(int x) {
    if (uf_parent[x] != x)
        uf_parent[x] = uf_find(uf_parent[x]);
    return uf_parent[x];
}
bool uf_unite(int x, int y) {
    int px = uf_find(x), py = uf_find(y);
    if (px == py) return false;
    if (uf_rank[px] < uf_rank[py]) swap(px, py);
    uf_parent[py] = px;
    if (uf_rank[px] == uf_rank[py]) uf_rank[px]++;
    uf_components--;
    return true;
}

// =============== Graph Utilities ===============
void initGraph(int n, int m) {
    V = n;
    E = m;
    adj.assign(V, {});
    edges.clear();
}
void addEdge(int u, int v) {
    adj[u].push_back(v);
    adj[v].push_back(u);
    edges.emplace_back(u, v);
}

// =============== DFS Helpers ===============
void computePreorderDFS(int u, int p, int &counter) {
    preorder[u] = counter;
    preorderToVertex[counter] = u;
    counter++;
    for (int v : treeAdj[u])
        if (v != p) computePreorderDFS(v, u, counter);
}
int computeDescendantsDFS(int u, int p) {
    int count = 1;
    for (int v : treeAdj[u])
        if (v != p)
            count += computeDescendantsDFS(v, u);
    numDescendants[preorder[u]] = count;
    return count;
}
void propagateLowHighDFS(int u, int p) {
    int pu = preorder[u];
    for (int v : treeAdj[u]) {
        if (v != p) {
            propagateLowHighDFS(v, u);
            int pv = preorder[v];
            low[pu] = min(low[pu], low[pv]);
            high[pu] = max(high[pu], high[pv]);
        }
    }
}

// =============== Tarjan-Vishkin Steps ===============
void step1_buildSpanningForest() {
    vector<bool> visited(V, false);
    parentv.assign(V, -1);
    treeAdj.assign(V, {});

    for (int root = 0; root < V; ++root) {
        if (visited[root]) continue;
        queue<int> q;
        q.push(root);
        visited[root] = true;
        while (!q.empty()) {
            int u = q.front(); q.pop();
            for (int v : adj[u]) {
                if (!visited[v]) {
                    visited[v] = true;
                    parentv[v] = u;
                    treeAdj[u].push_back(v);
                    treeAdj[v].push_back(u);
                    q.push(v);
                    for (int i = 0; i < E; i++) {
                        if ((edges[i].first == u && edges[i].second == v) ||
                            (edges[i].first == v && edges[i].second == u)) {
                            inTree[i] = true;
                            break;
                        }
                    }
                }
            }
        }
    }
}

void step2_eulerTourAndNumbering() {
    int counter = 0;
    for (int v = 0; v < V; v++)
        if (preorder[v] == -1) {
            computePreorderDFS(v, -1, counter);
            computeDescendantsDFS(v, -1);
        }
}

void step3_computeLowHigh() {
    for (int u = 0; u < V; u++) {
        int p = preorder[u];
        if (p == -1) continue; // Node not reachable
        low[p] = p;
        high[p] = p;
    }

    for (int i = 0; i < E; i++) {
        if (!inTree[i]) {
            int u = edges[i].first;
            int v = edges[i].second;
            int pu = preorder[u], pv = preorder[v];
            if (pu == -1 || pv == -1) continue; // Edge to unreachable node
            low[pu] = min(low[pu], pv);
            low[pv] = min(low[pv], pu);
            high[pu] = max(high[pu], pv);
            high[pv] = max(high[pv], pu);
        }
    }

    for (int u = 0; u < V; u++)
        if (parentv[u] == -1)
            propagateLowHighDFS(u, -1);
}

void step4_buildAuxiliaryGraph() {
    treeEdgeToId.clear();
    int treeEdgeCount = 0;

    for (int i = 0; i < E; i++) {
        if (inTree[i]) {
            int u = edges[i].first, v = edges[i].second;
            if (parentv[v] == u)
                treeEdgeToId[{preorder[u], preorder[v]}] = treeEdgeCount++;
            else if (parentv[u] == v)
                treeEdgeToId[{preorder[v], preorder[u]}] = treeEdgeCount++;
        }
    }

    if (treeEdgeCount == 0) {
        uf_init(E);
        for(int i=0; i < E; ++i) {
             if(!inTree[i]) {
                 edgeToBCC[i] = uf_find(i);
             }
        }
        numBCCs = E;
        return;
    }

    uf_init(treeEdgeCount);

    // ================== FIX START ==================
    // Rule (i): Unite components based on non-tree edges
    // A non-tree edge (u, v) "glues" the components of the
    // tree edges (parent(u), u) and (parent(v), v) together.
    for (int i = 0; i < E; i++) {
        if (!inTree[i]) {
            int u = edges[i].first, v = edges[i].second;
            int pu = preorder[u], pv = preorder[v];
            if(pu == -1 || pv == -1) continue; // Unreachable node

            // Find the tree edge ID for u, which is (parent(u), u)
            int e_u_id = -1;
            if (parentv[u] != -1) {
                auto it = treeEdgeToId.find({preorder[parentv[u]], pu});
                if (it != treeEdgeToId.end()) {
                    e_u_id = it->second;
                }
            }

            // Find the tree edge ID for v, which is (parent(v), v)
            int e_v_id = -1;
            if (parentv[v] != -1) {
                auto it = treeEdgeToId.find({preorder[parentv[v]], pv});
                if (it != treeEdgeToId.end()) {
                    e_v_id = it->second;
                }
            }

            // If both endpoints are part of the spanning tree (not roots)
            // and have valid tree edges, unite their components.
            if (e_u_id != -1 && e_v_id != -1) {
                uf_unite(e_u_id, e_v_id);
            }
        }
    }
    // =================== FIX END ===================


    // Rule (ii): Unite parent/child tree edges if they are not
    // separated by an articulation point.
    for (auto &entry : treeEdgeToId) {
        int pv = entry.first.first; // preorder of parent
        int pw = entry.first.second; // preorder of child
        int v = preorderToVertex[pv];

        if (parentv[v] != -1) { // if v is not a root
            int parentV = preorder[parentv[v]];
            auto e1_it = treeEdgeToId.find({parentV, pv}); // Find edge (parent(v), v)
            if (e1_it != treeEdgeToId.end()) {
                // If child can reach above parent OR child can reach
                // outside its parent's subtree, unite
                if (low[pw] < pv || high[pw] >= pv + numDescendants[pv]) {
                    uf_unite(e1_it->second, entry.second);
                }
            }
        }
    }

    numBCCs = uf_components;
}

void step5_assignEdges() {
    // Assign all tree edges to their final component ID
    for (int i = 0; i < E; i++) {
        if (inTree[i]) {
            int u = edges[i].first, v = edges[i].second;
            pair<int,int> key;
            if (parentv[v] == u) key = {preorder[u], preorder[v]};
            else key = {preorder[v], preorder[u]};
            
            auto it = treeEdgeToId.find(key);
            if (it != treeEdgeToId.end())
                edgeToBCC[i] = uf_find(it->second);
        }
    }

    // ================== FIX START ==================
    // Assign all non-tree edges to the component of one of their endpoints.
    // Since Step 4 already united the components, assigning the non-tree
    // edge to *either* endpoint's tree-edge-component is correct.
    for (int i = 0; i < E; i++) {
        if (!inTree[i]) {
            int u = edges[i].first;
            int pu = preorder[u];
            if (pu == -1) continue; // Unreachable

            // Find the parent tree edge for u, (parent(u), u)
            if (parentv[u] != -1) {
                auto it = treeEdgeToId.find({preorder[parentv[u]], pu});
                if (it != treeEdgeToId.end()) {
                    edgeToBCC[i] = uf_find(it->second);
                }
            }
            
            // If u was a root, try v
            if (edgeToBCC[i] == -1) {
                 int v = edges[i].second;
                 int pv = preorder[v];
                 if(pv == -1) continue;
                 
                 if (parentv[v] != -1) {
                    auto it = treeEdgeToId.find({preorder[parentv[v]], pv});
                    if (it != treeEdgeToId.end()) {
                        edgeToBCC[i] = uf_find(it->second);
                    }
                 }
            }
        }
    }
    // =================== FIX END ===================
}

// =============== Print Results (MODIFIED) ===============
void printResults() {
    // Map component IDs (which can be arbitrary) to a clean 1-based index
    map<int, int> bccIdToIndex;
    int nextIndex = 1;
    
    // Ensure consistent ordering
    vector<int> sortedComponentIds;
    for(int id : edgeToBCC) {
        if(id != -1) sortedComponentIds.push_back(id);
    }
    sort(sortedComponentIds.begin(), sortedComponentIds.end());
    
    for (int id : sortedComponentIds) {
        if (id != -1 && bccIdToIndex.find(id) == bccIdToIndex.end()) {
            bccIdToIndex[id] = nextIndex++;
        }
    }
    
    // Store edges by their new, clean index
    map<int, set<pair<int,int>>> bccEdges;
    for (int i = 0; i < E; i++) {
        if (edgeToBCC[i] != -1) {
            int cleanIndex = bccIdToIndex[edgeToBCC[i]];
            // Store canonical edge (min, max)
            bccEdges[cleanIndex].insert({min(edges[i].first, edges[i].second), max(edges[i].first, edges[i].second)});
        }
    }

    cout << "\n--- Tarjan-Vishkin Algorithm's results ---" << endl;
    
    // 1. Total Count
    cout << "Total Biconnected Components (BCCs) found: " << bccEdges.size() << endl;

    // 2. BCC List
    for (auto const& [index, edgeSet] : bccEdges) {
        string type;
        if (edgeSet.size() == 1) {
            type = "Bridge";
        } else {
             // Heuristic to detect triangles for cleaner output
            if (edgeSet.size() == 3) {
                 set<int> nodes;
                 for(auto p : edgeSet) { nodes.insert(p.first); nodes.insert(p.second); }
                 if (nodes.size() == 3) type = "Triangle";
                 else type = "Component " + to_string(index);
            } else {
                 type = "Component " + to_string(index);
            }
        }

        cout << "BCC " << index << " (" << type << "): {";
        bool firstEdge = true;
        for (const auto& edge : edgeSet) {
            if (!firstEdge) {
                cout << ", ";
            }
            cout << "(" << edge.first << ", " << edge.second << ")";
            firstEdge = false;
        }
        cout << "}" << endl;
    }


    // 3. Articulation Points
    set<int> articulationPoints;
    for (int v = 0; v < V; v++) {
        set<int> neighborBCCs;
        for (int i = 0; i < E; i++) {
            if (edges[i].first == v || edges[i].second == v) {
                if (edgeToBCC[i] != -1) {
                    neighborBCCs.insert(edgeToBCC[i]);
                }
            }
        }
        // A vertex is an AP if it's part of more than one BCC
        if (neighborBCCs.size() > 1) {
            articulationPoints.insert(v);
        }
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

// =============== Main Algorithm Runner ===============
void runTarjanVishkin() {
    inTree.assign(E, false);
    parentv.assign(V, -1);
    treeAdj.assign(V, {});
    preorder.assign(V, -1);
    preorderToVertex.resize(V);
    fill(preorderToVertex.begin(), preorderToVertex.end(), -1);
    numDescendants.resize(V);
    fill(numDescendants.begin(), numDescendants.end(), 0);
    low.resize(V);
    fill(low.begin(), low.end(), 0);
    high.resize(V);
    fill(high.begin(), high.end(), 0);
    edgeToBCC.assign(E, -1);
    treeEdgeToId.clear();

    auto start = chrono::high_resolution_clock::now();
    step1_buildSpanningForest();
    step2_eulerTourAndNumbering();
    step3_computeLowHigh();
    step4_buildAuxiliaryGraph();
    step5_assignEdges();
    auto end = chrono::high_resolution_clock::now();

    printResults();
    
    cout << "\nAlgorithm 2 (Tarjan-Vishkin) sequential simulation finished." << endl;
    cout << "Execution time: "
         << chrono::duration_cast<chrono::microseconds>(end - start).count()
         << " microseconds\n";
}

// =============== MAIN (MODIFIED) ===============
int main() {
    

    int n, m;
    // Skip comment lines and read V E
    string line;
    while (getline(cin, line)) {
        if (line.empty() || line[0] == '#') continue;
        stringstream ss(line);
        if (ss >> n >> m) break;
    }

    initGraph(n, m);
    
    // Read edges, skipping comments
    for (int i = 0; i < m; i++) {
        int u, v;
        bool success = false;
        while (getline(cin, line)) {
            if (line.empty() || line[0] == '#') continue;
            stringstream ss(line);
            if (ss >> u >> v) {
                if (u < 0 || u >= n || v < 0 || v >= n) {
                    cerr << "Error: Invalid edge (" << u << ", " << v << "). Vertices must be in range [0, " << n-1 << "].\n";
                    continue;
                }
                if (u == v) {
                    cerr << "Error: Self-loop detected (" << u << ", " << v << "). Not supported.\n";
                    continue;
                }
                addEdge(u, v);
                success = true;
                break;
            }
        }
        if (!success) {
            cerr << "Error reading edge " << i << endl;
            break;
        }
    }

    runTarjanVishkin();
    return 0;
}