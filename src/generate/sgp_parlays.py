from itertools import combinations
from collections import Counter
from typing import List, Dict, Any
import logging
import time

log = logging.getLogger(__name__)


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
    if len({l["player_id"] for l in legs}) != size:
        return False

    teams = Counter(l["team_id"] for l in legs)
    if any(v > team_cap_for_sgp(size) for v in teams.values()):
        return False

    markets = Counter(l["market"] for l in legs)
    if any(v > market_cap_for_sgp(size) for v in markets.values()):
        return False

    if violates_same_player_correlation(legs):
        return False

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

    log.info(
        "generate_sgp_parlays: start (%d games, sizes=%s)",
        len(game_props),
        sizes
    )

    for game_idx, (game_id, game) in enumerate(game_props.items(), start=1):
        props = game["props"]
        game_results = {}

        log.info(
            "SGP game %d / %d: %s (%d props)",
            game_idx,
            len(game_props),
            game_id,
            len(props),
        )

        for size in sizes:
            t0 = time.time()
            sgps = []
            checked = 0

            log.info(
                "Game %s: generating %d-leg SGPs",
                game_id,
                size,
            )

            for combo in combinations(props, size):
                checked += 1

                # heartbeat every N combos
                if checked % 2_000 == 0:
                    log.info(
                        "Game %s | %d-leg: checked %d combos, found %d",
                        game_id,
                        size,
                        checked,
                        len(sgps),
                    )

                if validate_sgp(list(combo), size):
                    sgps.append({
                        "game_id": game_id,
                        "size": size,
                        "legs": list(combo),
                    })

                    log.info(
                        "Game %s | %d-leg: accepted %d / %d",
                        game_id,
                        size,
                        len(sgps),
                        max_per_game,
                    )

                if len(sgps) >= max_per_game:
                    log.info(
                        "Game %s | %d-leg: reached max_per_game (%d), stopping",
                        game_id,
                        size,
                        max_per_game,
                    )
                    break

            elapsed = time.time() - t0
            log.info(
                "Game %s | %d-leg complete: %d checked, %d accepted (%.2fs)",
                game_id,
                size,
                checked,
                len(sgps),
                elapsed,
            )

            game_results[f"{size}_leg"] = sgps

        results[game_id] = game_results

    log.info("generate_sgp_parlays: complete")

    return results
