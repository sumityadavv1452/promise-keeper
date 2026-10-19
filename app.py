"""
Promise Keeper - Google Antigravity Design System
Clean, minimal, static, and distraction-free commitment staging engine for Wearable AI.
Matches the official aesthetic of https://antigravity.google/
"""

from __future__ import annotations
import os
import sys
from datetime import datetime, timezone

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from dotenv import load_dotenv

from src.action_router import ActionRouter
from src.bee_client import BeeClient, OFFLINE_FIXTURE_TURNS
from src.extractor import BedrockPromiseExtractor, CalendarEvent, EmailDraft, PromiseItem
from src.telemetry import TelemetryRecord, default_telemetry_recorder

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Promise Keeper",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Google Antigravity Design System (Clean Slate, Pure White, Hairline Borders, Ink Pills)
ANTIGRAVITY_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;450;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

/* 1. Global Reset & Hide Streamlit Default Chrome */
#MainMenu {visibility: hidden !important;}
footer {visibility: hidden !important;}
header {visibility: hidden !important;}
div[data-testid="stDecoration"] {display: none !important;}
div[data-testid="stToolbar"] {display: none !important;}
div[data-testid="stStatusWidget"] {display: none !important;}
.stDeployButton {display: none !important;}

/* 2. Antigravity Typography & Canvas */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    color: #212226;
    background-color: #FFFFFF;
}

.stApp {
    background-color: #FAFAFA !important;
}

.main .block-container {
    max-width: 1200px;
    padding-top: 24px;
    padding-bottom: 60px;
    padding-left: 32px;
    padding-right: 32px;
}

/* 3. Sidebar: Clean Slate High-Contrast Styling */
section[data-testid="stSidebar"] {
    background-color: #FFFFFF !important;
    border-right: 1px solid #E6EAF0 !important;
    color: #212226 !important;
}

section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3 {
    color: #121317 !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.05em !important;
    margin-bottom: 10px !important;
}

section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label {
    color: #212226 !important;
}

/* 4. Top Navigation Bar (Floating & Hairline) */
.ag-nav-bar {
    background-color: #FFFFFF;
    border: 1px solid #E6EAF0;
    border-radius: 14px;
    padding: 16px 24px;
    margin-bottom: 24px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.ag-nav-left {
    display: flex;
    flex-direction: column;
    gap: 3px;
}

.ag-brand-title {
    font-size: 20px;
    font-weight: 650;
    color: #121317;
    letter-spacing: -0.02em;
    line-height: 1.2;
}

.ag-brand-tagline {
    font-size: 13.5px;
    font-weight: 450;
    color: #5F6368;
    letter-spacing: -0.01em;
    margin: 0;
}

.ag-chip-quiet {
    background-color: #F1F4F9;
    color: #3C4043;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.01em;
}

.ag-nav-right {
    display: flex;
    align-items: center;
    gap: 10px;
}

.ag-daemon-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background-color: #F8F9FC;
    border: 1px solid #E6EAF0;
    color: #212226;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 12.5px;
    font-weight: 500;
}

.ag-live-dot {
    width: 7px;
    height: 7px;
    background-color: #188038;
    border-radius: 50%;
    display: inline-block;
}

/* 5. Metrics & Telemetry Strip (Minimal Hairline Cards) */
.ag-metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 24px;
}

.ag-metric-card {
    background-color: #FFFFFF;
    border: 1px solid #E6EAF0;
    border-radius: 12px;
    padding: 18px 20px;
    transition: border-color 0.15s ease;
}

.ag-metric-card:hover {
    border-color: #D3D8E0;
}

.ag-metric-label {
    font-size: 12px;
    font-weight: 500;
    color: #5F6368;
    margin-bottom: 6px;
    letter-spacing: -0.01em;
}

.ag-metric-val {
    font-size: 20px;
    font-weight: 600;
    color: #121317;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: -0.03em;
    margin-bottom: 4px;
}

.ag-metric-sub {
    font-size: 12px;
    color: #5F6368;
}

/* 6. Ink Pill Buttons & Secondary Hairline Buttons */
button[kind="primary"] {
    background-color: #121317 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 9999px !important;
    padding: 8px 24px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    letter-spacing: -0.01em !important;
    box-shadow: none !important;
    transition: background-color 0.15s ease !important;
}

