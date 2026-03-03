"""
Script to build training-ready data for a single NBA player.

This file:
- Reads raw player game statistics from data/raw/players/<PLAYER_ID>/game_stats.csv
- Computes lag, rolling, season, and rest-based features
- Saves the processed dataset to data/processed/players/<PLAYER_ID>/training_ready_data.csv

If any step fails, the script prints a clear error message and exits safely.
"""


# Import required libraries
import sys
import os
import pandas as pd


# Function to build training-ready data for a single player
def build_player_training_ready_data(player_id):
    """
    Returns:
        dict: A dictionary containing:
            - fatal_error (bool): True if a fatal exception occurred.
            - warnings (int): Number of non-fatal issues encountered.
            - error_code (int):
                0   -> Success
                -1  -> Unexpected fatal exception
                -11 -> game_stats.csv not found
                -12 -> players.csv not found
    """

    # Track warnings used for better logging
    warning_count = 0

    try:
        print(f"[INFO] Building training data for player {player_id}...")

        # Path to player raw stats
        game_stats_path = os.path.join("data", "raw", "players", str(player_id), "game_stats.csv")

        # Check if game_stats.csv exists
        if not os.path.exists(game_stats_path):
            print(f"[WARN] game_stats.csv not found for player {player_id}")
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -11
            }

        # Load player stats
        df = pd.read_csv(game_stats_path)

        if df.empty:
            print(f"[WARN] No games found for player {player_id}")
            return {
                "fatal_error": False,
                "warnings": 1,
                "error_code": 0
            }

        # Ensure correct types and sorting
        df["date"] = pd.to_datetime(df["date"])
        df = df.sort_values("date").reset_index(drop=True)

        # Lag Features
        df["fantasy_last_game"] = df["fantasy_points"].shift(1)
        df["seconds_last_game"] = df["seconds_played"].shift(1)

        # Rolling Play Time (Seconds)
        df["avg_seconds_last5"] = df["seconds_played"].shift(1).rolling(5).mean()
        df["avg_seconds_last10"] = df["seconds_played"].shift(1).rolling(10).mean()
        df["std_seconds_last5"] = df["seconds_played"].shift(1).rolling(5).std()

        # Rolling Production
        stats = ["points", "rebounds", "assists", "blocks", "steals"]
        for stat in stats:
            df[f"avg_{stat}_last5"] = df[stat].shift(1).rolling(5).mean()

        # Rolling Fantasy
        df["avg_fantasy_last3"] = df["fantasy_points"].shift(1).rolling(3).mean()
        df["avg_fantasy_last5"] = df["fantasy_points"].shift(1).rolling(5).mean()
        df["avg_fantasy_last10"] = df["fantasy_points"].shift(1).rolling(10).mean()

        df["std_fantasy_last5"] = df["fantasy_points"].shift(1).rolling(5).std()
        df["max_fantasy_last5"] = df["fantasy_points"].shift(1).rolling(5).max()

        df["trend_fantasy"] = df["avg_fantasy_last3"] - df["avg_fantasy_last10"]

        # Season Expanding Features
        df["season_avg_fantasy"] = df["fantasy_points"].shift(1).expanding().mean()
        df["season_avg_seconds"] = df["seconds_played"].shift(1).expanding().mean()

        # Rest Features
        df["days_since_last_game"] = df["date"].diff().dt.days
        df["is_back_to_back"] = (df["days_since_last_game"] == 1).astype(int)

        # Games in last 7 days
        df = df.set_index("date")
        df["games_last_7_days"] = df["fantasy_points"].shift(1).rolling("7D").count() # We can use anycolumn insted of "fantasy_points" just not "date"
        df = df.reset_index()

        # Target
        df["target_fantasy_points_game"] = df["fantasy_points"]

        # Add Player Metadata
        players_path = os.path.join("data", "raw", "players.csv")

        if not os.path.exists(players_path):
            print("[WARN] players.csv not found.")
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -12
            }

        players_df = pd.read_csv(players_path)
        player_row = players_df[players_df["PLAYER_ID"] == player_id]

        if player_row.empty:
            print(f"[WARN] Position not found for player {player_id}")
            position = "UNKNOWN"
            warning_count += 1
        else:
            position = player_row.iloc[0]["POSITION"]

        df["player_id"] = player_id
        df["position"] = position

        # Build output DataFrame
        output_df = pd.DataFrame()
        # Meta
        output_df["game_id"] = df["game_id"]
        output_df["player_id"] = df["player_id"]
        output_df["position"] = df["position"]
        output_df["date"] = df["date"]
        # Lag
        output_df["fantasy_last_game"] = df["fantasy_last_game"]
        output_df["seconds_last_game"] = df["seconds_last_game"]
        # Rolling time
        output_df["avg_seconds_last5"] = df["avg_seconds_last5"]
        output_df["avg_seconds_last10"] = df["avg_seconds_last10"]
        output_df["std_seconds_last5"] = df["std_seconds_last5"]
        # Rolling production
        output_df["avg_points_last5"] = df["avg_points_last5"]
        output_df["avg_rebounds_last5"] = df["avg_rebounds_last5"]
        output_df["avg_assists_last5"] = df["avg_assists_last5"]
        output_df["avg_blocks_last5"] = df["avg_blocks_last5"]
        output_df["avg_steals_last5"] = df["avg_steals_last5"]
        # Fantasy rolling
        output_df["avg_fantasy_last3"] = df["avg_fantasy_last3"]
        output_df["avg_fantasy_last5"] = df["avg_fantasy_last5"]
        output_df["avg_fantasy_last10"] = df["avg_fantasy_last10"]
        output_df["std_fantasy_last5"] = df["std_fantasy_last5"]
        output_df["max_fantasy_last5"] = df["max_fantasy_last5"]
        output_df["trend_fantasy"] = df["trend_fantasy"]
        # Expanding season
        output_df["season_avg_fantasy"] = df["season_avg_fantasy"]
        output_df["season_avg_seconds"] = df["season_avg_seconds"]
        # Rest
        output_df["days_since_last_game"] = df["days_since_last_game"]
        output_df["is_back_to_back"] = df["is_back_to_back"]
        output_df["games_last_7_days"] = df["games_last_7_days"]
        # Context
        output_df["is_home_game"] = df["is_home_game"]
        output_df["opponent"] = df["opponent"]
        # Target
        output_df["target_fantasy_points_game"] = df["target_fantasy_points_game"]

        # Drop early rows caused by rolling windows
        output_df = output_df.dropna()

        # Save Output
        output_folder = os.path.join(
            "data", "processed", "players", str(player_id)
        )
        os.makedirs(output_folder, exist_ok=True)

        output_path = os.path.join(output_folder, "training_ready_data.csv")
        output_df.to_csv(output_path, index=False)

        # Success info message
        print(f"[INFO] Training rows created: {len(output_df)}")

        # Return structured result
        return {
            "fatal_error": False,
            "warnings": warning_count,
            "error_code": 0
        }

    except Exception as e:
        # Fatal error for the function
        print("[ERROR] build_player_training() failed.", file=sys.stderr)
        print(f"[ERROR] {e}", file=sys.stderr)
        return {
            "fatal_error": True,
            "warnings": warning_count,
            "error_code": -1
        }


# Used for terminal calls (203999 - Jokic <3)
if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python build_player_training_ready_data.py <PLAYER_ID>")
        sys.exit(1)

    player_id_input = int(sys.argv[1])
    print(build_player_training_ready_data(player_id_input))