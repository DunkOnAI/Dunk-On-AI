"""
Script to fetch NBA player game stats for a defined period.
This file reads Data/players.csv and fetches each player's game logs.
It converts minutes to seconds, computes week of the year, and saves each player's
stats to Data/player_<PLAYER_ID>/player_stats.csv
If any step fails, the script prints a clear error message and exits safely
"""


# Import required libraries
import sys
import os
import time
import pandas as pd
from datetime import datetime
from nba_api.stats.endpoints import playergamelog


# Function to convert "MM:SS" string to total seconds
def convert_minutes_to_seconds(min_str):
    if pd.isna(min_str) or min_str == "":
        return 0

    try:
        minutes, seconds = min_str.split(":")
        return int(minutes) * 60 + int(seconds)
    except Exception:
        return 0


# Function to fetch player stats and save to individual CSVs
def get_player_stats():
    """
    Returns:
        dict: A dictionary containing:
            - fatal_error (bool): True if a fatal exception occurred.
            - warnings (int): Number of player-specific processing errors encountered.
            - error_code (int):
                0   -> Success
                -2  -> Unexpected fatal exception
                -21 -> players.csv not found
    """

    # Track warnings used for better logging
    warning_count = 0

    try:
        print("[INFO] Fetching player stats for 2025 regular season...")

        # Path to players.csv
        players_path = os.path.join("Data", "players.csv")

        # Check if players.csv exists
        if not os.path.exists(players_path):
            print("[WARN] players.csv not found. Run get_players() first.")
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -21
            }

        # Read players
        players_df = pd.read_csv(players_path)

        # Define date range
        start_date = pd.to_datetime("2025-01-01")
        end_date = pd.to_datetime("2025-12-31")

        # Loop over each player
        for _, row in players_df.iterrows():
            player_id = row["PLAYER_ID"]
            player_name = row["PLAYER_NAME"]

            print(f"[INFO] Processing {player_id} - {player_name}...")

            try:
                # Fetch player game logs
                gamelog = playergamelog.PlayerGameLog(
                    player_id=player_id,
                    season="2024-25",
                    season_type_all_star="Regular Season"
                )

                # Delay to avoid API throttling
                time.sleep(0.5)

                df = gamelog.get_data_frames()[0]

                if df.empty:
                    print(f"[INFO] No games found for {player_name}")
                    continue

                # Convert GAME_DATE to datetime
                df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])

                # Filter games by date range
                df = df[(df["GAME_DATE"] >= start_date) & (df["GAME_DATE"] <= end_date)]

                if df.empty:
                    print(f"[INFO] No games in 2025 for {player_name}")
                    continue

                # Build output DataFrame
                output_df = pd.DataFrame()
                output_df["game_id"] = df["Game_ID"]
                output_df["week_of_year"] = df["GAME_DATE"].dt.isocalendar().week
                output_df["seconds_played"] = df["MIN"].apply(convert_minutes_to_seconds)
                output_df["points"] = df["PTS"]
                output_df["rebounds"] = df["REB"]
                output_df["assists"] = df["AST"]
                output_df["steals"] = df["STL"]
                output_df["blocks"] = df["BLK"]

                # Standard fantasy scoring formula
                output_df["fantasy_points"] = (
                    output_df["points"] * 1.0
                    + output_df["rebounds"] * 1.2
                    + output_df["assists"] * 1.5
                    + output_df["steals"] * 3.0
                    + output_df["blocks"] * 3.0
                )

                # Create player folder
                player_folder = os.path.join("Data", f"player_{player_id}")
                os.makedirs(player_folder, exist_ok=True)

                # Save CSV (overwrite)
                output_path = os.path.join(player_folder, "player_stats.csv")
                output_df.to_csv(output_path, index=False)

            except Exception as e:
                # Error specific to this player
                warning_count += 1
                print(f"[WARN] Error processing player {player_id} - {player_name}: {e}")

        # Return structured result
        return {
            "fatal_error": False,
            "warnings": warning_count,
            "error_code": 0
        }

    except Exception as e:
        # Fatal error for the function
        print("[ERROR] get_player_stats() failed.", file=sys.stderr)
        print(f"[ERROR] {e}", file=sys.stderr)
        return {
            "fatal_error": True,
            "warnings": warning_count,
            "error_code": -2
        }
