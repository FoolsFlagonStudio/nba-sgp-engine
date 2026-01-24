from src.ai.prompt_builder import build_prompt
from src.ai.decision_engine import run_decision_engine
from src.ai.response_validator import validate_response

MAX_RETRIES = 3

def generate_bets(by_game: dict) -> dict:
    """
    End-to-end AI bet generation.
    """

    prompt = build_prompt(by_game)

    for attempt in range(MAX_RETRIES):
        raw = run_decision_engine(prompt)
        parsed = validate_response(raw)

        if parsed is not None:
            return parsed

    # Hard fail-safe
    return {
        "straight_bets": [],
        "parlays": [],
        "notes": "NO BET — MODEL OUTPUT INVALID AFTER RETRIES"
    }
