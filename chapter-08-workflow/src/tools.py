# src/tools.py
from datetime import datetime

def tool_update_route(shipment_id: str, new_date: str) -> str:
    """
    Safe tool with a guardrail.
    Returns:
      Success: ...  on success
      Error: ...    on failure
    """
    try:
        dt = datetime.strptime(new_date, "%Y-%m-%d")
    except ValueError:
        return "Error: Invalid date format. Use YYYY-MM-DD."

    if dt < datetime.now():
        return f"Error: Date {new_date} is in the past! Time travel not allowed."

    print(f"   [DB] Updating shipment {shipment_id} to {new_date}...")
    return "Success: Route updated."


def registry() -> dict:
    return {
        "update_route": tool_update_route,
    }


def is_error(result: str) -> bool:
    return isinstance(result, str) and result.startswith("Error:")
