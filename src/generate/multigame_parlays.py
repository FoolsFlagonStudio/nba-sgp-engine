from itertools import combinations
from typing import List, Dict, Any
from collections import Counter
import logging
import time
log = logging.getLogger(__name__)


def team_limit_for_size(size: int) -> int:
    if size <= 3:
        return 1
    return 2


def market_cap_for_size(size: int) -> int:
    if size <= 3:
        return 1
    if size <= 5:
        return 2
    return 3


def validate_team_and_market_caps(legs: list[dict]) -> bool:
    size = len(legs)
    team_cap = team_limit_for_size(size)
    market_cap = market_cap_for_size(size)

    teams = Counter(l["team_id"] for l in legs)
    if any(v > team_cap for v in teams.values()):
        return False

    markets = Counter(l["market"] for l in legs)
    if any(v > market_cap for v in markets.values()):
        return False

    return True


def min_markets_for_size(size: int) -> int:
    if size <= 3:
        return 2
    if size <= 5:
        return 3
    return 3


def is_valid_multi_game_parlay(
    legs: List[Dict[str, Any]],
    size: int
) -> bool:
    # unique players (never allow same player twice)
    players = {p["player_id"] for p in legs}
    if len(players) != size:
        return False

    # team + market caps
    if not validate_team_and_market_caps(legs):
        return False

    # minimum market diversity
    markets = {p["market"] for p in legs}
    if len(markets) < min_markets_for_size(size):
        return False

    # confidence composition
    conf_counts = Counter(p["confidence"] for p in legs)
    c5 = conf_counts.get(5, 0)
    c4 = conf_counts.get(4, 0)
    c3 = conf_counts.get(3, 0)

    if size == 3:
        return (
            c5 >= 2 and
            c3 <= 1
        )

    if size == 5:
        return (
            c5 >= 3 and
            c3 <= 1 and
            c4 <= 2
        )

    if size >= 8:
        return (
            c3 == 0 and
            c5 >= size // 2
        )

    return False


def generate_multi_game_parlays(
    props: List[Dict[str, Any]],
    sizes=(3, 5),
    max_per_size=25
) -> Dict[str, List[Dict[str, Any]]]:

    results = {}

    log.info(
        "generate_multi_game_parlays: start (%d props, sizes=%s)",
        len(props),
        sizes
    )

    for size in sizes:
        t0 = time.time()
        parlays = []
        checked = 0

        log.info("Parlay size %d: generating combinations", size)

        for combo in combinations(props, size):
            checked += 1

            # heartbeat every N combos
            if checked % 5_000 == 0:
                log.info(
                    "Size %d: checked %d combos, found %d",
                    size,
                    checked,
                    len(parlays),
                )

            if is_valid_multi_game_parlay(list(combo), size):
                parlays.append({
                    "size": size,
                    "legs": list(combo),
                })

                log.info(
                    "Size %d: accepted parlay %d / %d",
                    size,
                    len(parlays),
                    max_per_size,
                )

            if len(parlays) >= max_per_size:
                log.info(
                    "Size %d: reached max_per_size (%d), stopping early",
                    size,
                    max_per_size,
                )
                break

        elapsed = time.time() - t0
        log.info(
            "Parlay size %d complete: %d checked, %d accepted (%.2fs)",
            size,
            checked,
            len(parlays),
            elapsed,
        )

        results[f"{size}_leg"] = parlays

    log.info("generate_multi_game_parlays: complete")

    return results
