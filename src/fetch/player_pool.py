# src/fetch/player_pool.py

from nba_api.live.nba.endpoints import scoreboard, boxscore
import pandas as pd


def get_last_completed_games_by_team():
    """
    Uses live scoreboard to find most recent completed game per team.
    """
    sb = scoreboard.ScoreBoard()
    games = sb.get_dict()["scoreboard"]["games"]

    last_game_by_team = {}

    for g in games:
        if g["gameStatus"] != 3:  # 3 = Final
            continue

        home = g["homeTeam"]["teamId"]
        away = g["awayTeam"]["teamId"]
        game_id = g["gameId"]

        last_game_by_team[home] = game_id
        last_game_by_team[away] = game_id

    return last_game_by_team


def get_players_from_live_boxscore(game_id: str) -> pd.DataFrame:
    bs = boxscore.BoxScore(game_id)
    data = bs.get_dict()["game"]

    players = []

    for side in ["homeTeam", "awayTeam"]:
        team = data[side]
        team_id = team["teamId"]

        for p in team["players"]:
            mins = p["statistics"]["minutes"]
            if mins is None or mins == "0:00":
                continue

            players.append({
                "PLAYER_ID": p["personId"],
                "PLAYER_NAME": f'{p["firstName"]} {p["familyName"]}',
                "TEAM_ID": team_id
            })

    return pd.DataFrame(players)


def build_player_pool_live_only() -> pd.DataFrame:
    last_games = get_last_completed_games_by_team()

    frames = []
    for team_id, game_id in last_games.items():
        df = get_players_from_live_boxscore(game_id)
        frames.append(df)

    pool = pd.concat(frames, ignore_index=True)
    pool = pool.drop_duplicates(subset=["PLAYER_ID"])

    return pool
