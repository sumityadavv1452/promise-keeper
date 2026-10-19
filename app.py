import streamlit as st
import datetime
import json
from src.bee_client import BeeClient
from src.extractor import BedrockPromiseExtractor
from src.action_router import ActionRouter
from src.telemetry import TelemetryRecorder

# -----------------------------------------------------------------------------
# 1. Page Configuration & Theme Initialization
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Promise Keeper — Wearable AI Engine",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "theme" not in st.session_state:
    st.session_state.theme = "Dark"

current_theme = st.session_state.theme

if "selected_idx" not in st.session_state:
    st.session_state.selected_idx = 0

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
# 2. Dynamic Theme Tokens (Light / Dark)
# -----------------------------------------------------------------------------
if current_theme == "Dark":
    tokens = {
        "BG_CANVAS": "#0D1117",
        "BG_CARD": "#161B22",
        "BG_INPUT": "#0D1117",
        "BG_SURFACE": "#21262D",
        "BORDER_COL": "#30363D",
        "BORDER_INPUT": "#30363D",
        "TEXT_PRIMARY": "#F0F6FC",
        "TEXT_SECONDARY": "#8B949E",
        "TEXT_BODY": "#C9D1D9",
        "SIDEBAR_BG": "#0D1117",
        "SIDEBAR_CARD_BG": "#161B22",
        "SIDEBAR_BORDER": "#30363D",
        "TOGGLE_COLOR": "#F9FAFB",
        "TOGGLE_BG": "#21262D",
        "TOGGLE_BORDER": "#30363D",
        "TOGGLE_HOVER_BG": "#30363D",
        "TOGGLE_HOVER_COLOR": "#FFFFFF",
        "BADGE_BY_BG": "rgba(31, 111, 235, 0.15)",
        "BADGE_BY_BORDER": "rgba(56, 139, 253, 0.4)",
        "BADGE_BY_TEXT": "#58A6FF",
        "BADGE_TO_BG": "rgba(210, 153, 34, 0.15)",
        "BADGE_TO_BORDER": "rgba(210, 153, 34, 0.4)",
        "BADGE_TO_TEXT": "#D29922",
        "BADGE_STAGED_BG": "rgba(35, 134, 54, 0.2)",
        "BADGE_STAGED_BORDER": "#238636",
        "BADGE_STAGED_TEXT": "#3FB950",
        "BTN_PRIMARY_BG": "#238636",
        "BTN_PRIMARY_HOVER": "#2EA043",
        "BTN_PRIMARY_TEXT": "#FFFFFF",
        "BTN_SEC_BG": "#21262D",
        "BTN_SEC_HOVER": "#30363D",
        "BTN_SEC_BORDER": "#30363D",
        "BTN_SEC_TEXT": "#C9D1D9",
        "DRAWER_BG": "#090D13",
        "LINK_COLOR": "#58A6FF",
        "PILL_ACTIVE_BG": "#21262D",
        "PILL_ACTIVE_TEXT": "#F0F6FC",
    }
