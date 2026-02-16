# src/main_multimodal.py
import os
from src.infrastructure.chroma_store import ChromaVectorStore
from src.services.text_ingestion import TextIngestionService
from src.services.multimodal_ingestion import MultimodalIngestionService
from src.services.generation import MockLLMService
from src.models import ShipmentCase, ShipmentArtifact

def run_real_lab():
    # --- SETUP ---
    # Define paths to the REAL files we created in Step 1
    base_dir = os.path.join(os.getcwd(), "data")
    img_path = os.path.join(base_dir, "damage_evidence.jpg")
    txt_path = os.path.join(base_dir, "shipping_manifest.txt")

    # Initialize System
    vector_db = ChromaVectorStore(collection_name="logismart_real_files")
    vector_db.reset() # Clean slate
    
    text_svc = TextIngestionService(vector_db)
    multimodal_svc = MultimodalIngestionService(vector_db, text_svc)
    llm = MockLLMService()

    # --- STEP 1: INGESTION (IO Operations) ---
    print(f"📂 Reading files from: {base_dir}")
    
    case = ShipmentCase(
        shipment_id="LS-2026-X",
        customer_id="GLOBAL-IMPORTS-LTD",
        artifacts=[
            # We point the system to the actual files on your disk
            ShipmentArtifact(img_path, "damage_photo", {"camera": "Dock-04"}),
            ShipmentArtifact(txt_path, "ocr_text", {"scanner": "Gate-1"})
        ]
    )
    
    # This triggers the real file opening logic
    multimodal_svc.ingest_case(case)

    # --- STEP 2: RAG CHAT (The User Experience) ---
    user_question = "What evidence of damage do we have?"
    print(f"\n👤 User Question: '{user_question}'")
    
    # A. Retrieve
    results = vector_db.search("damage", limit=3)
    
    # B. Generate
    answer = llm.generate_answer(user_question, results)
    
    print(f"\n💡 LogiSmart AI Answer: {answer}")

if __name__ == "__main__":
    run_real_lab()