"""
Validation utilities for roster management API.

This module provides validation functions for user requests, roster constraints,
and data integrity checks used across roster endpoints.
"""

from Backend.models import User, Player, UserTeamPlayer
from Backend import db
from Backend.constants import MAX_ROSTER_SIZE, MAX_STARTERS, VALID_ROLES, ErrorCodes


def validate_user_exists(user_id):
    """
    Validate that a user exists in the database.

    Args:
        user_id (int): User ID to validate

    Returns:
        tuple: (user_object, error_dict)
            - If user exists: (User, None)
            - If user not found: (None, {"error": message, "code": error_code})
    """
    user = db.session.query(User).get(user_id)
    if not user:
        return None, {
            "error": f"User with ID {user_id} not found",
            "code": ErrorCodes.USER_NOT_FOUND
        }
    return user, None


def validate_player_exists(player_id):
    """
    Validate that a player exists in the database.

    Args:
        player_id (int): Player ID to validate

    Returns:
        tuple: (player_object, error_dict)
            - If player exists: (Player, None)
            - If player not found: (None, {"error": message, "code": error_code})
    """
    player = db.session.query(Player).get(player_id)
    if not player:
        return None, {
            "error": f"Player with ID {player_id} not found",
            "code": ErrorCodes.PLAYER_NOT_FOUND
        }
    return player, None


def validate_roster_size(user_id, adding_count=1):
    """
    Check if adding players would exceed the maximum roster size.

    Args:
        user_id (int): User ID to check
        adding_count (int): Number of players being added (default: 1)

    Returns:
        tuple: (is_valid, error_dict)
            - If valid: (True, None)
            - If would exceed limit: (False, {"error": message, "code": error_code, "details": {...}})
    """
    current_count = db.session.query(UserTeamPlayer).filter_by(user_id=user_id).count()

    if current_count + adding_count > MAX_ROSTER_SIZE:
        return False, {
            "error": f"Cannot add player(s). Roster already contains {current_count} player(s) and maximum is {MAX_ROSTER_SIZE}.",
            "code": ErrorCodes.ROSTER_FULL,
            "details": {
                "current_roster_size": current_count,
                "max_roster_size": MAX_ROSTER_SIZE,
                "attempting_to_add": adding_count
            }
        }

    return True, None


def validate_starter_count(user_id, adding_starter_count=1):
    """
    Check if adding starters would exceed the maximum starter count.

    Args:
        user_id (int): User ID to check
        adding_starter_count (int): Number of starters being added (default: 1)

    Returns:
        tuple: (is_valid, error_dict)
            - If valid: (True, None)
            - If would exceed limit: (False, {"error": message, "code": error_code, "details": {...}})
    """
    current_starters = (
        db.session.query(UserTeamPlayer)
        .filter_by(user_id=user_id, role='starter')
        .count()
    )

    if current_starters + adding_starter_count > MAX_STARTERS:
        return False, {
            "error": f"Cannot add as starter. Already have {current_starters} starter(s) and maximum is {MAX_STARTERS}.",
            "code": ErrorCodes.STARTERS_FULL,
            "details": {
                "current_starters": current_starters,
                "max_starters": MAX_STARTERS,
                "attempting_to_add": adding_starter_count
            }
        }

    return True, None


def is_player_on_roster(user_id, player_id):
    """
    Check if a player is already on a user's roster.

    Args:
        user_id (int): User ID to check
        player_id (int): Player ID to check

    Returns:
        bool: True if player is on roster, False otherwise
    """
    entry = (
        db.session.query(UserTeamPlayer)
        .filter_by(user_id=user_id, player_id=player_id)
        .first()
    )
    return entry is not None


def validate_role(role):
    """
    Validate that a role is one of the valid roles.

    Args:
        role (str): Role to validate

    Returns:
        tuple: (is_valid, error_dict)
            - If valid: (True, None)
            - If invalid: (False, {"error": message, "code": error_code})
    """
    if role not in VALID_ROLES:
        return False, {
            "error": f"Role must be one of: {', '.join(VALID_ROLES)}. Got: '{role}'",
            "code": ErrorCodes.INVALID_ROLE
        }
    return True, None


def get_roster_entry(user_id, player_id):
    """
    Get a roster entry with player and team details loaded.

    Args:
        user_id (int): User ID
        player_id (int): Player ID

    Returns:
        UserTeamPlayer or None: Roster entry with relationships loaded, or None if not found
    """
    import sqlalchemy.orm as so

    entry = (
        db.session.query(UserTeamPlayer)
        .filter_by(user_id=user_id, player_id=player_id)
        .join(Player)
        .options(
            so.joinedload(UserTeamPlayer.player).joinedload(Player.team)
        )
        .first()
    )
    return entry
