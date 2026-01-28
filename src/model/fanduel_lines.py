# src/model/fanduel_lines.py

from typing import Dict, Any, List
from math import floor

FANDUEL_LADDERS = {
    "points":   [15, 18, 20, 25, 30, 35, 40, 45, 50],
    "rebounds": [4, 6, 8, 10, 12, 14, 16],
    "assists":  [3, 4, 6, 8, 10, 12, 14],
    "threes":   [1, 2, 3, 4, 5, 6, 7, 8],
}

FLOOR_PCT = 0.85
MIN_HITS = 3  # keep 3/5+


def snap_to_ladder(value: float, ladder: List[int]) -> int | None:
    for step in reversed(ladder):
        if value >= step:
            return step
    return None


def apply_fanduel_lines(cleaned_players: Dict[int, Dict[str, Any]]):
    """
    Generates line-level props from cleaned last-5 stats.
    Returns a flat list of props.
    """
    results = []
    for pid, p in cleaned_players.items():
        stats = p.get("stats", {})

        for stat, ladder in FANDUEL_LADDERS.items():
            sdata = stats.get(stat)
            if not sdata:
                continue

            values = sdata.get("values")
            if not values:
                continue

            values = [int(v) for v in values]

            min_val = min(values)
            dynamic_floor = snap_to_ladder(min_val * FLOOR_PCT, ladder)
            if dynamic_floor is None:
                continue

            for line in ladder:
                if line < dynamic_floor:
                    continue

                hits = sum(1 for v in values if v >= line)
                if hits < MIN_HITS:
                    continue

                results.append({
                    "player_id": pid,
                    "player": p["player_name"],
                    "team_id": p["team_id"],
                    "market": stat,
                    "line": line,
                    "confidence": hits,
                    "hit_rate_last_5": hits / 5,
                })


    return results
