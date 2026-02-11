# Fantasy Basketball Predictor

### Right now - Database created

## Dev setup (Flask + React Vite)

Backend:

1. `python -m venv venv`
2. `venv\\Scripts\\activate`
3. `pip install -r Backend\\requirements.txt`
4. `flask --app Fantasy_Basketball.py run`

Frontend:

1. `cd Frontend`
2. `npm install`
3. `npm run dev`

The Vite dev server proxies `/api` requests to Flask on `http://127.0.0.1:5000`.

## Backend API routes

Base URL: `http://127.0.0.1:5000/api`

Health:
1. `GET /health` -> `{ "status": "ok" }`

Roster:
1. `GET /users/<user_id>/roster` -> List roster (optional `?role=starter|bench`)
2. `POST /users/<user_id>/roster` -> Add player  
   Body: `{ "player_id": 123, "role": "starter|bench" }`
3. `DELETE /users/<user_id>/roster/<player_id>` -> Remove player
4. `PATCH /users/<user_id>/roster/<player_id>` -> Update role  
   Body: `{ "role": "starter|bench" }`
5. `POST /users/<user_id>/roster/swap` -> Swap two players  
   Body: `{ "player_1_id": 1, "player_2_id": 2 }`
6. `DELETE /users/<user_id>/roster?confirm=true` -> Clear roster
7. `POST /users/<user_id>/roster/bulk` -> Bulk add players  
   Body: `{ "players": [{ "player_id": 1, "role": "starter" }, { "player_id": 2 }] }`

## Connecting all backend routes

Blueprints must be registered in `Backend/__init__.py` to be active. At minimum:
1. `Backend/routes.py` (health)
2. `Backend/roster_routes.py` (roster endpoints)

Example snippet (already the pattern we use):
```python
from Backend.routes import bp as api_bp
from Backend.roster_routes import bp as roster_bp

app.register_blueprint(api_bp)
app.register_blueprint(roster_bp)
```

When you add new route modules, define a `Blueprint` in that module and register it in `create_app`.