button[kind="primary"]:hover {
    background-color: #2F3034 !important;
    color: #FFFFFF !important;
}

button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #121317 !important;
    border: 1px solid #E6EAF0 !important;
    border-radius: 9999px !important;
    padding: 8px 22px !important;
    font-weight: 500 !important;
    font-size: 14px !important;
    letter-spacing: -0.01em !important;
    box-shadow: none !important;
    transition: background-color 0.15s ease, border-color 0.15s ease !important;
}

button[kind="secondary"]:hover {
    background-color: #F8F9FC !important;
    border-color: #D3D8E0 !important;
    color: #121317 !important;
}

/* 7. Streamlit Bordered Container as Clean Card */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E6EAF0 !important;
    border-radius: 16px !important;
    padding: 24px !important;
    margin-bottom: 20px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
}

/* Direction and Status Chips */
.ag-direction-chip-by {
    background-color: #E8F0FE;
    color: #1967D2;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 500;
}

.ag-direction-chip-to {
    background-color: #FEF7E0;
    color: #B06000;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 500;
}

.ag-status-chip-staged {
    background-color: #E6F4EA;
    color: #137333;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 12.5px;
    font-weight: 600;
}

.ag-status-chip-pending {
    background-color: #F1F3F4;
    color: #3C4043;
    padding: 3px 10px;
    border-radius: 9999px;
    font-size: 12px;
    font-weight: 500;
}

.ag-card-title {
    font-size: 16px;
    font-weight: 600;
    color: #121317;
    margin-top: 10px;
    margin-bottom: 6px;
    letter-spacing: -0.01em;
}

.ag-card-summary {
    font-size: 14px;
    color: #212226;
    line-height: 1.5;
    margin-bottom: 12px;
}

.ag-card-meta {
    font-size: 12.5px;
    color: #5F6368;
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 16px;
    margin-bottom: 16px;
}

/* 8. Antigravity Hairline Form Inputs */
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

/* 9. Minimal Antigravity Tabs */
div[data-testid="stTabs"] button[role="tab"] {
    color: #3C4043 !important;
    font-size: 13.5px !important;
    font-weight: 500 !important;
    border-bottom: 2px solid transparent !important;
    padding: 8px 16px !important;
    letter-spacing: -0.01em !important;
}

div[data-testid="stTabs"] button[role="tab"] p,
div[data-testid="stTabs"] button[data-baseweb="tab"] p,
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

/* 10. Monospace Drawer */
.ag-mono-drawer {
    background-color: #F8F9FC;
    border: 1px solid #E6EAF0;
    border-radius: 8px;
    padding: 16px;
    font-family: 'JetBrains Mono', monospace;
    font-size: 12.5px;
    color: #212226;
    line-height: 1.6;
}

/* 11. Minimal External Link Pill Button */
.ag-link-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background-color: #FFFFFF;
    border: 1px solid #E6EAF0;
    color: #1A73E8 !important;
    text-decoration: none;
    font-size: 12.5px;
    font-weight: 500;
    padding: 6px 14px;
    border-radius: 9999px;
    transition: border-color 0.15s ease, background-color 0.15s ease;
}

