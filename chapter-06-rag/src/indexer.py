import os
import chromadb
from chromadb.utils import embedding_functions

# Initialize a persistent Chroma client.
# This will store the vector index on disk under ./chroma_db
client = chromadb.PersistentClient(path="./chroma_db")

# Try to read the OpenAI API key from environment variables
openai_key = os.getenv("OPENAI_API_KEY")

# Choose embedding function:
# - If OPENAI_API_KEY is set -> use OpenAI embeddings (higher quality, remote)
# - Otherwise -> fall back to a local/default embedding function (no external calls)
if openai_key:
    emb_fn = embedding_functions.OpenAIEmbeddingFunction(api_key=openai_key)
else:
    emb_fn = embedding_functions.DefaultEmbeddingFunction()

# Get or create a collection named "driver_policy".
# A collection is like a logical table for related documents and their embeddings.
collection = client.get_or_create_collection(
    name="driver_policy",
    embedding_function=emb_fn,
)

def index_document(file_path: str):
    """
    Read a text file, split it into chunks, and index those chunks into ChromaDB.
    """
    # Read the entire document from disk
    with open(file_path, 'r', encoding='utf-8') as f:
        text = f.read()
    
    # Naive chunking strategy: split the text by double newlines (paragraph-level)
    chunks = text.split('\n\n')
    
    # Create unique IDs for each chunk
    ids = [f"chunk_{i}" for i in range(len(chunks))]
    
    # Attach simple metadata to each chunk (can be extended later)
    metadatas = [{"source": "policy_v1", "chapter": "unknown"} for _ in chunks]
    
    # Upsert = insert new chunks or update existing ones with the same IDs
    collection.upsert(ids=ids, documents=chunks, metadatas=metadatas)
    
    # Print a simple confirmation message
    print(
        f"Indexed {len(chunks)} chunks into ChromaDB using "
        f"{'OpenAIEmbeddingFunction' if openai_key else 'DefaultEmbeddingFunction'}."
    )

if __name__ == "__main__":
    # Entry point for manual execution: index the sample policy file
    index_document("data/sample_policy.txt")
