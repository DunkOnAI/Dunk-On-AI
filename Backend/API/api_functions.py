"""
This file contains API utility functions for fetching static NBA reference data.

Included functions:
    - get_teams(): Fetches all NBA teams and prepares structured data.
    - get_players(): Fetches all active NBA players and prepares structured data.
    - get_game_stats(): (Placeholder) Intended for fetching game-level statistics.

Each function returns a standardized dictionary containing:
    - fatal_error flag
    - warnings count
    - error_code
    - structured data payload
"""


# Import required libraries
import sys
import time
import pandas as pd
from datetime import datetime
from nba_api.stats.static import teams
from nba_api.stats.static import players
from nba_api.stats.endpoints import leaguegamelog


# Function to fetch all teams
def get_teams():
    """
    Returns:
        dict: A dictionary containing:
            - fatal_error (bool): True if a fatal exception occurred.
            - warnings (int): Number of non-fatal parsing errors encountered.
            - error_code (int): 0 if successful, -1 if fatal error.
            - teams (list[dict]): List of cleaned team dictionaries with keys:
                - id (int)
                - name (str)
                - city (str)
                - abbreviation (str)
    """

    # Track warnings used for better logging
    warning_count = 0

    try:
        print("[INFO] Fetching NBA teams...")

        # Fetch all NBA teams
        nba_teams = teams.get_teams()

        # Wait briefly to avoid API throttling
        time.sleep(0.5)

        # Prepare clean list for database insertion
        clean_teams = []

        for team in nba_teams:
            try:
                team_id = team["id"]
                team_name = team["full_name"]
                team_city = team["city"]
                team_abbreviation = team["abbreviation"]

                clean_teams.append({
                    "id": team_id,
                    "name": team_name,
                    "city": team_city,
                    "abbreviation": team_abbreviation
                })

            except Exception as e:
                print(f"[WARN] Failed to parse team {team.get('full_name', 'Unknown')}: {e}")
                warning_count += 1
                continue

        print(f"[INFO] Successfully fetched {len(clean_teams)} teams.")
        return {
            "fatal_error": False,
            "warnings": warning_count,
            "error_code": 0,
            "teams": clean_teams
        }

    except Exception as e:
        # Fatal error for the function
        print("[WARN] Failed to fetch teams.")
        print(f"[ERROR] {e}", file=sys.stderr)

        return {
            "fatal_error": True,
            "warnings": warning_count,
            "error_code": -1,
            "teams": []
        }


# Function to fetch all active NBA players
def get_players():
    """
    Returns:
        dict: A dictionary containing:
            - fatal_error (bool): True if a fatal exception occurred.
            - warnings (int): Number of non-fatal parsing errors encountered.
            - error_code (int): 0 if successful, -1 if fatal error.
            - players (list[dict]): List of cleaned player dictionaries with keys:
                - id (int)
                - name (str)
                - team_id (int | None)
                - position (str)
                - height_weight (str)
    """

    # Track warnings used for better logging
    warning_count = 0

    try:
        print("[INFO] Fetching active NBA players...")

        # Fetch all players
        nba_players = players.get_players()

        # Wait briefly to avoid API throttling
        time.sleep(0.5)

        # Filter only active players
        active_players = [p for p in nba_players if p["is_active"]]

        # Prepare clean list for database insertion
        clean_players = []

        for player in active_players:
            try:
                player_id = player["id"]
                player_name = player["full_name"]
                team_id = player.get("team_id", None)

                # Position and height/weight must be called for each player individually
                # Set for "Unknown" now bc of rate limits
                position = "Unknown"
                height_weight = "Unknown"

                clean_players.append({
                    "id": player_id,
                    "name": player_name,
                    "team_id": team_id,
                    "position": position,
                    "height_weight": height_weight
                })

            except Exception as e:
                print(f"[WARN] Failed to parse player {player.get('full_name', 'Unknown')}: {e}")
                warning_count += 1
                continue

        print(f"[INFO] Successfully fetched {len(clean_players)} active players.")
        return {
            "fatal_error": False,
            "warnings": warning_count,
            "error_code": 0,
            "players": clean_players
        }

    except Exception as e:
        # Fatal error for the function
        print("[WARN] Failed to fetch players.")
        print(f"[ERROR] {e}", file=sys.stderr)

        return {
            "fatal_error": True,
            "warnings": warning_count,
            "error_code": -1,
            "players": []
        }


