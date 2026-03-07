"""
Script to score a matchup between a user's team and the AI team for a given week.
Reads weekly fantasy points for each player on both rosters,
sums the scores, and returns the result (win/loss/tie).

Usage:
    from score_matchup import score_matchup

    result = score_matchup(
        week_number=5,
        user_player_ids=[203999, 1629029, 201142]  # list of NBA player IDs
    )
"""


import os
import sys
import pandas as pd
from build_ai_team import build_ai_team, ROSTER_SIZE


def score_matchup(week_number, user_player_ids):
    """
    Args:
        week_number (int): The ISO week number of the matchup.
        user_player_ids (list[int]): List of NBA player IDs on the user's team.

    Returns:
        dict: A dictionary containing:
            - fatal_error (bool): True if a fatal exception occurred.
            - warnings (int): Number of non-fatal issues.
            - error_code (int):
                0   -> Success
                -1  -> Unexpected fatal exception
                -11 -> weekly_scores.csv not found
                -12 -> Failed to build AI team
            - week_number (int): The week scored.
            - user_score (float): Total fantasy points for the user's team.
            - ai_score (float): Total fantasy points for the AI team.
            - result (str): "win", "loss", or "tie" from the user's perspective.
            - user_roster (list[dict]): Per-player breakdown for user.
            - ai_roster (list[dict]): Per-player breakdown for AI.
    """

    warning_count = 0

    try:
        print(f"[INFO] Scoring matchup for week {week_number}...")

        weekly_path = os.path.join("Data", "weekly_scores.csv")

        if not os.path.exists(weekly_path):
            print("[WARN] weekly_scores.csv not found. Run compute_weekly_scores() first.")
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -11,
                "week_number": week_number,
                "user_score": 0.0,
                "ai_score": 0.0,
                "result": None,
                "user_roster": [],
                "ai_roster": []
            }

        weekly_df = pd.read_csv(weekly_path)
        week_df = weekly_df[weekly_df["week_of_year"] == week_number]

        # --- Score user team ---
        user_rows = week_df[week_df["player_id"].isin(user_player_ids)]
        user_roster = user_rows[["player_id", "player_name", "total_fantasy_points"]].to_dict(orient="records")

        # Players on the user roster with no data that week score 0
        found_ids = set(user_rows["player_id"].tolist())
        for pid in user_player_ids:
            if pid not in found_ids:
                warning_count += 1
                print(f"[WARN] Player ID {pid} has no stats for week {week_number} — scoring 0.")
                user_roster.append({
                    "player_id": pid,
                    "player_name": "Unknown",
                    "total_fantasy_points": 0.0
                })

        user_score = sum(p["total_fantasy_points"] for p in user_roster)

        # --- Build and score AI team ---
        ai_result = build_ai_team(week_number)

        if ai_result["fatal_error"]:
            print("[ERROR] Could not build AI team.")
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -12,
                "week_number": week_number,
                "user_score": 0.0,
                "ai_score": 0.0,
                "result": None,
                "user_roster": user_roster,
                "ai_roster": []
            }

        ai_roster = [
            {
                "player_id": p["player_id"],
                "player_name": p["player_name"],
                "total_fantasy_points": p["total_fantasy_points"]
            }
            for p in ai_result["roster"]
        ]
        ai_score = sum(p["total_fantasy_points"] for p in ai_roster)

        # --- Determine result ---
        if user_score > ai_score:
            result = "win"
        elif user_score < ai_score:
            result = "loss"
        else:
            result = "tie"

        # --- Print summary ---
        print(f"\n{'='*40}")
        print(f"  Week {week_number} Matchup Result")
        print(f"{'='*40}")
        print(f"  User Score : {user_score:.1f} pts")
        print(f"  AI Score   : {ai_score:.1f} pts")
        print(f"  Result     : {result.upper()}")
        print(f"{'='*40}\n")

        return {
            "fatal_error": False,
            "warnings": warning_count,
            "error_code": 0,
            "week_number": week_number,
            "user_score": round(user_score, 2),
            "ai_score": round(ai_score, 2),
            "result": result,
            "user_roster": user_roster,
            "ai_roster": ai_roster
        }

    except Exception as e:
        print("[ERROR] score_matchup() failed.", file=sys.stderr)
        print(f"[ERROR] {e}", file=sys.stderr)
        return {
            "fatal_error": True,
            "warnings": warning_count,
            "error_code": -1,
            "week_number": week_number,
            "user_score": 0.0,
            "ai_score": 0.0,
            "result": None,
            "user_roster": [],
            "ai_roster": []
        }


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python score_matchup.py <week_number> <player_id1> <player_id2> ...")
        sys.exit(1)

    try:
        week = int(sys.argv[1])
        player_ids = [int(pid) for pid in sys.argv[2:]]
    except ValueError:
        print("[ERROR] week_number and player_ids must be integers.")
        sys.exit(1)

    result = score_matchup(week, player_ids)
    if result["fatal_error"]:
        sys.exit(result["error_code"])
