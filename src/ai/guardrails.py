def validate_players_are_active(bets: dict, active_team_ids: set[int]) -> bool:
    """
    Ensures every bet references a player on an active team.
    """

    def check_leg(leg):
        return leg.get("team_id") in active_team_ids

    # Straight bets
    for bet in bets.get("straight_bets", []):
        if not check_leg(bet):
            return False

    # Parlays
    for parlay in bets.get("parlays", []):
        for leg in parlay.get("legs", []):
            if not check_leg(leg):
                return False

    return True