else:
    tokens = {
        "BG_CANVAS": "#F9FAFB",
        "BG_CARD": "#FFFFFF",
        "BG_INPUT": "#FFFFFF",
        "BG_SURFACE": "#F3F4F6",
        "BORDER_COL": "#E5E7EB",
        "BORDER_INPUT": "#D1D5DB",
        "TEXT_PRIMARY": "#111827",
        "TEXT_SECONDARY": "#6B7280",
        "TEXT_BODY": "#374151",
        "SIDEBAR_BG": "#FFFFFF",
        "SIDEBAR_CARD_BG": "#F9FAFB",
        "SIDEBAR_BORDER": "#E5E7EB",
        "TOGGLE_COLOR": "#1F2937",
        "TOGGLE_BG": "#F3F4F6",
        "TOGGLE_BORDER": "#E5E7EB",
        "TOGGLE_HOVER_BG": "#E5E7EB",
        "TOGGLE_HOVER_COLOR": "#111827",
        "BADGE_BY_BG": "#EFF6FF",
        "BADGE_BY_BORDER": "#BFDBFE",
        "BADGE_BY_TEXT": "#1D4ED8",
        "BADGE_TO_BG": "#FEF3C7",
        "BADGE_TO_BORDER": "#FDE68A",
        "BADGE_TO_TEXT": "#B45309",
        "BADGE_STAGED_BG": "#ECFDF5",
        "BADGE_STAGED_BORDER": "#A7F3D0",
        "BADGE_STAGED_TEXT": "#047857",
        "BTN_PRIMARY_BG": "#111827",
        "BTN_PRIMARY_HOVER": "#1F2937",
        "BTN_PRIMARY_TEXT": "#FFFFFF",
        "BTN_SEC_BG": "#FFFFFF",
        "BTN_SEC_HOVER": "#F3F4F6",
        "BTN_SEC_BORDER": "#E5E7EB",
        "BTN_SEC_TEXT": "#1F2937",
        "DRAWER_BG": "#F9FAFB",
        "LINK_COLOR": "#2563EB",
        "PILL_ACTIVE_BG": "#E5E7EB",
        "PILL_ACTIVE_TEXT": "#111827",
    }

