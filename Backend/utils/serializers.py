"""
Serialization utilities for roster management API.

This module provides functions to convert database models into
JSON-serializable dictionaries for API responses.
"""

from Backend.models import UserTeamPlayer, Player
from Backend import db
from Backend.constants import MAX_ROSTER_SIZE
import sqlalchemy.orm as so


def serialize_player_with_roster_info(roster_entry):
    """
    Convert a UserTeamPlayer entry with relationships to API response format.

    Args:
        roster_entry (UserTeamPlayer): Roster entry with player and team relationships loaded

    Returns:
        dict: Serialized player data with roster information
    """
    player = roster_entry.player
    team = player.team if player else None

    return {
        "roster_entry_id": roster_entry.id,
        "player_id": player.id if player else None,
        "player_name": player.name if player else None,
        "team": team.name if team else None,
        "team_abbreviation": team.abbreviation if team else None,
        "position": player.position if player else None,
        "height_weight": player.height_weight if player else None,
        "role": roster_entry.role,
        "added_at": roster_entry.added_at.isoformat() if roster_entry.added_at else None
    }


def serialize_player_basic(player):
    """
    Convert a Player to basic API response format (without roster info).

    Args:
        player (Player): Player object with team relationship loaded

    Returns:
        dict: Serialized player data
    """
    team = player.team if player else None

    return {
        "player_id": player.id,
        "player_name": player.name,
        "team": team.name if team else None,
        "team_abbreviation": team.abbreviation if team else None,
        "position": player.position,
        "height_weight": player.height_weight
    }


def get_roster_summary(user_id):
    """
    Get current roster statistics for a user.

    Args:
        user_id (int): User ID

    Returns:
        dict: Roster summary with counts and available slots
    """
    total = db.session.query(UserTeamPlayer).filter_by(user_id=user_id).count()
    starters = (
        db.session.query(UserTeamPlayer)
        .filter_by(user_id=user_id, role='starter')
        .count()
    )

    return {
        "total_players": total,
        "starters": starters,
        "bench": total - starters,
        "slots_remaining": MAX_ROSTER_SIZE - total
    }


def get_roster_with_details(user_id, role=None):
    """
    Get full roster with player and team details, efficiently loaded.

    Args:
        user_id (int): User ID
        role (str, optional): Filter by role ('starter' or 'bench')

    Returns:
        list[UserTeamPlayer]: Roster entries with relationships loaded
    """
    query = (
        db.session.query(UserTeamPlayer)
        .filter_by(user_id=user_id)
        .join(Player)
        .options(
            so.joinedload(UserTeamPlayer.player).joinedload(Player.team)
        )
        .order_by(
            # Starters first, then bench
            db.case(
                (UserTeamPlayer.role == 'starter', 0),
                else_=1
            ),
            UserTeamPlayer.added_at.desc()
        )
    )

    if role:
        query = query.filter(UserTeamPlayer.role == role)

    return query.all()
