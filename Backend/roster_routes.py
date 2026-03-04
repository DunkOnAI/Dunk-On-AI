"""
Roster management API endpoints.
Uses the Supabase PostgREST API instead of SQLAlchemy.
"""

from flask import Blueprint, jsonify, request

from Backend.constants import DEFAULT_ROLE, ErrorCodes
from Backend.supabaseclient import get_supabase_client
from Backend.utils.validators import (
    validate_user_exists,
    validate_player_exists,
    validate_roster_size,
    validate_starter_count,
    is_player_on_roster,
    validate_role,
    get_roster_entry,
)
from Backend.utils.serializers import (
    serialize_player_with_roster_info,
    get_roster_summary,
    get_roster_with_details,
)
from Backend.utils.errors import (
    bad_request,
    not_found,
    conflict,
    internal_server_error,
)

bp = Blueprint("roster", __name__, url_prefix="/api")


@bp.get("/users/<int:user_id>/roster")
def get_roster(user_id):
    client = get_supabase_client()

    _, error = validate_user_exists(client, user_id)
    if error:
        return not_found(error["code"], error["error"])

    role_filter = request.args.get("role")
    if role_filter:
        is_valid, error = validate_role(role_filter)
        if not is_valid:
            return bad_request(error["code"], error["error"])

    roster_entries = get_roster_with_details(client, user_id, role_filter)
    players = [serialize_player_with_roster_info(entry) for entry in roster_entries]
    summary = get_roster_summary(client, user_id)

    return jsonify({
        "user_id": user_id,
        "roster_size": summary["total_players"],
        "starters_count": summary["starters"],
        "bench_count": summary["bench"],
        "players": players,
    }), 200


@bp.post("/users/<int:user_id>/roster")
def add_player(user_id):
    if not request.is_json:
        return bad_request(ErrorCodes.INVALID_REQUEST, "Content-Type must be application/json")

    data = request.get_json()
    player_id = data.get("player_id")
    role = data.get("role", DEFAULT_ROLE)

    if not player_id:
        return bad_request(ErrorCodes.MISSING_REQUIRED_FIELD, "player_id is required")

    is_valid, error = validate_role(role)
    if not is_valid:
        return bad_request(error["code"], error["error"])

    client = get_supabase_client()

    _, error = validate_user_exists(client, user_id)
    if error:
        return not_found(error["code"], error["error"])

    _, error = validate_player_exists(client, player_id)
    if error:
        return not_found(error["code"], error["error"])

    if is_player_on_roster(client, user_id, player_id):
        return conflict(ErrorCodes.PLAYER_ALREADY_ON_ROSTER, "Player is already on this roster")

    is_valid, error = validate_roster_size(client, user_id, 1)
    if not is_valid:
        return conflict(error["code"], error["error"], error.get("details"))

    if role == "starter":
        is_valid, error = validate_starter_count(client, user_id, 1)
        if not is_valid:
            return conflict(error["code"], error["error"], error.get("details"))

    try:
        client.table("user_team_players").insert({
            "user_id": user_id,
            "player_id": player_id,
            "role": role,
        }).execute()

        entry_with_details = get_roster_entry(client, user_id, player_id)

        return jsonify({
            "message": "Player added to roster successfully",
            "roster_entry": serialize_player_with_roster_info(entry_with_details),
            "roster_summary": get_roster_summary(client, user_id),
        }), 201

    except Exception as exc:
        err_str = str(exc).lower()
        if "23505" in err_str or "unique" in err_str or "duplicate" in err_str:
            return conflict(ErrorCodes.PLAYER_ALREADY_ON_ROSTER, "Player is already on this roster")
        return internal_server_error(ErrorCodes.DATABASE_ERROR, "Failed to add player to roster")


@bp.delete("/users/<int:user_id>/roster/<int:player_id>")
def remove_player(user_id, player_id):
    client = get_supabase_client()

    _, error = validate_user_exists(client, user_id)
    if error:
        return not_found(error["code"], error["error"])

    entry = get_roster_entry(client, user_id, player_id)
    if not entry:
        return not_found(
            ErrorCodes.PLAYER_NOT_ON_ROSTER,
            f"Player with ID {player_id} is not on this roster",
        )

    player = entry.get("players") or {}
    player_info = {
        "player_id": player.get("id"),
        "player_name": player.get("name"),
        "was_starter": entry.get("role") == "starter",
    }

    try:
        client.table("user_team_players").delete().eq("user_id", user_id).eq("player_id", player_id).execute()

        return jsonify({
            "message": "Player removed from roster successfully",
            "removed_player": player_info,
            "roster_summary": get_roster_summary(client, user_id),
        }), 200

    except Exception:
        return internal_server_error(ErrorCodes.DATABASE_ERROR, "Failed to remove player from roster")