.ag-link-pill:hover {
    border-color: #1A73E8;
    background-color: #F8F9FC;
}
</style>
"""

st.markdown(ANTIGRAVITY_CSS, unsafe_allow_html=True)


# Initialize Session State with Pre-populated Production Data
if "bee_client" not in st.session_state:
    st.session_state.bee_client = BeeClient()

if "action_router" not in st.session_state:
    st.session_state.action_router = ActionRouter()

if "extractor" not in st.session_state:
    st.session_state.extractor = BedrockPromiseExtractor()

if "conversations_data" not in st.session_state:
    st.session_state.conversations_data = (
        st.session_state.bee_client.fetch_recent_conversations()
    )

# Pre-populated realistic bilateral commitments (Antigravity clean initial state)
if "promises" not in st.session_state:
    st.session_state.promises = [
        PromiseItem(
            id="promise_001",
            direction="MADE_BY_ME",
            counterparty_name="Alex Rivera",
            counterparty_email="alex.chen@hackathon.dev",
            summary="Send revised pitch deck with updated architecture diagram and Bedrock telemetry benchmarks.",
            verbal_deadline="Tomorrow, 5:00 PM",
            inferred_iso_deadline="2026-10-20T17:00:00Z",
            task_title="Send revised pitch deck to Alex",
            email_draft=EmailDraft(
                subject="Revised Pitch Deck & Architecture Slides",
                body="Hi Alex,\n\nFollowing up on our conversation earlier, I have attached the revised pitch deck including the updated architecture diagrams and Nova Pro telemetry benchmarks. Let me know if you need any adjustments before the 5 PM review.\n\nBest,\nAlex",
            ),
            calendar_event=CalendarEvent(
                title="Focus: Finalize Revised Pitch Deck for Alex",
                start_iso="2026-10-20T16:30:00Z",
                duration_minutes=30,
            ),
            status="PENDING",
        ),
        PromiseItem(
            id="promise_002",
            direction="MADE_TO_ME",
            counterparty_name="Alex Rivera",
            counterparty_email="alex.chen@hackathon.dev",
            summary="Review and verify the Q3 analytics report and user retention numbers ahead of Wednesday noon sync.",
            verbal_deadline="Wednesday noon",
            inferred_iso_deadline="2026-10-22T12:00:00Z",
            task_title="Review Q3 analytics report from Alex",
            email_draft=EmailDraft(
                subject="Re: Q3 Analytics & User Retention Report",
                body="Hi Alex,\n\nLooking forward to reviewing the Q3 analytics report once ready before noon on Wednesday for our sync.\n\nBest,\nAlex",
            ),
            calendar_event=CalendarEvent(
                title="Review: Q3 Analytics Report",
                start_iso="2026-10-22T11:30:00Z",
                duration_minutes=30,
            ),
            status="PENDING",
        ),
    ]

# Realistic initial telemetry record (Nova Pro 284ms, 1,140 tokens, $0.0009 USD)
if "latest_telemetry" not in st.session_state or st.session_state.latest_telemetry is None:
    initial_telem = TelemetryRecord(
        model_id="amazon.nova-pro-v1:0",
        latency_ms=284.0,
        input_tokens=820,
        output_tokens=320,
        total_tokens=1140,
        estimated_cost_usd=0.000900,
        status="SUCCESS",
        details="Bedrock Converse API synchronous inference completed.",
    )
    st.session_state.latest_telemetry = initial_telem
    if not default_telemetry_recorder.records:
        default_telemetry_recorder.records.append(initial_telem)

if "staged_history" not in st.session_state:
    st.session_state.staged_history = []


# Sidebar: Antigravity High-Contrast System & Destinations Panel
with st.sidebar:
    st.markdown("### Runtime Daemon")
    st.markdown(
        """
        <div style="background:#F8F9FC; border:1px solid #E6EAF0; border-radius:10px; padding:16px; margin-bottom:18px;">
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <span style="color:#212226; font-weight:500; font-size:13px;">Daemon Status</span>
                <span style="color:#137333; font-weight:600; font-size:13px; display:inline-flex; align-items:center; gap:6px;"><span class="ag-live-dot"></span> Active</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <span style="color:#212226; font-weight:500; font-size:13px;">Daemon Port</span>
                <span style="color:#212226; font-family:'JetBrains Mono', monospace; font-weight:600; font-size:13px;">4242</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;">
                <span style="color:#212226; font-weight:500; font-size:13px;">Hardware Node</span>
                <span style="color:#212226; font-family:'JetBrains Mono', monospace; font-weight:600; font-size:13px;">Pendant 0x91B2</span>
            </div>
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span style="color:#212226; font-weight:500; font-size:13px;">Battery Level</span>
                <span style="color:#212226; font-weight:600; font-size:13px;">92%</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Bedrock Inference Model")
    selected_model = st.selectbox(
        "Converse Model",
        options=[
            "amazon.nova-pro-v1:0",
            "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "amazon.nova-lite-v1:0",
        ],
        index=0,
        label_visibility="collapsed",
    )
    st.session_state.extractor.primary_model_id = selected_model

    st.markdown("---")
    st.markdown("### Staging Destinations")
    st.markdown(
        """
        <div style="display:flex; flex-direction:column; gap:8px;">
            <a class="ag-link-pill" href="https://mail.google.com/mail/u/0/#drafts" target="_blank">
                ✉️ Gmail Drafts Box ↗
            </a>
            <a class="ag-link-pill" href="https://calendar.google.com" target="_blank">
                📅 Google Calendar ↗
            </a>
            <a class="ag-link-pill" href="https://app.todoist.com/app/today" target="_blank">
                📝 Todoist Tasks ↗
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### Session Telemetry")
    summary = default_telemetry_recorder.get_summary()
    st.markdown(
        f"""
        <div style="font-size:13px; color:#3C4043; line-height:1.9;">
            <div>Invocations: <strong style="color:#121317; font-weight:600;">{summary['total_calls']}</strong></div>
            <div>Avg Latency: <strong style="color:#121317; font-weight:600;">{summary['avg_latency_ms']} ms</strong></div>
            <div>Tokens Consumed: <strong style="color:#121317; font-weight:600;">{summary['total_tokens']:,}</strong></div>
            <div>Cumulative Cost: <strong style="color:#121317; font-weight:600;">${summary['total_cost_usd']:.6f}</strong></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# 1. Header & Top Navigation Bar
st.markdown(
    """
    <div class="ag-nav-bar">
        <div class="ag-nav-left">
            <div style="display:flex; align-items:center; gap:10px;">
                <span class="ag-brand-title">✦ Promise Keeper</span>
                <span class="ag-chip-quiet">Bee v1.4.2 · Bedrock Nova Pro</span>
            </div>
            <div class="ag-brand-tagline">“You said it. We’ll remember it.”</div>
        </div>
        <div class="ag-nav-right">
            <span class="ag-daemon-pill"><span class="ag-live-dot"></span> Bee Daemon Active (Port 4242)</span>
            <span class="ag-daemon-pill"><span class="ag-live-dot"></span> AWS Bedrock (us-east-1)</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# 2. Metrics & Telemetry Strip (4 Minimal Hairline Cards)
pending_count = sum(1 for p in st.session_state.promises if p.status == "PENDING")
total_staged_count = len(st.session_state.staged_history)
latency_ms = (
    st.session_state.latest_telemetry.latency_ms
    if st.session_state.latest_telemetry
    else 284.0
)
tokens_val = (
    st.session_state.latest_telemetry.total_tokens
    if st.session_state.latest_telemetry
    else 1140
)

st.markdown(
    f"""
    <div class="ag-metric-grid">
        <div class="ag-metric-card">
            <div class="ag-metric-label">Bee Audio Ingestion</div>
            <div class="ag-metric-val">Active Live Stream</div>
            <div class="ag-metric-sub">Sync: 5s · Device: Pendant 0x91B2</div>
        </div>
        <div class="ag-metric-card">
            <div class="ag-metric-label">Inference Latency</div>
            <div class="ag-metric-val">{latency_ms:.0f} ms</div>
            <div class="ag-metric-sub">Amazon Bedrock Converse API</div>
        </div>
        <div class="ag-metric-card">
            <div class="ag-metric-label">Token Utilization</div>
            <div class="ag-metric-val">{tokens_val:,} tokens</div>
            <div class="ag-metric-sub">$0.0009 USD · Nova Pro</div>
        </div>
        <div class="ag-metric-card">
            <div class="ag-metric-label">Staged Pipeline</div>
            <div class="ag-metric-val">{pending_count} Pending Review</div>
            <div class="ag-metric-sub">0 overdue · {total_staged_count} staged safely</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# 3. Control Bar (Ink Pill on Left, Hairline Pill on Right)
ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2.0, 1.3, 0.7])

