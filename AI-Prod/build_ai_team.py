"""
Script to build the AI team for a given week.
Reads Data/weekly_scores.csv, ranks all players by total fantasy points
for the specified week, and picks the top ROSTER_SIZE players as the AI team.
Saves the result to Data/ai_team_week_<WEEK>.csv.
"""


import os
import sys
import pandas as pd


# Number of players on the AI team roster
ROSTER_SIZE = 8


def build_ai_team(week_number):
    """
    Args:
        week_number (int): The ISO week number to build the AI team for.

    Returns:
        dict: A dictionary containing:
            - fatal_error (bool): True if a fatal exception occurred.
            - warnings (int): Number of non-fatal issues.
            - error_code (int):
                0   -> Success
                -1  -> Unexpected fatal exception
                -11 -> weekly_scores.csv not found
                -12 -> No data for the given week
                -13 -> Not enough players to fill roster
            - roster (list[dict]): The selected AI team roster.
    """

    warning_count = 0

    try:
        print(f"[INFO] Building AI team for week {week_number}...")

        weekly_path = os.path.join("Data", "weekly_scores.csv")

        if not os.path.exists(weekly_path):
            print("[WARN] weekly_scores.csv not found. Run compute_weekly_scores() first.")
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -11,
                "roster": []
            }

        df = pd.read_csv(weekly_path)

        # Filter to the requested week
        week_df = df[df["week_of_year"] == week_number].copy()

        if week_df.empty:
            print(f"[WARN] No data found for week {week_number}.")
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -12,
                "roster": []
            }

        if len(week_df) < ROSTER_SIZE:
            print(f"[WARN] Only {len(week_df)} players available for week {week_number}, need {ROSTER_SIZE}.")
            warning_count += 1

        # Rank players by total fantasy points and pick top ROSTER_SIZE
        week_df = week_df.sort_values("total_fantasy_points", ascending=False)
        ai_roster = week_df.head(ROSTER_SIZE).reset_index(drop=True)

        # Save to file
        output_path = os.path.join("Data", f"ai_team_week_{week_number}.csv")
        ai_roster.to_csv(output_path, index=False)

        roster_list = ai_roster.to_dict(orient="records")

        print(f"[INFO] AI team for week {week_number} saved to {output_path}.")
        print(f"[INFO] Roster ({len(roster_list)} players):")
        for i, player in enumerate(roster_list, 1):
            print(f"  {i}. {player['player_name']} — {player['total_fantasy_points']:.1f} pts")

        return {
            "fatal_error": False,
            "warnings": warning_count,
            "error_code": 0,
            "roster": roster_list
        }

    except Exception as e:
        print("[ERROR] build_ai_team() failed.", file=sys.stderr)
        print(f"[ERROR] {e}", file=sys.stderr)
        return {
            "fatal_error": True,
            "warnings": warning_count,
            "error_code": -1,
            "roster": []
        }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python build_ai_team.py <week_number>")
        sys.exit(1)

    try:
        week = int(sys.argv[1])
    except ValueError:
        print("[ERROR] week_number must be an integer.")
        sys.exit(1)

    result = build_ai_team(week)
    if result["fatal_error"]:
        sys.exit(result["error_code"])
