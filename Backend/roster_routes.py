"""
Roster management API endpoints.

This module provides RESTful API endpoints for managing user fantasy basketball rosters,
including CRUD operations, role swapping, and bulk operations.
"""

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError
from Backend import db
from Backend.models import UserTeamPlayer, Player
from Backend.constants import VALID_ROLES, DEFAULT_ROLE, ErrorCodes, MAX_STARTERS
from Backend.utils.validators import (
    validate_user_exists,
    validate_player_exists,
    validate_roster_size,
    validate_starter_count,
    is_player_on_roster,
    validate_role,
    get_roster_entry
)
from Backend.utils.serializers import (
    serialize_player_with_roster_info,
    serialize_player_basic,
    get_roster_summary,
    get_roster_with_details
)
from Backend.utils.errors import (
    bad_request,
    not_found,
    conflict,
    internal_server_error
)

bp = Blueprint("roster", __name__, url_prefix="/api")


@bp.get("/users/<int:user_id>/roster")
def get_roster(user_id):
    """
    Get user's roster with optional filtering.

    Query Parameters:
        role (str, optional): Filter by 'starter' or 'bench'

    Returns:
        JSON response with roster data and summary statistics
    """
    # Validate user exists
    user, error = validate_user_exists(user_id)
    if error:
        return not_found(error["code"], error["error"])

    # Get and validate query parameters
    role_filter = request.args.get('role')
    if role_filter:
        is_valid, error = validate_role(role_filter)
        if not is_valid:
            return bad_request(error["code"], error["error"])

    # Get roster with details
    roster_entries = get_roster_with_details(user_id, role_filter)

    # Serialize response
    players = [serialize_player_with_roster_info(entry) for entry in roster_entries]
    summary = get_roster_summary(user_id)

    return jsonify({
        "user_id": user_id,
        "roster_size": summary["total_players"],
        "starters_count": summary["starters"],
        "bench_count": summary["bench"],
        "players": players
    }), 200


@bp.post("/users/<int:user_id>/roster")
def add_player(user_id):
    """
    Add a player to user's roster.

    Request Body:
        {
            "player_id": int (required),
            "role": str (optional, defaults to "bench")
        }

    Returns:
        JSON response with added player info and roster summary
    """
    # Validate request
    if not request.is_json:
        return bad_request(
            ErrorCodes.INVALID_REQUEST,
            "Content-Type must be application/json"
        )

    data = request.get_json()
    player_id = data.get('player_id')
    role = data.get('role', DEFAULT_ROLE)

    # Validate required fields
    if not player_id:
        return bad_request(
            ErrorCodes.MISSING_REQUIRED_FIELD,
            "player_id is required"
        )

    # Validate role
    is_valid, error = validate_role(role)
    if not is_valid:
        return bad_request(error["code"], error["error"])

    # Validate user exists
    user, error = validate_user_exists(user_id)
    if error:
        return not_found(error["code"], error["error"])

    # Validate player exists
    player, error = validate_player_exists(player_id)
    if error:
        return not_found(error["code"], error["error"])

    # Check if player already on roster
    if is_player_on_roster(user_id, player_id):
        return conflict(
            ErrorCodes.PLAYER_ALREADY_ON_ROSTER,
            "Player is already on this roster"
        )

    # Validate roster size
    is_valid, error = validate_roster_size(user_id, 1)
    if not is_valid:
        return conflict(error["code"], error["error"], error.get("details"))

    # Validate starters count if adding as starter
    if role == 'starter':
        is_valid, error = validate_starter_count(user_id, 1)
        if not is_valid:
            return conflict(error["code"], error["error"], error.get("details"))

    # Create roster entry
    try:
        new_entry = UserTeamPlayer(
            user_id=user_id,
            player_id=player_id,
            role=role
        )
        db.session.add(new_entry)
        db.session.commit()

        # Refresh to get server-generated fields
        db.session.refresh(new_entry)

        # Load relationships for serialization
        entry_with_details = get_roster_entry(user_id, player_id)

        return jsonify({
            "message": "Player added to roster successfully",
            "roster_entry": serialize_player_with_roster_info(entry_with_details),
            "roster_summary": get_roster_summary(user_id)
        }), 201

    except IntegrityError:
        db.session.rollback()
        return conflict(
            ErrorCodes.PLAYER_ALREADY_ON_ROSTER,
            "Player is already on this roster"
        )
    except Exception as e:
        db.session.rollback()
        return internal_server_error(
            ErrorCodes.DATABASE_ERROR,
            "Failed to add player to roster"
        )


@bp.delete("/users/<int:user_id>/roster/<int:player_id>")
def remove_player(user_id, player_id):
    """
    Remove a player from the roster.

    Returns:
        JSON response with removed player info and updated roster summary
    """
    # Validate user exists
    user, error = validate_user_exists(user_id)
    if error:
        return not_found(error["code"], error["error"])

    # Find roster entry
    entry = get_roster_entry(user_id, player_id)
    if not entry:
        return not_found(
            ErrorCodes.PLAYER_NOT_ON_ROSTER,
            f"Player with ID {player_id} is not on this roster"
        )

    # Store info before deletion
    player_info = {
        "player_id": entry.player.id,
        "player_name": entry.player.name,
        "was_starter": entry.role == 'starter'
    }

    # Delete roster entry
    try:
        db.session.delete(entry)
        db.session.commit()

        return jsonify({
            "message": "Player removed from roster successfully",
            "removed_player": player_info,
            "roster_summary": get_roster_summary(user_id)
        }), 200

    except Exception as e:
        db.session.rollback()
        return internal_server_error(
            ErrorCodes.DATABASE_ERROR,
            "Failed to remove player from roster"
        )


