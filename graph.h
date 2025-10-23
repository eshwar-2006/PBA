#ifndef GRAPH_H
#define GRAPH_H

#include <stdio.h>
#include <stdlib.h>
#include <limits.h>

// --- Data Structures ---

typedef struct {
    int u, v;       // Source and destination node indices (0-indexed)
    int weight;     // Original edge weight (w_e)
    int effective_cost; // Calculated cost (w_e + w_u + w_v)
} Edge;

typedef struct {
    int V;          // Number of vertices (nodes)
    int E;          // Number of edges
    int* node_weights; // Array to store node weights
    Edge* edges;    // Array of all edges
} Graph;

// --- DSU Prototypes ---
void initDSU(int V);
int find(int i);
int unionSets(int u, int v);
void cleanupDSU();

// --- Graph Prototypes ---
Graph* createGraph(int V, int E);
void setNodeWeight(Graph* graph, int node_id, int weight);
void addEdge(Graph* graph, int edge_index, int u, int v, int weight);
void freeGraph(Graph* graph);

// --- MST Solver Prototypes ---
int compareEdges(const void* a, const void* b);
int findExtendedMST(Graph* graph, Edge** mst_edges_out);
void print_mst_result(int total_cost, const Edge* mst_edges, int num_edges, const Graph* graph);

#endif
