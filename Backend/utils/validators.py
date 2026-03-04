"""
Validation utilities for roster management API.
Uses the Supabase PostgREST API instead of SQLAlchemy.
"""

from Backend.constants import MAX_ROSTER_SIZE, MAX_STARTERS, VALID_ROLES, ErrorCodes


def validate_user_exists(client, user_id):
    result = client.table("users").select("id").eq("id", user_id).limit(1).execute()
    if not result.data:
        return None, {
            "error": f"User with ID {user_id} not found",
            "code": ErrorCodes.USER_NOT_FOUND,
        }
    return result.data[0], None


def validate_player_exists(client, player_id):
    result = client.table("players").select("*").eq("id", player_id).limit(1).execute()
    if not result.data:
        return None, {
            "error": f"Player with ID {player_id} not found",
            "code": ErrorCodes.PLAYER_NOT_FOUND,
        }
    return result.data[0], None


def validate_roster_size(client, user_id, adding_count=1):
    result = (
        client.table("user_team_players")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .execute()
    )
    current_count = result.count or 0

    if current_count + adding_count > MAX_ROSTER_SIZE:
        return False, {
            "error": (
                f"Cannot add player(s). Roster already contains {current_count} "
                f"player(s) and maximum is {MAX_ROSTER_SIZE}."
            ),
            "code": ErrorCodes.ROSTER_FULL,
            "details": {
                "current_roster_size": current_count,
                "max_roster_size": MAX_ROSTER_SIZE,
                "attempting_to_add": adding_count,
            },
        }
    return True, None


def validate_starter_count(client, user_id, adding_starter_count=1):
    result = (
        client.table("user_team_players")
        .select("id", count="exact")
        .eq("user_id", user_id)
        .eq("role", "starter")
        .execute()
    )
    current_starters = result.count or 0

    if current_starters + adding_starter_count > MAX_STARTERS:
        return False, {
            "error": (
                f"Cannot add as starter. Already have {current_starters} "
                f"starter(s) and maximum is {MAX_STARTERS}."
            ),
            "code": ErrorCodes.STARTERS_FULL,
            "details": {
                "current_starters": current_starters,
                "max_starters": MAX_STARTERS,
                "attempting_to_add": adding_starter_count,
            },
        }
    return True, None


def is_player_on_roster(client, user_id, player_id):
    result = (
        client.table("user_team_players")
        .select("id")
        .eq("user_id", user_id)
        .eq("player_id", player_id)
        .limit(1)
        .execute()
    )
    return len(result.data) > 0


def validate_role(role):
    if role not in VALID_ROLES:
        return False, {
            "error": f"Role must be one of: {', '.join(VALID_ROLES)}. Got: '{role}'",
            "code": ErrorCodes.INVALID_ROLE,
        }
    return True, None


def get_roster_entry(client, user_id, player_id):
    """
    Fetch a single roster entry with its player and team details.
    Returns a dict or None.
    """
    result = (
        client.table("user_team_players")
        .select("*, players(*, teams(*))")
        .eq("user_id", user_id)
        .eq("player_id", player_id)
        .limit(1)
        .execute()
    )
    return result.data[0] if result.data else None