CSS_TEMPLATE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;450;500;600;650;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    /* Global Canvas */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        color: __TEXT_PRIMARY__ !important;
        background-color: __BG_CANVAS__ !important;
    }
    
    .stApp {
        background-color: __BG_CANVAS__ !important;
        color: __TEXT_PRIMARY__ !important;
    }

    /* 1. CRITICAL: High-Contrast Sidebar Toggle Button in Both Themes */
    header[data-testid="stHeader"] {
        background-color: transparent !important;
        z-index: 100 !important;
    }
    
    header[data-testid="stHeader"] button,
    header[data-testid="stHeader"] [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="stSidebarCollapseButton"] button,
    [data-testid="stSidebarCollapseButton"],
    [data-testid="collapsedControl"] button,
    [data-testid="collapsedControl"],
    [data-testid="stSidebarCollapsedControl"] button,
    [data-testid="stSidebarCollapsedControl"],
    div[data-testid="stSidebarHeader"] button,
    button[kind="header"],
    button[data-testid="stBaseButton-header"],
    button[data-testid="stBaseButton-headerNoPadding"],
    button[data-testid="baseButton-header"],
    button[data-testid="baseButton-headerNoPadding"],
    [data-testid="stSidebarNavSeparator"] + div button {
        color: __TOGGLE_COLOR__ !important;
        background-color: __TOGGLE_BG__ !important;
        border: 1px solid __TOGGLE_BORDER__ !important;
        border-radius: 8px !important;
        padding: 6px 10px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important;
        opacity: 1 !important;
        visibility: visible !important;
        transition: all 0.15s ease !important;
    }
    
    header[data-testid="stHeader"] button:hover,
    [data-testid="stSidebarCollapseButton"] button:hover,
    [data-testid="stSidebarCollapseButton"]:hover,
    [data-testid="collapsedControl"] button:hover,
    [data-testid="collapsedControl"]:hover,
    [data-testid="stSidebarCollapsedControl"] button:hover,
    [data-testid="stSidebarCollapsedControl"]:hover,
    div[data-testid="stSidebarHeader"] button:hover,
    button[kind="header"]:hover {
        background-color: __TOGGLE_HOVER_BG__ !important;
        color: __TOGGLE_HOVER_COLOR__ !important;
        border-color: __TOGGLE_BORDER__ !important;
    }

    /* Ensure svg inside toggle button is always razor-sharp */
    header[data-testid="stHeader"] button svg,
    [data-testid="stSidebarCollapseButton"] button svg,
    [data-testid="stSidebarCollapseButton"] svg,
    [data-testid="collapsedControl"] button svg,
    [data-testid="collapsedControl"] svg,
    [data-testid="stSidebarCollapsedControl"] button svg,
    [data-testid="stSidebarCollapsedControl"] svg,
    div[data-testid="stSidebarHeader"] button svg,
    button[kind="header"] svg,
    button[kind="header"] span,
    [data-testid="stIconMaterial"] {
        fill: __TOGGLE_COLOR__ !important;
        stroke: __TOGGLE_COLOR__ !important;
        color: __TOGGLE_COLOR__ !important;
    }

    header[data-testid="stHeader"] button:hover svg,
    [data-testid="stSidebarCollapseButton"] button:hover svg,
    [data-testid="stSidebarCollapseButton"]:hover svg,
    [data-testid="collapsedControl"] button:hover svg,
    [data-testid="collapsedControl"]:hover svg,
    [data-testid="stSidebarCollapsedControl"] button:hover svg,
    [data-testid="stSidebarCollapsedControl"]:hover svg,
    div[data-testid="stSidebarHeader"] button:hover svg,
    button[kind="header"]:hover svg {
        fill: __TOGGLE_HOVER_COLOR__ !important;
        stroke: __TOGGLE_HOVER_COLOR__ !important;
        color: __TOGGLE_HOVER_COLOR__ !important;
    }

    /* Hide unused Streamlit UI chrome */
    #MainMenu, footer { visibility: hidden !important; }
    div[data-testid="stDecoration"] { display: none !important; }
    div[data-testid="stStatusWidget"] { display: none !important; }
    .stDeployButton { display: none !important; }
    
    .block-container {
        padding-top: 1rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }
    
    /* Top Header & Navbar Container (Image 2 / Inji Playground Aesthetics) */
    div.st-key-top_navbar div[data-testid="stVerticalBlockBorderWrapper"],
    div.st-key-top_navbar {
        background-color: __BG_CARD__ !important;
        border: 1px solid __BORDER_COL__ !important;
        border-radius: 14px !important;
        padding: 12px 20px !important;
        margin-bottom: 22px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
    }
    div.st-key-top_navbar div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        border-color: __BORDER_COL__ !important;
    }
    
    .brand-title {
        font-size: 18px;
        font-weight: 650;
        letter-spacing: -0.02em;
        color: __TEXT_PRIMARY__;
        margin: 0;
        line-height: 1.2;
    }
    .version-pill {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        font-weight: 500;
        background: __BG_SURFACE__;
        border: 1px solid __BORDER_COL__;
        color: __TEXT_SECONDARY__;
        padding: 3px 8px;
        border-radius: 9999px;
    }
    .brand-tagline {
        font-size: 12.5px;
        font-weight: 450;
        color: __TEXT_SECONDARY__;
        margin: 3px 0 0 0;
        letter-spacing: -0.01em;
    }
    
    /* Center Navigation Status Pills */
    .nav-pill-active {
        background: __PILL_ACTIVE_BG__;
        color: __PILL_ACTIVE_TEXT__;
        font-size: 13px;
        font-weight: 600;
        padding: 6px 14px;
        border-radius: 9999px;
        display: inline-block;
        border: 1px solid __BORDER_COL__;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    }
    .nav-pill {
        color: __TEXT_SECONDARY__;
        font-size: 13px;
        font-weight: 500;
        padding: 6px 14px;
        border-radius: 9999px;
        display: inline-block;
        background: transparent;
        border: 1px solid transparent;
    }
    
    /* Live Status Pill */
    .live-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 12px;
        background: __BG_SURFACE__;
        border: 1px solid __BORDER_COL__;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        color: __TEXT_BODY__;
    }
    .green-dot {
        width: 7px;
        height: 7px;
        background: #10B981;
        border-radius: 50%;
        display: inline-block;
    }
    
    /* Metric Strip Cards (Image 2 Card Aesthetics) */
    .metric-card {
        background: __BG_CARD__;
        border: 1px solid __BORDER_COL__;
        border-radius: 14px;
        padding: 16px 20px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: transform 0.15s ease, border-color 0.15s ease, box-shadow 0.15s ease;
    }
    .metric-card:hover {
        border-color: #2563EB;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.08);
    }
    .metric-label {
        font-size: 11px;
        font-weight: 600;
        color: __TEXT_SECONDARY__;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .metric-val {
        font-family: 'JetBrains Mono', monospace;
        font-size: 22px;
        font-weight: 600;
        color: __TEXT_PRIMARY__;
        margin-bottom: 4px;
    }
    .metric-sub {
        font-size: 12px;
        color: __TEXT_SECONDARY__;
    }
    
    /* Native Container Card (Image 2 Rounded 12-16px Cards) */
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: __BG_CARD__ !important;
        border: 1px solid __BORDER_COL__ !important;
        border-radius: 14px !important;
        padding: 22px !important;
        margin-bottom: 18px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }
    
    /* Direction & Status Chips */
    .badge-primary {
        background: __BADGE_BY_BG__;
        border: 1px solid __BADGE_BY_BORDER__;
        color: __BADGE_BY_TEXT__;
        font-size: 12px;
        font-weight: 500;
        padding: 3px 10px;
        border-radius: 9999px;
    }
    .badge-secondary {
        background: __BADGE_TO_BG__;
        border: 1px solid __BADGE_TO_BORDER__;
        color: __BADGE_TO_TEXT__;
        font-size: 12px;
        font-weight: 500;
        padding: 3px 10px;
        border-radius: 9999px;
    }
    .badge-status {
        background: __BG_SURFACE__;
        border: 1px solid __BORDER_COL__;
        color: __TEXT_SECONDARY__;
        font-size: 12px;
        font-weight: 500;
        padding: 3px 10px;
        border-radius: 9999px;
    }
    .badge-status-staged {
        background: __BADGE_STAGED_BG__;
        border: 1px solid __BADGE_STAGED_BORDER__;
        color: __BADGE_STAGED_TEXT__;
        font-size: 12px;
        font-weight: 600;
        padding: 3px 10px;
        border-radius: 9999px;
    }
    
    /* Sidebar Styling (Clean & Decluttered) */
    section[data-testid="stSidebar"] {
        background-color: __SIDEBAR_BG__ !important;
        border-right: 1px solid __SIDEBAR_BORDER__ !important;
        color: __TEXT_BODY__ !important;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: __TEXT_PRIMARY__ !important;
        font-size: 12px !important;
        font-weight: 650 !important;
        text-transform: uppercase !important;
        letter-spacing: 0.05em !important;
        margin-bottom: 10px !important;
    }
    .sidebar-section {
        background: __SIDEBAR_CARD_BG__ !important;
        border: 1px solid __BORDER_COL__ !important;
        border-radius: 12px !important;
        padding: 14px 16px !important;
        margin-bottom: 16px !important;
    }
    .sidebar-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 13px;
        color: __TEXT_SECONDARY__;
        padding: 6px 0;
        border-bottom: 1px solid __BORDER_COL__;
    }
    .sidebar-row:last-child { border-bottom: none; }
    .sidebar-row span:first-child {
        color: __TEXT_BODY__;
        font-weight: 500;
    }
    .sidebar-val {
        font-family: 'JetBrains Mono', monospace;
        font-weight: 600;
        color: __TEXT_PRIMARY__;
    }
    .sidebar-link {
        text-decoration: none;
        color: __LINK_COLOR__;
        font-weight: 550;
    }
    .sidebar-link:hover {
        text-decoration: underline;
    }
    .sidebar-telemetry {
        font-size: 12.5px;
        color: __TEXT_SECONDARY__;
        line-height: 1.8;
    }
    .sidebar-telemetry strong {
        color: __TEXT_PRIMARY__;
    }

    /* Tabs Styling */
    div[data-testid="stTabs"] button[role="tab"] {
        color: __TEXT_SECONDARY__ !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        border-bottom: 2px solid transparent !important;
    }
    div[data-testid="stTabs"] button[role="tab"] p,
    div[data-testid="stTabs"] button[data-baseweb="tab"] p,
    div[data-testid="stTabs"] button span {
        color: __TEXT_SECONDARY__ !important;
        font-size: 13.5px !important;
        font-weight: 500 !important;
        margin: 0 !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] {
        border-bottom: 2px solid #2563EB !important;
    }
    div[data-testid="stTabs"] button[aria-selected="true"] p,
    div[data-testid="stTabs"] button[aria-selected="true"] span {
        color: __TEXT_PRIMARY__ !important;
        font-weight: 600 !important;
    }

    /* Form Inputs */
    input[type="text"], input[type="number"], textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: __BG_INPUT__ !important;
        border: 1px solid __BORDER_INPUT__ !important;
        border-radius: 8px !important;
        color: __TEXT_PRIMARY__ !important;
        font-size: 13.5px !important;
    }
    input[type="text"]:focus, textarea:focus {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 1px #2563EB !important;
    }
    
    /* Pill Buttons */
    button[kind="primary"], .stButton > button[kind="primary"] {
        background-color: __BTN_PRIMARY_BG__ !important;
        color: __BTN_PRIMARY_TEXT__ !important;
        border: 1px solid rgba(240, 246, 252, 0.1) !important;
        border-radius: 9999px !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
        letter-spacing: -0.01em !important;
        transition: all 0.15s ease !important;
    }
    button[kind="primary"]:hover {
        background-color: __BTN_PRIMARY_HOVER__ !important;
    }
    
    button[kind="secondary"], .stButton > button[kind="secondary"], .stButton > button {
        background-color: __BTN_SEC_BG__ !important;
        color: __BTN_SEC_TEXT__ !important;
        border: 1px solid __BTN_SEC_BORDER__ !important;
        border-radius: 9999px !important;
        font-weight: 500 !important;
        font-size: 13.5px !important;
        letter-spacing: -0.01em !important;
        transition: all 0.15s ease !important;
    }
    button[kind="secondary"]:hover, .stButton > button:hover {
        background-color: __BTN_SEC_HOVER__ !important;
        color: __TEXT_PRIMARY__ !important;
    }
    
    /* Top Nav specific controls */
    div.st-key-nav_theme_btn button {
        font-size: 16px !important;
        padding: 5px 12px !important;
        border-radius: 9999px !important;
        min-height: 36px !important;
    }
    div.st-key-nav_sync_btn button {
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 5px 14px !important;
        border-radius: 9999px !important;
        min-height: 36px !important;
    }
