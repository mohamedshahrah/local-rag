import streamlit as st
import yaml
import uuid
from rag_engine import ingest_folder, query_rag, get_subfolders
from database import save_message, get_history

# Load Config
with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

st.set_page_config(page_title=config['app']['title'], layout="wide")
st.title("⚡ " + config['app']['title'])

# --- SESSION STATE INITIALIZATION ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- SIDEBAR ---
with st.sidebar:
    st.header("⚙️ Data Settings")
    
    # 1. Folder Selector
    folders = get_subfolders()
    if folders:
        selected_folder = st.selectbox("Select Topic Folder", folders)
        
        # 2. Chunk Control Sliders (Reading Defaults from Config)
        st.caption("Chunking Parameters")
        
        chunk_size = st.slider(
            "Chunk Size", 
            min_value=100, 
            max_value=2000, 
            value=config['processing']['chunk_size'], 
            step=100
        )
        
        chunk_overlap = st.slider(
            "Chunk Overlap", 
            min_value=0, 
            max_value=500, 
            value=config['processing']['chunk_overlap'], 
            step=50
        )
        
        if st.button("🔄 Update / Ingest DB"):
            with st.spinner(f"Processing '{selected_folder}' with Size {chunk_size}..."):
                # Pass the slider values to the engine
                msg = ingest_folder(selected_folder, chunk_size, chunk_overlap)
                st.success(msg)
    else:
        st.warning("Create folders in 'data/' to start.")
        selected_folder = None

    st.divider()
    
    # 3. New Chat / Reset Function
    st.header("💬 Chat Management")
    st.write(f"Current Session: `{st.session_state.session_id[:8]}...`")
    
    if st.button("🗑️ New Chat / Reset"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.rerun()

# --- CHAT LOGIC ---

# Load History (Only if messages are empty, to support page refresh)
if not st.session_state.messages:
    db_history = get_history(st.session_state.session_id)
    if db_history:
        st.session_state.messages = db_history

# Display Chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("Ask a question..."):
    if not selected_folder:
        st.error("Select a folder first!")
        st.stop()

    # Show User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    save_message(st.session_state.session_id, "user", prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate Answer
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            recent_history = st.session_state.messages[-4:] 
            response = query_rag(selected_folder, prompt, recent_history)
            st.markdown(response)

    # Save Assistant Message
    st.session_state.messages.append({"role": "assistant", "content": response})
    save_message(st.session_state.session_id, "assistant", response)