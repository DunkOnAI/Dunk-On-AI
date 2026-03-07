"""
Tests for get_player_stats.py

Covers:
- convert_minutes_to_seconds: normal, empty, NaN, bad format
- Fantasy points formula: correctness, zero-stat game, all-zero
- get_player_stats(): missing players.csv, no games in range, CSV output shape
"""

import os
import sys
import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

# Make the parent directory importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from get_player_stats import convert_minutes_to_seconds, get_player_stats
from tests.conftest import make_players_csv


# ---------------------------------------------------------------------------
# convert_minutes_to_seconds
# ---------------------------------------------------------------------------

class TestConvertMinutesToSeconds:
    def test_normal(self):
        assert convert_minutes_to_seconds("30:00") == 1800

    def test_with_seconds(self):
        assert convert_minutes_to_seconds("12:34") == 754

    def test_zero_minutes(self):
        assert convert_minutes_to_seconds("0:00") == 0

    def test_empty_string(self):
        assert convert_minutes_to_seconds("") == 0

    def test_nan(self):
        assert convert_minutes_to_seconds(float("nan")) == 0

    def test_bad_format(self):
        assert convert_minutes_to_seconds("badvalue") == 0

    def test_none_via_nan(self):
        assert convert_minutes_to_seconds(None) == 0


# ---------------------------------------------------------------------------
# Fantasy points formula
# ---------------------------------------------------------------------------

class TestFantasyPointsFormula:
    """
    Verify the scoring formula: pts*1 + reb*1.2 + ast*1.5 + stl*3 + blk*3
    by running get_player_stats() against mocked API data.
    """

    def _make_game_row(self, pts, reb, ast, stl, blk):
        return {
            "Game_ID": "0022400001",
            "GAME_DATE": pd.Timestamp("2025-01-15"),
            "MIN": "30:00",
            "PTS": pts,
            "REB": reb,
            "AST": ast,
            "STL": stl,
            "BLK": blk,
        }

    def _run_with_mock_game(self, tmp_path, game_row):
        make_players_csv(str(tmp_path), [(1, "Test Player", "Test Team")])
        df = pd.DataFrame([game_row])

        mock_gamelog = MagicMock()
        mock_gamelog.get_data_frames.return_value = [df]

        with patch("get_player_stats.playergamelog.PlayerGameLog", return_value=mock_gamelog):
            os.chdir(tmp_path)
            result = get_player_stats()

        assert not result["fatal_error"]
        output = pd.read_csv(tmp_path / "Data" / "player_1" / "player_stats.csv")
        return output.iloc[0]

    def test_formula_typical_game(self, tmp_path):
        row = self._run_with_mock_game(tmp_path, self._make_game_row(25, 10, 8, 2, 1))
        expected = 25 * 1.0 + 10 * 1.2 + 8 * 1.5 + 2 * 3.0 + 1 * 3.0
        assert abs(row["fantasy_points"] - expected) < 0.001

    def test_formula_zero_stats(self, tmp_path):
        row = self._run_with_mock_game(tmp_path, self._make_game_row(0, 0, 0, 0, 0))
        assert row["fantasy_points"] == 0.0

    def test_formula_high_scoring_game(self, tmp_path):
        row = self._run_with_mock_game(tmp_path, self._make_game_row(50, 0, 0, 0, 0))
        assert abs(row["fantasy_points"] - 50.0) < 0.001

    def test_formula_defensive_player(self, tmp_path):
        # 5 steals + 5 blocks = 30 pts, 10 pts scored = 40 total
        row = self._run_with_mock_game(tmp_path, self._make_game_row(10, 0, 0, 5, 5))
        expected = 10.0 + 5 * 3.0 + 5 * 3.0
        assert abs(row["fantasy_points"] - expected) < 0.001

    def test_formula_playmaker(self, tmp_path):
        # 10 ast = 15 pts
        row = self._run_with_mock_game(tmp_path, self._make_game_row(0, 0, 10, 0, 0))
        assert abs(row["fantasy_points"] - 15.0) < 0.001


# ---------------------------------------------------------------------------
# get_player_stats() integration
# ---------------------------------------------------------------------------

class TestGetPlayerStats:
    def test_missing_players_csv(self, tmp_path):
        os.chdir(tmp_path)
        result = get_player_stats()
        assert result["fatal_error"] is True
        assert result["error_code"] == -21

    def test_no_games_in_range(self, tmp_path):
        make_players_csv(str(tmp_path), [(99, "Old Player", "Old Team")])

        # Game outside 2025
        df = pd.DataFrame([{
            "Game_ID": "0012300001",
            "GAME_DATE": pd.Timestamp("2023-11-01"),
            "MIN": "20:00",
            "PTS": 10, "REB": 5, "AST": 3, "STL": 1, "BLK": 0,
        }])

        mock_gamelog = MagicMock()
        mock_gamelog.get_data_frames.return_value = [df]

        with patch("get_player_stats.playergamelog.PlayerGameLog", return_value=mock_gamelog):
            os.chdir(tmp_path)
            result = get_player_stats()

        assert not result["fatal_error"]
        # No CSV should have been written since no games in 2025
        assert not os.path.exists(tmp_path / "Data" / "player_99" / "player_stats.csv")

    def test_output_csv_columns(self, tmp_path):
        make_players_csv(str(tmp_path), [(42, "Test Player", "Team")])

        df = pd.DataFrame([{
            "Game_ID": "0022400999",
            "GAME_DATE": pd.Timestamp("2025-03-01"),
            "MIN": "28:15",
            "PTS": 18, "REB": 7, "AST": 5, "STL": 2, "BLK": 1,
        }])

        mock_gamelog = MagicMock()
        mock_gamelog.get_data_frames.return_value = [df]

        with patch("get_player_stats.playergamelog.PlayerGameLog", return_value=mock_gamelog):
            os.chdir(tmp_path)
            get_player_stats()

        output = pd.read_csv(tmp_path / "Data" / "player_42" / "player_stats.csv")
        expected_cols = {"game_id", "week_of_year", "seconds_played", "points",
                         "rebounds", "assists", "steals", "blocks", "fantasy_points"}
        assert expected_cols.issubset(set(output.columns))

    def test_player_api_error_is_warning_not_fatal(self, tmp_path):
        make_players_csv(str(tmp_path), [(1, "Good Player", "Team"), (2, "Bad Player", "Team")])

        good_df = pd.DataFrame([{
            "Game_ID": "001", "GAME_DATE": pd.Timestamp("2025-02-10"),
            "MIN": "30:00", "PTS": 20, "REB": 5, "AST": 4, "STL": 1, "BLK": 0,
        }])

        def side_effect(player_id, **kwargs):
            mock = MagicMock()
            if player_id == 1:
                mock.get_data_frames.return_value = [good_df]
            else:
                mock.get_data_frames.side_effect = Exception("API error")
            return mock

        with patch("get_player_stats.playergamelog.PlayerGameLog", side_effect=side_effect):
            os.chdir(tmp_path)
            result = get_player_stats()

        assert not result["fatal_error"]
        assert result["warnings"] == 1
