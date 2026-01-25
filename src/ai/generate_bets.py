from src.ai.prompt_builder import build_prompt
from src.ai.decision_engine import run_decision_engine
from src.ai.response_validator import validate_response
from src.ai.guardrails import validate_players_are_active

MAX_RETRIES = 1


def generate_bets(by_game: dict, active_team_ids: set[int]) -> dict:
    prompt = build_prompt(by_game)

    print("=== PROMPT SENT TO MODEL ===")
    print(prompt)

    for attempt in range(MAX_RETRIES):
        raw = run_decision_engine(prompt)

        print(f"=== RAW MODEL RESPONSE (attempt {attempt + 1}) ===")
        print(raw)

        parsed = validate_response(raw)

        if parsed is None:
            break
        
        if parsed and validate_players_are_active(parsed, active_team_ids):
            return parsed

    return {
        "straight_bets": [],
        "parlays": [],
        "notes": "NO BET — MODEL OUTPUT INVALID AFTER RETRIES"
    }
