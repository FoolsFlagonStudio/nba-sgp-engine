import json
from dotenv import load_dotenv

from src.fetch.games import get_live_games
from src.fetch.league_index import get_last_5_games_by_team_league
from src.fetch.player_last5_stats import build_player_last5_stats
from src.clean.player_last5_clean import clean_player_last5
from src.model.stat_floors import compute_stat_floors
from src.model.fanduel_lines import apply_fanduel_lines
from src.model.group_props_by_game import group_props_by_game
from src.ai.generate_bets import generate_bets

load_dotenv(".env", override=True)

games = get_live_games()
last5 = get_last_5_games_by_team_league(games, use_cache=False)

raw = build_player_last5_stats(last5)
cleaned = clean_player_last5(raw)
floors = compute_stat_floors(cleaned)
fd_props = apply_fanduel_lines(floors)

by_game = group_props_by_game(games, fd_props)

bets = generate_bets(by_game)

print(json.dumps(bets, indent=2))
