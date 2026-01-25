def extract_active_team_ids(games_df) -> set[int]:
    team_ids = set()

    for _, row in games_df.iterrows():
        team_ids.add(int(row["home_team_id"]))
        team_ids.add(int(row["away_team_id"]))

    return team_ids
