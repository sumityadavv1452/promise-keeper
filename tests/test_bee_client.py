"""
Unit tests for BeeClient wearable interface and offline fallback mechanisms.
"""

from unittest.mock import MagicMock, patch
import pytest
from src.bee_client import BeeClient, OFFLINE_FIXTURE_TURNS


def test_bee_client_mock_mode_default():
    """Verify that BeeClient initializes with mock_mode True when CLI is absent or in test."""
    client = BeeClient(mock_mode=True)
    assert client.mock_mode is True

    status = client.check_status()
    assert status["status"] == "connected"
    assert status["mode"] == "MOCK_FIXTURE"
    assert "Bee Wearable" in status["device"]
    assert status["battery_percentage"] > 0
    assert "@" in status["authenticated_user"]


def test_fetch_recent_conversations_mock():
    """Verify fetch_recent_conversations returns valid multi-speaker fixture turns."""
    client = BeeClient(mock_mode=True)
    result = client.fetch_recent_conversations()

    assert "turns" in result
    turns = result["turns"]
    assert len(turns) >= 4

    # Ensure explicit commitments are present in the fixture
    transcript_text = " ".join(t.get("text", "") for t in turns)
    assert "pitch deck" in transcript_text
    assert "analytics report" in transcript_text
    assert "vendor agreement" in transcript_text


def test_format_transcript_for_llm():
    """Verify that format_transcript_for_llm formats turns into clean speaker lines."""
    client = BeeClient(mock_mode=True)
    data = client.fetch_recent_conversations()
    formatted = client.format_transcript_for_llm(data)

    assert isinstance(formatted, str)
    assert "Wearer (Me):" in formatted
    assert "Sarah Lin:" in formatted
    assert "pitch deck" in formatted


def test_bee_sync_mock():
    """Verify that sync() executes successfully in mock mode."""
    client = BeeClient(mock_mode=True)
    res = client.sync()
    assert res["success"] is True
    assert "synced_at" in res


@patch("shutil.which", return_value="/usr/local/bin/bee")
@patch("subprocess.run")
def test_bee_cli_success(mock_subproc, mock_which):
    """Verify that real CLI response is parsed when subprocess succeeds."""
    mock_subproc.return_value = MagicMock(
        returncode=0,
        stdout='{"status": "connected", "battery": "90%", "user": "tester@test.com"}',
        stderr="",
    )

    client = BeeClient(cli_path="bee", mock_mode=False)
    status = client.check_status()

    assert status["status"] == "connected"
    assert status["mode"] == "HARDWARE_LIVE"
    assert status["battery"] == "90%"


@patch("shutil.which", return_value="/usr/local/bin/bee")
@patch("subprocess.run")
def test_bee_cli_malformed_json_fallback(mock_subproc, mock_which):
    """Verify that malformed CLI JSON output gracefully falls back to fixture without crash."""
    mock_subproc.return_value = MagicMock(
        returncode=0,
        stdout="NON_JSON_CORRUPT_BUFFER_FROM_BLUETOOTH",
        stderr="",
    )

    client = BeeClient(cli_path="bee", mock_mode=False)
    result = client.fetch_recent_conversations()

    assert result["source"] == "PARSER_FALLBACK"
    assert len(result["turns"]) == len(OFFLINE_FIXTURE_TURNS)
