import chromadb
from crewai.memory.storage.rag_storage import RAGStorage

def get_agent_memory():
    """
    Initializes ChromaDB for long-term memory.
    Uses a persistent client to survive app restarts.
    """
    client = chromadb.PersistentClient(path="./agent_memory")
    
    # Create a storage instance for CrewAI
    storage = RAGStorage(
        embedder_config={"provider": "default"},
        type="short_term", # We use short_term for the demo, but the client persists
        allow_reset=True
    )
    # Note: CrewAI's memory settings will handle the actual storage calls.
    return storage
