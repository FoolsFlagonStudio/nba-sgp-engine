import re

DEBUG_ORDER = True          # 👈 flip this on/off
DEBUG_LIMIT = 3             # only log first N players


def _parse_minutes(min_str: str) -> float:
    """
    Convert 'PT32M21.00S' → 32.35
    """
    if not min_str or min_str == "PT00M00.00S":
        return 0.0

    m = re.match(r"PT(\d+)M([\d.]+)S", min_str)
    if not m:
        return 0.0

    minutes = int(m.group(1))
    seconds = float(m.group(2))
    return minutes + seconds / 60


def clean_player_last5(player_stats: dict) -> dict:
    """
    Enforces:
    - 5 unique games
    - non-zero minutes
    - minimum average minutes
    - logs game order for inspection
    """

    cleaned = {}
    MIN_AVG_MINUTES = 18
    debug_count = 0

    for pid, p in player_stats.items():
        seen = {}
        for i, gid in enumerate(p["games"]):
            if gid not in seen:
                seen[gid] = i

        idxs = list(seen.values())

        if len(idxs) < 5:
            continue

        idxs = sorted(seen.values())[:5]


        minutes = [_parse_minutes(p["minutes"][i]) for i in idxs]

        if any(m == 0 for m in minutes):
            continue

        avg_minutes = sum(minutes) / len(minutes)
        if avg_minutes < MIN_AVG_MINUTES:
            continue

        # 🔍 DEBUG LOGGING — inspect game order
        if DEBUG_ORDER and debug_count < DEBUG_LIMIT:
            print("\nDEBUG PLAYER:", p["player_name"])
            for i in idxs:
                print(
                    f"  index={i} "
                    f"game_id={p['games'][i]} "
                    f"minutes={minutes[idxs.index(i)]:.1f}"
                )
            debug_count += 1

        cleaned[pid] = {
            "player_name": p["player_name"],
            "team_id": p["team_id"],
            "games": [p["games"][i] for i in idxs],
            "minutes": minutes,
            "points": [p["points"][i] for i in idxs],
            "rebounds": [p["rebounds"][i] for i in idxs],
            "assists": [p["assists"][i] for i in idxs],
            "threes": [p["threes"][i] for i in idxs],
        }

    return cleaned
