#include "graph.h"
#include <string.h>

// --- Graph Functions (Implementation) ---

Graph* createGraph(int V, int E) {
    Graph* graph = (Graph*)malloc(sizeof(Graph));
    if (!graph) return NULL;

    graph->V = V;
    graph->E = E;
    graph->node_weights = (int*)calloc(V, sizeof(int));
    graph->edges = (Edge*)malloc(E * sizeof(Edge));

    if (!graph->node_weights || !graph->edges) {
        freeGraph(graph);
        return NULL;
    }
    return graph;
}

void setNodeWeight(Graph* graph, int node_id, int weight) {
    if (node_id >= 0 && node_id < graph->V) {
        graph->node_weights[node_id] = weight;
    }
}

void addEdge(Graph* graph, int edge_index, int u, int v, int weight) {
    if (edge_index >= 0 && edge_index < graph->E) {
        graph->edges[edge_index].u = u;
        graph->edges[edge_index].v = v;
        graph->edges[edge_index].weight = weight;
    }
}

void freeGraph(Graph* graph) {
    if (graph) {
        if (graph->node_weights) free(graph->node_weights);
        if (graph->edges) free(graph->edges);
        free(graph);
    }
}

int compareEdges(const void* a, const void* b) {
    const Edge* edgeA = (const Edge*)a;
    const Edge* edgeB = (const Edge*)b;
    return edgeA->effective_cost - edgeB->effective_cost;
}

// --- Extended MST Core Logic ---

static void calculateEffectiveCosts(Graph* graph) {
    for (int i = 0; i < graph->E; i++) {
        int u = graph->edges[i].u;
        int v = graph->edges[i].v;
        int w_e = graph->edges[i].weight;
        
        if (u >= 0 && u < graph->V && v >= 0 && v < graph->V) {
            int w_u = graph->node_weights[u];
            int w_v = graph->node_weights[v];
            graph->edges[i].effective_cost = w_e + w_u + w_v;
        } else {
            graph->edges[i].effective_cost = INT_MAX; 
        }
    }
}

int findExtendedMST(Graph* graph, Edge** mst_edges_out) {
    int total_cost = 0;
    int edges_in_mst = 0;
    int V = graph->V;
    int E = graph->E;

    if (V <= 1) return 0;
    
    calculateEffectiveCosts(graph);
    qsort(graph->edges, E, sizeof(Edge), compareEdges);

    initDSU(V);
    if (!find(0) && V > 0) { return -1; }

    *mst_edges_out = (Edge*)malloc((V - 1) * sizeof(Edge));
    if (!*mst_edges_out) { cleanupDSU(); return -1; }

    for (int i = 0; i < E && edges_in_mst < V - 1; i++) {
        Edge current_edge = graph->edges[i];

        if (unionSets(current_edge.u, current_edge.v)) {
            (*mst_edges_out)[edges_in_mst] = current_edge;
            total_cost += current_edge.effective_cost;
            edges_in_mst++;
        }
    }

    cleanupDSU();

    if (edges_in_mst != V - 1) {
        free(*mst_edges_out);
        *mst_edges_out = NULL;
        return -1; // Disconnected graph
    }

    return total_cost;
}

void print_mst_result(int total_cost, const Edge* mst_edges, int num_edges, const Graph* graph) {
    printf("TOTAL_COST:%d\n", total_cost);
    printf("MST_EDGES_START\n");
    for (int i = 0; i < num_edges; i++) {
        // Output format: u_idx,v_idx,w_e,w_u,w_v,C_e
        printf("%d,%d,%d,%d,%d,%d\n",
               mst_edges[i].u,
               mst_edges[i].v,
               mst_edges[i].weight,
               graph->node_weights[mst_edges[i].u],
               graph->node_weights[mst_edges[i].v],
               mst_edges[i].effective_cost);
    }
    printf("MST_EDGES_END\n");
}

// --- Main Driver for Streamlit Integration ---

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "ERROR: Missing input file path. Usage: %s <input_file_path>\n", argv[0]);
        return 1;
    }

    FILE *fp = fopen(argv[1], "r");
    if (!fp) {
        fprintf(stderr, "ERROR: Could not open input file: %s\n", argv[1]);
        return 1;
    }

    int V, E;
    if (fscanf(fp, "%d %d\n", &V, &E) != 2) { goto error_exit; }
    
    Graph* graph = createGraph(V, E);
    if (!graph) { goto error_exit; }

    for (int i = 0; i < V; i++) {
        int weight;
        if (fscanf(fp, "%d", &weight) != 1) { goto error_cleanup; }
        setNodeWeight(graph, i, weight);
    }

    for (int i = 0; i < E; i++) {
        int u, v, w;
        if (fscanf(fp, "%d %d %d", &u, &v, &w) != 3) { goto error_cleanup; }
        addEdge(graph, i, u, v, w);
    }
    
    fclose(fp);
    
    Edge* mst_result_edges = NULL;
    int total_cost = findExtendedMST(graph, &mst_result_edges);
    
    if (total_cost == -1) {
        printf("TOTAL_COST:-1\n");
    } else {
        print_mst_result(total_cost, mst_result_edges, V - 1, graph);
    }

    if (mst_result_edges) free(mst_result_edges);
    freeGraph(graph);
    return 0;

error_cleanup:
    freeGraph(graph);
error_exit:
    if (fp) fclose(fp);
    return 1;
}
