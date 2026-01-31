# src/fetch/last_5_games.py

from nba_api.stats.endpoints import playergamelog
import pandas as pd
import time

from src.fetch.headers import HEADERS


def get_last_5_game_ids(
    player_id: int,
    season: str = "2025-26",
    timeout: int = 15 # was 60
) -> list[str] | None:
    """
    Returns last 5 completed GAME_IDs for a player.
    If data is incomplete or request fails, returns None.
    """

    try:
        pg = playergamelog.PlayerGameLog(
            player_id=player_id,
            season=season,
            headers=HEADERS,
            timeout=timeout
        )

        df = pg.get_data_frames()[0]

        if df.empty:
            return None

        # Ensure correct ordering
        df = df.sort_values("GAME_DATE", ascending=False)

        # Exclude today (defensive, usually not present anyway)
        df = df[df["MIN"] > 0]

        if len(df) < 5:
            return None

        return df["GAME_ID"].head(5).tolist()

    except Exception:
        return None
