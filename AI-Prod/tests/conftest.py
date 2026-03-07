"""
Shared pytest fixtures for AI-Prod tests.
All fixtures that write to the filesystem use tmp_path so tests are fully isolated.
"""

import os
import pytest
import pandas as pd


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_players_csv(directory, players):
    """Write a players.csv into `directory/Data/`."""
    data_dir = os.path.join(directory, "Data")
    os.makedirs(data_dir, exist_ok=True)
    df = pd.DataFrame(players, columns=["PLAYER_ID", "PLAYER_NAME", "TEAM_NAME"])
    df.to_csv(os.path.join(data_dir, "players.csv"), index=False)


def make_player_stats_csv(directory, player_id, rows):
    """Write a player_stats.csv for a given player into `directory/Data/player_<id>/`."""
    player_dir = os.path.join(directory, "Data", f"player_{player_id}")
    os.makedirs(player_dir, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(player_dir, "player_stats.csv"), index=False)


def make_weekly_scores_csv(directory, rows):
    """Write a weekly_scores.csv into `directory/Data/`."""
    data_dir = os.path.join(directory, "Data")
    os.makedirs(data_dir, exist_ok=True)
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(data_dir, "weekly_scores.csv"), index=False)