@bp.patch("/users/<int:user_id>/roster/<int:player_id>")
def update_player_role(user_id, player_id):
    """
    Update a player's role (starter <-> bench).

    Request Body:
        {
            "role": str (required, must be "starter" or "bench")
        }

    Returns:
        JSON response with updated player info
    """
    # Validate request
    if not request.is_json:
        return bad_request(
            ErrorCodes.INVALID_REQUEST,
            "Content-Type must be application/json"
        )

    data = request.get_json()
    new_role = data.get('role')

    # Validate role field
    if not new_role:
        return bad_request(
            ErrorCodes.MISSING_REQUIRED_FIELD,
            "role is required"
        )

    is_valid, error = validate_role(new_role)
    if not is_valid:
        return bad_request(error["code"], error["error"])

    # Validate user exists
    user, error = validate_user_exists(user_id)
    if error:
        return not_found(error["code"], error["error"])

    # Find roster entry
    entry = get_roster_entry(user_id, player_id)
    if not entry:
        return not_found(
            ErrorCodes.PLAYER_NOT_ON_ROSTER,
            f"Player with ID {player_id} is not on this roster"
        )

    # Store previous role
    previous_role = entry.role

    # If changing to starter, validate starters count
    if new_role == 'starter' and previous_role != 'starter':
        is_valid, error = validate_starter_count(user_id, 1)
        if not is_valid:
            return conflict(error["code"], error["error"], error.get("details"))

    # Update role
    try:
        entry.role = new_role
        db.session.commit()

        # Refresh for updated data
        db.session.refresh(entry)
        entry_with_details = get_roster_entry(user_id, player_id)

        return jsonify({
            "message": "Player role updated successfully",
            "roster_entry": {
                **serialize_player_with_roster_info(entry_with_details),
                "previous_role": previous_role,
                "new_role": new_role
            },
            "roster_summary": get_roster_summary(user_id)
        }), 200

    except Exception as e:
        db.session.rollback()
        return internal_server_error(
            ErrorCodes.DATABASE_ERROR,
            "Failed to update player role"
        )


@bp.post("/users/<int:user_id>/roster/swap")
def swap_player_roles(user_id):
    """
    Atomically swap roles between two players.

    Request Body:
        {
            "player_1_id": int (required),
            "player_2_id": int (required)
        }

    Returns:
        JSON response with swapped player info
    """
    # Validate request
    if not request.is_json:
        return bad_request(
            ErrorCodes.INVALID_REQUEST,
            "Content-Type must be application/json"
        )

    data = request.get_json()
    player_1_id = data.get('player_1_id')
    player_2_id = data.get('player_2_id')

    # Validate required fields
    if not player_1_id or not player_2_id:
        return bad_request(
            ErrorCodes.MISSING_REQUIRED_FIELD,
            "Both player_1_id and player_2_id are required"
        )

    if player_1_id == player_2_id:
        return bad_request(
            ErrorCodes.INVALID_REQUEST,
            "Cannot swap a player with itself"
        )

    # Validate user exists
    user, error = validate_user_exists(user_id)
    if error:
        return not_found(error["code"], error["error"])

    # Find both roster entries
    entry1 = get_roster_entry(user_id, player_1_id)
    entry2 = get_roster_entry(user_id, player_2_id)

    if not entry1 or not entry2:
        missing = []
        if not entry1:
            missing.append(str(player_1_id))
        if not entry2:
            missing.append(str(player_2_id))
        return not_found(
            ErrorCodes.PLAYER_NOT_ON_ROSTER,
            f"Player(s) with ID(s) {', '.join(missing)} not on this roster"
        )

    # Store old roles
    old_role_1 = entry1.role
    old_role_2 = entry2.role

    # Swap roles using transaction
    try:
        with db.session.begin_nested():
            # Lock rows for update
            entry1_locked = (
                db.session.query(UserTeamPlayer)
                .filter_by(user_id=user_id, player_id=player_1_id)
                .with_for_update()
                .first()
            )
            entry2_locked = (
                db.session.query(UserTeamPlayer)
                .filter_by(user_id=user_id, player_id=player_2_id)
                .with_for_update()
                .first()
            )

            # Swap roles
            entry1_locked.role, entry2_locked.role = entry2_locked.role, entry1_locked.role

        db.session.commit()

        return jsonify({
            "message": "Player roles swapped successfully",
            "swapped_players": [
                {
                    "player_id": entry1.player.id,
                    "player_name": entry1.player.name,
                    "old_role": old_role_1,
                    "new_role": entry2.role
                },
                {
                    "player_id": entry2.player.id,
                    "player_name": entry2.player.name,
                    "old_role": old_role_2,
                    "new_role": entry1.role
                }
            ]
        }), 200

    except Exception as e:
        db.session.rollback()
        return internal_server_error(
            ErrorCodes.DATABASE_ERROR,
            "Failed to swap player roles"
        )


