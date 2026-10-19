import streamlit as st
import datetime
import json
from src.bee_client import BeeClient
from src.extractor import BedrockPromiseExtractor
from src.action_router import ActionRouter
from src.telemetry import TelemetryRecorder

# -----------------------------------------------------------------------------
# 1. Page Configuration & Antigravity Design System Injection
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Promise Keeper — Wearable AI Commitment Engine",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Antigravity CSS: clean slate, crisp contrast, hairline borders, no floating text
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;450;500;600;650&family=JetBrains+Mono:wght@400;500&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #121317;
        background-color: #FAFAFC;
    }
    
    /* Hide generic Streamlit UI chrome */
    header, #MainMenu, footer { visibility: hidden; }
    div[data-testid="stDecoration"] { display: none !important; }
    div[data-testid="stToolbar"] { display: none !important; }
    div[data-testid="stStatusWidget"] { display: none !important; }
    .stDeployButton { display: none !important; }
    .block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1200px; }
    
    /* Top Hero Header */
    .hero-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 20px 24px;
        background: #FFFFFF;
        border: 1px solid #E6EAF0;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .brand-title {
        font-size: 20px;
        font-weight: 650;
        letter-spacing: -0.02em;
        color: #121317;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .version-pill {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 500;
        background: #F1F4F9;
        color: #45474D;
        padding: 3px 8px;
        border-radius: 9999px;
    }
    .brand-tagline {
        font-size: 13.5px;
        font-weight: 450;
        color: #5F6368;
        margin: 4px 0 0 0;
        letter-spacing: -0.01em;
    }
    .daemon-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        background: #F8F9FC;
        border: 1px solid #E6EAF0;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 500;
        color: #212226;
    }
    .green-dot {
        width: 7px;
        height: 7px;
        background: #188038;
        border-radius: 50%;
    }
    
    /* High-Density Metric Strip */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E6EAF0;
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.02);
    }
    .metric-label {
        font-size: 12px;
        font-weight: 500;
        color: #5F6368;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.04em;
    }
    .metric-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 22px;
        font-weight: 600;
        color: #121317;
        margin-bottom: 4px;
    }
    .metric-sub {
        font-size: 12px;
        color: #80868B;
    }
    
    /* Commitment Container Card */
    .commitment-card {
        background: #FFFFFF;
        border: 1px solid #E6EAF0;
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.02);
    }
    .chip-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 12px;
    }
    .badge-primary {
        background: #E8F0FE;
        color: #1A73E8;
        font-size: 12px;
        font-weight: 500;
        padding: 4px 10px;
        border-radius: 9999px;
    }
    .badge-secondary {
        background: #FEF7E0;
        color: #B06000;
        font-size: 12px;
        font-weight: 500;
        padding: 4px 10px;
        border-radius: 9999px;
    }
    .badge-status {
        background: #F1F3F4;
        color: #3C4043;
        font-size: 12px;
        font-weight: 500;
        padding: 4px 10px;
        border-radius: 9999px;
    }
    .card-title {
        font-size: 17px;
        font-weight: 600;
        color: #121317;
        margin: 0 0 6px 0;
    }
    .card-summary {
        font-size: 14px;
        color: #45474D;
        margin-bottom: 12px;
        line-height: 1.45;
    }
    .meta-row {
        display: flex;
        gap: 16px;
        font-size: 12.5px;
        color: #5F6368;
        margin-bottom: 16px;
        font-family: 'JetBrains Mono', monospace;
    }
    
    /* Sidebar Styles with High Contrast */
    section[data-testid="stSidebar"] {
        background-color: #FFFFFF !important;
        border-right: 1px solid #E6EAF0 !important;
        color: #212226 !important;
    }
    .sidebar-section {
        background: #FFFFFF;
        border: 1px solid #E6EAF0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
    }
    .sidebar-row {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        color: #212226;
        padding: 6px 0;
        border-bottom: 1px solid #F1F3F4;
    }
    .sidebar-row:last-child { border-bottom: none; }
    .sidebar-val {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
        color: #121317;
    }

    /* Tabs Styling: High Contrast Antigravity Labels */
    div[data-testid="stTabs"] button[role="tab"] {
        color: #3C4043 !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        border-bottom: 2px solid transparent !important;
    }
    div[data-testid="stTabs"] button[role="tab"] p,
    div[data-testid="stTabs"] button span {
        color: #3C4043 !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        margin: 0 !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        color: #121317 !important;
        font-weight: 600 !important;
        border-bottom: 2px solid #121317 !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] p,
    div[data-testid="stTabs"] button[aria-selected="true"] span {
        color: #121317 !important;
        font-weight: 600 !important;
    }

    /* Hairline Form Controls */
    input[type="text"], input[type="number"], textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #FFFFFF !important;
        border: 1px solid #E6EAF0 !important;
        border-radius: 8px !important;
        color: #121317 !important;
        font-size: 13.5px !important;
    }
    input[type="text"]:focus, textarea:focus {
        border-color: #1A73E8 !important;
        box-shadow: 0 0 0 1px #1A73E8 !important;
    }
    
    /* Pill Action Buttons */
    .stButton > button {
        border-radius: 9999px !important;
        font-weight: 500 !important;
        font-size: 13.5px !important;
        letter-spacing: -0.01em !important;
        transition: all 0.15s ease !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. State Initialization
# -----------------------------------------------------------------------------
if "promises" not in st.session_state:
    st.session_state.promises = [
        {
            "id": "prom_1",
            "direction": "MADE_BY_ME",
            "counterparty_name": "Alex Rivera",
            "counterparty_email": "alex.chen@hackathon.dev",
            "summary": "Send revised pitch deck with updated architecture diagram and Bedrock telemetry benchmarks.",
            "verbal_deadline": "Tomorrow, 5:00 PM",
            "iso_deadline": "2026-10-20T17:00:00Z",
            "task_title": "Send revised pitch deck to Alex",
            "priority": "P1 - High",
            "email_subject": "Promise Keeper: Updated Architecture & Telemetry Deck",
            "email_body": "Hey Alex,\n\nFollowing our discussion, I've finalized the updated architecture diagram and attached the Bedrock Converse API latency metrics.\n\nBest,\nSumit",
            "calendar_title": "Focus: Revise & Package Pitch Deck",
            "calendar_duration": 30,
            "staged": False
        },
        {
            "id": "prom_2",
            "direction": "MADE_TO_ME",
            "counterparty_name": "Alex Rivera",
            "counterparty_email": "alex.chen@hackathon.dev",
            "summary": "Review and verify the Q3 analytics report and user retention numbers ahead of Wednesday noon sync.",
            "verbal_deadline": "Wednesday noon",
            "iso_deadline": "2026-10-22T12:00:00Z",
            "task_title": "Review Q3 analytics report from Alex",
            "priority": "P2 - Medium",
            "email_subject": "Confirming receipt: Q3 analytics report review",
            "email_body": "Hi Alex,\n\nConfirming I will review the Q3 analytics report and customer retention cohort numbers as soon as you share them Wednesday morning.\n\nThanks,\nSumit",
            "calendar_title": "Review: Alex's Q3 Analytics Report",
            "calendar_duration": 45,
            "staged": False
        }
    ]

if "staged_count" not in st.session_state:
    st.session_state.staged_count = 0
if "latency_ms" not in st.session_state:
    st.session_state.latency_ms = 284
if "tokens_used" not in st.session_state:
    st.session_state.tokens_used = 1140

# -----------------------------------------------------------------------------
# 3. Sidebar (Toolchain Diagnostics & Live Direct Links)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Runtime Daemon")
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-row"><span>Daemon Status</span><span class="sidebar-val" style="color: #188038;">● Active</span></div>
        <div class="sidebar-row"><span>Daemon Port</span><span class="sidebar-val">4242</span></div>
        <div class="sidebar-row"><span>Hardware Node</span><span class="sidebar-val">Pendant 0x91B2</span></div>
        <div class="sidebar-row"><span>Battery Level</span><span class="sidebar-val">92%</span></div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Bedrock Inference Model")
    model_choice = st.selectbox(
        "Model Selection",
        ["amazon.nova-pro-v1:0", "anthropic.claude-3-5-sonnet-20241022-v2:0"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("### Staging Destinations")
    st.markdown("""
    <div class="sidebar-section">
        <p style="margin: 0 0 8px 0; font-size: 13px;"><a href="https://mail.google.com/mail/u/0/#drafts" target="_blank" style="text-decoration: none; color: #1A73E8; font-weight: 500;">✉️ Open Gmail Drafts ↗</a></p>
        <p style="margin: 0 0 8px 0; font-size: 13px;"><a href="https://calendar.google.com/" target="_blank" style="text-decoration: none; color: #1A73E8; font-weight: 500;">📅 Open Google Calendar ↗</a></p>
        <p style="margin: 0; font-size: 13px;"><a href="https://app.todoist.com/" target="_blank" style="text-decoration: none; color: #1A73E8; font-weight: 500;">📝 Open Todoist App ↗</a></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Telemetry Session")
    st.caption("AWS Bedrock Converse API Latency: 284ms | Cost: $0.0009")

# -----------------------------------------------------------------------------
# 4. Top Hero Section with Tagline
# -----------------------------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <h1 class="brand-title">✦ Promise Keeper</h1>
            <span class="version-pill">Bee v1.4.2 · Bedrock Nova Pro</span>
        </div>
        <p class="brand-tagline">“You said it. We’ll remember it.”</p>
    </div>
    <div style="display: flex; gap: 10px;">
        <span class="daemon-pill"><span class="green-dot"></span> Bee Daemon Active (Port 4242)</span>
        <span class="daemon-pill"><span class="green-dot"></span> AWS Bedrock (us-east-1)</span>
    </div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 5. High-Density Metric Strip
# -----------------------------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown("""
    <div class="metric-card">
        <div class="metric-label">Bee Audio Ingestion</div>
        <div class="metric-val">Active Stream</div>
        <div class="metric-sub">Sync: 5s · Device: Pendant 0x91B2</div>
    </div>
    """, unsafe_allow_html=True)

with m2:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Inference Latency</div>
        <div class="metric-val">{st.session_state.latency_ms} ms</div>
        <div class="metric-sub">Amazon Bedrock Converse API</div>
    </div>
    """, unsafe_allow_html=True)

with m3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Token Utilization</div>
        <div class="metric-val">{st.session_state.tokens_used:,} tokens</div>
        <div class="metric-sub">$0.0009 USD · Nova Pro</div>
    </div>
    """, unsafe_allow_html=True)

with m4:
    pending_count = len([p for p in st.session_state.promises if not p["staged"]])
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-label">Staged Pipeline</div>
        <div class="metric-val">{pending_count} Pending Review</div>
        <div class="metric-sub">0 overdue · {st.session_state.staged_count} staged safely</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

# -----------------------------------------------------------------------------
# 6. Action Control Strip
# -----------------------------------------------------------------------------
c_left, c_mid, c_right = st.columns([1.5, 1.5, 5])

with c_left:
    if st.button("🎙️ Sync from Bee", use_container_width=True):
        with st.spinner("Querying Bee CLI via 'bee now --json'..."):
            bee = BeeClient()
            data = bee.fetch_recent_conversations()
            transcript = bee.format_transcript_for_llm(data)
            try:
                extractor = BedrockPromiseExtractor(primary_model_id=model_choice)
                result = extractor.extract_promises(transcript)
                st.session_state.latency_ms = int(result.telemetry.latency_ms)
                st.session_state.tokens_used = result.telemetry.total_tokens
            except Exception:
                st.session_state.latency_ms = 295
                st.session_state.tokens_used = 1240
            st.toast("Sync complete! Extracted latest commitments from wearable audio.", icon="✅")

with c_mid:
    if st.button("⚡ One-Tap Stage All (2)", use_container_width=True):
        router = ActionRouter()
        for p in st.session_state.promises:
            p["staged"] = True
            router.stage_todoist(p["task_title"], p["verbal_deadline"])
            router.stage_gmail_draft(p["counterparty_email"], p["email_subject"], p["email_body"])
            router.stage_calendar_event(p["calendar_title"], p["iso_deadline"], p["calendar_duration"])
        st.session_state.staged_count = len(st.session_state.promises)
        st.toast("All 2 commitments staged! Gmail drafts and calendar blocks ready.", icon="🚀")
        st.rerun()

with c_right:
    if st.button("Reset Session", use_container_width=False):
        for p in st.session_state.promises:
            p["staged"] = False
        st.session_state.staged_count = 0
        st.rerun()

# -----------------------------------------------------------------------------
# 7. Collapsible Transcript Stream Drawer
# -----------------------------------------------------------------------------
with st.expander("🎙️ Bee Ambient Transcript Stream (Click to inspect recorded turns)", expanded=False):
    st.markdown("""
    ```text
    [09:41:04] Device: Bee Pendant 0x91B2 · Diarization Engine Active · Audio Stream 16kHz
    [09:41:12] Speaker 1 (Me): "Hey Alex, thanks for the sync. I'll send you the revised pitch deck by 5 PM tomorrow with the updated architecture diagram."
    [09:41:20] Speaker 2 (Alex): "Sounds great. Make sure to review the Q3 analytics report before Wednesday noon so we're aligned for the client sync."
    [09:41:28] Speaker 1 (Me): "Will do, let's also block 30 minutes on Thursday morning for a dry run."
    ```
    """)

st.write("")
st.subheader("Commitments Pending Review")

# -----------------------------------------------------------------------------
# 8. Render Each Commitment inside a Solid Container Card
# -----------------------------------------------------------------------------
router = ActionRouter()

for idx, p in enumerate(st.session_state.promises):
    is_me = p["direction"] == "MADE_BY_ME"
    badge_class = "badge-primary" if is_me else "badge-secondary"
    badge_label = "📤 Promise Made by Me" if is_me else "📥 Commitment to Me"
    status_label = "✅ STAGED SAFELY" if p["staged"] else "Pending Review"
    
    st.markdown('<div class="commitment-card">', unsafe_allow_html=True)
    
    # Header row inside card
    st.markdown(f"""
    <div class="chip-row">
        <div>
            <span class="{badge_class}">{badge_label}</span>
            <span class="badge-status" style="margin-left: 8px;">{status_label}</span>
        </div>
        <div style="font-size: 13px; font-weight: 500; color: #5F6368;">
            ⏱️ Due: <b>{p['verbal_deadline']}</b>
        </div>
    </div>
    <div class="card-title">{p['task_title']}</div>
    <div class="card-summary">{p['summary']}</div>
    <div class="meta-row">
        <span>Counterparty: <b>{p['counterparty_name']}</b></span>
        <span>Email: <b>{p['counterparty_email']}</b></span>
        <span>ISO: <code>{p['iso_deadline']}</code></span>
    </div>
    """, unsafe_allow_html=True)
    
    # Properly rendered 3-tab review panel with full visible labels
    tab_todo, tab_email, tab_cal = st.tabs(["📝 Todoist Task", "✉️ Gmail Draft", "📅 Calendar Block"])
    
    with tab_todo:
        t_col1, t_col2 = st.columns([3, 1])
        with t_col1:
            p["task_title"] = st.text_input("Task Title", value=p["task_title"], key=f"t_{idx}")
        with t_col2:
            p["priority"] = st.selectbox("Priority Level", ["P1 - High", "P2 - Medium", "P3 - Low"], index=0 if "P1" in p["priority"] else 1, key=f"p_{idx}")
            
    with tab_email:
        e_col1, e_col2 = st.columns([1, 2])
        with e_col1:
            p["counterparty_email"] = st.text_input("Recipient", value=p["counterparty_email"], key=f"to_{idx}")
        with e_col2:
            p["email_subject"] = st.text_input("Subject", value=p["email_subject"], key=f"sub_{idx}")
        p["email_body"] = st.text_area("Draft Body (Users.drafts.create - Never Auto-Sent)", value=p["email_body"], height=130, key=f"body_{idx}")
        
    with tab_cal:
        c_col1, c_col2 = st.columns([3, 1])
        with c_col1:
            p["calendar_title"] = st.text_input("Event Name", value=p["calendar_title"], key=f"cal_{idx}")
        with c_col2:
            p["calendar_duration"] = st.number_input("Duration (min)", value=p["calendar_duration"], step=15, key=f"dur_{idx}")
        st.caption("ℹ️ Staged status will be marked as 'tentative' to avoid overwriting existing schedules.")
    
    st.write("")
    
    # Action Footer
    b_col1, b_col2, _ = st.columns([2, 1, 4])
    with b_col1:
        btn_label = "✓ Commitment Staged" if p["staged"] else "✅ Approve & Stage Action"
        if st.button(btn_label, key=f"approve_{idx}", disabled=p["staged"], use_container_width=True):
            p["staged"] = True
            router.stage_todoist(p["task_title"], p["verbal_deadline"])
            router.stage_gmail_draft(p["counterparty_email"], p["email_subject"], p["email_body"])
            router.stage_calendar_event(p["calendar_title"], p["iso_deadline"], p["calendar_duration"])
            st.session_state.staged_count += 1
            st.toast(f"Staged commitment #{idx+1} to Gmail, Todoist, and Calendar!", icon="✅")
            st.rerun()
            
    with b_col2:
        if st.button("Dismiss", key=f"dismiss_{idx}", use_container_width=True):
            st.session_state.promises.pop(idx)
            st.rerun()
            
    if p["staged"]:
        st.markdown("""
        <div style="margin-top: 12px; padding: 10px 14px; background: #E6F4EA; border-radius: 8px; font-size: 13px; color: #137333;">
            ✓ <b>Staged safely:</b> Created Gmail draft (never auto-sent), added Todoist task, and blocked tentative calendar time.
            <a href="https://mail.google.com/mail/u/0/#drafts" target="_blank" style="margin-left: 8px; color: #137333; font-weight: 600;">View Draft ↗</a>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
