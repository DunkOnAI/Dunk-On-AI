import os
import random
import joblib
import pandas as pd
from flask import Blueprint, jsonify, request

bp = Blueprint("matchup", __name__, url_prefix="/api/matchup")

# Paths relative to repo root (where Flask is launched from)
_TRAINING_DIR = os.path.join(os.path.dirname(__file__), "..", "AI-Prod", "training")
_DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "AI-Prod", "data_colection", "data")

MODEL_FILES = {
    "Guard":   "model_guard.pkl",
    "Forward": "model_forward.pkl",
    "Center":  "model_center.pkl",
}

LINEUP = {
    "Guard":   2,
    "Forward": 2,
    "Center":  1,
}

FEATURE_COLS = [
    "fantasy_last_game",
    "seconds_last_game",
    "avg_seconds_last5",
    "avg_seconds_last10",
    "std_seconds_last5",
    "avg_points_last5",
    "avg_rebounds_last5",
    "avg_assists_last5",
    "avg_blocks_last5",
    "avg_steals_last5",
    "avg_fantasy_last3",
    "avg_fantasy_last5",
    "avg_fantasy_last10",
    "std_fantasy_last5",
    "max_fantasy_last5",
    "trend_fantasy",
    "season_avg_fantasy",
    "season_avg_seconds",
    "days_since_last_game",
    "is_back_to_back",
    "games_last_7_days",
    "is_home_game",
]


@bp.get("/ai-team")
def get_ai_team():
    master_path = os.path.join(_DATA_DIR, "processed", "prediction_data.csv")
    players_path = os.path.join(_DATA_DIR, "raw", "players.csv")

    if not os.path.exists(master_path):
        return jsonify({"error": "prediction_data.csv not found. Run build_prediction_data.py first."}), 503
    if not os.path.exists(players_path):
        return jsonify({"error": "players.csv not found. Run get_players.py first."}), 503

    master_df = pd.read_csv(master_path)
    master_df["date"] = pd.to_datetime(master_df["date"])

    latest_df = (
        master_df
        .sort_values("date")
        .groupby("player_id", as_index=False)
        .last()
    )

    players_df = pd.read_csv(players_path)[["PLAYER_ID", "PLAYER_NAME"]]
    players_df = players_df.rename(columns={"PLAYER_ID": "player_id", "PLAYER_NAME": "player_name"})

    df = latest_df.merge(players_df, on="player_id", how="left")
    df = df[~(df["position"].isin(["UNKNOWN", None]) | df["position"].isna())].copy()

    team = []

    for position, slots in LINEUP.items():
        model_path = os.path.join(_TRAINING_DIR, MODEL_FILES[position])
        if not os.path.exists(model_path):
            return jsonify({"error": f"Model file not found: {MODEL_FILES[position]}"}), 503

        model = joblib.load(model_path)
        pos_df = df[df["position"] == position].copy()
        pos_df = pos_df.dropna(subset=FEATURE_COLS)

        if pos_df.empty:
            continue

        pos_df["predicted_fantasy_pts"] = model.predict(pos_df[FEATURE_COLS])

        top = (
            pos_df
            .sort_values("predicted_fantasy_pts", ascending=False)
            .head(slots)
        )
        team.append(top)

    if not team:
        return jsonify({"error": "No predictions could be generated."}), 500

    team_df = pd.concat(team, ignore_index=True)

    _POS_SHORT = {"Guard": "G", "Forward": "F", "Center": "C"}

    result = []
    for _, row in team_df.iterrows():
        raw_pos = str(row["position"])
        result.append({
            "id": int(row["player_id"]),
            "name": str(row.get("player_name", "Unknown")),
            "position": _POS_SHORT.get(raw_pos, raw_pos),
            "predicted_pts": round(float(row["predicted_fantasy_pts"]), 1),
            "pts": round(float(row.get("avg_points_last5", 0) or 0), 1),
            "reb": round(float(row.get("avg_rebounds_last5", 0) or 0), 1),
            "ast": round(float(row.get("avg_assists_last5", 0) or 0), 1),
        })

    return jsonify({"team": result})


