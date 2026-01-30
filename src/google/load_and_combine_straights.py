# src/google/load_and_combine_straights.py
import pandas as pd
import os

def load_and_combine_straights(run_date: str):
    base_dir = os.path.join("outputs", run_date)
    dfs = []

    for filename, risk in [
        ("straights_core.csv", "core"),
        ("straights_moderate.csv", "moderate"),
        ("straights_aggressive.csv", "aggressive"),
    ]:
        path = os.path.join(base_dir, filename)

        if not os.path.exists(path):
            print(f"⚠️ Missing {path}, skipping")
            continue

        df = pd.read_csv(path)
        df["risk"] = risk
        df["run_date"] = run_date 
        dfs.append(df)

    if not dfs:
        raise RuntimeError(f"No straights CSVs found for {run_date}")

    return pd.concat(dfs, ignore_index=True)
