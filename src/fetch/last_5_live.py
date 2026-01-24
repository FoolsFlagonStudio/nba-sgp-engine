# src/fetch/last_5_live.py

from nba_api.live.nba.endpoints import scoreboard
from datetime import datetime, timedelta
import pandas as pd
import time


def _date_str(dt: datetime) -> str:
    return dt.strftime("%Y-%m-%d")


def get_last_5_games_by_team_live(
    teams_df: pd.DataFrame,
    days_back: int = 10
) -> dict[int, list[str]]:
    """
    Returns:
      { team_id: [game_id_1, ..., game_id_5] }
    using ONLY nba_api.live scoreboard data.
    """

    # Teams playing today
    team_ids = set(teams_df["home_team_id"]).union(
        set(teams_df["away_team_id"])
    )

    today = datetime.today()
    games_by_team: dict[int, list[tuple[datetime, str]]] = {
        tid: [] for tid in team_ids
    }

    # Walk backward day-by-day
    for offset in range(1, days_back + 1):
        check_date = today - timedelta(days=offset)

        try:
            sb = scoreboard.ScoreBoard(game_date=_date_str(check_date))
            games = sb.get_dict()["scoreboard"]["games"]
        except Exception:
            continue

        for g in games:
            if g["gameStatus"] != 3:  # Final only
                continue

            game_id = g["gameId"]
            game_date = check_date

            home_id = g["homeTeam"]["teamId"]
            away_id = g["awayTeam"]["teamId"]

            if home_id in games_by_team:
                games_by_team[home_id].append((game_date, game_id))
            if away_id in games_by_team:
                games_by_team[away_id].append((game_date, game_id))

        # light throttle (CDN is forgiving, but be polite)
        time.sleep(0.3)

    # Reduce to last 5 per team (most recent first)
    last5_by_team: dict[int, list[str]] = {}

    for team_id, entries in games_by_team.items():
        entries = sorted(entries, key=lambda x: x[0], reverse=True)
        game_ids = [gid for _, gid in entries[:5]]

        if len(game_ids) == 5:
            last5_by_team[team_id] = game_ids
        # else: silently fail → team will drop later

    return last5_by_team