def _load_prediction_df():
    master_path = os.path.join(_DATA_DIR, "processed", "prediction_data.csv")
    players_path = os.path.join(_DATA_DIR, "raw", "players.csv")
    if not os.path.exists(master_path) or not os.path.exists(players_path):
        return None, None
    master_df = pd.read_csv(master_path)
    master_df["date"] = pd.to_datetime(master_df["date"])
    latest_df = master_df.sort_values("date").groupby("player_id", as_index=False).last()
    players_df = pd.read_csv(players_path)[["PLAYER_ID", "PLAYER_NAME"]]
    players_df = players_df.rename(columns={"PLAYER_ID": "player_id", "PLAYER_NAME": "player_name"})
    df = latest_df.merge(players_df, on="player_id", how="left")
    df = df[~(df["position"].isin(["UNKNOWN", None]) | df["position"].isna())].copy()
    df["_name_lower"] = df["player_name"].str.lower().str.strip()
    return df, os.path.join(_TRAINING_DIR)


def _predict_player(row, training_dir):
    position = str(row["position"])
    if position not in MODEL_FILES:
        return None
    model_path = os.path.join(training_dir, MODEL_FILES[position])
    if not os.path.exists(model_path):
        return None
    feat = row[FEATURE_COLS]
    if feat.isna().any():
        return None
    model = joblib.load(model_path)
    return float(model.predict([feat])[0])


def _fallback_score(p):
    return float(p.get("pts", 0)) * 3.3 + float(p.get("ast", 0)) * 1.6 + float(p.get("reb", 0)) * 0.8


@bp.post("/simulate")
def simulate():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    data = request.get_json(silent=True) or {}
    user_roster = data.get("roster", [])

    df, training_dir = _load_prediction_df()
    if df is None:
        return jsonify({"error": "prediction_data.csv not found. Run build_prediction_data.py first."}), 503

    _POS_SHORT = {"Guard": "G", "Forward": "F", "Center": "C"}

    # --- AI team: sample from top 10 per position ---
    ai_players = []
    for position, slots in LINEUP.items():
        model_path = os.path.join(training_dir, MODEL_FILES[position])
        if not os.path.exists(model_path):
            return jsonify({"error": f"Model not found: {MODEL_FILES[position]}"}), 503
        model = joblib.load(model_path)
        pos_df = df[df["position"] == position].dropna(subset=FEATURE_COLS).copy()
        if pos_df.empty:
            continue
        pos_df["predicted_fantasy_pts"] = model.predict(pos_df[FEATURE_COLS])
        top10 = pos_df.sort_values("predicted_fantasy_pts", ascending=False).head(10)
        selected = top10.sample(n=min(slots, len(top10)))
        for _, row in selected.iterrows():
            raw_pos = str(row["position"])
            ai_players.append({
                "name": str(row.get("player_name", "Unknown")),
                "position": _POS_SHORT.get(raw_pos, raw_pos),
                "predicted_pts": round(float(row["predicted_fantasy_pts"]), 1),
                "pts": round(float(row.get("avg_points_last5", 0) or 0), 1),
                "reb": round(float(row.get("avg_rebounds_last5", 0) or 0), 1),
                "ast": round(float(row.get("avg_assists_last5", 0) or 0), 1),
            })

    # --- User team: match by name, run through model ---
    your_players = []
    for p in user_roster:
        name_lower = str(p.get("name", "")).lower().strip()
        match = df[df["_name_lower"] == name_lower]
        if not match.empty:
            row = match.iloc[0]
            predicted = _predict_player(row, training_dir)
            if predicted is None:
                predicted = _fallback_score(p)
            position = _POS_SHORT.get(str(row["position"]), str(row["position"]))
        else:
            predicted = _fallback_score(p)
            position = p.get("position", "—")
        your_players.append({
            "name": p.get("name", "Unknown"),
            "position": position,
            "predicted_pts": round(predicted, 1),
            "pts": round(float(p.get("pts", 0)), 1),
            "reb": round(float(p.get("reb", 0)), 1),
            "ast": round(float(p.get("ast", 0)), 1),
        })

    your_base = sum(p["predicted_pts"] for p in your_players)
    ai_base = sum(p["predicted_pts"] for p in ai_players)
    your_score = round(your_base + random.uniform(-8, 8))
    ai_score = round(ai_base + random.uniform(-8, 8))
    winner = "you" if your_score >= ai_score else "ai"

    return jsonify({
        "yourScore": your_score,
        "aiScore": ai_score,
        "winner": winner,
        "yourPlayers": your_players,
        "aiPlayers": ai_players,
    }), 200