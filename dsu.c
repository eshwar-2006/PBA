#include "graph.h"

// Global arrays for DSU
static int* parent = NULL;
static int* rank = NULL;

void initDSU(int V) {
    if (parent != NULL) cleanupDSU();
    
    parent = (int*)malloc(V * sizeof(int));
    rank = (int*)calloc(V, sizeof(int));
    
    if (parent && rank) {
        for (int i = 0; i < V; i++) {
            parent[i] = i; 
        }
    } else {
        if (parent) free(parent);
        if (rank) free(rank);
        parent = NULL;
        rank = NULL;
    }
}

void cleanupDSU() {
    if (parent) free(parent);
    if (rank) free(rank);
    parent = NULL;
    rank = NULL;
}

// Find operation with path compression
int find(int i) {
    if (!parent || i < 0) return -1;
    if (parent[i] == i)
        return i;
    return parent[i] = find(parent[i]);
}

// Union operation by rank. Returns 1 if union happened, 0 otherwise.
int unionSets(int u, int v) {
    if (!parent || u < 0 || v < 0) return 0;
    int root_u = find(u);
    int root_v = find(v);

    if (root_u != root_v) {
        if (rank[root_u] < rank[root_v]) {
            parent[root_u] = root_v;
        } else if (rank[root_u] > rank[root_v]) {
            parent[root_v] = root_u;
        } else {
            parent[root_v] = root_u;
            rank[root_u]++;
        }
        return 1; // Union successful
    }
    return 0; // Already connected
}
