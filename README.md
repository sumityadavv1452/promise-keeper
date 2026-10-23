# ✦ Promise Keeper
> **Wearable AI Staging Engine for Everyday Verbal Commitments**  
> *Track: Bee Wearable Hardware | Mini-Challenges: AWS Builder, Open Source*

---

## 💡 The Human Story
Meet Maya, a freelance designer juggling client calls, team standups, and creative reviews.
Every day, she makes casual verbal promises:
- *"I'll send you the revised pitch deck by 5 PM tomorrow."*
- *"I'll review your analytics report before Wednesday noon."*

She can't stop mid-conversation to type reminders on her phone without breaking human rapport. By evening, those promises are forgotten. 

Existing "autonomous AI agents" are too risky—nobody wants an AI sending unreviewed emails to clients. **Promise Keeper** bridges the gap: it captures commitments via the **Bee wearable**, extracts them using **Amazon Bedrock**, and stages them in a human-in-the-loop dashboard. **Nothing is dispatched without explicit approval.**

---

## 🛡️ Architectural Safety Guarantees
1. **Zero Autonomous Send**: Authentication is strictly locked to `gmail.compose` scope. The application physically cannot send an email; it creates drafts in Gmail for you to inspect and hit "Send."
2. **Deterministic Human Review**: Every commitment must be reviewed, adjusted, and approved in the UI.
3. **Ambiguity & Confidence Guard**: Low-confidence statements ("Maybe I'll do it sometime") are flagged with a prominent **"Needs Confirmation"** warning rather than treated as firm deadlines.
4. **Local Hardware Ingestion**: Audio ingestion happens on-device via Bee wearable, diarizing speakers in real time.

---

## 🏗️ Technical Pipeline
```
[ Bee Wearable Stream ] ──▶ [ Amazon Bedrock (Nova Pro) ] ──▶ [ Promise Keeper UI ]
                                                                       │ (Approve)
                                                ┌─────────────────────┼─────────────────────┐
                                                ▼                     ▼                     ▼
                                         [ Todoist Task ]     [ Gmail Draft ]     [ Calendar Event ]
```

---

## ⚡ Setup & Quickstart

### Prerequisites
- Python 3.11+
- Bee CLI installed and paired with your wearable
- AWS Credentials configured with Bedrock access (`us-east-1`)

### 1. Installation
```bash
git clone https://github.com/your-username/promise-keeper.git
cd promise-keeper
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment Variables (.env)
```ini
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=amazon.nova-pro-v1:0
TODOIST_API_TOKEN=your_todoist_token_here
```

### 3. Run the Safety Test Suite
```bash
pytest tests/test_safety_invariants.py -v
```

### 4. Launch Next.js Dashboard (Turbopack)
```bash
npm run dev
# Dashboard opens on http://localhost:3000
```

---


## ⚖️ License
MIT License.
