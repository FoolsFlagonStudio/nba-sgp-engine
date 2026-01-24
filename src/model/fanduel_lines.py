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


def snap_to_ladder(value: float, ladder: list[int]) -> int | None:
    """
    Snap DOWN to nearest valid FanDuel ladder value.
    Returns None if value cannot be snapped.
    """
    for step in reversed(ladder):
        if value >= step:
            return step
    return None


def apply_fanduel_lines(stat_floors, buffer_pct=0.10):
    results = {}

    for player_id, data in stat_floors.items():
        props = {}

        for stat, floor_value in data["floors"].items():
            if stat not in FANDUEL_LADDERS:
                continue

            # 🔒 hard safety buffer + integer floor
            adjusted = floor(floor_value * (1 - buffer_pct))

            # snap DOWN to FanDuel ladder
            for step in reversed(FANDUEL_LADDERS[stat]):
                if adjusted >= step:
                    props[stat] = step
                    break

        if props:
            results[player_id] = {
                "player_name": data["player_name"],
                "team_id": data["team_id"],
                "props": props
            }

    return results