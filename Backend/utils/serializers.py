"""
Serialization utilities for roster management API.
Works with plain dicts returned by the Supabase PostgREST API.

Supabase nested select shape expected:
  user_team_players row → {
      "id": ..., "user_id": ..., "player_id": ..., "role": ..., "added_at": ...,
      "players": {
          "id": ..., "name": ..., "position": ..., "height_weight": ...,
          "teams": { "id": ..., "name": ..., "abbreviation": ..., "city": ... }
      }
  }
"""

from Backend.constants import MAX_ROSTER_SIZE


def serialize_player_with_roster_info(entry):
    """
    Convert a user_team_players dict (with nested players + teams) to API response format.
    """
    player = entry.get("players") or {}
    team = player.get("teams") or {}

    return {
        "roster_entry_id": entry.get("id"),
        "player_id": player.get("id"),
        "player_name": player.get("name"),
        "team": team.get("name"),
        "team_abbreviation": team.get("abbreviation"),
        "position": player.get("position"),
        "height_weight": player.get("height_weight"),
        "role": entry.get("role"),
        "added_at": entry.get("added_at"),
    }


def serialize_player_basic(player):
    """
    Convert a players dict (with nested teams) to basic API response format.
    """
    team = player.get("teams") or {}

    return {
        "player_id": player.get("id"),
        "player_name": player.get("name"),
        "team": team.get("name"),
        "team_abbreviation": team.get("abbreviation"),
        "position": player.get("position"),
        "height_weight": player.get("height_weight"),
    }


def get_roster_summary(client, user_id):
    """
    Count total players and starters on the roster via two Supabase count queries.
    """
    total_result = (
        client.table("user_team_players")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .execute()
    )
    total = total_result.count or 0

    starter_result = (
        client.table("user_team_players")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .eq("role", "starter")
        .execute()
    )
    starters = starter_result.count or 0

    return {
        "total_players": total,
        "starters": starters,
        "bench": total - starters,
        "slots_remaining": MAX_ROSTER_SIZE - total,
    }


def get_roster_with_details(client, user_id, role=None):
    """
    Fetch all roster entries for a user with nested player and team data.
    Starters are sorted first.
    """
    query = (
        client.table("user_team_players")
        .select("*, players(*, teams(*))")
        .eq("user_id", user_id)
    )
    if role:
        query = query.eq("role", role)

    result = query.execute()
    entries = result.data or []

    # Sort: starters first
    entries.sort(key=lambda e: (0 if e.get("role") == "starter" else 1))
    return entries
