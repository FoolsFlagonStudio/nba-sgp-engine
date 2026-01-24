from collections import defaultdict
from src.fetch.boxscore import get_boxscore_players
import time


def build_player_last5_stats(
    last5_games_by_team: dict[int, list[str]],
    sleep_sec: float = 0.4
) -> dict[int, dict]:
    """
    Builds per-player last-5 stat arrays.

    Returns:
      {
        player_id: {
          "player_name": str,
          "team_id": int,
          "games": [game_id x5],
          "points": [...],
          "rebounds": [...],
          "assists": [...],
          "threes": [...],
          "minutes": [...]
        }
      }
    """

    players = defaultdict(lambda: {
        "player_name": None,
        "team_id": None,
        "games": [],
        "points": [],
        "rebounds": [],
        "assists": [],
        "threes": [],
        "minutes": [],
    })

    for team_id, game_ids in last5_games_by_team.items():
        for game_id in game_ids:
            box_players = get_boxscore_players(game_id)

            for p in box_players:
                pid = p["player_id"]

                players[pid]["player_name"] = p["player_name"]
                players[pid]["team_id"] = p["team_id"]
                players[pid]["games"].append(game_id)
                players[pid]["points"].append(p["points"])
                players[pid]["rebounds"].append(p["rebounds"])
                players[pid]["assists"].append(p["assists"])
                players[pid]["threes"].append(p["threes"])
                players[pid]["minutes"].append(p["minutes"])

            time.sleep(sleep_sec)

    return players
