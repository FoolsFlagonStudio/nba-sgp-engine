from typing import Dict, Any, List
from collections import defaultdict
import logging
import time

log = logging.getLogger(__name__)


def generate_straights(
    by_game: Dict[str, Dict[str, Any]],
    min_confidence: int = 3
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Generates a full menu of straight prop candidates grouped by market.
    Acts as a 'build-your-own parlay' surface, not a bet selector.
    """

    t_start = time.time()
    log.info("generate_straights: start")

    # 1. Flatten all props
    all_props: List[Dict[str, Any]] = []
    games = list(by_game.values())

    for i, game in enumerate(games):
        if i % 5 == 0:
            log.info("Flattening props: game %d / %d", i + 1, len(games))

        all_props.extend(game["props"])

    log.info("Flattened %d total props", len(all_props))

    # 2. Filter by confidence floor
    filtered = [
        p for p in all_props
        if p["confidence"] >= min_confidence
    ]

    log.info(
        "Confidence filter >= %d: %d → %d props",
        min_confidence,
        len(all_props),
        len(filtered),
    )

    # 3. Score + risk tagging
    for i, p in enumerate(filtered):
        if i % 25 == 0:
            log.info("Scoring props: %d / %d", i + 1, len(filtered))

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

    log.info("Scoring complete")

    # 4. Group by market (keep sorted order for UX)
    grouped = defaultdict(list)
    sorted_props = sorted(filtered, key=lambda x: x["score"], reverse=True)

    for i, p in enumerate(sorted_props):
        if i % 25 == 0:
            log.info("Grouping props: %d / %d", i + 1, len(sorted_props))

        grouped[p["market"]].append(p)

    elapsed = time.time() - t_start
    log.info(
        "generate_straights complete in %.2fs (%d markets)",
        elapsed,
        len(grouped),
    )

    return dict(grouped)
