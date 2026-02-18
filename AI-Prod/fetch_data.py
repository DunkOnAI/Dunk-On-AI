# Main entry script for NBA data collection pipeline
# This file orchestrates the full data fetching process.
# It first collects players for the defined period,
# then collects detailed game statistics for each player.
# If any step fails, the script exits safely with a clear error message.


# Import required libraries
import sys
import traceback
from get_players import get_players
from get_player_stats import get_player_stats


# Explain function breafly
def main():
    print("Starting data fetch process...\n")

    # Step 1: Fetch all players who played in the defined time period
    try:
        print("Step 1/2: Fetching players...")
        result = get_players()  # Returns warning info

        if result["fatal_error"]:
            print("[WARN] Step 1 not completed: Fatal error occurred while fetching players.")
            sys.exit(result["error_code"])
        elif result["warnings"] != 0:
            print(f"[WARN] Step 1 completed with {result['warnings']} warnings.")
        else:
            print("Step 1 completed: Players fetched successfully.\n")

    except Exception as e:
        # If player fetching fails:
        # - Print clean error message
        # - Print full traceback for debugging
        # - Exit with failure code
        print("[WARN] Step 1 not completed: Fatal error occurred while fetching players.")
        print(f"[ERROR] {e}.")
        traceback.print_exc()
        sys.exit(-1)

    # Step 2: Fetch detailed game stats for each player
    try:
        print("[INFO] Step 2/2: Fetching player stats...")
        result = get_player_stats()  # Returns warning info

        if result["fatal_error"]:
            print("[WARN] Step 2 not completed: Fatal error occurred while fetching player stats.")
            sys.exit(result["error_code"])
        elif result["warnings"] != 0:
            print(f"[WARN] Step 2 completed with {result['warnings']} warnings.")
        else:
            print("[INFO] Step 2 completed: Player stats fetched successfully.\n")

    except Exception as e:
        # If stats fetching fails:
        # - Print clean error message
        # - Print full traceback for debugging
        # - Exit with failure code
        print("[WARN] Step 2 not completed: Fatal error occurred while fetching player stats.")
        print(f"[ERROR] {e}")
        traceback.print_exc()
        sys.exit(-2)

    # If both steps complete successfully
    print("Data fetch process completed successfully.")


# Run this block only if the script is executed directly (not imported)
if __name__ == "__main__":
    main()
