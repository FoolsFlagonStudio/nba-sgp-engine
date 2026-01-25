def filter_props_to_active_slate(
    fd_props: dict,
    active_team_ids: set[int]
) -> dict:
    """
    Drops any player props whose team is NOT playing tonight.
    """
    filtered = {}

    for player_id, pdata in fd_props.items():
        if pdata["team_id"] not in active_team_ids:
            continue

        filtered[player_id] = pdata

    return filtered
