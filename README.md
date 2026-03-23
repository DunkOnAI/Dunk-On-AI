# Dunk On AI — Fantasy Basketball App

A fantasy basketball web app where users build a team and compete against an AI opponent powered by a Random Forest model trained on real NBA data.

## Tech Stack

| Layer    | Technology                              |
| -------- | --------------------------------------- |
| Frontend | React 18 + Vite + Framer Motion         |
| Backend  | Python + Flask                          |
| Auth     | Supabase Auth (email/password)          |
| Database | Supabase (PostgreSQL via PostgREST API) |
| AI Model | scikit-learn Random Forest Regressor    |

All database access goes through the **Supabase PostgREST HTTP API** — no raw database connection string is needed.

---

## Dev Setup

### 1. Environment Variables

Create a `.env` file in the repo root:

```env
SUPABASE_URL=https://<your-project-ref>.supabase.co
SUPABASE_SERVICE_ROLE_KEY=<your-service-role-key>
```

Keep `.env` out of git — it's already in `.gitignore`.

### 2. Backend (Flask)

```bash
python -m venv venv
venv\Scripts\activate
pip install -r Backend\requirements.txt
flask --app Fantasy_Basketball run --debug
```

Flask starts on `http://127.0.0.1:5000`.

Quick backend smoke test:

```bash
bash Backend/smoke_test_backend.sh
```

### 3. AI Data Pipeline (required before first run)

Run these in order from `AI-Prod/data_colection/`:

```bash
python get_players.py
python get_player_stats.py
python build_training_ready_data.py
```

This generates `players.csv` and `master_training.csv` which the AI team endpoint reads at runtime. Without these files the matchup page falls back to mock player data.

### 4. Frontend (React + Vite)

```bash
cd Frontend
npm install
npm run dev
```

Vite starts on `http://localhost:5173` and proxies all `/api/*` requests to Flask automatically.

---

## How It Works

1. User builds a roster of **5 players** (2 Guards, 2 Forwards, 1 Center) from the Stats page.
2. On the Matchup page, the Flask backend runs three Random Forest models (one per position group) against recent NBA stats to pick the AI's optimal 5-player lineup.
3. Both teams are scored using a weighted formula: `PTS × 3.3 + AST × 1.6 + REB × 0.8` with a small random variance.
4. The result is saved to Supabase and shown on the Home page with full player snapshots for both teams.

---

## API Reference

Base URL: `http://127.0.0.1:5000/api`

### Health

| Method | Endpoint           | Description                               |
| ------ | ------------------ | ----------------------------------------- |
| GET    | `/health`          | Returns `{ "status": "ok" }`              |
| GET    | `/supabase/health` | Verifies Supabase connection and env vars |

### Auth

| Method | Endpoint       | Description             |
| ------ | -------------- | ----------------------- |
| POST   | `/auth/signup` | Register a new user     |
| POST   | `/auth/login`  | Log in an existing user |

**Signup body:**

```json
{
  "email": "user@example.com",
  "password": "mypassword",
  "username": "optional"
}
```

**Login body:**

```json
{ "email": "user@example.com", "password": "mypassword" }
```

**Both return:**

```json
{
  "user": {
    "id": 1,
    "email": "...",
    "username": "...",
    "supabase_auth_id": "..."
  },
  "auth": { "access_token": "...", "refresh_token": "...", "expires_at": 0 }
}
```

### Roster

All roster endpoints are scoped to a user via `<user_id>` (the `id` from the users table).

| Method | Endpoint                               | Description                                  |
| ------ | -------------------------------------- | -------------------------------------------- |
| GET    | `/users/<user_id>/roster`              | Get roster (optional `?role=starter\|bench`) |
| POST   | `/users/<user_id>/roster`              | Add a player                                 |
| DELETE | `/users/<user_id>/roster/<player_id>`  | Remove a player                              |
| PATCH  | `/users/<user_id>/roster/<player_id>`  | Update a player's role                       |
| POST   | `/users/<user_id>/roster/swap`         | Swap roles between two players               |
| DELETE | `/users/<user_id>/roster?confirm=true` | Clear entire roster                          |
| POST   | `/users/<user_id>/roster/bulk`         | Add multiple players at once                 |

