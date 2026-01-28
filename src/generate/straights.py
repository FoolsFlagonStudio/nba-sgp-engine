from typing import Dict, Any, List
from collections import defaultdict


def generate_straights(
    by_game: Dict[str, Dict[str, Any]],
    max_total: int = 50,
    min_confidence: int = 3
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generates a menu of straight bets grouped by market.
    """

    # 1. Flatten all props
    all_props: List[Dict[str, Any]] = []
    for game in by_game.values():
        all_props.extend(game["props"])

    # 2. Filter by confidence
    filtered = [
        p for p in all_props
        if p["confidence"] >= min_confidence
    ]

    # 3. Score props (v1 scoring)
    for p in filtered:
        p["score"] = (
            p["confidence"] * 10
            + p["hit_rate_last_5"] * 5
        )

        if p["confidence"] == 5:
            p["risk"] = "core"
        elif p["confidence"] == 4:
            p["risk"] = "moderate"
        else:
            p["risk"] = "aggressive"

    # 4. Sort globally by score
    filtered.sort(key=lambda x: x["score"], reverse=True)

    # 5. Group by market
    grouped = defaultdict(list)
    for p in filtered:
        grouped[p["market"]].append(p)

    # 6. Trim to max_total while preserving market grouping
    result = {}
    total = 0

    for market, props in grouped.items():
        if total >= max_total:
            break

        remaining = max_total - total
        take = min(len(props), remaining)

        result[market] = props[:take]
        total += take

    return result