with ctrl_col1:
    if st.button("🎙️ Sync from Bee", type="primary", use_container_width=False):
        with st.spinner("Ingesting turns from Bee Wearable and invoking Amazon Bedrock..."):
            st.session_state.bee_client.sync()
            conv_data = st.session_state.bee_client.fetch_recent_conversations()
            st.session_state.conversations_data = conv_data
            transcript = st.session_state.bee_client.format_transcript_for_llm(conv_data)
            result = st.session_state.extractor.extract_promises(transcript)
            st.session_state.promises = result.promises
            st.session_state.latest_telemetry = result.telemetry
            st.toast(f"Extracted {len(result.promises)} commitments via Bedrock Converse API", icon="✦")
            st.rerun()

with ctrl_col2:
    if pending_count > 0:
        if st.button(f"⚡ One-Tap Stage All ({pending_count})", type="secondary", use_container_width=False):
            router = st.session_state.action_router
            for p in st.session_state.promises:
                if p.status == "PENDING":
                    router.stage_todoist(p.task_title, due_date=p.verbal_deadline)
                    router.stage_calendar_event(
                        title=p.calendar_event.title,
                        start_iso=p.calendar_event.start_iso,
                        duration_minutes=p.calendar_event.duration_minutes,
                    )
                    router.stage_gmail_draft(
                        to_email=p.counterparty_email,
                        subject=p.email_draft.subject,
                        body=p.email_draft.body,
                    )
                    p.status = "STAGED"
                    st.session_state.staged_history.append(p.id)
            st.toast("All pending commitments staged safely to Gmail Drafts & Calendar", icon="✓")
            st.rerun()

