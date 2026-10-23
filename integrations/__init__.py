"""
Promise Keeper Integrations Package.
Modular interfaces for Bee Wearable Ingestion, Amazon Bedrock Extraction, and Atomic Dispatch.
"""

from integrations.bee_client import BeeClient, fetch_latest_bee_transcript, fetch_bee_transcripts
from integrations.bedrock_extractor import (
    BedrockPromiseExtractor,
    PromiseItem,
    ExtractionResult,
    extract_commitments_from_transcript,
)
from integrations.dispatcher import Dispatcher, stage_commitment_atomically, undo_staging

__all__ = [
    "BeeClient",
    "fetch_latest_bee_transcript",
    "fetch_bee_transcripts",
    "BedrockPromiseExtractor",
    "PromiseItem",
    "ExtractionResult",
    "extract_commitments_from_transcript",
    "Dispatcher",
    "stage_commitment_atomically",
    "undo_staging",
]
