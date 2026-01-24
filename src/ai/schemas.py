BET_SCHEMA = {
    "type": "object",
    "properties": {
        "straight_bets": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "game_id": {"type": "string"},
                    "player_name": {"type": "string"},
                    "stat": {"type": "string"},
                    "line": {"type": "number"},
                    "confidence": {"type": "string"}  # SAFE | MODERATE
                },
                "required": ["game_id", "player_name", "stat", "line", "confidence"]
            }
        },
        "parlays": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "legs": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "game_id": {"type": "string"},
                                "player_name": {"type": "string"},
                                "stat": {"type": "string"},
                                "line": {"type": "number"}
                            },
                            "required": ["game_id", "player_name", "stat", "line"]
                        }
                    },
                    "type": {"type": "string"}  # 3-leg | 5-leg | 8-leg
                },
                "required": ["legs", "type"]
            }
        }
    },
    "required": ["straight_bets", "parlays"]
}
