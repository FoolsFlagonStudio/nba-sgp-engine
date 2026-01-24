from nba_api.stats.endpoints import leaguegamelog
from datetime import datetime, timedelta
import pandas as pd
import json
from pathlib import Path

from src.fetch.headers import HEADERS

CACHE_DIR = Path(".cache")
CACHE_DIR.mkdir(exist_ok=True)


def get_last_5_games_by_team_league(
    teams_df: pd.DataFrame,
    season: str = "2025-26",
    timeout: int = 60,
    use_cache: bool = True,
    initial_days_back: int = 25,
    max_days_back: int = 35,
    step: int = 5,
) -> dict[int, list[str]]:
    """
    Dynamically expands lookback window until all teams
    playing today have 5 recent games (or max_days_back).
    """

    team_ids = set(teams_df["home_team_id"]).union(
        set(teams_df["away_team_id"])
    )

    today = datetime.today().date()

    cache_key = f"leaguegamelog_{season}_{today}.json"
    cache_path = CACHE_DIR / cache_key

    if use_cache and cache_path.exists():
        with open(cache_path, "r") as f:
            return {int(k): v for k, v in json.load(f).items()}

    # One stats call only
    lg = leaguegamelog.LeagueGameLog(
        season=season,
        headers=HEADERS,
        timeout=timeout
    )

    df = lg.get_data_frames()[0]
    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])

    result: dict[int, list[str]] = {}

    days_back = initial_days_back

    while days_back <= max_days_back:
        cutoff = datetime.today() - timedelta(days=days_back)

        filtered = df[
            (df["TEAM_ID"].isin(team_ids)) &
            (df["GAME_DATE"] >= cutoff)
        ]

        temp: dict[int, list[str]] = {}

        for team_id, group in filtered.groupby("TEAM_ID"):
            gids = (
                group.sort_values("GAME_DATE", ascending=False)
                     .drop_duplicates("GAME_ID")
                     .head(5)["GAME_ID"]
                     .astype(str)
                     .tolist()
            )

            if len(gids) == 5:
                temp[int(team_id)] = gids

        # Check if all teams are covered
        if team_ids.issubset(temp.keys()):
            result = temp
            break

        days_back += step

    # Final pass: keep only teams with full 5
    result = {
        team_id: gids
        for team_id, gids in result.items()
        if len(gids) == 5
    }

    with open(cache_path, "w") as f:
        json.dump(result, f, indent=2)

    return result
