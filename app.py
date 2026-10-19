"""
Promise Keeper - Streamlit Dashboard
Real-time wearable sync, Amazon Bedrock extraction, and human-in-the-loop staging.
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
from src.bee_client import BeeClient
from src.extractor import BedrockPromiseExtractor, PromiseItem
from src.telemetry import default_telemetry_recorder

load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Promise Keeper | Wearable AI Executive Assistant",
    page_icon="🐝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for state-of-the-art UI styling
CUSTOM_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
}

/* Base theme adjustments */
.stApp {
    background: radial-gradient(circle at top left, #0e172a 0%, #050b17 100%);
    color: #f1f5f9;
}

/* Top Hero Header */
.hero-container {
    background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(15, 23, 42, 0.9) 100%);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    box-shadow: 0 10px 30px -10px rgba(0, 0, 0, 0.5);
    backdrop-filter: blur(12px);
}

.hero-title {
    font-size: 2.2rem;
    font-weight: 800;
    background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #f472b6 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em;
    margin-bottom: 8px;
}

.hero-subtitle {
    font-size: 1.05rem;
    color: #94a3b8;
    max-width: 820px;
    line-height: 1.5;
}

/* Metric Pill Cards */
.metric-card {
    background: rgba(17, 24, 39, 0.75);
    border: 1px solid rgba(255, 255, 255, 0.07);
    border-radius: 14px;
    padding: 16px 20px;
    transition: transform 0.2s ease, border-color 0.2s ease;
}

.metric-card:hover {
    border-color: rgba(56, 189, 248, 0.3);
    transform: translateY(-2px);
}

.metric-label {
    font-size: 0.78rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
    margin-bottom: 6px;
}

.metric-value {
    font-size: 1.5rem;
    font-weight: 700;
    color: #f8fafc;
    font-family: 'JetBrains Mono', monospace;
}

/* Status Badges */
.badge-live {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.35);
    color: #34d399;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-mock {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(245, 158, 11, 0.15);
    border: 1px solid rgba(245, 158, 11, 0.35);
    color: #fbbf24;
    padding: 4px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
}

.badge-by-me {
    background: linear-gradient(135deg, rgba(14, 165, 233, 0.2) 0%, rgba(59, 130, 246, 0.25) 100%);
    border: 1px solid rgba(56, 189, 248, 0.4);
    color: #38bdf8;
    padding: 4px 12px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}

.badge-to-me {
    background: linear-gradient(135deg, rgba(236, 72, 153, 0.2) 0%, rgba(245, 158, 11, 0.25) 100%);
    border: 1px solid rgba(244, 114, 182, 0.4);
    color: #f472b6;
    padding: 4px 12px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}

.badge-staged {
    background: rgba(16, 185, 129, 0.2);
    border: 1px solid rgba(16, 185, 129, 0.5);
    color: #10b981;
    padding: 4px 12px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 700;
}

.badge-pending {
    background: rgba(148, 163, 184, 0.15);
    border: 1px solid rgba(148, 163, 184, 0.3);
    color: #94a3b8;
    padding: 4px 12px;
    border-radius: 8px;
    font-size: 0.8rem;
    font-weight: 700;
}

/* Card Container */
.promise-card {
    background: rgba(15, 23, 42, 0.7);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 20px;
    box-shadow: 0 4px 20px -2px rgba(0, 0, 0, 0.3);
}

.promise-card.staged {
    border-color: rgba(16, 185, 129, 0.4);
    background: rgba(6, 78, 59, 0.15);
}

/* Quick link buttons */
.quick-link-btn {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: rgba(30, 41, 59, 0.8);
    border: 1px solid rgba(255, 255, 255, 0.1);
    color: #e2e8f0 !important;
    text-decoration: none;
    padding: 8px 14px;
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 500;
    transition: all 0.2s ease;
    margin-right: 8px;
    margin-bottom: 8px;
}

.quick-link-btn:hover {
    background: rgba(56, 189, 248, 0.15);
    border-color: rgba(56, 189, 248, 0.4);
    color: #38bdf8 !important;
}

/* Dialogue turn bubble */
.turn-bubble {
    padding: 10px 14px;
    border-radius: 10px;
    margin-bottom: 8px;
    font-size: 0.9rem;
    line-height: 1.4;
}

.turn-me {
    background: rgba(14, 165, 233, 0.12);
    border-left: 3px solid #0284c7;
}

.turn-other {
    background: rgba(148, 163, 184, 0.08);
    border-left: 3px solid #64748b;
}
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# Initialize Session State
if "bee_client" not in st.session_state:
    st.session_state.bee_client = BeeClient()

if "action_router" not in st.session_state:
    st.session_state.action_router = ActionRouter()

if "extractor" not in st.session_state:
    st.session_state.extractor = BedrockPromiseExtractor()

if "conversations_data" not in st.session_state:
    # Pre-fetch initial conversations so the screen looks immediately alive
    st.session_state.conversations_data = (
        st.session_state.bee_client.fetch_recent_conversations()
    )

if "promises" not in st.session_state:
    st.session_state.promises = []

if "latest_telemetry" not in st.session_state:
    st.session_state.latest_telemetry = None

if "staged_history" not in st.session_state:
    st.session_state.staged_history = []


# Sidebar controls & system configuration
with st.sidebar:
    st.markdown("### 🐝 Bee Wearable AI")
    bee_status = st.session_state.bee_client.check_status()
    is_live = bee_status.get("mode") == "HARDWARE_LIVE"

    if is_live:
        st.markdown(
            '<div class="badge-live">● LIVE HARDWARE CONNECTED</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            '<div class="badge-mock">⚡ OFFLINE FIXTURE MODE</div>',
            unsafe_allow_html=True,
        )

    st.caption(f"Device: {bee_status.get('device', 'Bee Wearable')}")
    st.caption(f"Authenticated: {bee_status.get('authenticated_user', 'alex@dev')}")
    st.caption(f"Battery: {bee_status.get('battery_percentage', 92)}%")

    st.markdown("---")
    st.markdown("### ☁️ AWS Bedrock Engine")
    selected_model = st.selectbox(
        "Converse Model",
        options=[
            "amazon.nova-pro-v1:0",
            "anthropic.claude-3-5-sonnet-20241022-v2:0",
            "amazon.nova-lite-v1:0",
        ],
        index=0,
        help="Model invoked through Amazon Bedrock Converse API.",
    )
    st.session_state.extractor.primary_model_id = selected_model

    st.markdown("---")
    st.markdown("### 🔗 Staging Destinations")
    st.markdown(
        """
        <div style="display:flex; flex-direction:column; gap:6px;">
            <a class="quick-link-btn" href="https://mail.google.com/mail/u/0/#drafts" target="_blank">
                ✉️ Gmail Drafts Box
            </a>
            <a class="quick-link-btn" href="https://calendar.google.com" target="_blank">
                📅 Google Calendar
            </a>
            <a class="quick-link-btn" href="https://app.todoist.com/app/today" target="_blank">
                📝 Todoist Tasks
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown("### 📊 Cumulative Telemetry")
    summary = default_telemetry_recorder.get_summary()
    st.write(f"**Total Invocations:** {summary['total_calls']}")
    st.write(f"**Avg Latency:** {summary['avg_latency_ms']} ms")
    st.write(f"**Total Tokens:** {summary['total_tokens']:,}")
    st.write(f"**Total Cost:** ${summary['total_cost_usd']:.6f}")

    if st.button("Reset Telemetry Log", use_container_width=True):
        default_telemetry_recorder.clear()
        st.session_state.latest_telemetry = None
        st.rerun()


