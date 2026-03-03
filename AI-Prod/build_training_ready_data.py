"""
Script to build master training dataset for all NBA players.
This file reads data/raw/players.csv,
calls build_player_training_ready_data.py for each player,
merges all player training datasets into master_training.csv,
and creates position-specific training files.
If any step fails, the script prints a clear error message and exits safely.
"""


# Import required libraries
import sys
import os
import pandas as pd
from build_player_training_ready_data import build_player_training_ready_data


# Function to build master training dataset
def build_master_training_data():
    """
    Returns:
        dict: A dictionary containing:
            - fatal_error (bool): True if a fatal exception occurred.
            - warnings (int): Number of non-fatal issues encountered.
            - error_code (int):
                0   -> Success
                -1  -> Unexpected fatal exception
                -11 -> players.csv not found
                -12 -> No player training data created
    """

    # Track warnings used for better logging
    warning_count = 0
    empty_players = 0

    try:
        print("[INFO] Building master training dataset...")

        # Path to players.csv
        players_path = os.path.join("data", "raw", "players.csv")

        # Check if players.csv exists
        if not os.path.exists(players_path):
            print("[WARN] players.csv not found. Run get_players() first.")
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -11
            }

        # Load players
        players_df = pd.read_csv(players_path)
        total_players = len(players_df)

        print(f"[INFO] Total players to process: {total_players}")

        master_data = []

        # Loop through all players
        for index, row in enumerate(players_df.itertuples(index=False), start=1):
            player_id = row.PLAYER_ID

            print(f"[PROGRESS] {index}/{total_players} processing player {player_id}")

            # Create training_ready_data.csv for player
            result = build_player_training_ready_data(player_id)

            # Check if script failed
            if result["fatal_error"]:
                warning_count += 1
                print(f"[WARN] build_player_training_ready_data() failed, skipping player {player_id}")
                continue

            # Locate the training_ready_data.csv
            processed_path = os.path.join(
                "data", "processed", "players",
                str(player_id),
                "training_ready_data.csv"
            )

            if not os.path.exists(processed_path):
                warning_count += 1
                print(f"[WARN] training_ready_data.csv not found for player {player_id}")
                continue

            # Append data to master_data
            df = pd.read_csv(processed_path)
            if df.empty:
                empty_players += 1
                print(f"[INFO] Player {player_id} produced 0 training rows")
                continue
            master_data.append(df)

        # Ensure at least one dataset exists
        if not master_data:
            print("[ERROR] No player training data was created.")
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -12
            }

        # Merge all players
        master_df = pd.concat(master_data, ignore_index=True)

        # Ensure correct datetime type
        master_df["date"] = pd.to_datetime(master_df["date"])

        # Sort master dataset
        master_df = master_df.sort_values(["date", "player_id"]).reset_index(drop=True)

        # Save Master Dataset
        processed_root = os.path.join("data", "processed")
        os.makedirs(processed_root, exist_ok=True)

        master_path = os.path.join(processed_root, "master_training.csv")
        master_df.to_csv(master_path, index=False)

        print(f"[INFO] Master dataset rows: {len(master_df)}")

        # Save Position-Specific Datasets
        # (Dont need for now)

        # Success info message
        print(
            f"[INFO] Players fetched: {total_players} | "
            f"With training data: {len(master_data)} | "
            f"Empty: {empty_players} | "
            f"Failed: {warning_count}"
        )

        # Return structured result
        return {
            "fatal_error": False,
            "warnings": warning_count,
            "error_code": 0
        }

    except Exception as e:
        # Fatal error for the function
        print("[ERROR] build_master_training_data() failed.", file=sys.stderr)
        print(f"[ERROR] {e}", file=sys.stderr)
        return {
            "fatal_error": True,
            "warnings": warning_count,
            "error_code": -1
        }


# Used for terminal calls
if __name__ == "__main__":
    print(build_master_training_data())