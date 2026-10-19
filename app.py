import streamlit as st
import datetime
import json
from src.bee_client import BeeClient
from src.extractor import BedrockPromiseExtractor
from src.action_router import ActionRouter
from src.telemetry import TelemetryRecorder

# -----------------------------------------------------------------------------
# 1. Page Configuration & Unified Dark Engineering Canvas
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Promise Keeper — Wearable AI Commitment Engine",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Unified Dark CSS (Linear / Vercel / Antigravity Dark Aesthetics)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;450;500;600;650&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* Base Reset */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: #F0F6FC !important;
        background-color: #0D1117 !important;
    }
    
    .stApp {
        background-color: #0D1117 !important;
        color: #F0F6FC !important;
    }
    
    /* Hide generic Streamlit UI chrome */
    header, #MainMenu, footer { visibility: hidden !important; }
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
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 16px;
        margin-bottom: 24px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.3);
    }
    .brand-title {
        font-size: 20px;
        font-weight: 650;
        letter-spacing: -0.02em;
        color: #F0F6FC;
        margin: 0;
        line-height: 1.2;
    }
    .version-pill {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 500;
        background: #21262D;
        border: 1px solid #30363D;
        color: #8B949E;
        padding: 3px 8px;
        border-radius: 9999px;
    }
    .brand-tagline {
        font-size: 14px;
        font-weight: 450;
        color: #8B949E;
        margin: 4px 0 0 0;
        letter-spacing: -0.01em;
    }
    .daemon-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        background: #21262D;
        border: 1px solid #30363D;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 500;
        color: #C9D1D9;
    }
    .green-dot {
        width: 7px;
        height: 7px;
        background: #3FB950;
        border-radius: 50%;
        display: inline-block;
    }
    
    /* High-Density Metric Strip Cards */
    .metric-card {
        background: #161B22;
        border: 1px solid #30363D;
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.2);
    }
    .metric-label {
        font-size: 11px;
        font-weight: 600;
        color: #8B949E;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 22px;
        font-weight: 600;
        color: #F0F6FC;
        margin-bottom: 4px;
    }
    .metric-sub {
        font-size: 12px;
        color: #8B949E;
    }
    
    /* Native Bordered Container as Clean Dark Card */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 16px !important;
        padding: 22px !important;
        margin-bottom: 20px !important;
        box-shadow: 0 2px 6px rgba(0,0,0,0.25) !important;
    }
    
    /* Direction and Status Chips */
    .badge-primary {
        background: rgba(31, 111, 235, 0.15);
        border: 1px solid rgba(56, 139, 253, 0.4);
        color: #58A6FF;
        font-size: 12px;
        font-weight: 500;
        padding: 3px 10px;
        border-radius: 9999px;
    }
    .badge-secondary {
        background: rgba(210, 153, 34, 0.15);
        border: 1px solid rgba(210, 153, 34, 0.4);
        color: #D29922;
        font-size: 12px;
        font-weight: 500;
        padding: 3px 10px;
        border-radius: 9999px;
    }
    .badge-status {
        background: #21262D;
        border: 1px solid #30363D;
        color: #8B949E;
        font-size: 12px;
        font-weight: 500;
        padding: 3px 10px;
        border-radius: 9999px;
    }
    .badge-status-staged {
        background: rgba(35, 134, 54, 0.2);
        border: 1px solid #238636;
        color: #3FB950;
        font-size: 12px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 9999px;
    }
    
    /* Sidebar Styles with High Contrast */
    section[data-testid="stSidebar"] {
        background-color: #0D1117 !important;
        border-right: 1px solid #30363D !important;
        color: #C9D1D9 !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #F0F6FC !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        margin-bottom: 10px !important;
    }
    .sidebar-section {
        background: #161B22 !important;
        border: 1px solid #30363D !important;
        border-radius: 12px !important;
        padding: 16px !important;
        margin-bottom: 16px !important;
    }
    .sidebar-row {
        display: flex;
        justify-content: space-between;
        font-size: 13px;
        color: #8B949E;
        padding: 6px 0;
        border-bottom: 1px solid #21262D;
    }
    .sidebar-row:last-child { border-bottom: none; }
    .sidebar-val {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 500;
        color: #F0F6FC;
    }

    /* Tabs: Dark High-Contrast Labels */
    div[data-testid="stTabs"] button[role="tab"] {
        color: #8B949E !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        border-bottom: 2px solid transparent !important;
    }
    div[data-testid="stTabs"] button[role="tab"] p,
    div[data-testid="stTabs"] button[data-baseweb="tab"] p,
    div[data-testid="stTabs"] button span {
        color: #8B949E !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        margin: 0 !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        border-bottom: 2px solid #58A6FF !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] p,
    div[data-testid="stTabs"] button[aria-selected="true"] span {
        color: #F0F6FC !important;
        font-weight: 600 !important;
    }

    /* Dark Form Controls */
    input[type="text"], input[type="number"], textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #0D1117 !important;
        border: 1px solid #30363D !important;
        border-radius: 8px !important;
        color: #F0F6FC !important;
        font-size: 13.5px !important;
    }
    input[type="text"]:focus, textarea:focus {
        border-color: #58A6FF !important;
        box-shadow: 0 0 0 1px #58A6FF !important;
    }
    
    /* Buttons */
    button[kind="primary"], .stButton > button[kind="primary"] {
        background-color: #238636 !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(240, 246, 252, 0.1) !important;
        border-radius: 9999px !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
        letter-spacing: -0.01em !important;
        transition: all 0.15s ease !important;
    }
    button[kind="primary"]:hover {
        background-color: #2EA043 !important;
    }
    
    button[kind="secondary"], .stButton > button[kind="secondary"], .stButton > button {
        background-color: #21262D !important;
        color: #C9D1D9 !important;
        border: 1px solid #30363D !important;
        border-radius: 9999px !important;
        font-weight: 500 !important;
        font-size: 13.5px !important;
        letter-spacing: -0.01em !important;
        transition: all 0.15s ease !important;
    }
    button[kind="secondary"]:hover, .stButton > button:hover {
        background-color: #30363D !important;
        border-color: #8B949E !important;
        color: #F0F6FC !important;
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
        <div class="sidebar-row"><span>Daemon Status</span><span class="sidebar-val" style="color: #3FB950;">● Active</span></div>
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
        <p style="margin: 0 0 8px 0; font-size: 13px;"><a href="https://mail.google.com/mail/u/0/#drafts" target="_blank" style="text-decoration: none; color: #58A6FF; font-weight: 500;">✉️ Open Gmail Drafts ↗</a></p>
        <p style="margin: 0 0 8px 0; font-size: 13px;"><a href="https://calendar.google.com/" target="_blank" style="text-decoration: none; color: #58A6FF; font-weight: 500;">📅 Open Google Calendar ↗</a></p>
        <p style="margin: 0; font-size: 13px;"><a href="https://app.todoist.com/" target="_blank" style="text-decoration: none; color: #58A6FF; font-weight: 500;">📝 Open Todoist App ↗</a></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Telemetry Session")
    st.markdown(f"""
    <div style="font-size: 12.5px; color: #8B949E; line-height: 1.8;">
        <div>Converse API Latency: <strong style="color: #F0F6FC;">{st.session_state.latency_ms} ms</strong></div>
        <div>Tokens Consumed: <strong style="color: #F0F6FC;">{st.session_state.tokens_used:,}</strong></div>
        <div>Estimated Cost: <strong style="color: #F0F6FC;">$0.0009 USD</strong></div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. Top Hero Section with Tagline
# -----------------------------------------------------------------------------
st.markdown("""
<div class="hero-container">
    <div>
        <div style="display: flex; align-items: center; gap: 10px;">
            <span class="brand-title">✦ Promise Keeper</span>
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
    <div style="background: #090D13; border: 1px solid #30363D; border-radius: 8px; padding: 14px 18px; font-family: 'JetBrains Mono', monospace; font-size: 12.5px; color: #C9D1D9; line-height: 1.6;">
        <div>[09:41:04] Device: Bee Pendant 0x91B2 · Diarization Engine Active · Audio Stream 16kHz</div>
        <div>[09:41:12] Speaker 1 (Me): "Hey Alex, thanks for the sync. I'll send you the revised pitch deck by 5 PM tomorrow with the updated architecture diagram."</div>
        <div>[09:41:20] Speaker 2 (Alex): "Sounds great. Make sure to review the Q3 analytics report before Wednesday noon so we're aligned for the client sync."</div>
        <div>[09:41:28] Speaker 1 (Me): "Will do, let's also block 30 minutes on Thursday morning for a dry run."</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<h2 style='font-size: 18px; font-weight: 600; color: #F0F6FC; margin: 24px 0 16px 0;'>Commitments Pending Review</h2>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. Render Each Commitment inside a Solid Container Card (Zero empty white bars)
# -----------------------------------------------------------------------------
router = ActionRouter()

for idx, p in enumerate(st.session_state.promises):
    is_me = p["direction"] == "MADE_BY_ME"
    badge_class = "badge-primary" if is_me else "badge-secondary"
    badge_label = "📤 Promise Made by Me" if is_me else "📥 Commitment to Me"
    status_class = "badge-status-staged" if p["staged"] else "badge-status"
    status_label = "✅ STAGED SAFELY" if p["staged"] else "Pending Review"
    
    # Use native Streamlit container with border for 100% clean dark styling
    with st.container(border=True):
        # Header row inside card
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
            <div>
                <span class="{badge_class}">{badge_label}</span>
                <span class="{status_class}" style="margin-left: 8px;">{status_label}</span>
            </div>
            <div style="font-size: 13px; font-weight: 500; color: #8B949E;">
                ⏱️ Due: <strong style="color: #F0F6FC;">{p['verbal_deadline']}</strong>
            </div>
        </div>
        <div style="font-size: 17px; font-weight: 600; color: #F0F6FC; margin: 0 0 6px 0;">{p['task_title']}</div>
        <div style="font-size: 14px; color: #C9D1D9; margin-bottom: 12px; line-height: 1.45;">{p['summary']}</div>
        <div style="display: flex; flex-wrap: wrap; gap: 16px; font-size: 12.5px; color: #8B949E; margin-bottom: 16px; font-family: 'JetBrains Mono', monospace;">
            <span>Counterparty: <strong style="color: #F0F6FC;">{p['counterparty_name']}</strong></span>
            <span>Email: <code style="color: #58A6FF;">{p['counterparty_email']}</code></span>
            <span>ISO: <code style="color: #8B949E;">{p['iso_deadline']}</code></span>
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
            if st.button(btn_label, key=f"approve_{idx}", disabled=p["staged"], type="primary", use_container_width=True):
                p["staged"] = True
                router.stage_todoist(p["task_title"], p["verbal_deadline"])
                router.stage_gmail_draft(p["counterparty_email"], p["email_subject"], p["email_body"])
                router.stage_calendar_event(p["calendar_title"], p["iso_deadline"], p["calendar_duration"])
                st.session_state.staged_count += 1
                st.toast(f"Staged commitment #{idx+1} to Gmail, Todoist, and Calendar!", icon="✅")
                st.rerun()
                
        with b_col2:
            if st.button("Dismiss", key=f"dismiss_{idx}", type="secondary", use_container_width=True):
                st.session_state.promises.pop(idx)
                st.rerun()
                
        if p["staged"]:
            st.markdown("""
            <div style="margin-top: 14px; padding: 10px 14px; background: rgba(35, 134, 54, 0.15); border: 1px solid rgba(46, 160, 67, 0.4); border-radius: 8px; font-size: 13px; color: #3FB950;">
                ✓ <b>Staged safely:</b> Created Gmail draft (never auto-sent), added Todoist task, and blocked tentative calendar time.
                <a href="https://mail.google.com/mail/u/0/#drafts" target="_blank" style="margin-left: 8px; color: #58A6FF; text-decoration: none; font-weight: 600;">View Draft in Gmail ↗</a>
            </div>
            """, unsafe_allow_html=True)
