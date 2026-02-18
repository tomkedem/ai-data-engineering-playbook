# src/state.py
from typing import TypedDict, List, Optional

class AgentState(TypedDict):
    """
    The brain's short-term memory.
    Holds the conversation history and the structured facts we've gathered.
    """
    messages: List[dict]         # The conversation log (role: user/assistant)
    shipment_id: Optional[str]   # Extracted shipment ID
    is_complete: bool            # Task completion flag