@bp.delete("/users/<int:user_id>/roster")
def clear_roster(user_id):
    """
    Clear entire roster (remove all players).

    Query Parameters:
        confirm (str, required): Must be "true" to prevent accidental deletions

    Returns:
        JSON response with count of removed players
    """
    # Require confirmation
    confirm = request.args.get('confirm')
    if confirm != 'true':
        return bad_request(
            ErrorCodes.CONFIRMATION_REQUIRED,
            "Must include confirm=true query parameter to clear roster"
        )

    # Validate user exists
    user, error = validate_user_exists(user_id)
    if error:
        return not_found(error["code"], error["error"])

    # Get all roster entries before deletion
    roster_entries = get_roster_with_details(user_id)

    if not roster_entries:
        return jsonify({
            "message": "Roster is already empty",
            "removed_count": 0
        }), 200

    # Store player info before deletion
    former_roster = [
        {
            "player_id": entry.player.id,
            "player_name": entry.player.name,
            "role": entry.role
        }
        for entry in roster_entries
    ]

    # Delete all roster entries
    try:
        db.session.query(UserTeamPlayer).filter_by(user_id=user_id).delete()
        db.session.commit()

        return jsonify({
            "message": "Roster cleared successfully",
            "removed_count": len(former_roster),
            "former_roster": former_roster
        }), 200

    except Exception as e:
        db.session.rollback()
        return internal_server_error(
            ErrorCodes.DATABASE_ERROR,
            "Failed to clear roster"
        )


@bp.post("/users/<int:user_id>/roster/bulk")
def bulk_add_players(user_id):
    """
    Add multiple players to roster at once.

    Request Body:
        {
            "players": [
                {"player_id": int, "role": str (optional)},
                ...
            ]
        }

    Returns:
        JSON response with results for each player (201 or 207 status)
    """
    # Validate request
    if not request.is_json:
        return bad_request(
            ErrorCodes.INVALID_REQUEST,
            "Content-Type must be application/json"
        )

    data = request.get_json()
    players_data = data.get('players')

    # Validate required fields
    if not players_data or not isinstance(players_data, list):
        return bad_request(
            ErrorCodes.MISSING_REQUIRED_FIELD,
            "players array is required"
        )

    if len(players_data) == 0:
        return bad_request(
            ErrorCodes.INVALID_REQUEST,
            "players array cannot be empty"
        )

    # Validate user exists
    user, error = validate_user_exists(user_id)
    if error:
        return not_found(error["code"], error["error"])

    # Validate that adding all players won't exceed roster limit
    total_to_add = len(players_data)
    is_valid, error = validate_roster_size(user_id, total_to_add)
    if not is_valid:
        return conflict(error["code"], error["error"], error.get("details"))

    # Count starters being added
    starters_to_add = sum(
        1 for p in players_data
        if p.get('role') == 'starter'
    )
    if starters_to_add > 0:
        is_valid, error = validate_starter_count(user_id, starters_to_add)
        if not is_valid:
            return conflict(error["code"], error["error"], error.get("details"))

    # Process each player
    results = []
    successful = 0
    failed = 0

    try:
        for player_data in players_data:
            player_id = player_data.get('player_id')
            role = player_data.get('role', DEFAULT_ROLE)

            if not player_id:
                results.append({
                    "player_id": None,
                    "status": "failed",
                    "error": "player_id is required"
                })
                failed += 1
                continue

            # Validate role
            is_valid, role_error = validate_role(role)
            if not is_valid:
                results.append({
                    "player_id": player_id,
                    "status": "failed",
                    "error": role_error["error"]
                })
                failed += 1
                continue

            # Validate player exists
            player, player_error = validate_player_exists(player_id)
            if player_error:
                results.append({
                    "player_id": player_id,
                    "status": "failed",
                    "error": player_error["error"]
                })
                failed += 1
                continue

            # Check if already on roster
            if is_player_on_roster(user_id, player_id):
                results.append({
                    "player_id": player_id,
                    "status": "failed",
                    "error": "Player already on roster"
                })
                failed += 1
                continue

            # Add player
            new_entry = UserTeamPlayer(
                user_id=user_id,
                player_id=player_id,
                role=role
            )
            db.session.add(new_entry)
            db.session.flush()

            results.append({
                "player_id": player_id,
                "status": "success",
                "roster_entry_id": new_entry.id
            })
            successful += 1

        # Commit all changes
        db.session.commit()

        status_code = 201 if failed == 0 else 207

        return jsonify({
            "message": "Bulk add completed",
            "successful": successful,
            "failed": failed,
            "results": results,
            "roster_summary": get_roster_summary(user_id)
        }), status_code

    except Exception as e:
        db.session.rollback()
        return internal_server_error(
            ErrorCodes.DATABASE_ERROR,
            "Failed to add players to roster"
        )
