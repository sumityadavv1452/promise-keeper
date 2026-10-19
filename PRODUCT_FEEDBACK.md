# Product Feedback: Wearable AI & Cloud Foundation
**Actionable Recommendations for the Bee Wearable Team & AWS Bedrock Team**  
*Project:* Promise Keeper  
*Date:* October 2026  

---

## 1. Actionable Feedback for the Bee Team (`@beeai/cli` & Wearable Hardware)

### Recommendation 1.1: Event-Driven Daemon / Local WebSocket Push (vs Polling `bee now`)
- **Current Limitation:** Currently, applications must periodically poll the CLI via `bee now --json` or run `bee sync`. This introduces polling latency (up to 5-10 seconds) and causes unnecessary Bluetooth battery drain on the wearable.
- **Proposed Solution:** Provide a background daemon (`bee daemon --port 8765`) or Unix domain socket / WebSocket server that streams speech turns and voice activity events in real time.
- **Value Impact:** Enables near-instantaneous promise extraction the moment a sentence finishes, reducing user wait time to sub-second levels.

### Recommendation 1.2: Wearable Hardware Button Tap Metadata in Turn Schemas
- **Current Limitation:** The physical button on the Bee pendant is primarily used for device pairing or manual mute.
- **Proposed Solution:** Expose hardware button events in the `bee now --json` payload:
  ```json
  {
    "turn_id": "turn_042",
    "speaker": "Wearer",
    "hardware_flags": {
      "button_tapped": true,
      "tap_count": 2,
      "tap_timestamp": "2026-10-19T09:16:12Z"
    },
    "text": "I will get that agreement signed by 3 PM."
  }
  ```
- **Value Impact:** The wearer could double-tap the Bee wearable mid-conversation to mark a high-priority promise, giving the extraction agent an explicit signal to boost task priority to P1.

### Recommendation 1.3: Enhanced Speaker Diarization Confidence Scores
- **Current Limitation:** Turn diarization tags occasionally alternate unpredictably when background ambient speech or cross-talk is present.
- **Proposed Solution:** Include speaker attribution confidence scores (`speaker_confidence: 0.88`) and voice biometric distance metrics in the turn metadata.
- **Value Impact:** Enables agents to filter out background strangers at coffee shops and focus strictly on verified speaker interactions.

---

## 2. Actionable Feedback for the AWS Bedrock Team (Bedrock Converse API)

### Recommendation 2.1: Native JSON Schema Enforcement (Without `toolConfig` Overhead)
- **Current Limitation:** In the Bedrock Converse API (`bedrock-runtime.converse`), enforcing structured output currently requires wrapping schemas in `toolConfig` (`toolUse`), which introduces 200+ tokens of schema serialization overhead and up to 3 seconds of cold-start latency with Nova Pro.
- **Proposed Solution:** Introduce a first-class `responseFormat` parameter in `converse()`:
  ```python
  client.converse(
      modelId="amazon.nova-pro-v1:0",
      messages=messages,
      responseFormat={
          "type": "json_object",
          "schema": PromiseListSchema.model_json_schema()
      }
  )
  ```
- **Value Impact:** Eliminates markdown code block stripping, guarantees 100% JSON schema conformity at the decoder level, and saves up to 25% token cost per invocation.

### Recommendation 2.2: Ultra-Low-Latency Provisioned Warm Pools for Wearable Agents
- **Current Limitation:** Ambient wearable AI agents require response times under 800ms to feel conversational. On-demand Nova Pro invocations periodically experience cold starts ranging between 2.5s and 4.2s.
- **Proposed Solution:** Offer dynamic warm instance pools or latency-optimized endpoints for `amazon.nova-pro-v1:0` tailored for ambient edge computing.
- **Value Impact:** Enables instant user notifications on companion smartwatches as soon as a meeting concludes.

### Recommendation 2.3: Native Temporal Grounding Primitives
- **Current Limitation:** LLMs struggle with relative temporal grounding ("next Tuesday", "in two hours", "by tomorrow at 5") unless prompt-engineered with reference timestamps, which wastes context window tokens.
- **Proposed Solution:** Add an optional `temporalContext` block to the Bedrock Converse API:
  ```python
  converse(
      modelId="amazon.nova-pro-v1:0",
      temporalContext={
          "referenceTime": "2026-10-19T11:20:00Z",
          "userTimeZone": "America/New_York"
      }
  )
  ```
- **Value Impact:** Native temporal understanding in the foundation model ensures accurate deadline resolution without complex post-processing or datetime calculation prompts.

---

*Authored by the Promise Keeper team for submission to the Amazon Developer Hackathon evaluation committee.*
