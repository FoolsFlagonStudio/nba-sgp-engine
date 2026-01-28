from typing import List, Dict, Any, Set


def filter_props_to_active_slate(
    fd_props: List[Dict[str, Any]],
    active_team_ids: Set[int]
) -> List[Dict[str, Any]]:
    """
    Drops any props whose team is NOT playing tonight.
    Operates on flat, line-level props.
    """
    return [
        prop
        for prop in fd_props
        if prop.get("team_id") in active_team_ids
    ]
