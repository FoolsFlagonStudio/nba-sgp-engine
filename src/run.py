# NOTE:
# run.py produces canonical, line-level betting data.
# Downstream generators must not reshape this structure.
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

load_dotenv(".env", override=True)

DEBUG_LINES_ALL = os.getenv("DEBUG_LINES_ALL") == "1"
DEBUG_LINES_SLATE = os.getenv("DEBUG_LINES_SLATE", "1") == "0"


# 1. Fetch tonight's games
games = get_live_games()

# 2. Determine active slate
active_team_ids = extract_active_team_ids(games)

# 3. Build player data
last5 = get_last_5_games_by_team_league(games, use_cache=False)
raw = build_player_last5_stats(last5)
cleaned = clean_player_last5(raw)

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

# 7. Generate Bet Menu
straights_output = generate_straights(by_game, max_total=50)

flat_props = [
    p
    for market in straights_output.values()
    for p in market
]

mgp_output = generate_multi_game_parlays(flat_props)

sgp_output = generate_sgp_parlays(
    by_game,
    sizes=(3, 5),
    max_per_game=25
)

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

export_results(engine_output)
