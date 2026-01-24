import threading
import queue
import time
from nba_api.stats.endpoints import teamgamelog
from src.fetch.headers import HEADERS


def _fetch_team_games_safe(team_id: int, season: str, timeout_sec: int = 20):
    """
    HARD timeout wrapper around TeamGameLog.
    Returns DataFrame or None.
    """

    result_queue = queue.Queue()

    def worker():
        try:
            tg = teamgamelog.TeamGameLog(
                team_id=team_id,
                season=season,
                headers=HEADERS,
                timeout=timeout_sec
            )
            result_queue.put(tg.get_data_frames()[0])
        except Exception:
            result_queue.put(None)

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()

    try:
        return result_queue.get(timeout=timeout_sec)
    except queue.Empty:
        return None
def get_last_5_games_by_team_teamgamelog(
    teams_df,
    days_back: int = 10,
    season: str = "2025-26"
):
    from datetime import datetime, timedelta
    import pandas as pd

    team_ids = set(teams_df["home_team_id"]).union(set(teams_df["away_team_id"]))
    cutoff = datetime.today() - timedelta(days=days_back)

    last5 = {}

    for tid in team_ids:
        print(f"Fetching team {tid}...")

        df = _fetch_team_games_safe(tid, season=season)
        if df is None or df.empty:
            print(f"  ❌ failed or timed out")
            continue

        df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])
        df = df[df["GAME_DATE"] >= cutoff].sort_values("GAME_DATE", ascending=False)

        gid_col = "GAME_ID" if "GAME_ID" in df.columns else "Game_ID"
        gids = df[gid_col].head(5).astype(str).tolist()

        if len(gids) == 5:
            last5[tid] = gids
            print(f"  ✅ {gids}")
        else:
            print(f"  ⚠️ only {len(gids)} games")

        time.sleep(0.5)

    return last5
