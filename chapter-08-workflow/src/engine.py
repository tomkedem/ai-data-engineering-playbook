# src/engine.py
from state import AgentState
from openai_adapter import OpenAIAdapter
from agent_runtime import run_agent

if __name__ == "__main__":
    print("--- Starting LogiSmart Autonomous Agent Lab ---")

    state: AgentState = {
        "messages": [],
        "shipment_id": None,
        "is_complete": False
    }

    adapter = OpenAIAdapter(model="gpt-4o", temperature=0.1)

    run_agent(
        state,
        "Please move shipment LS-2026-X to yesterday (2020-01-01) because I forgot.",
        adapter
    )

    if state["messages"]:
        last_msg = state["messages"][-1]
        # Support different formats: content, response, text
        last = last_msg.get("content") or last_msg.get("response") or str(last_msg)
    else:
        last = ""

    print(f"Agent: {last}")
    
