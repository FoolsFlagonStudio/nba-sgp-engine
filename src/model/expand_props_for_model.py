def expand_props_for_model(by_game: dict) -> dict:
    """
    Flattens nested floor/straight props into model-consumable rows.
    """

    expanded = {}

    for game_id, game in by_game.items():
        rows = []

        for p in game["props"]:
            base = {
                "player_id": p["player_id"],
                "player_name": p["player_name"],
                "team_id": p["team_id"],
                "stat": p["stat"],
            }

            floor = p["line"].get("floor")
            if floor:
                rows.append({
                    **base,
                    "line": floor["line"],
                    "line_type": "floor",
                    "confidence": floor["confidence"],
                })

            straight = p["line"].get("straight")
            if straight:
                rows.append({
                    **base,
                    "line": straight["line"],
                    "line_type": "straight",
                    "confidence": straight["confidence"],
                })

        expanded[game_id] = {
            **game,
            "props": rows
        }

    return expanded
