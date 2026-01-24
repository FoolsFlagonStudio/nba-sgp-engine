from nba_api.live.nba.endpoints import boxscore
import time


def get_boxscore_players(game_id: str) -> list[dict]:
    """
    Returns a list of player stat dicts for a completed game.
    """
    bs = boxscore.BoxScore(game_id=game_id)
    game = bs.get_dict()["game"]

    players = []

    for side in ("homeTeam", "awayTeam"):
        team = game[side]
        team_id = team["teamId"]

        for p in team["players"]:
            stats = p.get("statistics", {})
            minutes = stats.get("minutes")

            # Skip DNPs / inactive
            if not minutes or minutes == "PT00M":
                continue

            players.append({
                "game_id": game_id,
                "team_id": team_id,
                "player_id": p["personId"],
                "player_name": f"{p['firstName']} {p['familyName']}",
                "minutes": minutes,
                "points": stats.get("points", 0),
                "rebounds": stats.get("reboundsTotal", 0),
                "assists": stats.get("assists", 0),
                "threes": stats.get("threePointersMade", 0),
            })

    return players
