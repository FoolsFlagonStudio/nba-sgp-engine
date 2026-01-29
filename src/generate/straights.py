from typing import Dict, Any, List
from collections import defaultdict


def generate_straights(
    by_game: Dict[str, Dict[str, Any]],
    min_confidence: int = 3
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generates a full menu of straight prop candidates grouped by market.
    Acts as a 'build-your-own parlay' surface, not a bet selector.
    """

    # 1. Flatten all props
    all_props: List[Dict[str, Any]] = []
    for game in by_game.values():
        all_props.extend(game["props"])

    # 2. Filter by confidence floor
    filtered = [
        p for p in all_props
        if p["confidence"] >= min_confidence
    ]

    # 3. Score + risk tagging
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

    # 4. Group by market (keep sorted order for UX)
    grouped = defaultdict(list)
    for p in sorted(filtered, key=lambda x: x["score"], reverse=True):
        grouped[p["market"]].append(p)

    return dict(grouped)
