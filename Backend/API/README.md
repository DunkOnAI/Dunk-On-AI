# NBA Database Synchronization Layer

## Overview

This module is responsible for **synchronizing NBA reference and statistical data into a Supabase database**.

It consists of two scripts:

1. `api_functions.py` – Handles raw data fetching from the NBA API.
2. `database_functions.py` – Syncs fetched data into the Supabase database with upsert logic.

The system ensures:

* Safe execution
* Structured logging (`[INFO]`, `[WARN]`, `[ERROR]`)
* Controlled rate limiting
* Incremental game stat synchronization
* Consistent return structure across all functions

---

## Architecture

### 1. `api_functions.py`

Responsible for fetching and structuring data from `nba_api`.

Includes:

* `get_teams()` – Fetches all NBA teams
* `get_players()` – Fetches all active NBA players
* `get_game_stats(start_date=None)` – Fetches player-level game stats from a given date onward (defaults to `2024-01-01`)

Each function:

* Handles internal parsing
* Counts non-fatal warnings
* Returns a standardized dictionary
* Never crashes silently

---

### 2. `database_functions.py`

Responsible for integrating API data with Supabase.

Includes:

* `sync_teams()` – Upserts teams into `teams` table
* `sync_players()` – Enriches player data and upserts into `players` table
* `sync_game_stats()` – Incrementally syncs game stats into `game_stats` table

Key features:

* Automatic detection of latest `game_date` in DB
* Incremental syncing (only new games are fetched)
* Filtering of invalid player IDs
* Batch upserts (1000 rows per batch)
* Full error-code propagation

---

## Database Tables Expected

The following Supabase tables must exist:

### `teams`

Columns:

```
id (primary key)
name
city
abbreviation
```

---

### `players`

Columns:

```
id (primary key)
name
team_id
position
height_weight
```

---

### `game_stats`

Columns:

```
player_id
game_id
game_date
team_id
points
rebounds
assists
steals
blocks
turnovers
minutes_played
```

---

## Required Libraries

Install the following Python packages:

```bash
pip install nba_api
pip install supabase
pip install pandas
```

Libraries usage:

* `nba_api` – NBA data access
* `supabase` – Database integration
* `pandas` – Date parsing and data handling
* Standard libraries: `sys`, `time`, `datetime`

---

## How to Use

You can import and call synchronization functions directly:

```python
from database_functions import sync_teams, sync_players, sync_game_stats

sync_teams()
sync_players()
sync_game_stats()
```

Or call them inside a higher-level orchestration script.

---

## Behavior

### Teams Sync

* Fetches all NBA teams
* Upserts into database
* Stops on fatal fetch or database error

---

### Players Sync

* Fetches active players
* Enriches each player via `CommonPlayerInfo`
* Applies 0.6s delay per player (rate limit safety)
* Upserts into database

---

### Game Stats Sync

1. Reads latest `game_date` from DB
2. Fetches only newer games
3. Filters out players not present in DB
4. Upserts in batches of 1000
5. Logs progress per batch

If database is empty, it defaults to baseline date `2024-01-01`.

---

## Internal Return Structure

All functions return:

```
{
    "fatal_error": bool,
    "warnings": int,
    "error_code": int
}
```

Where:

* `fatal_error=True` indicates immediate script termination.
* `warnings` counts non-fatal issues.
* `error_code` specifies the exit code if a fatal error occurs.

---

## Error Codes

### `sync_teams()`

| Code | Meaning               |
| ---- | --------------------- |
| 0    | Success               |
| -1   | Unexpected exception  |
| -21  | Failed to fetch teams |
| -22  | No teams returned     |
| -23  | Database upsert error |

---

### `sync_players()`

| Code | Meaning                      |
| ---- | ---------------------------- |
| 0    | Success                      |
| -1   | Unexpected exception         |
| -21  | Failed to fetch players      |
| -22  | No players returned          |
| -23  | No enriched players produced |
| -24  | Database upsert error        |

---

### `sync_game_stats()`

| Code | Meaning                             |
| ---- | ----------------------------------- |
| 0    | Success                             |
| -1   | Unexpected exception                |
| -31  | Failed to fetch latest game_date    |
| -32  | Failed to fetch game stats from API |
| -33  | Failed to fetch player IDs          |
| -34  | Player ID filtering error           |
| -35  | Database batch upsert error         |

---

## Rate Limiting Strategy

To avoid NBA API throttling:

* 0.5s delay for static fetches
* 0.6s delay for player detail calls
* 0.6s delay per season when fetching game logs

---

## Notes

* All database writes use **upsert**, so running sync multiple times is safe.
* Game stats syncing is **incremental**, preventing duplicate data pulls.
* Player enrichment converts NumPy types to native Python types before database insertion.
* Supabase credentials are currently hardcoded and should be moved to environment variables in production.

---
