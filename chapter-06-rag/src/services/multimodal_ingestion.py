# src/services/multimodal_ingestion.py
import os
from typing import List
from PIL import Image  # This handles the actual image binary data
from src.interfaces import VectorStoreInterface, IngestionDocument
from src.models import ShipmentCase
from src.services.text_ingestion import TextIngestionService

class MultimodalIngestionService:
    def __init__(self, vector_store: VectorStoreInterface, text_service: TextIngestionService):
        self.vector_store = vector_store
        self.text_service = text_service

    def _extract_image_features(self, file_path: str) -> str:
        """
        Opens the physical file, verifies it's an image, and extracts metadata.
        In a real AI system, this is where we would send the image bytes to CLIP/Gemini.
        """
        try:
            with Image.open(file_path) as img:
                # We are actually reading the binary header of the file here
                width, height = img.size
                format_desc = img.format_description
                filename = os.path.basename(file_path)
                
                # We return a structured description of what we found
                return f"[IMAGE FOUND: File={filename} | Dim={width}x{height} | Type={format_desc}]"
        except Exception as e:
            print(f"❌ Error opening image {file_path}: {e}")
            return "[IMAGE ERROR: Corrupt or missing file]"

    def _read_text_file(self, file_path: str) -> str:
        """Reads the raw content of a text file from disk."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                filename = os.path.basename(file_path)
                return f"[FILE CONTENT ({filename}): {content}]"
        except Exception as e:
             return f"[TEXT ERROR: {e}]"

    def ingest_case(self, case: ShipmentCase) -> int:
        print(f"--- 📥 Starting Ingestion for Case: {case.shipment_id} ---")
        docs_to_ingest = []

        for artifact in case.artifacts:
            # Validation: Does the file actually exist?
            if not os.path.exists(artifact.content_path):
                print(f"⚠️ Warning: File not found at {artifact.content_path}")
                continue

            base_metadata = {
                "parent_id": case.shipment_id,
                "type": artifact.artifact_type,
                **artifact.metadata
            }

            # Branching logic based on artifact type
            if artifact.artifact_type == 'damage_photo':
                # Open and process the image file
                visual_description = self._extract_image_features(artifact.content_path)
                
                doc = IngestionDocument(
                    content=visual_description, 
                    metadata=base_metadata,
                    doc_id=f"{case.shipment_id}_{artifact.artifact_type}"
                )
                docs_to_ingest.append(doc)
                print(f"📸 Processed Real Image: {artifact.content_path}")

            elif artifact.artifact_type == 'ocr_text':
                # Open and read the text file
                text_content = self._read_text_file(artifact.content_path)
                
                doc = IngestionDocument(
                    content=text_content,
                    metadata=base_metadata,
                    doc_id=f"{case.shipment_id}_{artifact.artifact_type}"
                )
                docs_to_ingest.append(doc)
                print(f"📄 Processed Real Text: {artifact.content_path}")

        # Store everything in the vector DB
        self.vector_store.add_documents(docs_to_ingest)
        return len(docs_to_ingest)