from nba_api.stats.endpoints import leaguegamelog
from src.fetch.headers import HEADERS

print("Requesting leaguegamelog...")

lg = leaguegamelog.LeagueGameLog(
    season="2025-26",
    headers=HEADERS,
    timeout=60
)

df = lg.get_data_frames()[0]
print("Rows returned:", len(df))
print(df.head())
