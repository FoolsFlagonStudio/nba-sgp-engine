from nba_api.live.nba.endpoints import scoreboard
import pandas as pd


def get_live_games():
    sb = scoreboard.ScoreBoard()
    data = sb.get_dict()

    games = data["scoreboard"]["games"]

    rows = []
    for g in games:
        rows.append({
            "game_id": g["gameId"],
            "game_code": g["gameCode"],
            "status": g["gameStatusText"].strip(),
            "home_team": g["homeTeam"]["teamTricode"],
            "away_team": g["awayTeam"]["teamTricode"],
            "home_team_id": g["homeTeam"]["teamId"],
            "away_team_id": g["awayTeam"]["teamId"],
            "period": g["period"],
            "game_clock": g["gameClock"]
        })

    return pd.DataFrame(rows)
