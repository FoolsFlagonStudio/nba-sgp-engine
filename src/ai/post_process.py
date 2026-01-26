def add_parlay_type(bets: dict) -> dict:
    """
    Adds parlay_type (e.g. '3-leg', '5-leg') to each parlay
    AFTER schema validation.
    """
    for parlay in bets.get("parlays", []):
        parlay["parlay_type"] = f"{len(parlay['legs'])}-leg"
    return bets
