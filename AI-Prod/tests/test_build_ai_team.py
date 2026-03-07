"""
Tests for build_ai_team.py

Covers:
- Missing weekly_scores.csv → fatal error -11
- No data for requested week → fatal error -12
- Correct top-N selection (highest fantasy points)
- Players from other weeks are not included
- Fewer players than ROSTER_SIZE → warning, uses all available
- Output CSV is saved with correct content
"""

import os
import sys
import pytest
import pandas as pd

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from build_ai_team import build_ai_team, ROSTER_SIZE
from tests.conftest import make_weekly_scores_csv


def _weekly_row(player_id, name, week, fp, games=3):
    return {
        "player_id": player_id,
        "player_name": name,
        "week_of_year": week,
        "games_played": games,
        "total_points": 0,
        "total_rebounds": 0,
        "total_assists": 0,
        "total_steals": 0,
        "total_blocks": 0,
        "total_fantasy_points": fp,
    }


class TestBuildAiTeamErrors:
    def test_missing_weekly_scores(self, tmp_path):
        os.chdir(tmp_path)
        result = build_ai_team(5)
        assert result["fatal_error"] is True
        assert result["error_code"] == -11
        assert result["roster"] == []

    def test_no_data_for_week(self, tmp_path):
        make_weekly_scores_csv(str(tmp_path), [_weekly_row(1, "Player", 3, 50.0)])
        os.chdir(tmp_path)
        result = build_ai_team(9)  # week 9 doesn't exist
        assert result["fatal_error"] is True
        assert result["error_code"] == -12


class TestBuildAiTeamSelection:
    def _make_many_players(self, week, count):
        return [_weekly_row(i, f"Player {i}", week, float(100 - i)) for i in range(1, count + 1)]

    def test_selects_top_n_players(self, tmp_path):
        rows = self._make_many_players(week=5, count=20)
        make_weekly_scores_csv(str(tmp_path), rows)
        os.chdir(tmp_path)
        result = build_ai_team(5)

        assert not result["fatal_error"]
        assert len(result["roster"]) == ROSTER_SIZE
        # The top ROSTER_SIZE players should be player 1..8 (highest fp)
        selected_ids = [p["player_id"] for p in result["roster"]]
        assert selected_ids == list(range(1, ROSTER_SIZE + 1))

    def test_players_from_other_weeks_excluded(self, tmp_path):
        rows = (
            [_weekly_row(i, f"Week5 P{i}", 5, float(100 - i)) for i in range(1, 10)]
            + [_weekly_row(50, "Week3 Player", 3, 999.0)]  # huge fp but wrong week
        )
        make_weekly_scores_csv(str(tmp_path), rows)
        os.chdir(tmp_path)
        result = build_ai_team(5)

        assert not result["fatal_error"]
        selected_ids = [p["player_id"] for p in result["roster"]]
        assert 50 not in selected_ids

    def test_fewer_than_roster_size_is_warning_not_fatal(self, tmp_path):
        rows = [_weekly_row(i, f"Player {i}", 7, float(50 - i)) for i in range(1, 4)]
        make_weekly_scores_csv(str(tmp_path), rows)
        os.chdir(tmp_path)
        result = build_ai_team(7)

        assert not result["fatal_error"]
        assert result["warnings"] >= 1
        assert len(result["roster"]) == 3  # uses all available

    def test_roster_sorted_by_fantasy_points_descending(self, tmp_path):
        rows = [
            _weekly_row(1, "Low", 2, 30.0),
            _weekly_row(2, "High", 2, 90.0),
            _weekly_row(3, "Mid", 2, 60.0),
        ]
        make_weekly_scores_csv(str(tmp_path), rows)
        os.chdir(tmp_path)
        result = build_ai_team(2)

        fps = [p["total_fantasy_points"] for p in result["roster"]]
        assert fps == sorted(fps, reverse=True)

    def test_output_csv_is_written(self, tmp_path):
        rows = self._make_many_players(week=10, count=10)
        make_weekly_scores_csv(str(tmp_path), rows)
        os.chdir(tmp_path)
        build_ai_team(10)

        output_path = tmp_path / "Data" / "ai_team_week_10.csv"
        assert output_path.exists()
        df = pd.read_csv(output_path)
        assert len(df) == ROSTER_SIZE

    def test_roster_dict_has_expected_keys(self, tmp_path):
        rows = self._make_many_players(week=1, count=10)
        make_weekly_scores_csv(str(tmp_path), rows)
        os.chdir(tmp_path)
        result = build_ai_team(1)

        for player in result["roster"]:
            assert "player_id" in player
            assert "player_name" in player
            assert "total_fantasy_points" in player
