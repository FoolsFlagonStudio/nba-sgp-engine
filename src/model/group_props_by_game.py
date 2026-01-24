# src/model/group_props_by_game.py

from collections import defaultdict
from typing import Dict, Any
import pandas as pd


def group_props_by_game(
    games_df: pd.DataFrame,
    fd_props: Dict[int, Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """
    Groups FanDuel props by game.

    Returns:
      {
        game_id: {
          "game_id": str,
          "home_team_id": int,
          "away_team_id": int,
          "props": [
            {
              "player_id": int,
              "player_name": str,
              "team_id": int,
              "stat": str,
              "line": int
            }
          ]
        }
      }
    """

    games_by_team = {}
    games = {}

    # Index games by team
    for _, row in games_df.iterrows():
        game_id = row["game_id"]
        home = row["home_team_id"]
        away = row["away_team_id"]

        games[game_id] = {
            "game_id": game_id,
            "home_team_id": home,
            "away_team_id": away,
            "props": []
        }

        games_by_team[home] = game_id
        games_by_team[away] = game_id

    # Assign props to games
    for player_id, pdata in fd_props.items():
        team_id = pdata["team_id"]
        game_id = games_by_team.get(team_id)

        if not game_id:
            continue

        for stat, line in pdata["props"].items():
            games[game_id]["props"].append({
                "player_id": player_id,
                "player_name": pdata["player_name"],
                "team_id": team_id,
                "stat": stat,
                "line": line
            })

    return games