@bp.patch("/users/<int:user_id>/roster/<int:player_id>")
def update_player_role(user_id, player_id):
    if not request.is_json:
        return bad_request(ErrorCodes.INVALID_REQUEST, "Content-Type must be application/json")

    data = request.get_json()
    new_role = data.get("role")

    if not new_role:
        return bad_request(ErrorCodes.MISSING_REQUIRED_FIELD, "role is required")

    is_valid, error = validate_role(new_role)
    if not is_valid:
        return bad_request(error["code"], error["error"])

    client = get_supabase_client()

    _, error = validate_user_exists(client, user_id)
    if error:
        return not_found(error["code"], error["error"])

    entry = get_roster_entry(client, user_id, player_id)
    if not entry:
        return not_found(
            ErrorCodes.PLAYER_NOT_ON_ROSTER,
            f"Player with ID {player_id} is not on this roster",
        )

    previous_role = entry.get("role")

    if new_role == "starter" and previous_role != "starter":
        is_valid, error = validate_starter_count(client, user_id, 1)
        if not is_valid:
            return conflict(error["code"], error["error"], error.get("details"))

    try:
        client.table("user_team_players").update({"role": new_role}).eq("user_id", user_id).eq("player_id", player_id).execute()

        entry_with_details = get_roster_entry(client, user_id, player_id)

        return jsonify({
            "message": "Player role updated successfully",
            "roster_entry": {
                **serialize_player_with_roster_info(entry_with_details),
                "previous_role": previous_role,
                "new_role": new_role,
            },
            "roster_summary": get_roster_summary(client, user_id),
        }), 200

    except Exception:
        return internal_server_error(ErrorCodes.DATABASE_ERROR, "Failed to update player role")


@bp.post("/users/<int:user_id>/roster/swap")
def swap_player_roles(user_id):
    if not request.is_json:
        return bad_request(ErrorCodes.INVALID_REQUEST, "Content-Type must be application/json")

    data = request.get_json()
    player_1_id = data.get("player_1_id")
    player_2_id = data.get("player_2_id")

    if not player_1_id or not player_2_id:
        return bad_request(ErrorCodes.MISSING_REQUIRED_FIELD, "Both player_1_id and player_2_id are required")

    if player_1_id == player_2_id:
        return bad_request(ErrorCodes.INVALID_REQUEST, "Cannot swap a player with itself")

    client = get_supabase_client()

    _, error = validate_user_exists(client, user_id)
    if error:
        return not_found(error["code"], error["error"])

    entry1 = get_roster_entry(client, user_id, player_1_id)
    entry2 = get_roster_entry(client, user_id, player_2_id)

    if not entry1 or not entry2:
        missing = []
        if not entry1:
            missing.append(str(player_1_id))
        if not entry2:
            missing.append(str(player_2_id))
        return not_found(
            ErrorCodes.PLAYER_NOT_ON_ROSTER,
            f"Player(s) with ID(s) {', '.join(missing)} not on this roster",
        )

    old_role_1 = entry1.get("role")
    old_role_2 = entry2.get("role")

    try:
        client.table("user_team_players").update({"role": old_role_2}).eq("user_id", user_id).eq("player_id", player_1_id).execute()
        client.table("user_team_players").update({"role": old_role_1}).eq("user_id", user_id).eq("player_id", player_2_id).execute()

        p1 = entry1.get("players") or {}
        p2 = entry2.get("players") or {}

        return jsonify({
            "message": "Player roles swapped successfully",
            "swapped_players": [
                {
                    "player_id": p1.get("id"),
                    "player_name": p1.get("name"),
                    "old_role": old_role_1,
                    "new_role": old_role_2,
                },
                {
                    "player_id": p2.get("id"),
                    "player_name": p2.get("name"),
                    "old_role": old_role_2,
                    "new_role": old_role_1,
                },
            ],
        }), 200

    except Exception:
        return internal_server_error(ErrorCodes.DATABASE_ERROR, "Failed to swap player roles")


