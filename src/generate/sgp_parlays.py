# src/model/sgp.py

from itertools import combinations
from collections import Counter
from typing import List, Dict, Any


def team_cap_for_sgp(size: int) -> int:
    if size <= 3:
        return 2
    return 3


def market_cap_for_sgp(size: int) -> int:
    if size <= 3:
        return 2
    if size <= 5:
        return 3
    return 4


def confidence_ok(legs: list[dict], size: int) -> bool:
    counts = Counter(l["confidence"] for l in legs)
    c5 = counts.get(5, 0)
    c4 = counts.get(4, 0)
    c3 = counts.get(3, 0)

    if size == 3:
        return c5 >= 2 and c3 <= 1

    if size == 5:
        return c5 >= 3 and c3 <= 1 and c4 <= 2

    if size >= 8:
        return c3 == 0 and c5 >= size // 2

    return False


def violates_same_player_correlation(legs: list[dict]) -> bool:
    by_player = {}

    for l in legs:
        by_player.setdefault(l["player_id"], set()).add(l["market"])

    for markets in by_player.values():
        if len(markets) > 1:
            return True

    return False


def validate_sgp(legs: list[dict], size: int) -> bool:
    # unique players
    if len({l["player_id"] for l in legs}) != size:
        return False

    # team caps
    teams = Counter(l["team_id"] for l in legs)
    if any(v > team_cap_for_sgp(size) for v in teams.values()):
        return False

    # market caps
    markets = Counter(l["market"] for l in legs)
    if any(v > market_cap_for_sgp(size) for v in markets.values()):
        return False

    # correlation rules
    if violates_same_player_correlation(legs):
        return False

    # confidence rules
    return confidence_ok(legs, size)


def generate_sgp_parlays(
    game_props: dict,
    sizes=(3, 5),
    max_per_game=20
) -> dict:
    """
    game_props format:
    {
      game_id: {
        "game_id": str,
        "props": [ {...}, {...} ]
      }
    }
    """

    results = {}

    for game_id, game in game_props.items():
        props = game["props"]
        game_results = {}

        for size in sizes:
            sgps = []

            for combo in combinations(props, size):
                if validate_sgp(list(combo), size):
                    sgps.append({
                        "game_id": game_id,
                        "size": size,
                        "legs": list(combo)
                    })

                if len(sgps) >= max_per_game:
                    break

            game_results[f"{size}_leg"] = sgps

        results[game_id] = game_results

    return results
