"""
Telemetry and observability module for Promise Keeper.
Tracks latency, token consumption, and cost metrics for Amazon Bedrock Converse API calls.
"""

from __future__ import annotations
import datetime
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

# Pricing table per 1,000 tokens (USD)
# Source: AWS Bedrock pricing for Amazon Nova and Anthropic Claude models
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "amazon.nova-pro-v1:0": {
        "input_per_1k": 0.0008,
        "output_per_1k": 0.0032,
    },
    "amazon.nova-lite-v1:0": {
        "input_per_1k": 0.00006,
        "output_per_1k": 0.00024,
    },
    "anthropic.claude-3-5-sonnet-20241022-v2:0": {
        "input_per_1k": 0.0030,
        "output_per_1k": 0.0150,
    },
    "anthropic.claude-3-haiku-20240307-v1:0": {
        "input_per_1k": 0.00025,
        "output_per_1k": 0.00125,
    },
}

DEFAULT_PRICING = {
    "input_per_1k": 0.0008,
    "output_per_1k": 0.0032,
}


def calculate_cost(model_id: str, input_tokens: int, output_tokens: int) -> float:
    """Calculates estimated cost in USD based on model pricing."""
    pricing = MODEL_PRICING.get(model_id, DEFAULT_PRICING)
    cost = (input_tokens / 1000.0) * pricing["input_per_1k"] + (
        output_tokens / 1000.0
    ) * pricing["output_per_1k"]
    return round(cost, 6)


class TelemetryRecord(BaseModel):
    """Represents a single Bedrock API execution record."""

    id: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).strftime(
            "%Y%m%d%H%M%S%f"
        )
    )
    timestamp: str = Field(
        default_factory=lambda: datetime.datetime.now(datetime.timezone.utc).isoformat()
    )
    model_id: str
    latency_ms: float
    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    estimated_cost_usd: float = 0.0
    status: str = "SUCCESS"  # SUCCESS, FALLBACK, or ERROR
    details: Optional[str] = None
    error_message: Optional[str] = None


class TelemetryRecorder:
    """Maintains an in-memory audit log of Bedrock performance and costs."""

    def __init__(self) -> None:
        self.records: List[TelemetryRecord] = []

    def record(
        self,
        model_id: str | TelemetryRecord,
        latency_ms: float = 0.0,
        input_tokens: int = 0,
        output_tokens: int = 0,
        status: str = "SUCCESS",
        details: Optional[str] = None,
    ) -> TelemetryRecord:
        """Records a new inference metric entry."""
        if isinstance(model_id, TelemetryRecord):
            self.records.append(model_id)
            return model_id

        actual_model_id = str(model_id)
        total_tokens = input_tokens + output_tokens
        cost = calculate_cost(actual_model_id, input_tokens, output_tokens)

        entry = TelemetryRecord(
            model_id=actual_model_id,
            latency_ms=round(latency_ms, 2),
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            total_tokens=total_tokens,
            estimated_cost_usd=cost,
            status=status,
            details=details,
        )
        self.records.append(entry)
        return entry

    def get_latest(self) -> Optional[TelemetryRecord]:
        """Returns the most recent telemetry record if available."""
        if not self.records:
            return None
        return self.records[-1]

    def get_summary(self) -> Dict[str, float | int]:
        """Computes aggregate metrics across all runs."""
        if not self.records:
            return {
                "total_calls": 0,
                "avg_latency_ms": 0.0,
                "total_input_tokens": 0,
                "total_output_tokens": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
            }

        total_latency = sum(r.latency_ms for r in self.records)
        total_in = sum(r.input_tokens for r in self.records)
        total_out = sum(r.output_tokens for r in self.records)
        total_cost = sum(r.estimated_cost_usd for r in self.records)

        return {
            "total_calls": len(self.records),
            "avg_latency_ms": round(total_latency / len(self.records), 2),
            "total_input_tokens": total_in,
            "total_output_tokens": total_out,
            "total_tokens": total_in + total_out,
            "total_cost_usd": round(total_cost, 6),
        }

    def clear(self) -> None:
        """Clears all records."""
        self.records.clear()


# Default singleton instance
default_telemetry_recorder = TelemetryRecorder()
