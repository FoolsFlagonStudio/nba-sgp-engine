import json

def validate_response(response: str) -> dict | None:
    try:
        data = json.loads(response)
    except json.JSONDecodeError:
        return None

    if not isinstance(data, dict):
        return None

    if "straight_bets" not in data or "parlays" not in data:
        return None

    return data
