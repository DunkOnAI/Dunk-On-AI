# NBA Data Collection Pipeline

## Overview

This Python pipeline collects **NBA player and game statistics** for a defined period (currently hardcoded to the **2025 regular season**).  
It consists of three scripts:

1. **`fetch_data.py`** – Main entry point; orchestrates the full data fetching process.  
2. **`get_players.py`** – Fetches all NBA players who played during the period and saves them to `Data/players.csv`.  
3. **`get_player_stats.py`** – Reads `players.csv` and fetches each player’s game logs; saves stats to individual CSVs.  

The pipeline ensures **safe execution**, proper logging, and preserves exit codes for fatal errors.

---

## Output

1. **Players CSV**  
   - Path: `Data/players.csv`  
   - Format (columns):  
     ```
     PLAYER_ID,PLAYER_NAME,TEAM_NAME
     ```  
   - Player IDs are the official NBA API IDs.  
   - Commas are removed from names and teams.

2. **Player stats CSVs**  
   - Path: `Data/player_<PLAYER_ID>/player_stats.csv`  
   - Columns:
     ```
     game_id,week_of_year,seconds_played,points,rebounds,assists,steals,blocks,fantasy_points
     ```  
   - Each row represents one game.  
   - Minutes are converted to seconds.  
   - `fantasy_points` is defaulted to 0.

---

## Required Libraries

Install the following Python packages:

```bash
pip install nba_api
pip install requests
pip install numpy
pip install pandas
```

Libraries usage:

* `nba-api` – for fetching NBA data  
* `pandas` – for data processing  
* `requests` – for API calls  
* `numpy` – dependency for pandas  
* Standard libraries: `os`, `sys`, `time`, `datetime`, `traceback`

---

## How to Run

```bash
python fetch_data.py
```

---

### Behavior

- **Step 1:** Fetches players → prints `[INFO]` / `[WARN]` messages depending on warnings or errors 
- **Step 2:** Fetches player stats → prints `[INFO]` / `[WARN]` messages depending on warnings or errors  
- Fatal errors stop execution immediately using `sys.exit(error_code)`.
- Non-fatal issues are logged as `[WARN]` and counted, but do not interrupt the pipeline.

---

### Internal Return Structure

Both `get_players()` and `get_player_stats()` return a dictionary:

{
    "fatal_error": bool,
    "warnings": int,
    "error_code": int
}

- `fatal_error=True` indicates immediate script termination.
- `warnings` counts non-fatal issues.
- `error_code` specifies the exit code if a fatal error occurs.

---

## Error Codes

The pipeline uses specific exit codes to indicate fatal errors:

| Exit Code | Meaning |
|-----------|---------|
| `-1`      | Fatal error during **player fetching** in `get_players.py`. |
| `-2`      | Fatal error during **player stats fetching** in `get_player_stats.py`. |
| `-21`     | `players.csv` not found when running `get_player_stats.py`. Ensure `get_players()` has been run successfully. |

**Note:**  
- Player-level warnings (e.g., temporary API issues for a single player) do **not** trigger a fatal exit; they are reported as `[WARN]` but the script continues.

---

## Notes

- Currently hardcoded to the **2025 regular season**; dates and season can be updated in the scripts.  
- A 0.5s delay is used between API calls to avoid rate-limiting.  
- CSV files are overwritten if they already exist.
