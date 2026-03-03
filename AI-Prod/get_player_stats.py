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
import configparser
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
    warning_skipped = 0

    try:
        print("[INFO] Fetching player stats for 2025 regular season...")

        # Load configuration
        config = configparser.ConfigParser()
        config.read("settings.cfg")

        start_date = pd.to_datetime(config["API"]["start_date"])
        end_date = pd.to_datetime(config["API"]["end_date"])
        api_delay = float(config["API"]["api_delay"])
        season = config["API"]["season"]

        # Fantasy weights
        w_points = float(config["FANTASY"]["points"])
        w_rebounds = float(config["FANTASY"]["rebounds"])
        w_assists = float(config["FANTASY"]["assists"])
        w_steals = float(config["FANTASY"]["steals"])
        w_blocks = float(config["FANTASY"]["blocks"])

        # Path to players.csv
        players_path = os.path.join("data", "raw", "players.csv")

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
        total_players = len(players_df)
        print(f"[INFO] Total players to process: {total_players}")

        # Loop over each player
        for index, row in enumerate(players_df.itertuples(index=False), start=1):
            player_id = row.PLAYER_ID

            print(f"[PROGRESS] {index}/{total_players} processing player {player_id}")

            try:
                # Fetch player game logs
                gamelog = playergamelog.PlayerGameLog(
                    player_id=player_id,
                    season=season,
                    season_type_all_star="Regular Season"
                )

                # Delay to avoid API throttling
                time.sleep(api_delay)

                df = gamelog.get_data_frames()[0]

                if df.empty:
                    warning_skipped += 1
                    print(f"[INFO] No games found for {player_id}")
                    continue

                # Convert GAME_DATE to datetime
                df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])

                # Filter games by date range
                df = df[(df["GAME_DATE"] >= start_date) & (df["GAME_DATE"] <= end_date)]

                if df.empty:
                    print(f"[INFO] No games in 2025 for {player_id}")
                    continue

                # Determine home/away + opponent
                df["is_home_game"] = df["MATCHUP"].apply(lambda x: 1 if "vs." in x else 0)
                df["opponent"] = df["MATCHUP"].apply(
                    lambda x: x.split("vs. ")[1] if "vs." in x else x.split("@ ")[1]
                )

                # Calculate fantasy points
                df["fantasy_points"] = (
                    w_points * df["PTS"] +
                    w_rebounds * df["REB"] +
                    w_assists * df["AST"] +
                    w_steals * df["STL"] +
                    w_blocks * df["BLK"]
                )

                # Build output DataFrame
                output_df = pd.DataFrame()
                output_df["game_id"] = df["Game_ID"]
                output_df["date"] = df["GAME_DATE"]
                output_df["seconds_played"] = df["MIN"].apply(convert_minutes_to_seconds)
                output_df["points"] = df["PTS"]
                output_df["rebounds"] = df["REB"]
                output_df["assists"] = df["AST"]
                output_df["steals"] = df["STL"]
                output_df["blocks"] = df["BLK"]
                output_df["opponent"] = df["opponent"]
                output_df["is_home_game"] = df["is_home_game"]
                output_df["fantasy_points"] = df["fantasy_points"]

                # Sort by date
                output_df = output_df.sort_values("date")

                # Create player folder
                player_folder = os.path.join("data", "raw", "players", str(player_id))
                os.makedirs(player_folder, exist_ok=True)

                # Save CSV (overwrite)
                output_path = os.path.join(player_folder, "game_stats.csv")
                output_df.to_csv(output_path, index=False)

            except Exception as e:
                # Error specific to this player
                warning_count += 1
                print(f"[WARN] Error processing player {player_id}: {e}")

        # Success info message
        print(f"[INFO] Players fetched: {total_players} | Processed: {total_players-warning_count} | Skipped: {warning_skipped} | Failed: {warning_count}")
        
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


# Used for terminal calls
if __name__ == "__main__":
    print(get_player_stats())