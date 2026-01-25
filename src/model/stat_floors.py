def compute_stat_floors(cleaned: dict) -> dict:
    result = {}

    for pid, p in cleaned.items():
        result[pid] = {
            "player_name": p["player_name"],
            "team_id": p["team_id"],
            "stats": {}
        }

        for stat in ["points", "rebounds", "assists", "threes"]:
            values = p.get(stat)
            if not values or len(values) < 5:
                continue

            sorted_vals = sorted(values)

            floor_value = sorted_vals[0]      
            safe_alt = sorted_vals[1]         
            moderate_alt = sorted_vals[2]    

            result[pid]["stats"][stat] = {
                "floor": floor_value,
                "safe_alt": safe_alt,
                "moderate_alt": moderate_alt,
                "values": values
            }

    return result
