"""
Tests for compute_weekly_scores.py

Covers:
- Missing players.csv → fatal error -11
- No player stat files exist → fatal error -12
- Single player, single week → correct aggregation
- Single player, multiple weeks → correct grouping
- Multiple players → all appear in output sorted correctly
- Player with missing stat file is skipped (warning)
- Output CSV has expected columns
"""

import os
import sys
import pytest
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from compute_weekly_scores import compute_weekly_scores
from tests.conftest import make_players_csv, make_player_stats_csv


STAT_COLS = ["game_id", "week_of_year", "seconds_played",
             "points", "rebounds", "assists", "steals", "blocks", "fantasy_points"]


def _stat_row(game_id, week, pts, reb, ast, stl, blk):
    fp = pts * 1.0 + reb * 1.2 + ast * 1.5 + stl * 3.0 + blk * 3.0
    return {
        "game_id": game_id,
        "week_of_year": week,
        "seconds_played": 1800,
        "points": pts,
        "rebounds": reb,
        "assists": ast,
        "steals": stl,
        "blocks": blk,
        "fantasy_points": fp,
    }


class TestComputeWeeklyScoresMissingFiles:
    def test_missing_players_csv(self, tmp_path):
        os.chdir(tmp_path)
        result = compute_weekly_scores()
        assert result["fatal_error"] is True
        assert result["error_code"] == -11

    def test_no_stat_files(self, tmp_path):
        make_players_csv(str(tmp_path), [(1, "Player One", "Team A")])
        os.chdir(tmp_path)
        result = compute_weekly_scores()
        assert result["fatal_error"] is True
        assert result["error_code"] == -12


class TestComputeWeeklyScoresAggregation:
    def test_single_player_single_week(self, tmp_path):
        make_players_csv(str(tmp_path), [(1, "LeBron James", "Lakers")])
        make_player_stats_csv(str(tmp_path), 1, [
            _stat_row("G1", 5, 30, 8, 7, 2, 1),
            _stat_row("G2", 5, 25, 6, 5, 3, 2),
        ])
        os.chdir(tmp_path)
        result = compute_weekly_scores()

        assert not result["fatal_error"]
        df = pd.read_csv(tmp_path / "Data" / "weekly_scores.csv")
        assert len(df) == 1
        assert df.iloc[0]["week_of_year"] == 5
        assert df.iloc[0]["games_played"] == 2
        assert df.iloc[0]["total_points"] == 55
        assert abs(df.iloc[0]["total_fantasy_points"] - (
            _stat_row("", 5, 30, 8, 7, 2, 1)["fantasy_points"] +
            _stat_row("", 5, 25, 6, 5, 3, 2)["fantasy_points"]
        )) < 0.001

    def test_single_player_multiple_weeks(self, tmp_path):
        make_players_csv(str(tmp_path), [(2, "Steph Curry", "Warriors")])
        make_player_stats_csv(str(tmp_path), 2, [
            _stat_row("G1", 1, 40, 5, 6, 1, 0),
            _stat_row("G2", 2, 28, 4, 10, 2, 0),
            _stat_row("G3", 2, 32, 3, 8, 1, 0),
        ])
        os.chdir(tmp_path)
        result = compute_weekly_scores()

        assert not result["fatal_error"]
        df = pd.read_csv(tmp_path / "Data" / "weekly_scores.csv")
        assert len(df) == 2

        week1 = df[df["week_of_year"] == 1].iloc[0]
        assert week1["games_played"] == 1
        assert week1["total_points"] == 40

        week2 = df[df["week_of_year"] == 2].iloc[0]
        assert week2["games_played"] == 2
        assert week2["total_points"] == 60

    def test_multiple_players_appear_in_output(self, tmp_path):
        make_players_csv(str(tmp_path), [
            (10, "Player A", "Team X"),
            (20, "Player B", "Team Y"),
        ])
        make_player_stats_csv(str(tmp_path), 10, [_stat_row("G1", 3, 20, 5, 4, 1, 0)])
        make_player_stats_csv(str(tmp_path), 20, [_stat_row("G2", 3, 10, 8, 2, 3, 1)])
        os.chdir(tmp_path)
        result = compute_weekly_scores()

        assert not result["fatal_error"]
        df = pd.read_csv(tmp_path / "Data" / "weekly_scores.csv")
        assert len(df) == 2
        assert set(df["player_id"].tolist()) == {10, 20}

    def test_sorted_by_fantasy_points_descending_within_week(self, tmp_path):
        make_players_csv(str(tmp_path), [
            (1, "Low Scorer", "Team"),
            (2, "High Scorer", "Team"),
        ])
        make_player_stats_csv(str(tmp_path), 1, [_stat_row("G1", 4, 5, 0, 0, 0, 0)])
        make_player_stats_csv(str(tmp_path), 2, [_stat_row("G2", 4, 50, 10, 8, 3, 2)])
        os.chdir(tmp_path)
        compute_weekly_scores()

        df = pd.read_csv(tmp_path / "Data" / "weekly_scores.csv")
        week4 = df[df["week_of_year"] == 4].reset_index(drop=True)
        assert week4.iloc[0]["player_id"] == 2  # High Scorer first

    def test_player_without_stat_file_is_skipped(self, tmp_path):
        make_players_csv(str(tmp_path), [
            (1, "Has Stats", "Team"),
            (2, "No Stats", "Team"),
        ])
        make_player_stats_csv(str(tmp_path), 1, [_stat_row("G1", 6, 18, 4, 3, 1, 0)])
        # Player 2 has no CSV — should be silently skipped
        os.chdir(tmp_path)
        result = compute_weekly_scores()

        assert not result["fatal_error"]
        df = pd.read_csv(tmp_path / "Data" / "weekly_scores.csv")
        assert list(df["player_id"]) == [1]

    def test_output_csv_has_expected_columns(self, tmp_path):
        make_players_csv(str(tmp_path), [(5, "Test", "Team")])
        make_player_stats_csv(str(tmp_path), 5, [_stat_row("G1", 7, 10, 4, 2, 1, 1)])
        os.chdir(tmp_path)
        compute_weekly_scores()

        df = pd.read_csv(tmp_path / "Data" / "weekly_scores.csv")
        expected = {"player_id", "player_name", "week_of_year", "games_played",
                    "total_points", "total_rebounds", "total_assists",
                    "total_steals", "total_blocks", "total_fantasy_points"}
        assert expected.issubset(set(df.columns))
