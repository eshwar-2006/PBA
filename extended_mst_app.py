import streamlit as st
import subprocess
import os

# --- Configuration ---
# NOTE: The C executable must be compiled and placed in the same directory.
C_EXECUTABLE_PATH = "./extended_mst"  
INPUT_FILE_PATH = "graph_input.txt"

# ====================================================================
# Utility Functions for C Communication
# ====================================================================

def generate_input_file(node_weights_str, edges_str):
    """
    Translates user-friendly input (A:10, B,C,5) into a structured format
    required by the C executable and saves it to INPUT_FILE_PATH.
    
    C Input File Format:
    Line 1: V E
    Line 2: w0 w1 w2 ... (Node weights by index)
    Line 3+: u_idx v_idx w_e
    """
    nodes = []
    node_weights = {}
    
    try:
        # 1. Parse Node Weights (ID:Weight)
        for line in node_weights_str.split('\n'):
            if line.strip():
                node_id, weight = line.split(':')
                nodes.append(node_id.strip())
                node_weights[node_id.strip()] = int(weight.strip())
        
        # 2. Parse Edges (u,v,w_e)
        edges = []
        for line in edges_str.split('\n'):
            if line.strip():
                u, v, w_e = line.split(',')
                u = u.strip()
                v = v.strip()
                w_e = int(w_e.strip())
                
                if u not in node_weights or v not in node_weights:
                    st.error(f"Edge error: Node '{u}' or '{v}' not defined in Node Weights.")
                    return False, [], {}
                
                edges.append((u, v, w_e))

    except Exception as e:
        st.error(f"Input parsing error: Check formatting (ID:Weight or u,v,w_e). Details: {e}")
        return False, [], {}

    V = len(nodes)
    E = len(edges)

    # 3. Create the input file
    try:
        with open(INPUT_FILE_PATH, 'w') as f:
            # Line 1: V and E
            f.write(f"{V} {E}\n")
            
            # Line 2: Node weights (mapped to C's 0-indexed structure)
            node_map = {name: i for i, name in enumerate(nodes)}
            
            weight_list = [0] * V
            for name, idx in node_map.items():
                weight_list[idx] = node_weights[name]
                
            f.write(" ".join(map(str, weight_list)) + "\n")
            
            # Line 3+: Edges (u_idx, v_idx, w_e)
            for u, v, w_e in edges:
                f.write(f"{node_map[u]} {node_map[v]} {w_e}\n")

    except Exception as e:
        st.error(f"Failed to write input file: {e}")
        return False, [], {}

    return True, nodes, node_weights

def run_c_solver():
    """Executes the compiled C program and captures its stdout."""
    st.info(f"Executing C program: {C_EXECUTABLE_PATH} {INPUT_FILE_PATH}")
    try:
        # Run C executable, passing the input file path as an argument
        result = subprocess.run(
            [C_EXECUTABLE_PATH, INPUT_FILE_PATH], 
            capture_output=True, 
            text=True, 
            check=True  # Raises an error if C program returns non-zero exit code
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        st.error(f"C program (Extended MST) failed with exit code {e.returncode}.")
        st.code(f"STDERR:\n{e.stderr}\n\nSTDOUT:\n{e.stdout}")
        return None
    except FileNotFoundError:
        st.error(f"C executable not found. Ensure '{C_EXECUTABLE_PATH}' exists and is compiled.")
        return None

def parse_c_output(output, node_names):
    """Parses the structured output from the C program."""
    lines = output.strip().split('\n')
    total_cost = None
    mst_edges = []
    parsing_edges = False

    # Create reverse map: Node Index -> Node Name (e.g., 0->A, 1->B)
    name_map = {i: name for i, name in enumerate(node_names)}

    for line in lines:
        if line.startswith("TOTAL_COST:"):
            total_cost = int(line.split(':')[1])
        elif line == "MST_EDGES_START":
            parsing_edges = True
        elif line == "MST_EDGES_END":
            parsing_edges = False
        elif parsing_edges:
            try:
                # Format: u_idx,v_idx,w_e,w_u,w_v,C_e
                parts = line.split(',')
                u_idx, v_idx, w_e, w_u, w_v, C_e = map(int, parts)
                
                mst_edges.append({
                    'u': name_map.get(u_idx, str(u_idx)), 
                    'v': name_map.get(v_idx, str(v_idx)), 
                    'w_e': w_e, 
                    'w_u': w_u, 
                    'w_v': w_v, 
                    'C_e': C_e
                })
            except Exception:
                st.warning(f"Failed to parse edge line: {line}. Skipping.")

    return total_cost, mst_edges

# ====================================================================
# Streamlit Interface
# ====================================================================

st.set_page_config(layout="wide")
st.title("🗜️ C Core Extended MST Solver (via Streamlit)")
st.markdown(
    "This app uses a **C program** as its core solver, executed via Python's `subprocess`."
)
st.markdown("---")

st.header("1. Define Node Weights")
st.markdown("Enter node IDs (letters/numbers) and their weights, separated by a colon (e.g., `A:10`).")
node_input = st.text_area(
    "Node Weights (ID:Weight)", 
    "A:10\nB:5\nC:3\nD:1",
    height=100
)

st.header("2. Define Edges")
st.markdown("Enter edges as `Node1,Node2,EdgeWeight` (e.g., `A,B,2`). Node IDs must match those defined above.")
edge_input = st.text_area(
    "Edges (u,v,w_e)", 
    "A,B,2\nB,C,3\nC,D,4\nA,D,5\nB,D,1",
    height=150
)

st.header("3. Run Algorithm")
st.markdown(
    "The algorithm (Extended Kruskal's) minimizes the **Effective Edge Cost ($C_e$)**: "
    "$$\\text{Effective Cost } (C_e) = w_{edge} + w_{node\_u} + w_{node\_v}$$"
)

if st.button("Calculate Extended MST"):
    
    # 1. Generate Input File
    success, nodes, node_weights_dict = generate_input_file(node_input, edge_input)

    if success:
        
        # 2. Execute C Core
        c_output = run_c_solver()

        st.markdown("---")
        st.subheader("✅ Results")

        if c_output:
            # 3. Parse and Display Results
            total_cost, mst_edges = parse_c_output(c_output, nodes)

            if total_cost == -1:
                st.error("The graph is **disconnected**. A spanning tree could not be formed.")
            elif total_cost is not None:
                st.success(f"**Minimum Extended Cost:** `{total_cost}`")
                
                # Display the selected MST edges
                st.markdown("##### Selected Edges in the Extended MST")
                
                table_data = []
                for edge in mst_edges:
                    table_data.append({
                        'Edge': f"**{edge['u']}** - **{edge['v']}**",
                        'Edge Weight ($w_e$)': edge['w_e'],
                        'Node Weights ($w_u+w_v$)': f"{edge['w_u']} + {edge['w_v']}",
                        'Effective Cost ($C_e$)': edge['C_e']
                    })
                
                st.dataframe(table_data, use_container_width=True, hide_index=True)

                cost_breakdown = ' + '.join(str(e['C_e']) for e in mst_edges)
                st.markdown(f"**Total Cost Sum:** $\\text{{{cost_breakdown}}} = \\mathbf{{{total_cost}}}$")

            else:
                st.error("C program output could not be parsed.")