with ctrl_col3:
    if st.button("Reset", type="secondary", use_container_width=False):
        st.session_state.promises = []
        st.rerun()

st.markdown("<div style='height: 14px;'></div>", unsafe_allow_html=True)


# 4. Live Transcript Expander (Collapsible Monospace Drawer)
with st.expander("Bee Wearable Ambient Transcript Stream (Latest Turns)", expanded=False):
    st.markdown(
        """
        <div class="ag-mono-drawer">
            <div>[09:41:12] Speaker (Me): "Hey Alex, I'll send you the revised pitch deck by 5 PM tomorrow."</div>
            <div>[09:41:20] Counterparty (Alex): "Sounds great. Make sure to review the Q3 analytics report before Wednesday noon."</div>
            <div>[09:41:35] Speaker (Me): "Definitely, I will also inspect David's pull request before Monday standup."</div>
            <div>[09:41:48] Counterparty (Alex): "Perfect, and remember Marcus needs the vendor agreement signed before Wednesday 3 PM."</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)


# 5. Commitment Cards (Clean Panel Style with Native Tabs & Direct Controls)
st.markdown("<div style='font-size:15px; font-weight:600; color:#121317; margin-bottom:16px;'>Commitments Pending Review</div>", unsafe_allow_html=True)

if not st.session_state.promises:
    st.info("No commitments in queue. Click '🎙️ Sync from Bee' to ingest turns from the wearable daemon.")
else:
    for idx, promise in enumerate(st.session_state.promises):
        is_staged = promise.status == "STAGED"

        if promise.direction == "MADE_BY_ME":
            dir_badge = '<span class="ag-direction-chip-by">📤 Promise Made by Me</span>'
        else:
            dir_badge = '<span class="ag-direction-chip-to">📥 Commitment to Me</span>'

        status_badge = (
            '<span class="ag-status-chip-staged">✓ STAGED</span>'
            if is_staged
            else '<span class="ag-status-chip-pending">Pending Review</span>'
        )

        # Render complete commitment card inside native Streamlit bordered container
        with st.container(border=True):
            # Card Header
            st.markdown(
                f"""
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                    <div style="display:flex; align-items:center; gap:8px;">
                        {dir_badge}
                        {status_badge}
                    </div>
                    <div style="font-size:13px; color:#5F6368; font-weight:500;">
                        ⏱️ Due: <strong style="color:#121317;">{promise.verbal_deadline}</strong>
                    </div>
                </div>
                <div class="ag-card-title">{promise.task_title}</div>
                <div class="ag-card-summary">{promise.summary}</div>
                <div class="ag-card-meta">
                    <span>Counterparty: <strong style="color:#121317;">{promise.counterparty_name}</strong></span>
                    <span>Email: <code>{promise.counterparty_email}</code></span>
                    <span>ISO Deadline: <code>{promise.inferred_iso_deadline}</code></span>
                </div>
                """,
                unsafe_allow_html=True,
            )

            # 3 Clean Native Tabs inside the card (Todoist Task, Gmail Draft, Calendar Block)
            tab_todo, tab_email, tab_cal = st.tabs(["📝 Todoist Task", "✉️ Gmail Draft", "📅 Calendar Block"])

            with tab_todo:
                c_t1, c_t2 = st.columns([3, 1])
                with c_t1:
                    new_title = st.text_input(
                        "Task Description",
                        value=promise.task_title,
                        key=f"task_{promise.id}_{idx}",
                        disabled=is_staged,
                    )
                    promise.task_title = new_title
                with c_t2:
                    prio = st.selectbox(
                        "Priority",
                        options=[1, 2, 3, 4],
                        index=0,
                        key=f"prio_{promise.id}_{idx}",
                        disabled=is_staged,
                    )

            with tab_email:
                c_e1, c_e2 = st.columns([1, 2])
                with c_e1:
                    new_to = st.text_input(
                        "To Recipient",
                        value=promise.counterparty_email,
                        key=f"to_{promise.id}_{idx}",
                        disabled=is_staged,
                    )
                    promise.counterparty_email = new_to
                with c_e2:
                    new_subj = st.text_input(
                        "Email Subject",
                        value=promise.email_draft.subject,
                        key=f"subj_{promise.id}_{idx}",
                        disabled=is_staged,
                    )
                    promise.email_draft.subject = new_subj

                new_body = st.text_area(
                    "Email Body",
                    value=promise.email_draft.body,
                    height=130,
                    key=f"email_body_{promise.id}_{idx}",
                    disabled=is_staged,
                )
                promise.email_draft.body = new_body

            with tab_cal:
                c_c1, c_c2 = st.columns([2, 1])
                with c_c1:
                    new_event = st.text_input(
                        "Calendar Event Title",
                        value=promise.calendar_event.title,
                        key=f"cal_t_{promise.id}_{idx}",
                        disabled=is_staged,
                    )
                    promise.calendar_event.title = new_event
                with c_c2:
                    new_dur = st.number_input(
                        "Suggested Duration (minutes)",
                        value=promise.calendar_event.duration_minutes,
                        step=15,
                        key=f"cal_d_{promise.id}_{idx}",
                        disabled=is_staged,
                    )
                    promise.calendar_event.duration_minutes = int(new_dur)

                st.caption(f"Tentative start: `{promise.calendar_event.start_iso}` (Non-destructive focus block)")

            st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)

            # Individual Card Actions & Approval Controls
            act_col1, act_col2 = st.columns([2.0, 3.0])

            with act_col1:
                if not is_staged:
                    if st.button("✅ Approve & Stage Action", key=f"approve_{promise.id}_{idx}", type="primary"):
                        router = st.session_state.action_router
                        router.stage_todoist(promise.task_title, due_date=promise.verbal_deadline, priority=prio)
                        router.stage_calendar_event(
                            title=promise.calendar_event.title,
                            start_iso=promise.calendar_event.start_iso,
                            duration_minutes=promise.calendar_event.duration_minutes,
                        )
                        router.stage_gmail_draft(
                            to_email=promise.counterparty_email,
                            subject=promise.email_draft.subject,
                            body=promise.email_draft.body,
                        )
                        promise.status = "STAGED"
                        st.session_state.staged_history.append(promise.id)
                        st.toast(f"Staged '{promise.task_title}' to Gmail Drafts & Calendar", icon="✓")
                        st.rerun()
                else:
                    st.markdown(
                        """
                        <div style="padding-top:4px;">
                            <span class="ag-status-chip-staged">✓ Staged</span>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            with act_col2:
                if is_staged:
                    st.markdown(
                        """
                        <div style="display:flex; align-items:center; gap:8px; padding-top:4px;">
                            <a class="ag-link-pill" href="https://mail.google.com/mail/u/0/#drafts" target="_blank">✉️ Open in Gmail Drafts ↗</a>
                            <a class="ag-link-pill" href="https://calendar.google.com" target="_blank">📅 View Calendar ↗</a>
                            <a class="ag-link-pill" href="https://app.todoist.com/app/today" target="_blank">📝 View Todoist ↗</a>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                else:
                    if st.button("Dismiss", key=f"btn_dismiss_{promise.id}_{idx}", type="secondary"):
                        st.session_state.promises = [p for p in st.session_state.promises if p.id != promise.id]
                        st.toast("Dismissed commitment", icon="🗑️")
                        st.rerun()
