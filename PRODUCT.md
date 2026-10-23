# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Busy professionals, executives, and knowledge workers wearing the Bee wearable audio device (or similar ambient audio hardware) who make and receive verbal promises, commitments, and deadlines during conversations throughout their workday.

## Product Purpose

Promise Keeper continuously captures spoken commitments from the ambient audio stream of the Bee wearable, extracts structured commitments and deadlines via AWS Bedrock (Amazon Nova Pro), and stages safe, editable drafts and calendar blocks into Gmail, Google Calendar, and Todoist for deterministic human review.

## Positioning

Unlike autonomous AI agents that send emails or book meetings directly, Promise Keeper implements a strict staging engine with zero autonomous execution. Outgoing emails are strictly composed as drafts (`gmail.compose` scope), calendar invites are tentative blocks, and todo items are pre-tagged with `#promise-keeper` — preserving human oversight while eliminating dropped verbal commitments.

## Operating Context

- **Audio Ingestion**: Bee wearable device capturing 16kHz PCM audio via Bluetooth Low Energy (BLE) / Bee CLI bridge.
- **Inference Pipeline**: AWS Bedrock Converse API extracting structured commitments (`amazon.nova-pro-v1:0` or `anthropic.claude-3-5-sonnet-20241022-v2:0`).
- **Human Review Dashboard**: Streamlit web dashboard running locally at `http://127.0.0.1:8501`.
- **Destinations**: Gmail (Drafts), Google Calendar (Tentative Timeblocks), Todoist (Tasks).

## Capabilities and Constraints

- **Zero Autonomous Send**: All communication actions must stage as editable drafts; auto-sending without human approval is strictly forbidden.
- **Deterministic Review**: Users review, modify, or dismiss every extracted commitment before dispatch.
- **Tentative Calendar Holds**: Calendar scheduling generates non-destructive tentative holds.
- **Atomic Dispatch & Idempotency**: Staging updates occur atomically across destinations; duplicate actions for the same commitment hash are prevented.
- **Ambiguity Guard**: Conversational commitments with low confidence (<70%) or tentative phrasing are prominently flagged for confirmation.

## Brand Commitments

- **Tagline**: "You said it. We'll remember it."
- **Tone**: Calm, precise, reliable, executive-grade.
- **Aesthetic**: Restrained craft, deep dark/crisp light mode, bespoke vector marks, high-contrast readable typography.

## Evidence on Hand

- Live running prototype at `http://127.0.0.1:8501`.
- Fully passing unit and integration tests (`tests/test_pipeline_health.py`, 30/30 passed).
- Real AWS Bedrock Converse API client and mock fallback in `integrations/bedrock_extractor.py`.
- Dispatcher and atomic staging in `integrations/dispatcher.py`.

## Product Principles

1. **Human is the Decider**: The machine listens and stages; the human approves and dispatches.
2. **Deterministic Over Magical**: Clear confidence percentages, exact transcript attribution, and inspectable payloads.
3. **Fail Safe, Never Loudly**: If an integration drops, rollback occurs atomically without leaving partial or corrupted artifacts.
4. **Calm Attention**: The interface is an executive instrument, not an arcade. No unnecessary animations, flashy badges, or decorative fluff.
