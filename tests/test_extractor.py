"""
Unit tests for BedrockPromiseExtractor, Converse API response handling, and telemetry.
"""

from unittest.mock import MagicMock, patch
import pytest
from src.extractor import BedrockPromiseExtractor, PromiseItem, ExtractionResult
from src.telemetry import calculate_cost, TelemetryRecorder


def test_sanitize_json_response_with_markdown_fence():
    """Ensure ```json fences are cleanly removed."""
    raw = """```json
[
  {
    "direction": "MADE_BY_ME",
    "counterparty_name": "Sarah",
    "counterparty_email": "sarah@example.com",
    "summary": "Send deck",
    "verbal_deadline": "5 PM",
    "inferred_iso_deadline": "2026-10-20T17:00:00Z",
    "task_title": "Send deck",
    "email_draft": {"subject": "Deck", "body": "Attached."},
    "calendar_event": {"title": "Send Deck", "start_iso": "2026-10-20T16:00:00Z", "duration_minutes": 30}
  }
]
```"""
    cleaned = BedrockPromiseExtractor.sanitize_json_response(raw)
    assert cleaned.startswith("[")
    assert cleaned.endswith("]")
    assert "```" not in cleaned


def test_sanitize_json_response_with_surrounding_chatter():
    """Ensure leading and trailing LLM chatter is cleanly stripped away."""
    raw = """Here is your extracted commitments list:
[
  {"test": 123}
]
Hope this helps! Let me know if you need more."""
    cleaned = BedrockPromiseExtractor.sanitize_json_response(raw)
    assert cleaned == '[{"test": 123}]' or cleaned.startswith("[") and cleaned.endswith("]")


def test_offline_mock_extraction():
    """Verify that offline mock extraction produces valid Pydantic promises and telemetry."""
    extractor = BedrockPromiseExtractor(primary_model_id="amazon.nova-pro-v1:0")
    # Force mock mode by having no AWS credentials
    result = extractor.extract_promises("Wearer (Me): I will send the pitch deck tomorrow.")

    assert isinstance(result, ExtractionResult)
    assert len(result.promises) > 0
    assert result.telemetry.latency_ms > 0
    assert result.telemetry.total_tokens > 0

    first = result.promises[0]
    assert first.direction in ("MADE_BY_ME", "MADE_TO_ME")
    assert first.counterparty_name != ""
    assert first.email_draft.subject != ""
    assert first.calendar_event.start_iso != ""


@patch("boto3.client")
def test_real_bedrock_converse_mocked_success(mock_boto_client):
    """Verify Bedrock converse() API parsing and usage metrics recording."""
    mock_runtime = MagicMock()
    mock_boto_client.return_value = mock_runtime

    mock_json_payload = """[
      {
        "direction": "MADE_TO_ME",
        "counterparty_name": "Sarah Lin",
        "counterparty_email": "sarah.lin@example.com",
        "summary": "Sarah asked for the analytics report",
        "verbal_deadline": "Thursday 9 AM",
        "inferred_iso_deadline": "2026-10-22T09:00:00Z",
        "task_title": "Share analytics with Sarah",
        "email_draft": {
          "subject": "Analytics Report",
          "body": "Hi Sarah, here is the report."
        },
        "calendar_event": {
          "title": "Review Analytics",
          "start_iso": "2026-10-22T08:30:00Z",
          "duration_minutes": 30
        }
      }
    ]"""

    mock_runtime.converse.return_value = {
        "output": {
            "message": {
                "content": [{"text": mock_json_payload}]
            }
        },
        "usage": {
            "inputTokens": 350,
            "outputTokens": 180,
        },
    }

    with patch.dict("os.environ", {"AWS_ACCESS_KEY_ID": "AKIA_MOCK_TEST"}):
        extractor = BedrockPromiseExtractor(primary_model_id="amazon.nova-pro-v1:0")
        extractor._client = mock_runtime

        res = extractor.extract_promises("Sample transcript")
        assert len(res.promises) == 1
        item = res.promises[0]
        assert item.direction == "MADE_TO_ME"
        assert item.counterparty_name == "Sarah Lin"
        assert res.telemetry.input_tokens == 350
        assert res.telemetry.output_tokens == 180
        assert res.telemetry.estimated_cost_usd > 0


def test_telemetry_cost_calculation():
    """Verify cost calculation for Amazon Nova Pro and Claude 3.5 Sonnet."""
    cost_nova = calculate_cost("amazon.nova-pro-v1:0", 1000, 1000)
    # Nova Pro: 0.0008 + 0.0032 = 0.0040 USD
    assert cost_nova == pytest.approx(0.004, rel=1e-3)

    cost_claude = calculate_cost("anthropic.claude-3-5-sonnet-20241022-v2:0", 1000, 1000)
    # Claude: 0.0030 + 0.0150 = 0.0180 USD
    assert cost_claude == pytest.approx(0.018, rel=1e-3)
