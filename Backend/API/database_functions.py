"""
This file contains database synchronization functions for NBA reference data.

Included functions:
    - sync_teams(): Fetches teams using API functions and upserts them into the database.
    - sync_players(): Fetches players, enriches them with detailed information,
                      and upserts them into the database.

Each function integrates external API data with the Supabase database and returns a
standardized dictionary containing:
    - fatal_error flag
    - warnings count
    - error_code
"""


# Import required libraries
import sys
import time
from supabase import create_client
from nba_api.stats.endpoints import commonplayerinfo
from api_functions import get_teams, get_players, get_game_stats


# Initialize Supabase client
# This must be replaced for localised function
SUPABASE_URL = "https://fncxnyydygcsxafohiwk.supabase.co"
SUPABASE_KEY = "sb_publishable_ASJifMadJhm5705VpjhgPg_Xyw7R0cM"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
# End of block


# Function to sync all active teams to database
def sync_teams():
    """
    Returns:
        dict: A dictionary containing:
            - fatal_error (bool): True if a fatal exception occurred.
            - warnings (int): Number of non-fatal issues encountered.
            - error_code (int):
                0   -> Success
                -1  -> Unexpected exception
                -21 -> Failed to fetch teams
                -22 -> No teams returned
                -23 -> Database upsert error
    """

    # Track warnings used for better logging
    warning_count = 0

    try:
        print("[INFO] Syncing teams to database...")

        result = get_teams()

        if result["fatal_error"]:
            print("[ERROR] Could not fetch teams.")
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -21,
            }

        teams_data = result["teams"]

        if not teams_data:
            print("[WARN] No teams returned.")
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -22,
            }

        # Upsert into database
        response = supabase.table("teams").upsert(teams_data).execute()

        if hasattr(response, "error") and response.error:
            print("[ERROR] Database error while syncing teams.")
            print(response.error, file=sys.stderr)
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -23,
            }

        print(f"[INFO] Synced {len(teams_data)} teams to database.")
        return {
            "fatal_error": False,
            "warnings": warning_count,
            "error_code": 0,
        }

    except Exception as e:
        # Fatal error for the function
        print("[ERROR] Failed to sync teams.")
        print(e, file=sys.stderr)

        return {
            "fatal_error": True,
            "warnings": warning_count,
            "error_code": -1,
        }


# Function to sync all active players to database
def sync_players():
    """
    Returns:
        dict: A dictionary containing:
            - fatal_error (bool): True if a fatal exception occurred.
            - warnings (int): Number of non-fatal issues encountered.
            - error_code (int):
                0   -> Success
                -1  -> Unexpected exception
                -21 -> Failed to fetch players
                -22 -> No players returned
                -23 -> No enriched players produced
                -24 -> Database upsert error
    """

    # Track warnings used for better logging
    warning_count = 0

    try:
        print("[INFO] Syncing players to database...")

        result = get_players()

        if result["fatal_error"]:
            print("[ERROR] Could not fetch players.")
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -21,
            }

        players_data = result["players"]

        if not players_data:
            print("[WARN] No players returned.")
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -22,
            }

        enriched_players = []

        for player in players_data:
            try:
                player_id = player["id"]

                print(f"[INFO] Fetching details for player {player_id}...")

                info = commonplayerinfo.CommonPlayerInfo(player_id=player_id)

                time.sleep(0.6)  # avoid rate limiting

                df = info.get_data_frames()[0]
                row = df.iloc[0]

                # Must be converted from numpy variable to standard python variable
                team_id = int(row["TEAM_ID"]) if row["TEAM_ID"] else None
                position = str(row["POSITION"]) if row["POSITION"] else "Unknown"
                height = str(row["HEIGHT"]) if row["HEIGHT"] else "Unknown"
                weight = str(row["WEIGHT"]) if row["WEIGHT"] else "Unknown"

                height_weight = f"{height} / {weight}"

                enriched_players.append({
                    "id": player_id,
                    "name": player["name"],
                    "team_id": team_id,
                    "position": position if position else "Unknown",
                    "height_weight": height_weight
                })

            except Exception as e:
                print(f"[WARN] Failed to fetch info for player {player['id']}: {e}")
                warning_count += 1
                continue

        if not enriched_players:
            print("[WARN] No enriched_players returned.")
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -23,
            }

        # Upsert into database
        response = supabase.table("players").upsert(enriched_players).execute()

        if hasattr(response, "error") and response.error:
            print("[ERROR] Database error while syncing players.")
            print(response.error, file=sys.stderr)
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -24,
            }

        print(f"[INFO] Synced {len(enriched_players)} players.")
        return {
            "fatal_error": False,
            "warnings": warning_count,
            "error_code": 0,
        }

    except Exception as e:
        # Fatal error for the function
        print("[ERROR] Failed to sync players.")
        print(e, file=sys.stderr)

        return {
            "fatal_error": True,
            "warnings": warning_count,
            "error_code": -1,
        }