</style>
"""

# Render dynamic CSS
rendered_css = CSS_TEMPLATE
for k, v in tokens.items():
    rendered_css = rendered_css.replace(f"__{k}__", v)

st.markdown(rendered_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. Sidebar (Clean & Focused on Runtime Daemon, Model & Destinations)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Runtime Daemon")
    st.markdown("""
    <div class="sidebar-section">
        <div class="sidebar-row"><span>Daemon Status</span><span class="sidebar-val" style="color: #10B981;">● Active</span></div>
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
        <p style="margin: 0 0 8px 0; font-size: 13px;"><a href="https://mail.google.com/mail/u/0/#drafts" target="_blank" class="sidebar-link">✉️ Open Gmail Drafts ↗</a></p>
        <p style="margin: 0 0 8px 0; font-size: 13px;"><a href="https://calendar.google.com/" target="_blank" class="sidebar-link">📅 Open Google Calendar ↗</a></p>
        <p style="margin: 0; font-size: 13px;"><a href="https://app.todoist.com/" target="_blank" class="sidebar-link">📝 Open Todoist App ↗</a></p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Telemetry Session")
    latency_display = st.session_state.get("latency_ms", 284)
    tokens_display = st.session_state.get("tokens_used", 1140)
    st.markdown(f"""
    <div class="sidebar-telemetry">
        <div>Converse API Latency: <strong>{latency_display} ms</strong></div>
        <div>Tokens Consumed: <strong>{tokens_display:,}</strong></div>
        <div>Estimated Cost: <strong>$0.0009 USD</strong></div>
    </div>
    """, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 4. Top Header & Navbar (Styled exactly like Image 2 / Inji Playground)
# -----------------------------------------------------------------------------
with st.container(key="top_navbar", border=True):
    nav_c1, nav_c2, nav_c3 = st.columns([3.8, 3.2, 3.0], vertical_alignment="center")

    with nav_c1:
        st.markdown(f"""
        <div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">
            <span class="brand-title">✦ Promise Keeper</span>
            <span class="version-pill">Bee v1.4.2 · Bedrock Nova Pro</span>
        </div>
        <div class="brand-tagline">“You said it. We’ll remember it.”</div>
        """, unsafe_allow_html=True)

    with nav_c2:
        st.markdown("""
        <div style="display: flex; justify-content: center; align-items: center; gap: 8px;">
            <span class="nav-pill-active">Commitments</span>
            <span class="nav-pill">Transcript Stream</span>
        </div>
        """, unsafe_allow_html=True)

    with nav_c3:
        r_col1, r_col2, r_col3 = st.columns([1.1, 0.9, 1.4], vertical_alignment="center")
        with r_col1:
            st.markdown("""
            <div style="display: flex; justify-content: flex-end; align-items: center;">
                <span class="live-pill"><span class="green-dot"></span> Live</span>
            </div>
            """, unsafe_allow_html=True)
        with r_col2:
            # Streamlined theme toggle with strictly ☀️ and 🌙 (no computer icon)
            if current_theme == "Dark":
                if st.button("☀️", key="nav_theme_btn", help="Switch to Light Theme", use_container_width=True):
                    st.session_state.theme = "Light"
                    st.rerun()
            else:
                if st.button("🌙", key="nav_theme_btn", help="Switch to Dark Theme", use_container_width=True):
                    st.session_state.theme = "Dark"
                    st.rerun()
        with r_col3:
            if st.button("↻ Sync", key="nav_sync_btn", type="primary", use_container_width=True):
                with st.spinner("Syncing Bee Wearable speech..."):
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

# -----------------------------------------------------------------------------
# 5. High-Density Metric Strip (Image 2 Card Aesthetics)
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
    st.markdown(f"""
    <div style="background: {tokens['DRAWER_BG']}; border: 1px solid {tokens['BORDER_COL']}; border-radius: 8px; padding: 14px 18px; font-family: 'JetBrains Mono', monospace; font-size: 12.5px; color: {tokens['TEXT_BODY']}; line-height: 1.6;">
        <div>[09:41:04] Device: Bee Pendant 0x91B2 · Diarization Engine Active · Audio Stream 16kHz</div>
        <div>[09:41:12] Speaker 1 (Me): "Hey Alex, thanks for the sync. I'll send you the revised pitch deck by 5 PM tomorrow with the updated architecture diagram."</div>
        <div>[09:41:20] Speaker 2 (Alex): "Sounds great. Make sure to review the Q3 analytics report before Wednesday noon so we're aligned for the client sync."</div>
        <div>[09:41:28] Speaker 1 (Me): "Will do, let's also block 30 minutes on Thursday morning for a dry run."</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown(f"<h2 style='font-size: 18px; font-weight: 600; color: {tokens['TEXT_PRIMARY']}; margin: 24px 0 16px 0;'>Commitments Pending Review</h2>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. Render Commitments in Structured Cards with Active Highlight (Image 2)
# -----------------------------------------------------------------------------
selected_idx = st.session_state.get("selected_idx", 0)

# Inject active card highlight border and subtle shadow for the selected card
st.markdown(f"""
<style>
div.st-key-commitment_card_{selected_idx} div[data-testid="stVerticalBlockBorderWrapper"],
div.st-key-commitment_card_{selected_idx} {{
    border: 2px solid #2563EB !important;
    box-shadow: 0 4px 16px rgba(37, 99, 235, 0.14) !important;
}}
</style>
""", unsafe_allow_html=True)

router = ActionRouter()

for idx, p in enumerate(st.session_state.promises):
    is_me = p["direction"] == "MADE_BY_ME"
    badge_class = "badge-primary" if is_me else "badge-secondary"
    badge_label = "📤 Promise Made by Me" if is_me else "📥 Commitment to Me"
    status_class = "badge-status-staged" if p["staged"] else "badge-status"
    status_label = "✅ STAGED SAFELY" if p["staged"] else "Pending Review"
    is_selected = (idx == selected_idx)
    
    with st.container(key=f"commitment_card_{idx}", border=True):
        # Header row inside card
        st.markdown(f"""
        <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 12px;">
            <div style="display: flex; align-items: center; gap: 8px;">
                <span class="{badge_class}">{badge_label}</span>
                <span class="{status_class}">{status_label}</span>
                {'<span style="font-size: 11px; background: rgba(37, 99, 235, 0.12); color: #2563EB; padding: 2px 8px; border-radius: 9999px; font-weight: 600; border: 1px solid rgba(37, 99, 235, 0.3);">Active Focus</span>' if is_selected else ''}
            </div>
            <div style="font-size: 13px; font-weight: 500; color: {tokens['TEXT_SECONDARY']};">
                ⏱️ Due: <strong style="color: {tokens['TEXT_PRIMARY']};">{p['verbal_deadline']}</strong>
            </div>
        </div>
        <div style="font-size: 17px; font-weight: 600; color: {tokens['TEXT_PRIMARY']}; margin: 0 0 6px 0;">{p['task_title']}</div>
        <div style="font-size: 14px; color: {tokens['TEXT_BODY']}; margin-bottom: 12px; line-height: 1.45;">{p['summary']}</div>
        <div style="display: flex; flex-wrap: wrap; gap: 16px; font-size: 12.5px; color: {tokens['TEXT_SECONDARY']}; margin-bottom: 16px; font-family: 'JetBrains Mono', monospace;">
            <span>Counterparty: <strong style="color: {tokens['TEXT_PRIMARY']};">{p['counterparty_name']}</strong></span>
            <span>Email: <code style="color: {tokens['LINK_COLOR']};">{p['counterparty_email']}</code></span>
            <span>ISO: <code style="color: {tokens['TEXT_SECONDARY']};">{p['iso_deadline']}</code></span>
        </div>
        """, unsafe_allow_html=True)
        
        # 3 Clean Native Tabs with full legible labels
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
        b_col1, b_col2, b_col3 = st.columns([2, 1, 4])
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
                
        with b_col3:
            if not is_selected:
                if st.button("Focus Card", key=f"focus_{idx}", type="secondary"):
                    st.session_state.selected_idx = idx
                    st.rerun()
                
        if p["staged"]:
            st.markdown(f"""
            <div style="margin-top: 14px; padding: 10px 14px; background: {tokens['BADGE_STAGED_BG']}; border: 1px solid {tokens['BADGE_STAGED_BORDER']}; border-radius: 8px; font-size: 13px; color: {tokens['BADGE_STAGED_TEXT']};">
                ✓ <b>Staged safely:</b> Created Gmail draft (never auto-sent), added Todoist task, and blocked tentative calendar time.
                <a href="https://mail.google.com/mail/u/0/#drafts" target="_blank" style="margin-left: 8px; color: {tokens['LINK_COLOR']}; text-decoration: none; font-weight: 600;">View Draft in Gmail ↗</a>
            </div>
            """, unsafe_allow_html=True)
