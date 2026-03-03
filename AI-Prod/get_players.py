"""
Script to fetch all NBA players who played in the defined period.
This file queries the NBA API for all players who played in 2025 regular season.
It removes commas from names and teams and saves the results to Data/players.csv
If any step fails, it prints a clear error message and exits safely
"""


# Import required libraries
import sys
import os
import time
import pandas as pd
import configparser
from datetime import datetime
from nba_api.stats.endpoints import leaguegamelog
from nba_api.stats.endpoints import commonplayerinfo


# Function to fetch all players and save to CSV
def get_players():
    """
    Returns:
        dict: A dictionary containing:
            - fatal_error (bool): True if a fatal exception occurred.
            - warnings (int): Number of non-fatal issues encountered.
            - error_code (int):
                0   -> Success
                -1  -> Unexpected fatal exception
    """

    # Track warnings used for better logging
    warning_count = 0

    try:
        print("[INFO] Fetching players for 2025 regular season...")

        # Load configuration
        config = configparser.ConfigParser()
        config.read("settings.cfg")

        start_date = config["API"]["start_date"]
        end_date = config["API"]["end_date"]
        api_delay = float(config["API"]["api_delay"])
        season = config["API"]["season"]

        # Fetch league game logs (Regular Season only)
        gamelog = leaguegamelog.LeagueGameLog(
            season=season,
            season_type_all_star="Regular Season",
            player_or_team_abbreviation="P"
        )

        # Wait briefly to avoid API throttling
        time.sleep(api_delay)

        # Extract DataFrame
        df = gamelog.get_data_frames()[0]

        # Convert GAME_DATE column to datetime for filtering
        df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])

        # Filter games within the specified period
        df = df[(df["GAME_DATE"] >= start_date) & (df["GAME_DATE"] <= end_date)]

        # Keep only unique players
        players_df = df[["PLAYER_ID", "PLAYER_NAME"]].drop_duplicates()

        # Remove commas from player names
        players_df["PLAYER_NAME"] = players_df["PLAYER_NAME"].str.replace(",", "", regex=False)

        # Add POSITION column
        positions = []

        print("[INFO] Fetching player positions...")
        total_players = len(players_df)
        print(f"[INFO] Total players to process: {total_players}")

        for index, player_id in enumerate(players_df["PLAYER_ID"], start=1):
            print(f"[PROGRESS] {index}/{total_players} processing player {player_id}")
            try:
                info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)
                time.sleep(api_delay)

                info_df = info.get_data_frames()[0]
                position = info_df.loc[0, "POSITION"]

                positions.append(position)

            except Exception as e:
                print(f"[WARN] Failed fetching position for {player_id}")
                print(e)
                positions.append("UNKNOWN")
                warning_count += 1

        players_df["POSITION"] = positions

        # Ensure data/raw directory exists
        data_folder = os.path.join("data", "raw")

        if not os.path.exists(data_folder):
            os.makedirs(data_folder)

        # Save players to CSV
        output_path = os.path.join(data_folder, "players.csv")
        players_df.to_csv(output_path, index=False)
        
        # Success info message
        print(f"[INFO] Players fetched: {total_players} | Processed: {total_players-warning_count} | Failed: {warning_count}")

        # Return structured result
        return {
            "fatal_error": False,
            "warnings": warning_count,
            "error_code": 0
        }

    except Exception as e:
        # Fatal error for the function
        print("[WARN] Failed to fetch players.")
        print(f"[ERROR] {e}", file=sys.stderr)
        return {
            "fatal_error": True,
            "warnings": warning_count,
            "error_code": -1
        }


# Used for terminal calls
if __name__ == "__main__":
    print(get_players())