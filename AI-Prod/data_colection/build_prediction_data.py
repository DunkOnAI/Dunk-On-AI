"""
Builds prediction_data.csv from the current season's game stats.

Uses the [PREDICTION] section of settings.cfg so the date range stays
separate from the historical training data. Run this after get_players.py
and get_player_stats.py have been run with [PREDICTION] settings.

Output: data/processed/prediction_data.csv
"""

import sys
import os
import configparser
import pandas as pd
from build_player_training_ready_data import build_player_training_ready_data


def build_prediction_data():
    config = configparser.ConfigParser()
    config.read("settings.cfg")

    if "PREDICTION" not in config:
        print("[ERROR] No [PREDICTION] section found in settings.cfg")
        return {"fatal_error": True, "error_code": -1}

    players_path = os.path.join("data", "raw", "players.csv")
    if not os.path.exists(players_path):
        print("[ERROR] players.csv not found. Run get_players.py first.")
        return {"fatal_error": True, "error_code": -11}

    players_df = pd.read_csv(players_path)
    total_players = len(players_df)
    print(f"[INFO] Building prediction data for {total_players} players...")

    master_data = []
    warnings = 0

    for index, row in enumerate(players_df.itertuples(index=False), start=1):
        player_id = row.PLAYER_ID
        print(f"[PROGRESS] {index}/{total_players} player {player_id}")

        result = build_player_training_ready_data(player_id)
        if result["fatal_error"]:
            warnings += 1
            continue

        processed_path = os.path.join(
            "data", "processed", "players", str(player_id), "training_ready_data.csv"
        )
        if not os.path.exists(processed_path):
            warnings += 1
            continue

        df = pd.read_csv(processed_path)
        if not df.empty:
            master_data.append(df)

    if not master_data:
        print("[ERROR] No prediction data produced.")
        return {"fatal_error": True, "error_code": -12}

    df_out = pd.concat(master_data, ignore_index=True)
    df_out["date"] = pd.to_datetime(df_out["date"])
    df_out = df_out.sort_values(["date", "player_id"]).reset_index(drop=True)

    out_path = os.path.join("data", "processed", "prediction_data.csv")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    df_out.to_csv(out_path, index=False)

    print(f"[INFO] prediction_data.csv saved — {len(df_out)} rows, {df_out['player_id'].nunique()} players")
    print(f"[INFO] Date range: {df_out['date'].min().date()} → {df_out['date'].max().date()}")
    return {"fatal_error": False, "warnings": warnings, "error_code": 0}


if __name__ == "__main__":
    print(build_prediction_data())