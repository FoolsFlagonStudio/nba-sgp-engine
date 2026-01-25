# src/model/fanduel_lines.py

from math import floor
from typing import Dict, Any


# FanDuel legal ladders
FANDUEL_LADDERS = {
    "points":    [5, 8, 10, 12, 15, 18, 20, 25, 30, 35, 40, 45, 50],
    "rebounds":  [4, 6, 8, 10, 12, 14, 16],
    "assists":   [3, 4, 6, 8, 10, 12, 14],
    "threes":    [1, 2, 3, 4, 5, 6, 7, 8],
}


def snap_to_ladder(value: int, ladder: list[int]) -> int | None:
    for step in reversed(ladder):
        if value >= step:
            return step
    return None


def apply_fanduel_lines(stat_floors: Dict[int, Dict[str, Any]], buffer_pct: float = 0.10):
    results = {}

    for player_id, data in stat_floors.items():
        props = {}

        for stat, sdata in data["stats"].items():
            if stat not in FANDUEL_LADDERS:
                continue

            ladder = FANDUEL_LADDERS[stat]

            def snap(val):
                adjusted = floor(val * (1 - buffer_pct))
                return snap_to_ladder(adjusted, ladder)

            floor_line = snap(sdata["floor"])
            safe_line = snap(sdata["safe_alt"])

            if floor_line is None:
                continue

            props[stat] = {
                "floor": {
                    "line": floor_line,
                    "confidence": "STRONG_SAFE"
                },
                "straight": {
                    "line": safe_line,
                    "confidence": "SAFE"
                } if safe_line and safe_line > floor_line else None
            }

        if props:
            results[player_id] = {
                "player_name": data["player_name"],
                "team_id": data["team_id"],
                "props": props
            }

    return results