**Add player body:**

```json
{ "player_id": 123, "role": "starter" }
```

**Roster constraints:** max 5 players — 2 Guards (G), 2 Forwards (F), 1 Center (C).

### Matchup

| Method | Endpoint             | Description                                              |
| ------ | -------------------- | -------------------------------------------------------- |
| GET    | `/matchup/ai-team`   | Returns AI's predicted 5-player lineup using ML models   |

**Response:**

```json
{
  "team": [
    { "id": 1, "name": "Player Name", "position": "G", "predicted_pts": 48.2, "pts": 27.1, "reb": 4.0, "ast": 7.5 }
  ]
}
```

### Match History

| Method | Endpoint                              | Description                              |
| ------ | ------------------------------------- | ---------------------------------------- |
| GET    | `/users/<user_id>/match-history`      | Get last 20 games for a user             |
| POST   | `/users/<user_id>/match-history`      | Save a completed match result            |

**Save body:**

```json
{
  "yourScore": 142,
  "aiScore": 135,
  "winner": "you",
  "yourPlayers": [{ "name": "...", "position": "G", "pts": 27.1, "reb": 4.0, "ast": 7.5 }],
  "aiPlayers":   [{ "name": "...", "position": "G", "pts": 28.2, "reb": 4.0, "ast": 8.0 }]
}
```

---

## Project Structure

```
Basketball-Fantasy-Helper/
├── Backend/
│   ├── __init__.py              # Flask app factory, blueprint registration
│   ├── auth_routes.py           # POST /api/auth/signup, /api/auth/login
│   ├── roster_routes.py         # Roster CRUD endpoints
│   ├── matchup_routes.py        # GET /api/matchup/ai-team (ML prediction)
│   ├── match_history_routes.py  # GET/POST /api/users/<id>/match-history
│   ├── routes.py                # Health check endpoints
│   ├── models.py                # SQLAlchemy models (schema reference)
│   ├── supabaseclient.py        # Cached Supabase client
│   ├── constants.py             # Roster limits, error codes, valid roles
│   └── utils/
│       ├── validators.py        # Input validation via Supabase API
│       ├── serializers.py       # Convert Supabase dicts to API response format
│       └── errors.py            # Standardized error response helpers
├── AI-Prod/
│   ├── data_colection/
│   │   ├── get_players.py               # Fetches player list from NBA API
│   │   ├── get_player_stats.py          # Fetches per-game stats
│   │   ├── build_training_ready_data.py # Builds master_training.csv
│   │   └── data/
│   │       ├── raw/players.csv          # Generated by get_players.py
│   │       └── processed/master_training.csv  # Generated by build step
│   └── training/
│       ├── train_model.py       # Trains Random Forest models per position group
│       ├── build_team.py        # Standalone team builder (used by Flask endpoint)
│       ├── model_guard.pkl      # Trained model for Guards
│       ├── model_forward.pkl    # Trained model for Forwards
│       └── model_center.pkl     # Trained model for Centers
├── Frontend/
│   ├── src/
│   │   ├── App.jsx              # All React components and routing
│   │   └── index.css            # All styles
│   ├── vite.config.js           # Dev server + /api proxy to Flask
│   └── package.json
├── Fantasy_Basketball.py        # Flask entry point (flask --app Fantasy_Basketball run)
├── .env                         # Supabase credentials (never commit this)
└── README.md
```

---

## Frontend Roster Rules

- Roster is capped at **5 players**: 2 G, 2 F, 1 C.
- Selecting a player whose position slot is full (saved or pending) is blocked with an error message.
- Players with a full position slot appear dimmed in the player list.
- The detail page add button shows `[POS] Slots are full` and is disabled when the slot is filled.
- Match history is saved per-user in Supabase — each account has its own game history.

## Adding New Routes

1. Create a new file e.g. `Backend/new_routes.py` with a `Blueprint`
2. Register it in `Backend/__init__.py` inside `create_app`
3. Get the Supabase client at the top of each endpoint with `client = get_supabase_client()`
4. Use `client.table("your_table").select/insert/update/delete(...)` for all DB access