# Top Hero Header
st.markdown(
    """
    <div class="hero-container">
        <div class="hero-title">Promise Keeper 🐝</div>
        <div class="hero-subtitle">
            Autonomous commitment staging engine for wearable AI. Ingests ambient spoken conversations from your
            <strong>Bee wearable</strong>, parses bilateral promises with <strong>Amazon Bedrock Converse API</strong>,
            and safely stages them into Google Calendar tentative blocks, Todoist tasks, and Gmail drafts with
            one-tap human-in-the-loop verification.
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)


# Top Metrics Bar
col_m1, col_m2, col_m3, col_m4 = st.columns(4)

with col_m1:
    badge_html = (
        '<span class="badge-live">ONLINE</span>'
        if is_live
        else '<span class="badge-mock">OFFLINE FIXTURE</span>'
    )
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Bee Wearable Status</div>
            <div class="metric-value">{badge_html}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_m2:
    latency_val = (
        f"{st.session_state.latest_telemetry.latency_ms:.0f} ms"
        if st.session_state.latest_telemetry
        else "Ready"
    )
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Bedrock Latency</div>
            <div class="metric-value" style="color:#38bdf8;">{latency_val}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_m3:
    tokens_val = (
        f"{st.session_state.latest_telemetry.total_tokens:,}"
        if st.session_state.latest_telemetry
        else "0"
    )
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Token Consumption</div>
            <div class="metric-value" style="color:#818cf8;">{tokens_val}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col_m4:
    total_staged = len(st.session_state.staged_history)
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Commitments Staged</div>
            <div class="metric-value" style="color:#34d399;">{total_staged}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)


# Interactive Action Bar: Sync & Extract
action_col1, action_col2, action_col3 = st.columns([1.8, 1.2, 1.0])

with action_col1:
    if st.button("🎙️ Sync from Bee & Extract Commitments", type="primary", use_container_width=True):
        with st.spinner("Syncing audio buffer from Bee & executing Bedrock Converse API..."):
            # 1. Sync turns from Bee
            st.session_state.bee_client.sync()
            conv_data = st.session_state.bee_client.fetch_recent_conversations()
            st.session_state.conversations_data = conv_data

            # 2. Format transcript
            transcript = st.session_state.bee_client.format_transcript_for_llm(conv_data)

            # 3. Extract promises via Bedrock Converse API
            result = st.session_state.extractor.extract_promises(transcript)
            st.session_state.promises = result.promises
            st.session_state.latest_telemetry = result.telemetry
            st.toast(f"Extracted {len(result.promises)} actionable commitments!", icon="✅")
            st.rerun()

with action_col2:
    if st.session_state.promises:
        pending_count = sum(1 for p in st.session_state.promises if p.status == "PENDING")
        if st.button(f"⚡ One-Tap Stage All ({pending_count})", use_container_width=True):
            with st.spinner("Staging all pending commitments across Todoist, Calendar & Gmail..."):
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
                st.toast("All pending commitments staged safely!", icon="🚀")
                st.rerun()

with action_col3:
    if st.button("🧹 Clear All", use_container_width=True):
        st.session_state.promises = []
        st.rerun()


# Audio Turn Stream Preview Expander
with st.expander("🗣️ Bee Wearable Ambient Transcript Stream (Click to inspect turns)", expanded=False):
    turns = st.session_state.conversations_data.get("turns", [])
    if not turns:
        st.info("No audio turns detected yet.")
    else:
        st.caption(f"Source: {st.session_state.conversations_data.get('source')} | Turns: {len(turns)}")
        for turn in turns:
            spk = turn.get("speaker", "Unknown")
            txt = turn.get("text", "")
            ts = turn.get("timestamp", "")
            is_wearer = "Wearer" in spk or "Me" in spk
            bubble_class = "turn-me" if is_wearer else "turn-other"
            badge = "👤 <strong>You</strong>" if is_wearer else f"👥 <strong>{spk}</strong>"

            st.markdown(
                f"""
                <div class="turn-bubble {bubble_class}">
                    <div style="font-size:0.75rem; color:#94a3b8; margin-bottom:4px;">{badge} • <span style="font-family:'JetBrains Mono';">{ts}</span></div>
                    <div>"{txt}"</div>
                </div>
                """,
                unsafe_allow_html=True,
            )


# Main Commitments Review & Human-In-The-Loop Approval Section
st.markdown("### 📋 Extracted Commitments Pending Review")

if not st.session_state.promises:
    st.info(
        "No promises currently in staging queue. Click **'🎙️ Sync from Bee & Extract Commitments'** above to ingest turns and run Amazon Bedrock."
    )
else:
    # Filter Tabs
    filter_choice = st.radio(
        "Filter Direction",
        ["All Commitments", "📤 Made By Me", "📥 Promised To Me"],
        horizontal=True,
        label_visibility="collapsed",
    )

    filtered_promises = st.session_state.promises
    if filter_choice == "📤 Made By Me":
        filtered_promises = [p for p in filtered_promises if p.direction == "MADE_BY_ME"]
    elif filter_choice == "📥 Promised To Me":
        filtered_promises = [p for p in filtered_promises if p.direction == "MADE_TO_ME"]

    for idx, promise in enumerate(filtered_promises):
        is_staged = promise.status == "STAGED"
        card_class = "promise-card staged" if is_staged else "promise-card"

        # Direction badge
        if promise.direction == "MADE_BY_ME":
            dir_badge = '<span class="badge-by-me">📤 I PROMISED</span>'
        else:
            dir_badge = '<span class="badge-to-me">📥 PROMISED TO ME</span>'

        status_badge = (
            '<span class="badge-staged">✅ STAGED</span>'
            if is_staged
            else '<span class="badge-pending">⏳ PENDING APPROVAL</span>'
        )

        with st.container():
            # Card Header
            header_col1, header_col2 = st.columns([3, 1])
            with header_col1:
                st.markdown(
                    f"""
                    <div style="display:flex; align-items:center; gap:10px; margin-bottom:6px;">
                        {dir_badge}
                        {status_badge}
                        <span style="font-weight:700; font-size:1.1rem; color:#f8fafc;">{promise.counterparty_name}</span>
                        <span style="color:#64748b; font-size:0.85rem;">({promise.counterparty_email})</span>
                    </div>
                    <div style="color:#cbd5e1; font-size:0.95rem; margin-bottom:12px;">
                        <strong>Agreement:</strong> {promise.summary}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with header_col2:
                st.markdown(
                    f"""
                    <div style="text-align:right;">
                        <span style="font-size:0.75rem; color:#94a3b8; text-transform:uppercase; font-weight:600;">Deadline</span><br>
                        <span style="font-size:0.9rem; color:#fbbf24; font-weight:700;">⏱️ {promise.verbal_deadline}</span><br>
                        <span style="font-size:0.72rem; color:#64748b; font-family:'JetBrains Mono';">{promise.inferred_iso_deadline}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

            # Three Approval Tabs for Human-In-The-Loop inspection & editing
            tab_task, tab_email, tab_cal = st.tabs(["📝 Todoist Task", "✉️ Gmail Draft", "📅 Calendar Tentative Block"])

            with tab_task:
                c_task1, c_task2 = st.columns([3, 1])
                with c_task1:
                    new_task_title = st.text_input(
                        "Task Title",
                        value=promise.task_title,
                        key=f"task_title_{promise.id}_{idx}",
                        disabled=is_staged,
                    )
                    promise.task_title = new_task_title
                with c_task2:
                    task_priority = st.selectbox(
                        "Priority",
                        options=[1, 2, 3, 4],
                        index=0,
                        key=f"task_prio_{promise.id}_{idx}",
                        disabled=is_staged,
                        help="1 = Normal, 4 = Urgent",
                    )

            with tab_email:
                c_em1, c_em2 = st.columns([1, 2])
                with c_em1:
                    new_to = st.text_input(
                        "To Recipient",
                        value=promise.counterparty_email,
                        key=f"email_to_{promise.id}_{idx}",
                        disabled=is_staged,
                    )
                    promise.counterparty_email = new_to
                with c_em2:
                    new_subj = st.text_input(
                        "Email Subject",
                        value=promise.email_draft.subject,
                        key=f"email_subj_{promise.id}_{idx}",
                        disabled=is_staged,
                    )
                    promise.email_draft.subject = new_subj

                new_body = st.text_area(
                    "Email Draft Body (Safe: Never sent automatically)",
                    value=promise.email_draft.body,
                    rows=3,
                    key=f"email_body_{promise.id}_{idx}",
                    disabled=is_staged,
                )
                promise.email_draft.body = new_body

            with tab_cal:
                c_c1, c_c2 = st.columns([2, 1])
                with c_c1:
                    new_cal_title = st.text_input(
                        "Calendar Event Summary",
                        value=promise.calendar_event.title,
                        key=f"cal_title_{promise.id}_{idx}",
                        disabled=is_staged,
                    )
                    promise.calendar_event.title = new_cal_title
                with c_c2:
                    new_duration = st.number_input(
                        "Duration (minutes)",
                        value=promise.calendar_event.duration_minutes,
                        step=15,
                        key=f"cal_dur_{promise.id}_{idx}",
                        disabled=is_staged,
                    )
                    promise.calendar_event.duration_minutes = int(new_duration)

                st.caption(f"Tentative start: `{promise.calendar_event.start_iso}` (Non-blocking placeholder)")

            # Staging Buttons per Card
            btn_col1, btn_col2, btn_col3 = st.columns([1.5, 1.0, 3.5])

            with btn_col1:
                if not is_staged:
                    if st.button("✅ Approve & Stage", key=f"stage_btn_{promise.id}_{idx}", type="primary"):
                        router = st.session_state.action_router

                        # Execute safe staging across the 3 destinations
                        todo_res = router.stage_todoist(promise.task_title, due_date=promise.verbal_deadline, priority=task_priority)
                        cal_res = router.stage_calendar_event(
                            title=promise.calendar_event.title,
                            start_iso=promise.calendar_event.start_iso,
                            duration_minutes=promise.calendar_event.duration_minutes,
                        )
                        mail_res = router.stage_gmail_draft(
                            to_email=promise.counterparty_email,
                            subject=promise.email_draft.subject,
                            body=promise.email_draft.body,
                        )

                        promise.status = "STAGED"
                        st.session_state.staged_history.append(promise.id)
                        st.toast(f"Staged '{promise.task_title}' to Todoist, Calendar & Gmail Drafts!", icon="🎉")
                        st.rerun()
                else:
                    st.success("Staged Safely")

            with btn_col2:
                if not is_staged:
                    if st.button("❌ Dismiss", key=f"dismiss_btn_{promise.id}_{idx}"):
                        st.session_state.promises = [p for p in st.session_state.promises if p.id != promise.id]
                        st.toast("Dismissed commitment", icon="🗑️")
                        st.rerun()

            with btn_col3:
                if is_staged:
                    st.markdown(
                        """
                        <div style="font-size:0.85rem; color:#34d399; padding-top:6px;">
                            🚀 Staged in: <a href="https://mail.google.com/mail/u/0/#drafts" target="_blank" style="color:#38bdf8;">Gmail Drafts</a> •
                            <a href="https://calendar.google.com" target="_blank" style="color:#38bdf8;">Google Calendar</a> •
                            <a href="https://app.todoist.com" target="_blank" style="color:#38bdf8;">Todoist</a>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            st.markdown("<hr style='border-color: rgba(255,255,255,0.06); margin: 18px 0;'>", unsafe_allow_html=True)


# Bedrock Telemetry Details Accordion for AWS Builders
if st.session_state.latest_telemetry:
    with st.expander("🔬 AWS Bedrock Converse API Telemetry & Payload Inspector", expanded=False):
        telem = st.session_state.latest_telemetry
        tc1, tc2, tc3, tc4 = st.columns(4)
        tc1.metric("Model Invocated", telem.model_id)
        tc2.metric("Latency", f"{telem.latency_ms:.1f} ms")
        tc3.metric("Tokens (In / Out)", f"{telem.input_tokens} / {telem.output_tokens}")
        tc4.metric("Estimated Cost", f"${telem.estimated_cost_usd:.6f}")

        st.json(telem.model_dump())
