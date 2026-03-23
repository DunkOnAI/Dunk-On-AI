"""
Script to fetch NBA player game statistics for a defined period.

This file:
- Fetches regular season game logs from the NBA API
- Filters games for players listed in data/raw/players.csv
- Saves per-player game logs to data/raw/players/<PLAYER_ID>/game_stats.csv

If any step fails, the script prints a clear error message and exits safely.
"""


# Import required libraries
import sys
import os
import time
import pandas as pd
import configparser
from nba_api.stats.endpoints import leaguegamelog


# Function to convert "MM:SS" string to total seconds
def convert_minutes_to_seconds(min_str):
    if pd.isna(min_str) or min_str == "":
        return 0
    try:
        return int(min_str) * 60
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
                -1  -> Unexpected fatal exception
                -11 -> players.csv not found
                -12 -> Invalid season format
                -13 -> No season data returned from API
                -14 -> No games found in selected period
                -15 -> No matching players found in selected period
    """

    # Track warnings used for better logging
    warning_count = 0

    try:
        print("[INFO] Fetching player stats for regular seasons in given period...")

        # Load configuration
        config = configparser.ConfigParser()
        config.read("settings.cfg")

        start_date = pd.to_datetime(config["API"]["start_date"])
        end_date = pd.to_datetime(config["API"]["end_date"])
        api_delay = float(config["API"]["api_delay"])
        season_str = config["API"]["season"]

        weights_by_position = {
            "Guard": {
                "points":   float(config["FANTASY_GUARD"]["points"]),
                "rebounds": float(config["FANTASY_GUARD"]["rebounds"]),
                "assists":  float(config["FANTASY_GUARD"]["assists"]),
                "steals":   float(config["FANTASY_GUARD"]["steals"]),
                "blocks":   float(config["FANTASY_GUARD"]["blocks"]),
            },
            "Forward": {
                "points":   float(config["FANTASY_FORWARD"]["points"]),
                "rebounds": float(config["FANTASY_FORWARD"]["rebounds"]),
                "assists":  float(config["FANTASY_FORWARD"]["assists"]),
                "steals":   float(config["FANTASY_FORWARD"]["steals"]),
                "blocks":   float(config["FANTASY_FORWARD"]["blocks"]),
            },
            "Center": {
                "points":   float(config["FANTASY_CENTER"]["points"]),
                "rebounds": float(config["FANTASY_CENTER"]["rebounds"]),
                "assists":  float(config["FANTASY_CENTER"]["assists"]),
                "steals":   float(config["FANTASY_CENTER"]["steals"]),
                "blocks":   float(config["FANTASY_CENTER"]["blocks"]),
            },
        }
        default_weights = weights_by_position["Guard"]

        # Load players.csv
        players_path = os.path.join("data", "raw", "players.csv")

        if not os.path.exists(players_path):
            print("[ERROR] players.csv not found. Run get_players.py first.")
            return {
                "fatal_error": True, 
                "warnings": 0, 
                "error_code": -11
            }

        players_df = pd.read_csv(players_path)

        valid_player_ids = set(players_df["PLAYER_ID"].astype(int))
        position_lookup = dict(zip(players_df["PLAYER_ID"].astype(int), players_df["POSITION"]))

        print(f"[INFO] Players in players.csv: {len(valid_player_ids)}")

        # Get all seasons in correct format
        if "-" in season_str:
            try:
                parts = season_str.split("-")

                if len(parts) != 2:
                    raise ValueError

                start_year = int(parts[0])
                end_year = int(parts[1])

                if start_year > end_year:
                    raise ValueError

                seasons = [f"{y}-{str(y+1)[-2:]}" for y in range(start_year, end_year + 1)]

            except ValueError:
                print(f"[ERROR] Invalid season format '{season_str}'; Expected format: 'YYYY-YYYY'.")
                return {
                    "fatal_error": True,
                    "warnings": warning_count,
                    "error_code": -12
                }
        else:
            print(f"[ERROR] Invalid season format '{season_str}'; Expected format: 'YYYY-YYYY'.")
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -12
            }

        # Fetch all league game logs
        all_seasons_data = []

        print(f"[INFO] Seasons to fetch: {len(seasons)}")
        for index, season in enumerate(seasons, start=1):
            print(f"[PROGRESS] {index}/{len(seasons)} Fetching season {season}")

            gamelog = leaguegamelog.LeagueGameLog(
                season=season,
                season_type_all_star="Regular Season",
                player_or_team_abbreviation="P"
            )

            time.sleep(api_delay)
            season_df = gamelog.get_data_frames()[0]
            if not season_df.empty:
                all_seasons_data.append(season_df)

        if not all_seasons_data:
            print("[ERROR] No season data returned from API.")
            return {
                "fatal_error": False, 
                "warnings": 0, 
                "error_code": -13
            }

        df = pd.concat(all_seasons_data, ignore_index=True)

        # Convert GAME_DATE column to datetime for filtering
        df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])

        # Filter games within the specified period
        df = df[(df["GAME_DATE"] >= start_date) & (df["GAME_DATE"] <= end_date)]

        # Check if we have any valid data
        if df.empty:
            print("[ERROR] No games found in selected period.")
            return {
                "fatal_error": False,
                "warnings": 0,
                "error_code": -14
            }

        print(f"[INFO] Total rows after filtering: {len(df)}")
        print(f"[INFO] Unique players before filtering: {df['PLAYER_ID'].nunique()}")

        # Keep only players from players.csv
        df = df[df["PLAYER_ID"].isin(valid_player_ids)]

        print(f"[INFO] Unique players after filtering: {df['PLAYER_ID'].nunique()}")

        # Check if we have any valid data
        if df.empty:
            print("[ERROR] No matching players found in selected period.")
            return {
                "fatal_error": False, 
                "warnings": 0, 
                "error_code": -15
            }

        # Split per player
        grouped = df.groupby("PLAYER_ID")

        # Saveing per player
        print("[INFO] Saving per-player game logs...")

        for index, (player_id, player_df) in enumerate(grouped, start=1):
            print(f"[PROGRESS] {index}/{len(grouped)} Player {player_id}")

            try:
                player_df = player_df.copy()

                # Determine home/away and opponent
                player_df["is_home_game"] = player_df["MATCHUP"].apply(lambda x: 1 if "vs." in x else 0)
                player_df["opponent"] = player_df["MATCHUP"].apply(lambda x: x.split("vs. ")[1] if "vs." in x else x.split("@ ")[1])

                # Fantasy points — use position-specific weights
                pos = position_lookup.get(int(player_id), "UNKNOWN")
                w = weights_by_position.get(pos, default_weights)
                player_df["fantasy_points"] = (
                    w["points"]   * player_df["PTS"] +
                    w["rebounds"] * player_df["REB"] +
                    w["assists"]  * player_df["AST"] +
                    w["steals"]   * player_df["STL"] +
                    w["blocks"]   * player_df["BLK"]
                )

                # Build output
                output_df = pd.DataFrame()
                output_df["game_id"] = player_df["GAME_ID"]
                output_df["date"] = player_df["GAME_DATE"]
                output_df["seconds_played"] = player_df["MIN"].apply(convert_minutes_to_seconds)
                output_df["points"] = player_df["PTS"]
                output_df["rebounds"] = player_df["REB"]
                output_df["assists"] = player_df["AST"]
                output_df["steals"] = player_df["STL"]
                output_df["blocks"] = player_df["BLK"]
                output_df["opponent"] = player_df["opponent"]
                output_df["is_home_game"] = player_df["is_home_game"]
                output_df["fantasy_points"] = player_df["fantasy_points"]

                output_df = output_df.sort_values("date")

                # Save
                player_folder = os.path.join("data", "raw", "players", str(player_id))
                os.makedirs(player_folder, exist_ok=True)

                output_path = os.path.join(player_folder, "game_stats.csv")
                output_df.to_csv(output_path, index=False)

            except Exception as e:
                warning_count += 1
                print(f"[WARN] Error processing player {player_id}: {e}")

        # Success info message
        print(f"[INFO] Players fetched: {len(grouped)} | Processed: {len(grouped)-warning_count} | Failed: {warning_count}")

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
            "error_code": -1
        }


# Used for terminal calls
if __name__ == "__main__":
    print(get_player_stats())