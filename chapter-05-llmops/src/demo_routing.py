import logging
from llm_wrapper import SmartLLM

# Configure logging to see the output
logging.basicConfig(level=logging.INFO, format='%(message)s')

def run_demo():
    llm = SmartLLM()
    
    print("--- Test 1: Simple Query ---")
    # Should route to cheap model
    llm.generate("Hello, who are you?")
    
    print("\n--- Test 2: Complex Planning ---")
    # Should route to expensive model due to keyword 'plan'
    llm.generate("Please plan a strategic route for 50 trucks across Europe.")
    
    print("\n--- Test 3: Long Context ---")
    # Should route to expensive model due to length
    long_prompt = "Context: " + ("data " * 200) + " Question: Summary?"
    llm.generate(long_prompt)

if __name__ == "__main__":
    run_demo()
