import streamlit as st
import subprocess
import os
import sys # Import sys module

# --- Configuration for Universal Pathing ---

# Set the executable name based on the Operating System
if sys.platform.startswith('win'):
    # Windows: requires the .exe extension
    EXECUTABLE_FILENAME = "extended_mst.exe" 
else:
    # Linux (Streamlit Cloud, WSL, Mac): no extension required
    EXECUTABLE_FILENAME = "extended_mst"

# Get the absolute path to the directory where the Python script is running
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
C_EXECUTABLE_PATH = os.path.join(BASE_DIR, EXECUTABLE_FILENAME)
INPUT_FILE_PATH = os.path.join(BASE_DIR, "graph_input.txt")

# ====================================================================
# Utility Functions for C Communication
# ====================================================================
# (The rest of the file remains the same)
# ...
def generate_input_file(node_weights_str, edges_str):
    # ... (function body unchanged)
    pass 

def run_c_solver():
    """Executes the compiled C program and captures its stdout."""
    st.info(f"Executing C program: {C_EXECUTABLE_PATH}")
    
    if not os.path.exists(C_EXECUTABLE_PATH):
        st.error(f"C executable not found. Checked path: `{C_EXECUTABLE_PATH}`")
        # Updated warning message to reflect the universal naming
        st.warning(f"Ensure you compiled to **{EXECUTABLE_FILENAME}** and placed it in the script's folder.")
        return None

    try:
        # Pass the absolute path to both the executable and the input file
        result = subprocess.run(
            [C_EXECUTABLE_PATH, INPUT_FILE_PATH], 
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        st.error(f"C program (Extended MST) failed with exit code {e.returncode}.")
        st.code(f"STDERR:\n{e.stderr}\n\nSTDOUT:\n{e.stdout}")
        return None
    except FileNotFoundError:
        st.error(f"C executable not found (Permission/OS error). Checked path: `{C_EXECUTABLE_PATH}`")
        return None

# ... (The rest of the Streamlit interface functions and main block remain unchanged)
# ...
