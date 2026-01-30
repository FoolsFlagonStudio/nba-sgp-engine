import pandas as pd


def load_and_combine_straights():
    dfs = []

    for path, risk in [
        ("output/straights_core.csv", "core"),
        ("output/straights_moderate.csv", "moderate"),
        ("output/straights_aggressive.csv", "aggressive"),
    ]:
        df = pd.read_csv(path)
        df["risk"] = risk  # optional but HIGHLY recommended
        dfs.append(df)

    combined = pd.concat(dfs, ignore_index=True)
    return combined
