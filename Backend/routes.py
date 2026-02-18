from flask import Blueprint, jsonify

from Backend.supabaseclient import SupabaseConfigError, get_supabase_client

bp = Blueprint("api", __name__, url_prefix="/api")


@bp.get("/health")
def health_check():
    return jsonify({"status": "ok"})


@bp.get("/supabase/health")
def supabase_health_check():
    """
    Validate Supabase client configuration and connectivity.
    """
    try:
        client = get_supabase_client()
        response = client.table("users").select("id").limit(1).execute()

        return jsonify(
            {
                "status": "ok",
                "supabase_connected": True,
                "sample_rows": len(response.data or []),
            }
        ), 200
    except SupabaseConfigError as exc:
        return jsonify(
            {
                "status": "error",
                "supabase_connected": False,
                "error": str(exc),
            }
        ), 500
    except Exception as exc:
        return jsonify(
            {
                "status": "error",
                "supabase_connected": False,
                "error": str(exc),
            }
        ), 500
