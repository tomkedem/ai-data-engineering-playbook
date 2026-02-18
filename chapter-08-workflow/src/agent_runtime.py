from __future__ import annotations

import json
from typing import Any, Dict, List, Optional, Tuple

from state import AgentState
from tools import registry as tool_registry, is_error as tool_is_error
from model_adapter import ModelAdapter

Message = Dict[str, str]

SYSTEM_PROMPT = """
You are a LogiSmart Logistics Agent.
You MUST output exactly one valid JSON object and nothing else.

Schema:
{
  "action": "call_tool" or "finish",
  "tool_name": string, only if action is call_tool
  "tool_args": object, only if action is call_tool
  "response": string only if action is finish
}

Rules:
1. If the user provides a specific date, ALWAYS call update_route with that exact date first.
2. If update_route returns Error, do NOT try the same date again.
3. Instead, explain the error naturally to the user (e.g., "I tried to update... but...") and ask for a valid date.
"""

def _decoder_extract_first_object(text: str) -> Optional[Dict[str, Any]]:
    """
    Safer than brace counting.
    Finds first JSON object and parses it using JSONDecoder.raw_decode.
    """
    decoder = json.JSONDecoder()
    start = text.find("{")
    while start != -1:
        try:
            obj, _end = decoder.raw_decode(text[start:])
            if isinstance(obj, dict):
                return obj
            return None
        except json.JSONDecodeError:
            start = text.find("{", start + 1)
    return None

def _validate_decision(obj: Dict[str, Any]) -> Tuple[bool, str]:
    action = obj.get("action")
    if action not in ("call_tool", "finish"):
        return False, "Invalid action"
    
    if action == "call_tool":
        if not isinstance(obj.get("tool_name"), str) or not obj["tool_name"].strip():
            return False, "Missing tool_name"
        if not isinstance(obj.get("tool_args"), dict):
            return False, "Missing tool_args"
            
    if action == "finish":
        if not isinstance(obj.get("response"), str):
            return False, "Missing response"
            
    return True, ""

def _repair_json_only(adapter: ModelAdapter, messages: List[Message], bad: str, reason: str) -> Optional[Dict[str, Any]]:
    repair_msg = f"""
Your previous output was invalid.
Reason:
{reason}

Previous output:
{bad}

Return ONLY one valid JSON object matching the schema.
No markdown. No extra text.
"""
    repaired = adapter.complete(messages + [{"role": "user", "content": repair_msg}])
    return _decoder_extract_first_object(repaired)

def _as_messages(state: AgentState) -> List[Message]:
    msgs: List[Message] = [{"role": "system", "content": SYSTEM_PROMPT}]
    for m in state["messages"]:
        if isinstance(m, dict) and "role" in m and "content" in m:
            role = str(m["role"])
            content = str(m["content"])
            if role in {"system", "user", "assistant"}:
                msgs.append({"role": role, "content": content})
            else:
                msgs.append({"role": "user", "content": f"[{role}] {content}"})
        else:
            msgs.append({"role": "user", "content": str(m)})
    return msgs

def run_agent(
    state: AgentState,
    user_text: str,
    adapter: ModelAdapter,
    *,
    max_steps: int = 8,
    max_repairs_per_step: int = 2,
) -> Dict[str, Any]:
    """
    Updates state in place.
    Logs steps to console for visibility (Thinking -> Action -> Output).
    """
    if not isinstance(state.get("messages"), list):
        state["messages"] = []
    
    state["messages"].append({"role": "user", "content": str(user_text)})
    
    tools = tool_registry()
    last_failed_date: Optional[str] = None
    last_tool_error: Optional[str] = None

    for _ in range(max_steps):
        messages = _as_messages(state)
        raw = adapter.complete(messages)
        decision = _decoder_extract_first_object(raw)
        
        # Repair logic
        repairs_left = max_repairs_per_step
        while decision is None and repairs_left > 0:
            decision = _repair_json_only(adapter, messages, raw, "No valid JSON object found")
            repairs_left -= 1
            
        if decision is None:
            final = {"action": "finish", "response": "Error: model returned no valid JSON"}
            state["messages"].append({"role": "assistant", "content": final["response"]})
            state["is_complete"] = True
            return final

        # Validate logic
        ok, err = _validate_decision(decision)
        while not ok and repairs_left > 0:
            decision2 = _repair_json_only(adapter, messages, json.dumps(decision), err)
            repairs_left -= 1
            if decision2 is None:
                break
            decision = decision2
            ok, err = _validate_decision(decision)

        if not ok:
            final = {"action": "finish", "response": f"Error: invalid decision schema: {err}"}
            state["messages"].append({"role": "assistant", "content": final["response"]})
            state["is_complete"] = True
            return final

        # --- EXECUTION LOGIC ---

        if decision["action"] == "finish":          
            state["messages"].append({"role": "assistant", "content": decision["response"]})
            state["is_complete"] = True
            return decision

        # It's a tool call
        tool_name = decision["tool_name"]
        tool_args = decision["tool_args"]

        # LOGGING: The "Thinking" step
        print(f"   [Thinking] I should call {tool_name} with {tool_args}...")

        if tool_name not in tools:
            final = {"action": "finish", "response": f"Error: unknown tool {tool_name}"}
            state["messages"].append({"role": "assistant", "content": final["response"]})
            state["is_complete"] = True
            return final

        # Normalizing args (hallucination fix)
        if tool_name == "update_route":
            if "new_date" not in tool_args:
                for date_key in ("date", "newDate", "route_date"):
                    if date_key in tool_args:
                        tool_args["new_date"] = tool_args[date_key]
                        break
            if "shipment_id" not in tool_args and isinstance(state.get("shipment_id"), str) and state["shipment_id"]:
                tool_args["shipment_id"] = state["shipment_id"]
        
        # Guardrail: Prevent infinite loop on same bad input
        new_date = str(tool_args.get("new_date", "")).strip()
        if last_failed_date and new_date == last_failed_date:
            final = {"action": "finish", "response": f"{last_tool_error} Please provide a different valid date."}
            state["messages"].append({"role": "assistant", "content": final["response"]})
            state["is_complete"] = True
            return final

        # Execute Tool
        try:
            result = tools[tool_name](**tool_args)
        except Exception as e:
            result = f"Error: Tool execution failed: {str(e)}"
        
        # LOGGING: The "Output" step
        print(f"   [Tool Output] {result}")

        # Update state based on tool result
        if tool_name == "update_route":
            if tool_is_error(result):
                last_failed_date = new_date
                last_tool_error = result
            else:
                last_failed_date = None
                last_tool_error = None
        
        # Add tool output to history so the model sees it in the next loop!
        state["messages"].append({"role": "tool", "content": f"{tool_name} result: {result}"})
    
    # End of loop
    final = {"action": "finish", "response": "Error: step limit reached"}
    state["messages"].append({"role": "assistant", "content": final["response"]})
    state["is_complete"] = True
    return final
