import uuid
from typing import List
from src.interfaces import VectorStoreInterface, IngestionDocument

class TextIngestionService:
    def __init__(self, vector_store: VectorStoreInterface, chunk_size: int = 50, chunk_overlap: int = 10):
        self.vector_store = vector_store
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _create_chunks(self, text: str) -> List[str]:
        """
        Simple overlapping chunker. In production, use LangChain's RecursiveCharacterTextSplitter.
        """
        words = text.split()
        chunks = [] 
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk = " ".join(words[i:i + self.chunk_size])
            chunks.append(chunk)
        return chunks

    def ingest_text(self, text: str, source_metadata: dict) -> int:
        """
        Orchestrates the ingestion flow: Chunk -> Wrap -> Store.
        Returns the number of chunks indexed.
        """
        chunks = self._create_chunks(text)
        docs_to_ingest = []
        
        for idx, chunk_text in enumerate(chunks):
            # Create a rich metadata object for traceability
            meta = {
                **source_metadata,
                "chunk_index": idx,
                "total_chunks": len(chunks)
            }
            
            doc = IngestionDocument(
                content=chunk_text,
                metadata=meta,
                doc_id=str(uuid.uuid4())
            )
            docs_to_ingest.append(doc)
        
        # Delegate storage to the interface implementation
        success = self.vector_store.add_documents(docs_to_ingest)
        if not success:
            raise RuntimeError("Failed to store documents in Vector DB.")
            
        return len(docs_to_ingest)
