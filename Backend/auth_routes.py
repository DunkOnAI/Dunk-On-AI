"""
Authentication API endpoints
"""

import re

from flask import Blueprint, current_app, jsonify, request

from Backend.constants import ErrorCodes
from Backend.supabaseclient import SupabaseConfigError, get_supabase_client
from Backend.utils.errors import bad_request, internal_server_error

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

AUTH_MANAGED_PASSWORD_HASH = "SUPABASE_AUTH_MANAGED"
MIN_PASSWORD_LENGTH = 8


def _is_debug_mode():
    """Return True when Flask debug mode is enabled."""
    return bool(current_app.debug)


def _exception_debug_details(exc):
    """
    Build a JSON-safe debug payload from an exception.
    """
    details = {
        "type": type(exc).__name__,
        "message": str(exc),
    }

    for attr in ("code", "status", "status_code", "name"):
        value = getattr(exc, attr, None)
        if value is not None:
            details[attr] = value

    if getattr(exc, "args", None):
        details["args"] = [str(arg) for arg in exc.args]

    return details


# This helper function abstracts away differences in how Supabase client responses may be structured (dict vs object).
def _extract_attr(value, key):
    """Support both object-style and dict-style Supabase responses."""
    if value is None:
        return None
    if isinstance(value, dict):
        return value.get(key)
    return getattr(value, key, None)


# This function generates a normalized username based on the preferred username or email.
def _normalize_username(raw_username, email):
    base = (raw_username or email.split("@")[0]).strip().lower()
    base = re.sub(r"[^a-z0-9_]+", "_", base).strip("_")
    return (base or "user")[:80]


# This function appends numeric suffixes to the base username until it finds a unique one.
def _unique_username(client, base_username):
    candidate = base_username
    suffix = 1
    while True:
        result = (
            client.table("users")
            .select("id")
            .eq("username", candidate)
            .limit(1)
            .execute()
        )
        if not result.data:
            break
        suffix_text = f"_{suffix}"
        candidate = f"{base_username[:80 - len(suffix_text)]}{suffix_text}"
        suffix += 1
    return candidate


# This function ensures that for every authenticated Supabase user, there is a corresponding local User record in our database.
def _ensure_local_user(client, auth_user_id, email, preferred_username=None):
    """
    Keep a local users table record mapped to the Supabase auth user.
    Uses the Supabase PostgREST API instead of SQLAlchemy.
    """
    # Look up by supabase_auth_id OR email
    result = (
        client.table("users")
        .select("*")
        .or_(f"supabase_auth_id.eq.{auth_user_id},email.eq.{email}")
        .limit(1)
        .execute()
    )

    if result.data:
        user = result.data[0]
        # Backfill supabase_auth_id if it was missing
        if not user.get("supabase_auth_id"):
            update_result = (
                client.table("users")
                .update({"supabase_auth_id": auth_user_id})
                .eq("id", user["id"])
                .execute()
            )
            if update_result.data:
                user = update_result.data[0]
        return user

    # Create a new local user record
    username = _unique_username(client, _normalize_username(preferred_username, email))
    insert_result = (
        client.table("users")
        .insert(
            {
                "username": username,
                "email": email,
                "password_hash": AUTH_MANAGED_PASSWORD_HASH,
                "supabase_auth_id": auth_user_id,
            }
        )
        .execute()
    )
    return insert_result.data[0]