# Function to fetch all NBA game stats from strat_date untill now
def get_game_stats(start_date=None):
    """
    Returns:
        dict: A dictionary containing:
            - fatal_error (bool): True if a fatal exception occurred.
            - warnings (int): Number of non-fatal parsing errors encountered.
            - error_code (int):
                0   -> Success
                -1  -> Unexpected fatal exception
            - game_stats (list[dict]): List of cleaned game stat dictionaries
    """

    # Track warnings used for better logging
    warning_count = 0

    # Prepare clean list for database insertion
    game_stats = []

    try:
        print("[INFO] Fetching game stats...")

        # If DB empty -> default baseline
        if start_date is None:
            start_date = datetime(2024, 1, 1)

        # Ensure datetime
        if isinstance(start_date, str):
            start_date = pd.to_datetime(start_date)

        today = datetime.utcnow()

        # -------- Season Helper --------
        def get_season_string(date_obj):
            year = date_obj.year
            if date_obj.month >= 10:
                return f"{year}-{str(year + 1)[-2:]}"
            else:
                return f"{year - 1}-{str(year)[-2:]}"
        # -------------------------------

        # Determine seasons to fetch
        seasons = set()

        current = start_date
        while current.year <= today.year + 1:
            seasons.add(get_season_string(current))
            current = datetime(current.year + 1, 1, 1)

        seasons = sorted(seasons)

        # Fetch Per Season
        for season in seasons:
            print(f"[INFO] Fetching season {season}...")

            try:
                gamelog = leaguegamelog.LeagueGameLog(
                    season=season,
                    season_type_all_star="Regular Season",
                    player_or_team_abbreviation="P"
                )

                time.sleep(0.6)

                df = gamelog.get_data_frames()[0]

                if df.empty:
                    continue

                df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"])

                # Filter strictly newer games
                df = df[df["GAME_DATE"] > start_date]

                for _, row in df.iterrows():
                    try:
                        min_value = row["MIN"]

                        if pd.isna(min_value):
                            minutes_played = 0.0
                        else:
                            minutes_played = float(min_value)

                        game_stats.append({
                            "player_id": int(row["PLAYER_ID"]),
                            "game_id": row["GAME_ID"],
                            "game_date": row["GAME_DATE"].isoformat(),
                            "team_id": int(row["TEAM_ID"]),
                            "points": int(row["PTS"]),
                            "rebounds": int(row["REB"]),
                            "assists": int(row["AST"]),
                            "steals": int(row["STL"]),
                            "blocks": int(row["BLK"]),
                            "turnovers": int(row["TOV"]),
                            "minutes_played": float(minutes_played)
                        })

                    except Exception as e:
                        print(f"[WARN] Failed to parse row for player {row.get('PLAYER_ID')} in game {row.get('GAME_ID')}: {e}")
                        warning_count += 1
                        continue

            except Exception as e:
                print(f"[WARN] Failed to fetch season {season}: {e}")
                warning_count += 1
                continue

        print(f"[INFO] Successfully collected {len(game_stats)} new game stat rows.")
        return {
            "fatal_error": False,
            "warnings": warning_count,
            "error_code": 0,
            "game_stats": game_stats
        }

    except Exception as e:
        # Fatal error for the function
        print("[WARN] Failed to fetch game stats.")
        print(e)

        return {
            "fatal_error": True,
            "warnings": warning_count,
            "error_code": -1,
            "game_stats": []
        }
