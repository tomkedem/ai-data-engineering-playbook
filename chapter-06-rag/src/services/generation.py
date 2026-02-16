# src/services/generation.py
from typing import List
from src.interfaces import IngestionDocument

class MockLLMService:
    """
    Simulates the AI generation layer.
    It takes the retrieved documents (context) and the user question to form an answer.
    """
    def generate_answer(self, user_query: str, context_docs: List[IngestionDocument]) -> str:
        # 1. Analyze the Context
        # We look at what the retrieval step found in the database
        found_image = any("IMAGE FOUND" in d.content for d in context_docs)
        found_manifest = any("SHIPMENT ID" in d.content for d in context_docs)
        
        print(f"\n🧠 AI Processing Context...")
        for doc in context_docs:
            print(f"   > Evidence: {doc.content[:60]}...") # Print preview

        # 2. Formulate Answer (Rule-based simulation for the lab)
        if "damage" in user_query.lower() or "broken" in user_query.lower():
            if found_image:
                return "DETECTED DAMAGE: I have analyzed the image file 'damage_evidence.jpg'. The visual data confirms severe damage (Broken Glass)."
            else:
                return "No visual evidence of damage was found in the files."
        
        elif "manifest" in user_query.lower() or "id" in user_query.lower():
            if found_manifest:
                return "MANIFEST VERIFIED: The shipment ID is LS-2026-X containing High-End Glassware."
            
        return "I have analyzed the provided files but cannot answer that specific question."