@bp.delete("/users/<int:user_id>/roster")
def clear_roster(user_id):
    confirm = request.args.get("confirm")
    if confirm != "true":
        return bad_request(
            ErrorCodes.CONFIRMATION_REQUIRED,
            "Must include confirm=true query parameter to clear roster",
        )

    client = get_supabase_client()

    _, error = validate_user_exists(client, user_id)
    if error:
        return not_found(error["code"], error["error"])

    roster_entries = get_roster_with_details(client, user_id)

    if not roster_entries:
        return jsonify({"message": "Roster is already empty", "removed_count": 0}), 200

    former_roster = [
        {
            "player_id": (entry.get("players") or {}).get("id"),
            "player_name": (entry.get("players") or {}).get("name"),
            "role": entry.get("role"),
        }
        for entry in roster_entries
    ]

    try:
        client.table("user_team_players").delete().eq("user_id", user_id).execute()

        return jsonify({
            "message": "Roster cleared successfully",
            "removed_count": len(former_roster),
            "former_roster": former_roster,
        }), 200

    except Exception:
        return internal_server_error(ErrorCodes.DATABASE_ERROR, "Failed to clear roster")


@bp.post("/users/<int:user_id>/roster/bulk")
def bulk_add_players(user_id):
    if not request.is_json:
        return bad_request(ErrorCodes.INVALID_REQUEST, "Content-Type must be application/json")

    data = request.get_json()
    players_data = data.get("players")

    if not players_data or not isinstance(players_data, list):
        return bad_request(ErrorCodes.MISSING_REQUIRED_FIELD, "players array is required")

    if len(players_data) == 0:
        return bad_request(ErrorCodes.INVALID_REQUEST, "players array cannot be empty")

    client = get_supabase_client()

    _, error = validate_user_exists(client, user_id)
    if error:
        return not_found(error["code"], error["error"])

    total_to_add = len(players_data)
    is_valid, error = validate_roster_size(client, user_id, total_to_add)
    if not is_valid:
        return conflict(error["code"], error["error"], error.get("details"))

    starters_to_add = sum(1 for p in players_data if p.get("role") == "starter")
    if starters_to_add > 0:
        is_valid, error = validate_starter_count(client, user_id, starters_to_add)
        if not is_valid:
            return conflict(error["code"], error["error"], error.get("details"))

    results = []
    successful = 0
    failed = 0

    for player_data in players_data:
        player_id = player_data.get("player_id")
        role = player_data.get("role", DEFAULT_ROLE)

        if not player_id:
            results.append({"player_id": None, "status": "failed", "error": "player_id is required"})
            failed += 1
            continue

        is_valid, role_error = validate_role(role)
        if not is_valid:
            results.append({"player_id": player_id, "status": "failed", "error": role_error["error"]})
            failed += 1
            continue

        _, player_error = validate_player_exists(client, player_id)
        if player_error:
            results.append({"player_id": player_id, "status": "failed", "error": player_error["error"]})
            failed += 1
            continue

        if is_player_on_roster(client, user_id, player_id):
            results.append({"player_id": player_id, "status": "failed", "error": "Player already on roster"})
            failed += 1
            continue

        try:
            insert_result = client.table("user_team_players").insert({
                "user_id": user_id,
                "player_id": player_id,
                "role": role,
            }).execute()
            entry_id = insert_result.data[0]["id"] if insert_result.data else None
            results.append({"player_id": player_id, "status": "success", "roster_entry_id": entry_id})
            successful += 1
        except Exception as exc:
            err_str = str(exc).lower()
            if "23505" in err_str or "unique" in err_str or "duplicate" in err_str:
                results.append({"player_id": player_id, "status": "failed", "error": "Player already on roster"})
            else:
                results.append({"player_id": player_id, "status": "failed", "error": "Database error"})
            failed += 1

    status_code = 201 if failed == 0 else 207

    return jsonify({
        "message": "Bulk add completed",
        "successful": successful,
        "failed": failed,
        "results": results,
        "roster_summary": get_roster_summary(client, user_id),
    }), status_code
