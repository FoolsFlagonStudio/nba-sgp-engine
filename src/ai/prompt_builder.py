import json
from src.ai.prompt import SYSTEM_PROMPT  # or inline if you prefer

def build_prompt(by_game: dict) -> str:
    """
    Injects grouped FanDuel-ready props into the system prompt.
    """

    data_block = json.dumps(by_game, indent=2)

    return f"""
{SYSTEM_PROMPT}

--------------------------------------------------
INPUT DATA (GROUPED BY GAME)
--------------------------------------------------
{data_block}

--------------------------------------------------
RETURN FORMAT
--------------------------------------------------
Return JSON matching the required schema.
"""
