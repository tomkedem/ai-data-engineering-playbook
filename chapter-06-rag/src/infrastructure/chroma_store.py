import chromadb
from src.interfaces import VectorStoreInterface, IngestionDocument
from typing import List

class ChromaVectorStore(VectorStoreInterface):
    def __init__(self, collection_name: str, persist_path: str = "./.chromadb"):
        self.client = chromadb.PersistentClient(path=persist_path)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def reset(self):
        """Clears all data in the collection."""
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.get_or_create_collection(name=self.collection.name)
    def add_documents(self, documents: List[IngestionDocument]) -> bool:
        try:
            ids = [doc.doc_id for doc in documents]
            contents = [doc.content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            self.collection.upsert(
                ids=ids,
                documents=contents,
                metadatas=metadatas
            )
            return True
        except Exception as e:
            print(f"ChromaDB Error: {e}")
            return False

    def search(self, query_text: str, limit: int = 3) -> List[IngestionDocument]:
        results = self.collection.query(query_texts=[query_text], n_results=limit)
        # Convert back to our standard IngestionDocument format
        docs = []
        if results['documents']:
            for i in range(len(results['documents'][0])):
                docs.append(IngestionDocument(
                    content=results['documents'][0][i],
                    metadata=results['metadatas'][0][i],
                    doc_id=results['ids'][0][i]
                ))
        return docs
