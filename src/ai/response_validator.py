import json
from jsonschema import validate, ValidationError

from src.ai.schemas import BET_SCHEMA


def validate_response(raw: str) -> dict | None:
    # 1️⃣ Parse JSON
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as e:
        print("❌ JSON PARSE ERROR")
        print(str(e))
        return None

    # 2️⃣ Enforce schema
    try:
        validate(instance=data, schema=BET_SCHEMA)
    except ValidationError as e:
        print("❌ SCHEMA VALIDATION FAILED")
        print(e.message)
        print("❌ FAILED AT PATH:", list(e.absolute_path))
        return None

    # 3️⃣ Ensure required top-level keys (your existing behavior)
    data.setdefault("straight_bets", [])
    data.setdefault("parlays", [])
    data.setdefault("notes", "")

    return data
