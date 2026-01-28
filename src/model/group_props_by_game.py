# src/model/group_props_by_game.py

from typing import List, Dict, Any
import pandas as pd


def group_props_by_game(
    games: pd.DataFrame,
    props: List[Dict[str, Any]]
) -> Dict[str, Dict[str, Any]]:
    """
    Groups line-level props by game_id.
    Expects games to be a pandas DataFrame with:
      - game_id
      - home_team_id
      - away_team_id
    """

    # Build team_id -> game_id lookup
    team_to_game = {}

    for _, row in games.iterrows():
        game_id = row["game_id"]
        team_to_game[row["home_team_id"]] = game_id
        team_to_game[row["away_team_id"]] = game_id

    grouped: Dict[str, Dict[str, Any]] = {}

    for prop in props:
        team_id = prop["team_id"]
        game_id = team_to_game.get(team_id)

        if not game_id:
            continue

        if game_id not in grouped:
            grouped[game_id] = {
                "game_id": game_id,
                "props": []
            }

        grouped[game_id]["props"].append(prop)

    return grouped
