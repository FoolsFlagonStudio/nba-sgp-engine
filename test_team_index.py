from src.fetch.games import get_live_games
from src.fetch.team_index import get_last_5_games_by_team_teamgamelog

if __name__ == "__main__":
    games = get_live_games()

    last5 = get_last_5_games_by_team_teamgamelog(
        games,
        days_back=31,
        season="2025-26",
        use_cache=False
    )

    for team_id, game_ids in last5.items():
        print(team_id, game_ids)

    print("Teams with full last-5:", len(last5))
