# src/fetch/rosters.py

from nba_api.stats.endpoints import commonteamroster
import pandas as pd
import time

from src.fetch.headers import HEADERS


def get_team_roster(team_id: int, season: str = "2025-26") -> pd.DataFrame:
    """
    Fetch current roster for a single team.
    Returns one row per player.
    """

    roster = commonteamroster.CommonTeamRoster(
        team_id=team_id,
        season=season,
        headers=HEADERS,
        timeout=30
    )

    df = roster.get_data_frames()[0]

    return df[[
        "PLAYER_ID",
        "PLAYER",
        "POSITION",
        "HEIGHT",
        "WEIGHT",
        "AGE",
        "EXP"
    ]]


def get_rosters_for_today(teams_df: pd.DataFrame, season: str = "2025-26") -> pd.DataFrame:
    """
    Pull rosters for all teams playing today.
    """

    all_players = []

    team_ids = set(teams_df["home_team_id"]).union(
        set(teams_df["away_team_id"])
    )

    for team_id in team_ids:
        df = get_team_roster(team_id, season=season)
        df["TEAM_ID"] = team_id
        all_players.append(df)

        # throttle to avoid NBA Stats bans
        time.sleep(0.6)

    players_df = pd.concat(all_players, ignore_index=True)

    # ensure uniqueness
    players_df = players_df.drop_duplicates(subset=["PLAYER_ID"])

    return players_df
