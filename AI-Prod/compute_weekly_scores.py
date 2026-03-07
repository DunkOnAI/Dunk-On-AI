"""
Script to aggregate per-game player stats into weekly fantasy scores.
Reads all player CSVs from Data/player_<PLAYER_ID>/player_stats.csv,
groups by week_of_year, sums fantasy_points, and saves to Data/weekly_scores.csv.
"""


import os
import sys
import pandas as pd


def compute_weekly_scores():
    """
    Returns:
        dict: A dictionary containing:
            - fatal_error (bool): True if a fatal exception occurred.
            - warnings (int): Number of player-specific processing errors.
            - error_code (int):
                0   -> Success
                -1  -> Unexpected fatal exception
                -11 -> players.csv not found
                -12 -> No player stat files found
    """

    warning_count = 0

    try:
        print("[INFO] Computing weekly fantasy scores...")

        players_path = os.path.join("Data", "players.csv")

        if not os.path.exists(players_path):
            print("[WARN] players.csv not found. Run get_players() first.")
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -11
            }

        players_df = pd.read_csv(players_path)

        all_rows = []

        for _, player_row in players_df.iterrows():
            player_id = player_row["PLAYER_ID"]
            player_name = player_row["PLAYER_NAME"]

            stats_path = os.path.join("Data", f"player_{player_id}", "player_stats.csv")

            if not os.path.exists(stats_path):
                continue

            try:
                df = pd.read_csv(stats_path)

                if df.empty:
                    continue

                # Group by week and sum fantasy points
                weekly = (
                    df.groupby("week_of_year")
                    .agg(
                        games_played=("game_id", "count"),
                        total_points=("points", "sum"),
                        total_rebounds=("rebounds", "sum"),
                        total_assists=("assists", "sum"),
                        total_steals=("steals", "sum"),
                        total_blocks=("blocks", "sum"),
                        total_fantasy_points=("fantasy_points", "sum")
                    )
                    .reset_index()
                )

                weekly.insert(0, "player_id", player_id)
                weekly.insert(1, "player_name", player_name)

                all_rows.append(weekly)

            except Exception as e:
                print(f"[WARN] Failed to process player {player_id} - {player_name}: {e}")
                warning_count += 1
                continue

        if not all_rows:
            print("[WARN] No player stat files found.")
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -12
            }

        # Combine all players into one DataFrame
        result_df = pd.concat(all_rows, ignore_index=True)
        result_df = result_df.sort_values(["week_of_year", "total_fantasy_points"], ascending=[True, False])

        output_path = os.path.join("Data", "weekly_scores.csv")
        result_df.to_csv(output_path, index=False)

        print(f"[INFO] Weekly scores saved to {output_path} ({len(result_df)} rows).")

        return {
            "fatal_error": False,
            "warnings": warning_count,
            "error_code": 0
        }

    except Exception as e:
        print("[ERROR] compute_weekly_scores() failed.", file=sys.stderr)
        print(f"[ERROR] {e}", file=sys.stderr)
        return {
            "fatal_error": True,
            "warnings": warning_count,
            "error_code": -1
        }


if __name__ == "__main__":
    result = compute_weekly_scores()
    if result["fatal_error"]:
        sys.exit(result["error_code"])
