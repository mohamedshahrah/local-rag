import os
import yaml
import chromadb
import ollama
import json
from glob import glob
from pypdf import PdfReader
import docx2txt

with open("config.yaml", "r") as f:
    config = yaml.safe_load(f)

client = chromadb.PersistentClient(path=config['paths']['chroma_db'])

def get_subfolders():
    if not os.path.exists(config['paths']['data']):
        os.makedirs(config['paths']['data'])
    return [f.name for f in os.scandir(config['paths']['data']) if f.is_dir()]

def read_file(file_path):
    """Reads PDF, TXT, DOCX, and JSON files."""
    ext = file_path.split('.')[-1].lower()
    text = ""
    try:
        if ext == 'pdf':
            reader = PdfReader(file_path)
            for page in reader.pages:
                text += page.extract_text() + "\n"
        
        elif ext == 'txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()
                
        elif ext == 'docx':
            text = docx2txt.process(file_path)

        elif ext == 'json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Convert JSON object to a pretty string
                text = json.dumps(data, indent=2) 
                
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        
    return text  # This must be OUTSIDE the try/except block

def ingest_folder(folder_name, chunk_size, chunk_overlap):
    """Reads files, chunks them dynamically based on inputs, and saves to Chroma"""
    folder_path = os.path.join(config['paths']['data'], folder_name)
    
    # Reset the collection
    try:
        client.delete_collection(folder_name)
    except:
        pass 
        
    collection = client.create_collection(name=folder_name)
    
    # Check for supported extensions (including .json)
    files = glob(os.path.join(folder_path, "**/*.*"), recursive=True)
    count = 0

    for file_path in files:
        if not file_path.lower().endswith(('.pdf', '.txt', '.docx', '.json')):
            continue
            
        text = read_file(file_path)
        if not text: continue

        # Dynamic Chunking Logic
        step = chunk_size - chunk_overlap
        if step <= 0: step = 1 
        
        chunks = [text[i:i+chunk_size] for i in range(0, len(text), step)]
        
        for i, chunk in enumerate(chunks):
            response = ollama.embeddings(model=config['llm']['embedding_model'], prompt=chunk)
            embedding = response["embedding"]
            
            collection.add(
                ids=[f"{file_path}_{i}"],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[{"source": file_path}]
            )
            count += 1
            
    return f"Success! Indexed {count} chunks (Size: {chunk_size}, Overlap: {chunk_overlap})."

def query_rag(folder_name, query, history=[]):
    try:
        collection = client.get_collection(name=folder_name)
    except:
        return "⚠️ Database not found. Please click 'Update DB' first."

    query_embed = ollama.embeddings(model=config['llm']['embedding_model'], prompt=query)["embedding"]

    results = collection.query(query_embeddings=[query_embed], n_results=10)
    
    if results['documents']:
        context_text = "\n\n".join(results['documents'][0])
    else:
        context_text = ""

    system_msg = (
        "You are a smart, helpful AI assistant. Your goal is to explain answers clearly and naturally. "
        "You have access to the following 'Context' from the user's files (including JSON data).\n"
        "---------------------\n"
        f"{context_text}\n"
        "---------------------\n"
        "INSTRUCTIONS:\n"
        "1. Read the Context carefully. If the answer is in there, explain it fully and conversationally.\n"
        "2. If the user asks about something completely unrelated to the Context, strict reply: 'I'm sorry, but I don't see that information in your uploaded files.'\n"
        "3. Do NOT make up facts. Stick to the provided context."
    )
    
    messages = [{'role': 'system', 'content': system_msg}]
    
    for msg in history:
        messages.append(msg)
        
    messages.append({'role': 'user', 'content': query})

    response = ollama.chat(model=config['llm']['model'], messages=messages)
    return response['message']['content']