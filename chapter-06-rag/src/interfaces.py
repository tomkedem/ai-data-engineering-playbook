from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class IngestionDocument:
    """Standardized document object for our pipeline."""
    content: str
    metadata: Dict[str, Any]
    doc_id: Optional[str] = None

class VectorStoreInterface(ABC):
    """Abstract Base Class for any Vector Database wrapper."""
    
    @abstractmethod
    def add_documents(self, documents: List[IngestionDocument]) -> bool:
        """Adds a batch of documents to the store."""
        pass

    @abstractmethod
    def search(self, query_text: str, limit: int = 3) -> List[IngestionDocument]:
        """Performs semantic search."""
        pass
