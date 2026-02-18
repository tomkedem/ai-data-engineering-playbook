# check_models.py
import os
import sys
from openai import OpenAI

# Verify the API key is set
api_key = (os.getenv("OPENAI_API_KEY") or "").strip()
if not api_key:
    print("Error: OPENAI_API_KEY environment variable is not set.")
    sys.exit(1)

client = OpenAI(api_key=api_key)

print("Fetching available models from OpenAI...")
try:
    # Fetch list of available models
    models = client.models.list()
    
    # Filter for chat/GPT models only (excluding Whisper, DALL-E, etc.)
    # We also explicitly include "o1" models as they are the new reasoning class
    gpt_models = [
        m.id for m in models.data 
        if "gpt" in m.id.lower() or "o1" in m.id.lower()
    ]
    
    # Sort for readability
    gpt_models.sort()
    
    print(f"\nFound {len(gpt_models)} GPT/Reasoning models available to you:\n")
    for model_id in gpt_models:
        print(f"- {model_id}")
        
except Exception as e:
    print(f"Error fetching models: {e}")
    sys.exit(1)
