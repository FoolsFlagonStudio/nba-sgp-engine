import json
from pathlib import Path
from datetime import date
from typing import Dict, Any, List
from collections import defaultdict

import pandas as pd


def _ensure_dir(path: Path):
    path.mkdir(parents=True, exist_ok=True)


def _write_json(path: Path, data: dict):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def _write_csv(path: Path, rows: List[Dict[str, Any]]):
    if not rows:
        return
    df = pd.DataFrame(rows)
    df.to_csv(path, index=False)


def export_results(
    engine_output: Dict[str, Any],
    base_dir: str = "outputs"
):
    """
    Writes engine output to:
      outputs/YYYY-MM-DD/
        engine_output.json
        straights_core.csv
        straights_moderate.csv
        straights_aggressive.csv
        mgp_3_leg.csv
        mgp_5_leg.csv
        mgp_8_leg.csv
        sgp_<game_id>.csv
    """

    run_date = engine_output["date"]
    out_dir = Path(base_dir) / run_date
    _ensure_dir(out_dir)

    # -----------------------------
    # 1. Master JSON
    # -----------------------------
    _write_json(out_dir / "engine_output.json", engine_output)

    # -----------------------------
    # 2. Straights CSVs
    # -----------------------------
    by_risk = defaultdict(list)

    straights_by_market = engine_output.get("straights", {})

    for market, rows in straights_by_market.items():
        for row in rows:
            risk = row.get("risk")
            if risk:
                by_risk[risk].append(row)

    for risk, rows in by_risk.items():
        _write_csv(
            out_dir / f"straights_{risk}.csv",
            rows
        )

    # -----------------------------
    # 3. Multi-game parlays CSVs
    # -----------------------------
    mgp = engine_output.get("multi_game_parlays", {})

    for size_key, parlays in mgp.items():
        flat_rows = []

        for idx, parlay in enumerate(parlays, start=1):
            for leg in parlay["legs"]:
                flat_rows.append({
                    "parlay_id": idx,
                    "size": parlay["size"],
                    **leg
                })

        _write_csv(
            out_dir / f"mgp_{size_key}.csv",
            flat_rows
        )

    # -----------------------------
    # 4. Same-game parlays CSVs
    # -----------------------------
    sgp_root = engine_output.get("sgp", {})
    by_game = sgp_root.get("by_game", {})

    for game_id, sizes in by_game.items():
        if not isinstance(sizes, dict):
            continue

        for size_key, parlays in sizes.items():
            if not isinstance(parlays, list) or not parlays:
                continue

            flat_rows = []

            for parlay_idx, parlay in enumerate(parlays, start=1):
                for leg in parlay.get("legs", []):
                    flat_rows.append({
                        "parlay_id": parlay_idx,
                        "size": parlay["size"],
                        **leg
                    })

            if flat_rows:
                _write_csv(
                    out_dir / f"sgp_{game_id}_{size_key}.csv",
                    flat_rows
                )

    print(f"Export complete → {out_dir}")
