"""
Tests for score_matchup.py

Covers:
- Missing weekly_scores.csv → fatal error -11
- build_ai_team failure → fatal error -12
- User wins (higher score)
- User loses (lower score)
- Tie (equal scores)
- User player with no stats that week scores 0 (warning)
- Returned scores are correct floats
- Result dict has all expected keys
"""

import os
import sys
import pytest
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from score_matchup import score_matchup
from tests.conftest import make_weekly_scores_csv


def _weekly_row(player_id, name, week, fp):
    return {
        "player_id": player_id,
        "player_name": name,
        "week_of_year": week,
        "games_played": 3,
        "total_points": 0,
        "total_rebounds": 0,
        "total_assists": 0,
        "total_steals": 0,
        "total_blocks": 0,
        "total_fantasy_points": fp,
    }


def _ai_success(roster):
    """Helper: return a successful build_ai_team result with the given roster list."""
    return {
        "fatal_error": False,
        "warnings": 0,
        "error_code": 0,
        "roster": roster,
    }


class TestScoreMatchupErrors:
    def test_missing_weekly_scores(self, tmp_path):
        os.chdir(tmp_path)
        result = score_matchup(5, [1, 2, 3])
        assert result["fatal_error"] is True
        assert result["error_code"] == -11

    def test_build_ai_team_failure(self, tmp_path):
        make_weekly_scores_csv(str(tmp_path), [_weekly_row(1, "User Player", 5, 80.0)])
        os.chdir(tmp_path)

        with patch("score_matchup.build_ai_team", return_value={
            "fatal_error": True, "warnings": 0, "error_code": -12, "roster": []
        }):
            result = score_matchup(5, [1])

        assert result["fatal_error"] is True
        assert result["error_code"] == -12


class TestScoreMatchupResults:
    def _setup(self, tmp_path, user_players, ai_players, week=5):
        """Writes weekly_scores.csv and returns a mock AI roster."""
        all_rows = user_players + ai_players
        make_weekly_scores_csv(str(tmp_path), all_rows)
        os.chdir(tmp_path)

        ai_roster = [
            {"player_id": p["player_id"], "player_name": p["player_name"],
             "total_fantasy_points": p["total_fantasy_points"]}
            for p in ai_players
        ]
        return _ai_success(ai_roster)

    def test_user_wins(self, tmp_path):
        user = [_weekly_row(1, "Star", 5, 200.0)]
        ai = [_weekly_row(10, "AI Star", 5, 100.0)]
        ai_mock = self._setup(tmp_path, user, ai)

        with patch("score_matchup.build_ai_team", return_value=ai_mock):
            result = score_matchup(5, [1])

        assert result["result"] == "win"
        assert result["user_score"] == 200.0
        assert result["ai_score"] == 100.0

    def test_user_loses(self, tmp_path):
        user = [_weekly_row(1, "Bench", 5, 50.0)]
        ai = [_weekly_row(10, "AI Ace", 5, 150.0)]
        ai_mock = self._setup(tmp_path, user, ai)

        with patch("score_matchup.build_ai_team", return_value=ai_mock):
            result = score_matchup(5, [1])

        assert result["result"] == "loss"
        assert result["user_score"] == 50.0
        assert result["ai_score"] == 150.0

    def test_tie(self, tmp_path):
        user = [_weekly_row(1, "Player A", 5, 100.0)]
        ai = [_weekly_row(10, "Player B", 5, 100.0)]
        ai_mock = self._setup(tmp_path, user, ai)

        with patch("score_matchup.build_ai_team", return_value=ai_mock):
            result = score_matchup(5, [1])

        assert result["result"] == "tie"
        assert result["user_score"] == result["ai_score"]

    def test_scores_are_summed_across_roster(self, tmp_path):
        user = [
            _weekly_row(1, "P1", 5, 40.0),
            _weekly_row(2, "P2", 5, 60.0),
            _weekly_row(3, "P3", 5, 30.0),
        ]
        ai = [_weekly_row(10, "AI", 5, 50.0)]
        ai_mock = self._setup(tmp_path, user, ai)

        with patch("score_matchup.build_ai_team", return_value=ai_mock):
            result = score_matchup(5, [1, 2, 3])

        assert result["user_score"] == 130.0
        assert result["result"] == "win"

    def test_player_with_no_stats_scores_zero_with_warning(self, tmp_path):
        # Only player 1 is in weekly_scores; player 99 has no data
        user = [_weekly_row(1, "Known", 5, 80.0)]
        ai = [_weekly_row(10, "AI", 5, 90.0)]
        ai_mock = self._setup(tmp_path, user, ai)

        with patch("score_matchup.build_ai_team", return_value=ai_mock):
            result = score_matchup(5, [1, 99])

        assert not result["fatal_error"]
        assert result["warnings"] >= 1
        assert result["user_score"] == 80.0  # player 99 contributes 0

    def test_result_has_all_expected_keys(self, tmp_path):
        user = [_weekly_row(1, "P", 5, 70.0)]
        ai = [_weekly_row(10, "AI", 5, 60.0)]
        ai_mock = self._setup(tmp_path, user, ai)

        with patch("score_matchup.build_ai_team", return_value=ai_mock):
            result = score_matchup(5, [1])

        expected_keys = {"fatal_error", "warnings", "error_code", "week_number",
                         "user_score", "ai_score", "result", "user_roster", "ai_roster"}
        assert expected_keys.issubset(result.keys())

    def test_week_number_in_result(self, tmp_path):
        user = [_weekly_row(1, "P", 8, 50.0)]
        ai = [_weekly_row(10, "AI", 8, 40.0)]
        ai_mock = self._setup(tmp_path, user, ai, week=8)

        with patch("score_matchup.build_ai_team", return_value=ai_mock):
            result = score_matchup(8, [1])

        assert result["week_number"] == 8