# Function to sync game stats to database
def sync_game_stats():
    """
    Returns:
        dict: A dictionary containing:
            - fatal_error (bool): True if a fatal exception occurred.
            - warnings (int): Number of non-fatal issues encountered.
            - error_code (int):
                0   -> Success
                -1  -> Unexpected exception
                -31 -> Failed to fetch latest game date
                -32 -> Failed to fetch game stats from API
                -33 -> No game stats returned
                -34 -> Database upsert error
    """

    # Track warnings used for better logging
    warning_count = 0

    try:
        print("[INFO] Syncing game stats to database...")

        # STEP 1: Get latest game_date from database
        try:
            response = (
                supabase
                .table("game_stats")
                .select("game_date")
                .order("game_date", desc=True)
                .limit(1)
                .execute()
            )

            if hasattr(response, "error") and response.error:
                print("[ERROR] Failed to fetch latest game_date.")
                print(response.error, file=sys.stderr)
                return {
                    "fatal_error": True,
                    "warnings": warning_count,
                    "error_code": -31,
                }

            data = response.data

            if data:
                latest_game_date = data[0]["game_date"]
                print(f"[INFO] Latest game in DB: {latest_game_date}")
            else:
                latest_game_date = None
                print("[INFO] Database empty. Using default baseline.")

        except Exception as e:
            print("[ERROR] Could not retrieve latest game date.")
            print(e, file=sys.stderr)
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -31,
            }

        # STEP 2: Fetch new game stats
        result = get_game_stats(start_date=latest_game_date)

        if result["fatal_error"]:
            print("[ERROR] Failed to fetch game stats from API.")
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -32,
            }

        game_stats_data = result["game_stats"]

        if not game_stats_data:
            print("[INFO] No new game stats to sync.")
            return {
                "fatal_error": False,
                "warnings": warning_count,
                "error_code": 0,
            }
        
        # STEP 2.5: Filter out players not present in DB
        try:
            players_response = supabase.table("players").select("id").execute()

            if hasattr(players_response, "error") and players_response.error:
                print("[ERROR] Failed to fetch player IDs from database.")
                print(players_response.error, file=sys.stderr)
                return {
                    "fatal_error": True,
                    "warnings": warning_count,
                    "error_code": -33,
                }

            valid_player_ids = {p["id"] for p in players_response.data}

            original_count = len(game_stats_data)

            game_stats_data = [
                row for row in game_stats_data
                if row["player_id"] in valid_player_ids
            ]

            filtered_out = original_count - len(game_stats_data)

            if filtered_out > 0:
                print(f"[INFO] Filtered out {filtered_out} rows due to missing players.")

        except Exception as e:
            print("[ERROR] Failed while filtering player IDs.")
            print(e, file=sys.stderr)
            return {
                "fatal_error": True,
                "warnings": warning_count,
                "error_code": -34,
            }

        # STEP 3: Batch upsert
        batch_size = 1000
        total_rows = len(game_stats_data)

        print(f"[INFO] Upserting {total_rows} rows in batches of {batch_size}...")

        for i in range(0, total_rows, batch_size):
            batch = game_stats_data[i:i + batch_size]

            response = (
                supabase
                .table("game_stats")
                .upsert(batch)
                .execute()
            )

            if hasattr(response, "error") and response.error:
                print("[ERROR] Database error during batch upsert.")
                print(response.error, file=sys.stderr)
                return {
                    "fatal_error": True,
                    "warnings": warning_count,
                    "error_code": -35,
                }

            print(f"[INFO] Synced rows {i} to {i + len(batch)}")

        print(f"[INFO] Successfully synced {total_rows} game stat rows.")

        return {
            "fatal_error": False,
            "warnings": warning_count,
            "error_code": 0,
        }

    except Exception as e:
        print("[ERROR] Failed to sync game stats.")
        print(e, file=sys.stderr)

        return {
            "fatal_error": True,
            "warnings": warning_count,
            "error_code": -1,
        }
