# NOTE:
# run.py produces canonical, line-level betting data.
# Downstream generators must not reshape this structure.
from collections import Counter
import json
import os
from dotenv import load_dotenv
from datetime import date
from src.fetch.games import get_live_games
from src.fetch.league_index import get_last_5_games_by_team_league
from src.fetch.player_last5_stats import build_player_last5_stats
from src.clean.player_last5_clean import clean_player_last5
from src.model.stat_floors import compute_stat_floors
from src.model.fanduel_lines import apply_fanduel_lines
from src.model.group_props_by_game import group_props_by_game
from src.model.filter_active_slate import filter_props_to_active_slate
from src.fetch.active_slate import extract_active_team_ids
from src.generate.straights import generate_straights
from src.generate.multigame_parlays import generate_multi_game_parlays
from src.generate.sgp_parlays import generate_sgp_parlays
from src.export.export_results import export_results
from src.google.google_auth import get_google_creds
from src.google.load_and_combine_straights import load_and_combine_straights
from src.google.write_to_sheets import write_straights_to_sheet
import logging
import signal
import sys

RUN_DATE = date.today().isoformat()

MAX_RUNTIME_SECONDS = 30 * 60

def timeout_handler(signum, frame):
    logging.error("❌ Max runtime exceeded — shutting down job")
    sys.exit(1)

# signal.signal(signal.SIGALRM, timeout_handler)
# signal.alarm(MAX_RUNTIME_SECONDS)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%H:%M:%S"
)
# LOG_DIR = "logs"
# os.makedirs(LOG_DIR, exist_ok=True)

# logging.basicConfig(
#     level=logging.INFO,
#     format="%(asctime)s | %(levelname)s | %(message)s",
#     handlers=[
#         logging.FileHandler(f"{LOG_DIR}/{RUN_DATE}.log"),
#         logging.StreamHandler(sys.stdout),
#     ],
# )


load_dotenv(".env", override=True)

DEBUG_LINES_ALL = os.getenv("DEBUG_LINES_ALL") == "1"
DEBUG_LINES_SLATE = os.getenv("DEBUG_LINES_SLATE", "1") == "0"


# 1. Fetch tonight's games
games = get_live_games()

# 2. Determine active slate
active_team_ids = extract_active_team_ids(games)

# 3. Build player data
MAX_NBA_RETRIES = 3

last5 = None
for attempt in range(1, MAX_NBA_RETRIES + 1):
    try:
        logging.info(f"📡 Fetching last-5 games (attempt {attempt})")
        last5 = get_last_5_games_by_team_league(
            games,
            use_cache=False,
            timeout=15,
        )
        break
    except Exception as e:
        logging.warning(f"⚠️ NBA API attempt {attempt} failed: {e}")
        if attempt == MAX_NBA_RETRIES:
            logging.error("❌ NBA API unavailable after retries")
            sys.exit(1)
if last5 is None:
    logging.error("❌ NBA API returned no data")
    sys.exit(1)

raw = build_player_last5_stats(last5)
cleaned = clean_player_last5(raw)
cleaned = {
    pid: p
    for pid, p in cleaned.items()
    if p["team_id"] in active_team_ids
}

# 4. Compute floors + FanDuel lines
floors = compute_stat_floors(cleaned)
fd_props = apply_fanduel_lines(floors)

# DEBUG 1 — raw line generation (optional, dev only)
if DEBUG_LINES_ALL:
    print(json.dumps(fd_props, indent=2))

# 5. Filter to active teams only
fd_props = filter_props_to_active_slate(fd_props, active_team_ids)

# DEBUG 2 — slate-only props (PRIMARY)
if DEBUG_LINES_SLATE:
    print(json.dumps(fd_props, indent=2))

# 6. Group by game
print("DEBUG games type:", type(games))
print("DEBUG games sample:", list(games)[:3])

by_game = group_props_by_game(games, fd_props)
print("STRAIGHTS INPUT STATS")
print("Games:", len(by_game))
print(
    "Total props:",
    sum(len(g["props"]) for g in by_game.values())
)

print(
    "Markets:",
    Counter(
        p["market"]
        for g in by_game.values()
        for p in g["props"]
    )
)

# 7. Generate Bet Menu
print("starting straights")
straights_output = generate_straights(by_game)
print("straights finished")
flat_props = [
    p
    for market in straights_output.values()
    for p in market
]
print("starting mgp")
mgp_output = generate_multi_game_parlays(flat_props)
print("mpg finished")
print("starting sgp")
sgp_output = generate_sgp_parlays(
    by_game,
    sizes=(3, 5),
    max_per_game=25
)
print("sgp finished")
engine_output = {
    "date": str(date.today()),
    "engine_version": "0.3.0",
    "generated_at": "...",

    "straights": straights_output,
    "multi_game_parlays": mgp_output,
    "sgp": {
        "by_game": sgp_output
    }
}
print("exporting...")
export_results(engine_output)

# ==============================
# GOOGLE OUTPUTS (POST-EXPORT)
# ==============================

print("Preparing Google outputs")

# 8. Load + combine straights CSVs
df_straights = load_and_combine_straights(RUN_DATE)
print(f"Combined straights rows: {len(df_straights)}")

# 9. Auth once
creds = get_google_creds()
print("Google credentials loaded")

# 10. Write to Google Sheets (authoritative)
write_straights_to_sheet(
    creds=creds,
    spreadsheet_id=os.environ["STRAIGHTS_SPREADSHEET_ID"],
    worksheet_name="Straights",
    df=df_straights,
)
print("Google Sheet updated")