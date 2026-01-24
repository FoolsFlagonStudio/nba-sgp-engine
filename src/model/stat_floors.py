import math


def compute_stat_floors(cleaned_players: dict) -> dict:
    """
    For each player, compute eligible stat floors
    based strictly on last-5 consistency.
    """

    result = {}

    for pid, p in cleaned_players.items():
        floors = {}

        # Points: always eligible
        floors["points"] = min(p["points"])

        # Rebounds
        if min(p["rebounds"]) > 0:
            floors["rebounds"] = min(p["rebounds"])

        # Assists
        if min(p["assists"]) > 0:
            floors["assists"] = min(p["assists"])

        # 3PM
        if min(p["threes"]) > 0:
            floors["threes"] = min(p["threes"])

        # Player must have at least ONE eligible stat
        if floors:
            result[pid] = {
                "player_name": p["player_name"],
                "team_id": p["team_id"],
                "floors": floors,
                "raw": p,
            }

    return result
