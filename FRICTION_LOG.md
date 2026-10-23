# 📝 Developer Friction Log (Bee, Bedrock & Destination APIs)

### 1. Colleague Speech Boundary vs. Self-Commitments
- **Hurdle**: Separating promises made *by* the user from promises made *to* the user in multi-speaker diarized streams.
- **Resolution**: Implemented two-pass classification in Bedrock system prompt evaluating subject pronoun anchors (`Speaker 1 (Me)` vs `Speaker 2`).

### 2. Colloquial Temporal Grounding to ISO-8601
- **Hurdle**: Expressions like "Wednesday noon" or "tomorrow 5 PM" cause date parsing drift when evaluated without timezone context.
- **Resolution**: Passed the client machine's current UTC anchor directly into Bedrock inference parameters to generate verifiable ISO-8601 timestamps.

### 3. OAuth Scope Security & User Trust
- **Hurdle**: Requesting `gmail.send` triggered significant security friction and invalidated the "human safety" proposition.
- **Resolution**: Strictly downgraded scope to `gmail.compose`. The app creates drafts exclusively, guaranteeing zero autonomous email transmissions.

### 4. Wearable Audio Stream Handshake
- **Hurdle**: Polling the Bee CLI directly during active background audio capture occasionally locked the local process output buffer.
- **Resolution**: Added subprocess timeout guards with automatic fallback to active session transcript buffers.

### 5. Streamlit Full-Page Rerun vs Next.js Client State
- **Hurdle**: Streamlit's full-page rerun lifecycle risked double-dispatching external API calls and squashed columns under Emotion container queries.
- **Resolution**: Transitioned to Next.js 15 with Turbopack, utilizing React state and atomic idempotency guards to eliminate container wrapping and double-dispatch.

