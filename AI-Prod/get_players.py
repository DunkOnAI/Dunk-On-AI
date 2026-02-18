# Script to fetch all NBA players who played in the defined period
# This file queries the NBA API for all players who played in 2025 regular season
# It removes commas from names and teams and saves the results to Data/players.csv
# If any step fails, it prints a clear error message and exits safely


# Import required libraries
import sys
import os
import time
import pandas as pd
from datetime import datetime
from nba_api.stats.endpoints import leaguegamelog


# Function to fetch all players and save to CSV
def get_players():
    # Track warnings used for better logging
    warning_count = 0

    try:
        print("[INFO] Fetching players for 2025 regular season...")

        # Hardcoded period for filtering
        start_date = "2025-01-01"
        end_date = "2025-12-31"

        # Fetch league game logs (Regular Season only)
        gamelog = leaguegamelog.LeagueGameLog(
            season="2024-25",  # 2025 calendar year belongs to 2024-25 season
            season_type_all_star="Regular Season",
            player_or_team_abbreviation="P"
        )

        # Wait briefly to avoid API throttling
        time.sleep(0.5)

        # Extract DataFrame
        df = gamelog.get_data_frames()[0]

        # Convert GAME_DATE column to datetime for filtering
        df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])

        # Filter games within the specified period
        df = df[(df["GAME_DATE"] >= start_date) & (df["GAME_DATE"] <= end_date)]

        # Keep only unique players
        players_df = df[["PLAYER_ID", "PLAYER_NAME", "TEAM_NAME"]].drop_duplicates()

        # Remove commas from player names and team names
        players_df["PLAYER_NAME"] = players_df["PLAYER_NAME"].str.replace(",", "", regex=False)
        players_df["TEAM_NAME"] = players_df["TEAM_NAME"].str.replace(",", "", regex=False)

        # Ensure Data directory exists
        data_folder = "Data"
        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

        # Save players to CSV (overwrite if exists)
        output_path = os.path.join(data_folder, "players.csv")
        players_df.to_csv(output_path, index=False)

        # Return warning info (no fatal error)
        return {"fatal_error": False, "warnings": warning_count, "error_code": 0}

    except Exception as e:
        # On error:
        # - Print a clear message
        # - Print the error details
        # - Exit with failure code
        print("[WARN] Failed to fetch players.")
        print(f"[ERROR] {e}", file=sys.stderr)
        return {"fatal_error": True, "warnings": warning_count, "error_code": -1}
    