@bp.post("/signup")
def signup():
    if not request.is_json:
        return bad_request(
            ErrorCodes.INVALID_REQUEST,
            "Content-Type must be application/json",
        )

    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""
    username = payload.get("username")

    if not email or not password:
        return bad_request(
            ErrorCodes.MISSING_REQUIRED_FIELD,
            "email and password are required",
        )

    if len(password) < MIN_PASSWORD_LENGTH:
        return bad_request(
            ErrorCodes.INVALID_REQUEST,
            f"password must be at least {MIN_PASSWORD_LENGTH} characters",
        )

    try:
        # Create Supabase client and attempt to sign up the user with Supabase Auth
        client = get_supabase_client()
        auth_response = client.auth.sign_up({"email": email, "password": password})

        auth_user = _extract_attr(auth_response, "user")
        if not auth_user:
            return bad_request(
                ErrorCodes.INVALID_REQUEST,
                "Signup failed. Check email/password or Supabase auth settings.",
            )

        # Extract the Supabase auth user ID and email, ensuring we have a valid user ID to work with
        auth_user_id = _extract_attr(auth_user, "id")
        auth_email = _extract_attr(auth_user, "email") or email
        if not auth_user_id:
            return internal_server_error(
                ErrorCodes.DATABASE_ERROR,
                "Supabase signup returned no user ID.",
            )

        # Ensure there is a corresponding local User record for this Supabase auth user, creating one if necessary
        local_user = _ensure_local_user(client, str(auth_user_id), auth_email, username)
        # Extract the session information from the Supabase auth response to return access and refresh tokens
        session = _extract_attr(auth_response, "session")

        return jsonify(
            {
                "message": "Signup successful",
                "user": {
                    "id": local_user["id"],
                    "email": local_user["email"],
                    "username": local_user["username"],
                    "supabase_auth_id": local_user["supabase_auth_id"],
                },
                "auth": {
                    "access_token": _extract_attr(session, "access_token"),
                    "refresh_token": _extract_attr(session, "refresh_token"),
                    "expires_at": _extract_attr(session, "expires_at"),
                },
            }
        ), 201

    except SupabaseConfigError as exc:
        return internal_server_error(ErrorCodes.DATABASE_ERROR, str(exc))
    except Exception as exc:
        current_app.logger.exception("Signup request failed for email=%s", email)
        message = str(exc) or "Signup request failed."

        if "User already registered" in message:
            return bad_request(
                ErrorCodes.INVALID_REQUEST,
                "User already registered. Please log in instead.",
            )

        return bad_request(
            ErrorCodes.INVALID_REQUEST,
            message,
        )


@bp.post("/login")
def login():
    if not request.is_json:
        return bad_request(
            ErrorCodes.INVALID_REQUEST,
            "Content-Type must be application/json",
        )

    payload = request.get_json(silent=True) or {}
    email = (payload.get("email") or "").strip().lower()
    password = payload.get("password") or ""

    if not email or not password:
        return bad_request(
            ErrorCodes.MISSING_REQUIRED_FIELD,
            "email and password are required",
        )

    try:
        client = get_supabase_client()
        auth_response = client.auth.sign_in_with_password(
            {"email": email, "password": password}
        )

        auth_user = _extract_attr(auth_response, "user")
        if not auth_user:
            return jsonify(
                {
                    "error": {
                        "code": ErrorCodes.INVALID_REQUEST,
                        "message": "Invalid email or password.",
                    }
                }
            ), 401

        auth_user_id = _extract_attr(auth_user, "id")
        auth_email = _extract_attr(auth_user, "email") or email
        if not auth_user_id:
            return internal_server_error(
                ErrorCodes.DATABASE_ERROR,
                "Supabase login returned no user ID.",
            )

        local_user = _ensure_local_user(client, str(auth_user_id), auth_email)
        session = _extract_attr(auth_response, "session")

        return jsonify(
            {
                "message": "Login successful",
                "user": {
                    "id": local_user["id"],
                    "email": local_user["email"],
                    "username": local_user["username"],
                    "supabase_auth_id": local_user["supabase_auth_id"],
                },
                "auth": {
                    "access_token": _extract_attr(session, "access_token"),
                    "refresh_token": _extract_attr(session, "refresh_token"),
                    "expires_at": _extract_attr(session, "expires_at"),
                },
            }
        ), 200

    except SupabaseConfigError as exc:
        return internal_server_error(ErrorCodes.DATABASE_ERROR, str(exc))
    except Exception as exc:
        current_app.logger.exception("Login request failed for email=%s", email)

        raw_message = str(exc) or "Login request failed."
        normalized = raw_message.lower()

        if "email not confirmed" in normalized:
            user_message = "Email not confirmed. Check your inbox and confirm your account."
            status_code = 401
        elif "invalid login credentials" in normalized:
            user_message = "Invalid email or password."
            status_code = 401
        elif "rate limit" in normalized:
            user_message = "Too many auth attempts. Please wait and try again."
            status_code = 429
        else:
            user_message = "Login request failed."
            status_code = 401

        error_payload = {
            "code": ErrorCodes.INVALID_REQUEST,
            "message": user_message,
        }

        if _is_debug_mode():
            error_payload["debug"] = _exception_debug_details(exc)

        return jsonify({"error": error_payload}), status_code
