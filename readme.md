⚡ Local RAG System
This is a private, high-performance Retrieval-Augmented Generation (RAG) system built with Streamlit, ChromaDB, and Ollama. It allows you to chat with your local documents (PDF, TXT, DOCX, JSON) while keeping all data and processing 100% offline.

🌟 Key Features

Dynamic Ingestion: Control chunk size and overlap directly from the UI.

Multi-Format Support: Processes PDFs, Word documents, Plain Text, and JSON files.

Persistent Memory: Saves chat sessions using an SQLite database via SQLAlchemy.

Topic Folders: Organize your data into subfolders; the system creates separate vector collections for each.

🛠️ Installation & Setup
1. Prerequisites
Ollama: Install from ollama.com.

Models: Open your terminal and pull the models specified in your config.yaml:

Bash
ollama pull llama3.2
ollama pull nomic-embed-text
2. Anaconda Environment Setup
Open your Anaconda Prompt or Terminal and run:

Bash
# Create the environment
conda create -n local-rag python=3.10 -y

# Activate the environment
conda activate local-rag

# Install dependencies from your requirements.txt
pip install -r requirements.txt
🚀 How to Run
Step 1: Organize Your Data
Place your documents into subfolders inside a directory named data/. For example:

data/AI_Research/paper.pdf

data/Finances/report.json

Step 2: Launch the App
Run the Streamlit interface:

Bash
streamlit run app.py
Step 3: Using the Interface

Select a Folder: Choose the topic you want to discuss from the sidebar.


Adjust Parameters: (Optional) Fine-tune the Chunk Size and Overlap sliders.


Ingest: Click "🔄 Update / Ingest DB" to vectorize your files.

Chat: Ask questions in the chat input. The system will retrieve context and answer using your local model.

📁 Project Overview

app.py: The Streamlit frontend and chat logic.

rag_engine.py: Handles file reading, dynamic chunking, and ChromaDB interactions.

database.py: Manages session-based chat history storage.

config.yaml: Central configuration for models, paths, and default processing settings.

requirements.txt: List of Python libraries required for the project.

⚙️ Configuration
You can modify config.yaml to change:

llm.model: Switch between different Ollama models (e.g., mistral or phi3).

processing: Change the default character count for document splitting.
