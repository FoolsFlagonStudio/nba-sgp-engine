BET_SCHEMA = {
    "type": "object",
    "properties": {
        "straight_bets": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "player_name": {"type": "string"},
                    "stat": {"type": "string"},
                    "line": {"type": "number"},
                    "line_type": {
                        "type": "string",
                        "enum": ["floor", "straight"]
                    },
                    "confidence": {"type": "string"}
                },
                "required": [
                    "player_name",
                    "stat",
                    "line",
                    "line_type",
                    "confidence"
                ]
            }
        },
        "parlays": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "legs": {
                        "type": "array",
                        "minItems": 3,
                        "items": {
                            "type": "object",
                            "properties": {
                                "player_name": {"type": "string"},
                                "stat": {"type": "string"},
                                "line": {"type": "number"},
                                "line_type": {
                                    "type": "string",
                                    "enum": ["floor"]
                                },
                                "confidence": {"type": "string"}
                            },
                            "required": [
                                "player_name",
                                "stat",
                                "line",
                                "line_type",
                                "confidence"
                            ]
                        }
                    }
                },
                "required": ["legs"]
            }
        }

    },
    "required": ["straight_bets", "parlays"]
}
