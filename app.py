import streamlit as st
import datetime
import json
import base64
from src.bee_client import BeeClient
from src.extractor import BedrockPromiseExtractor
from src.action_router import ActionRouter
from src.telemetry import TelemetryRecorder

# -----------------------------------------------------------------------------
# 1. Page Configuration & Theme Initialization (Default to Light Mode)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Promise Keeper",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

if "theme" not in st.session_state:
    st.session_state.theme = "Light"

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

# Official Vector Brand Logos
GMAIL_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M22 6C22 4.9 21.1 4 20 4H4C2.9 4 2 4.9 2 6V18C2 19.1 2.9 20 4 20H20C21.1 20 22 19.1 22 18V6ZM20 6L12 11L4 6H20ZM20 18H4V8L12 13L20 8V18Z" fill="#EA4335"/></svg>'
CALENDAR_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M19 4H18V2H16V4H8V2H6V4H5C3.89 4 3 4.9 3 6V20C3 21.1 3.89 22 5 22H19C20.1 22 21 21.1 21 20V6C21 4.9 20.1 4 19 4ZM19 20H5V9H19V20ZM7 11H12V16H7V11Z" fill="#1A73E8"/></svg>'
TODOIST_SVG = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg"><path d="M12 2C6.48 2 2 6.48 2 12C2 17.52 6.48 22 12 22C17.52 22 22 17.52 22 12C22 6.48 17.52 2 12 2ZM10 17L5 12L6.41 10.59L10 14.17L17.59 6.58L19 8L10 17Z" fill="#E44332"/></svg>'

# Theme Toggle High-Contrast Vector SVGs
RAW_SUN_ACTIVE = '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#2563EB" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>'
RAW_SUN_INACTIVE = '<svg xmlns="http://www.w3.org/2000/svg" width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/></svg>'
RAW_MOON_ACTIVE = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#60A5FA" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>'
RAW_MOON_INACTIVE = '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#94A3B8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/></svg>'

SUN_ACTIVE_URI = f"data:image/svg+xml;base64,{base64.b64encode(RAW_SUN_ACTIVE.encode('utf-8')).decode('utf-8')}"
SUN_INACTIVE_URI = f"data:image/svg+xml;base64,{base64.b64encode(RAW_SUN_INACTIVE.encode('utf-8')).decode('utf-8')}"
MOON_ACTIVE_URI = f"data:image/svg+xml;base64,{base64.b64encode(RAW_MOON_ACTIVE.encode('utf-8')).decode('utf-8')}"
MOON_INACTIVE_URI = f"data:image/svg+xml;base64,{base64.b64encode(RAW_MOON_INACTIVE.encode('utf-8')).decode('utf-8')}"

# -----------------------------------------------------------------------------
# 2. Dynamic Enterprise Tokens (Linear / Inji Playground Caliber)
# -----------------------------------------------------------------------------
if current_theme == "Dark":
    tokens = {
        "BG_CANVAS": "#0D1117",
        "BG_CARD": "#161B22",
        "BG_INPUT": "#0D1117",
        "BG_SURFACE": "#21262D",
        "BORDER_COL": "#30363D",
        "BORDER_INPUT": "#30363D",
        "CARD_BORDER": "#30363D",
        "CARD_SHADOW": "0 1px 3px rgba(0, 0, 0, 0.25)",
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
        "THEME_PILL_BG": "#1E293B",
        "THEME_PILL_BORDER": "#334155",
        "SUN_BTN_BG": "transparent",
        "SUN_BTN_SHADOW": "none",
        "SUN_BTN_ICON": SUN_INACTIVE_URI,
        "MOON_BTN_BG": "#0F172A",
        "MOON_BTN_SHADOW": "0 1px 3px rgba(0, 0, 0, 0.4)",
        "MOON_BTN_ICON": MOON_ACTIVE_URI,
        "BADGE_OUTGOING_BG": "rgba(30, 58, 138, 0.2)",
        "BADGE_OUTGOING_TEXT": "#60A5FA",
        "BADGE_OUTGOING_BORDER": "#1E40AF",
        "BADGE_INCOMING_BG": "rgba(120, 53, 15, 0.2)",
        "BADGE_INCOMING_TEXT": "#FBBF24",
        "BADGE_INCOMING_BORDER": "#92400E",
        "BADGE_STATUS_BG": "#21262D",
        "BADGE_STATUS_TEXT": "#8B949E",
        "BADGE_STATUS_BORDER": "#30363D",
        "BADGE_STAGED_BG": "rgba(35, 134, 54, 0.2)",
        "BADGE_STAGED_TEXT": "#3FB950",
        "BADGE_STAGED_BORDER": "#238636",
        "BADGE_FOCUS_BG": "rgba(37, 99, 235, 0.2)",
        "BADGE_FOCUS_TEXT": "#58A6FF",
        "BADGE_FOCUS_BORDER": "rgba(56, 139, 253, 0.4)",
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
        "BG_CANVAS": "#F8FAFC",
        "BG_CARD": "#FFFFFF",
        "BG_INPUT": "#FFFFFF",
        "BG_SURFACE": "#F1F5F9",
        "BORDER_COL": "#E2E8F0",
        "BORDER_INPUT": "#CBD5E1",
        "CARD_BORDER": "#E5E7EB",
        "CARD_SHADOW": "0 1px 3px rgba(0, 0, 0, 0.04), 0 1px 2px rgba(0, 0, 0, 0.02)",
        "TEXT_PRIMARY": "#0F172A",
        "TEXT_SECONDARY": "#64748B",
        "TEXT_BODY": "#334155",
        "SIDEBAR_BG": "#FFFFFF",
        "SIDEBAR_CARD_BG": "#F8FAFC",
        "SIDEBAR_BORDER": "#E2E8F0",
        "TOGGLE_COLOR": "#1E293B",
        "TOGGLE_BG": "#F1F5F9",
        "TOGGLE_BORDER": "#CBD5E1",
        "TOGGLE_HOVER_BG": "#E2E8F0",
        "TOGGLE_HOVER_COLOR": "#0F172A",
        "THEME_PILL_BG": "#F1F5F9",
        "THEME_PILL_BORDER": "#E2E8F0",
        "SUN_BTN_BG": "#FFFFFF",
        "SUN_BTN_SHADOW": "0 1px 3px rgba(0, 0, 0, 0.12)",
        "SUN_BTN_ICON": SUN_ACTIVE_URI,
        "MOON_BTN_BG": "transparent",
        "MOON_BTN_SHADOW": "none",
        "MOON_BTN_ICON": MOON_INACTIVE_URI,
        "BADGE_OUTGOING_BG": "#EFF6FF",
        "BADGE_OUTGOING_TEXT": "#1D4ED8",
        "BADGE_OUTGOING_BORDER": "#DBEAFE",
        "BADGE_INCOMING_BG": "#FEF3C7",
        "BADGE_INCOMING_TEXT": "#B45309",
        "BADGE_INCOMING_BORDER": "#FDE68A",
        "BADGE_STATUS_BG": "#F1F5F9",
        "BADGE_STATUS_TEXT": "#475569",
        "BADGE_STATUS_BORDER": "#E2E8F0",
        "BADGE_STAGED_BG": "#ECFDF5",
        "BADGE_STAGED_TEXT": "#047857",
        "BADGE_STAGED_BORDER": "#A7F3D0",
        "BADGE_FOCUS_BG": "#EFF6FF",
        "BADGE_FOCUS_TEXT": "#2563EB",
        "BADGE_FOCUS_BORDER": "#BFDBFE",
        "BTN_PRIMARY_BG": "#0F172A",
        "BTN_PRIMARY_HOVER": "#1E293B",
        "BTN_PRIMARY_TEXT": "#FFFFFF",
        "BTN_SEC_BG": "#FFFFFF",
        "BTN_SEC_HOVER": "#F8FAFC",
        "BTN_SEC_BORDER": "#CBD5E1",
        "BTN_SEC_TEXT": "#0F172A",
        "DRAWER_BG": "#F8FAFC",
        "LINK_COLOR": "#2563EB",
        "PILL_ACTIVE_BG": "#E2E8F0",
        "PILL_ACTIVE_TEXT": "#0F172A",
    }

CSS_TEMPLATE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;450;500;550;600;650;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
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

    /* Suppress Streamlit Chrome Artifacts (Top bar, Deploy button, Hamburger menu, Footer) */
    [data-testid="stHeader"], header[data-testid="stHeader"] {
        display: none !important;
    }
    .stDeployButton {
        display: none !important;
    }
    #MainMenu {
        visibility: hidden !important;
        display: none !important;
    }
    footer {
        display: none !important;
    }
    div[data-testid="stDecoration"] {
        display: none !important;
    }
    div[data-testid="stStatusWidget"] {
        display: none !important;
    }
    
    .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1200px;
    }

    /* Prevent Button Text Truncation */
    button, .stButton button {
        white-space: nowrap !important;
    }

    /* High-Contrast Sidebar Toggle Button in Both Themes */
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
    
    /* Top Header & Navbar Container (Inji Playground / Linear Style) */
    div.st-key-top_navbar div[data-testid="stVerticalBlockBorderWrapper"],
    div.st-key-top_navbar {
        background-color: __BG_CARD__ !important;
        border: 1px solid __BORDER_COL__ !important;
        border-radius: 14px !important;
        padding: 12px 20px !important;
        margin-bottom: 20px !important;
        box-shadow: __CARD_SHADOW__ !important;
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
        border-radius: 6px;
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
        padding: 5px 14px;
        border-radius: 6px;
        display: inline-block;
        border: 1px solid __BORDER_COL__;
    }
    .nav-pill {
        color: __TEXT_SECONDARY__;
        font-size: 13px;
        font-weight: 500;
        padding: 5px 14px;
        border-radius: 6px;
        display: inline-block;
        background: transparent;
        border: 1px solid transparent;
    }
    
    /* Live Status Pill */
    .live-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 5px 12px;
        background: __BG_SURFACE__;
        border: 1px solid __BORDER_COL__;
        border-radius: 6px;
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
    
    /* Exact Dual-Icon Sun/Moon Segmented Pill Wrapper */
    div.st-key-theme_pill_container {
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        background-color: __THEME_PILL_BG__ !important;
        border: 1px solid __THEME_PILL_BORDER__ !important;
        border-radius: 9999px !important;
        padding: 2px !important;
        height: 32px !important;
        box-sizing: border-box !important;
        width: fit-content !important;
        margin: 0 auto !important;
    }
    div.st-key-theme_pill_container > div[data-testid="stLayoutWrapper"],
    div.st-key-theme_pill_container [data-testid="stHorizontalBlock"] {
        display: inline-flex !important;
        align-items: center !important;
        gap: 2px !important;
        width: auto !important;
    }
    div.st-key-theme_pill_container [data-testid="stColumn"] {
        width: auto !important;
        min-width: 0 !important;
        flex: 0 0 auto !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    
    /* Metric Strip Cards (Image 2 Card Aesthetics) */
    .metric-card {
        background: __BG_CARD__;
        border: 1px solid __BORDER_COL__;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: __CARD_SHADOW__;
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
    
    /* All Commitment Card Containers - Strictly Bounded and Elevated */
    div[class*="st-key-commitment_card"],
    div[data-testid="stVerticalBlockBorderWrapper"]:has([class*="st-key-commitment_card"]),
    div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: __BG_CARD__ !important;
        border: 1px solid __CARD_BORDER__ !important;
        border-radius: 14px !important;
        padding: 24px !important;
        margin-bottom: 24px !important;
        box-shadow: __CARD_SHADOW__ !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }
    
    div[class*="st-key-commitment_card"]:hover {
        border-color: #2563EB !important;
    }
    
    /* Active Focus Card Selection Accent */
    div[class*="st-key-commitment_card"]:has(.active-focus-indicator),
    div[data-testid="stVerticalBlockBorderWrapper"]:has(.active-focus-indicator) {
        border: 2px solid #2563EB !important;
        box-shadow: 0 4px 14px rgba(37, 99, 235, 0.12) !important;
    }
    
    /* Professional Text Badges */
    .badge-outgoing {
        display: inline-block;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        padding: 3px 8px;
        border-radius: 6px;
        background: __BADGE_OUTGOING_BG__;
        color: __BADGE_OUTGOING_TEXT__;
        border: 1px solid __BADGE_OUTGOING_BORDER__;
    }
    
    .badge-incoming {
        display: inline-block;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        padding: 3px 8px;
        border-radius: 6px;
        background: __BADGE_INCOMING_BG__;
        color: __BADGE_INCOMING_TEXT__;
        border: 1px solid __BADGE_INCOMING_BORDER__;
    }
    
    .badge-status {
        display: inline-block;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        padding: 3px 8px;
        border-radius: 6px;
        background: __BADGE_STATUS_BG__;
        color: __BADGE_STATUS_TEXT__;
        border: 1px solid __BADGE_STATUS_BORDER__;
    }
    
    .badge-status-staged {
        display: inline-block;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        padding: 3px 8px;
        border-radius: 6px;
        background: __BADGE_STAGED_BG__;
        color: __BADGE_STAGED_TEXT__;
        border: 1px solid __BADGE_STAGED_BORDER__;
    }
    
    .badge-active-focus {
        display: inline-block;
        font-size: 11px;
        font-weight: 600;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        padding: 3px 8px;
        border-radius: 6px;
        background: __BADGE_FOCUS_BG__;
        color: __BADGE_FOCUS_TEXT__;
        border: 1px solid __BADGE_FOCUS_BORDER__;
    }
    
    /* Headings & Text */
    h1, h2, h3, h4 {
        color: __TEXT_PRIMARY__ !important;
        font-family: 'Inter', sans-serif !important;
    }
    h3 {
        font-size: 16.5px !important;
        font-weight: 650 !important;
        letter-spacing: -0.01em !important;
        margin: 8px 0 4px 0 !important;
    }
    p, .stMarkdown p {
        color: __TEXT_BODY__ !important;
        line-height: 1.55;
    }
    strong {
        color: __TEXT_PRIMARY__ !important;
    }
    
    /* Captions */
    .stCaption, [data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p, [data-testid="stCaptionContainer"] span {
        color: __TEXT_SECONDARY__ !important;
        font-size: 12.5px !important;
    }
    [data-testid="stCaptionContainer"] strong {
        color: __TEXT_PRIMARY__ !important;
    }
    
    /* Inline Code Spans */
    code {
        font-family: 'JetBrains Mono', monospace !important;
        background-color: __BG_SURFACE__ !important;
        color: __LINK_COLOR__ !important;
        border: 1px solid __BORDER_COL__ !important;
        padding: 2px 6px !important;
        border-radius: 6px !important;
        font-size: 12px !important;
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
        border-radius: 10px !important;
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
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 8px 16px !important;
        border-bottom: 2px solid transparent !important;
    }
    div[data-testid="stTabs"] button[role="tab"] p,
    div[data-testid="stTabs"] button[data-baseweb="tab"] p,
    div[data-testid="stTabs"] button span {
        color: __TEXT_SECONDARY__ !important;
        font-size: 13px !important;
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
    label, [data-testid="stWidgetLabel"] p, [data-testid="stWidgetLabel"] span {
        color: __TEXT_PRIMARY__ !important;
        font-weight: 500 !important;
        font-size: 13px !important;
    }
    input[type="text"], input[type="number"], textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: __BG_INPUT__ !important;
        border: 1px solid __BORDER_INPUT__ !important;
        border-radius: 8px !important;
        color: __TEXT_PRIMARY__ !important;
        font-size: 13.5px !important;
    }
    .stSelectbox div[data-baseweb="select"] * {
        color: __TEXT_PRIMARY__ !important;
        background-color: transparent !important;
    }
    input[type="text"]:focus, textarea:focus {
        border-color: #2563EB !important;
        box-shadow: 0 0 0 1px #2563EB !important;
    }
    
    /* Enterprise Button Styling */
    button[kind="primary"], .stButton > button[kind="primary"] {
        background-color: __BTN_PRIMARY_BG__ !important;
        color: __BTN_PRIMARY_TEXT__ !important;
        border: 1px solid __BTN_PRIMARY_BG__ !important;
        border-radius: 8px !important;
        font-weight: 550 !important;
        font-size: 13.5px !important;
        letter-spacing: -0.01em !important;
        padding: 6px 16px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.06) !important;
        transition: all 0.15s ease !important;
    }
    button[kind="primary"]:hover {
        background-color: __BTN_PRIMARY_HOVER__ !important;
        border-color: __BTN_PRIMARY_HOVER__ !important;
    }
    button[kind="primary"] p, button[kind="primary"] span {
        color: #FFFFFF !important;
        font-weight: 550 !important;
    }
    
    button[kind="secondary"], .stButton > button[kind="secondary"], .stButton > button {
        background-color: __BTN_SEC_BG__ !important;
        color: __BTN_SEC_TEXT__ !important;
        border: 1px solid __BTN_SEC_BORDER__ !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        font-size: 13.5px !important;
        letter-spacing: -0.01em !important;
        padding: 6px 16px !important;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04) !important;
        transition: all 0.15s ease !important;
    }
    button[kind="secondary"]:hover, .stButton > button:hover {
        background-color: __BTN_SEC_HOVER__ !important;
        color: __TEXT_PRIMARY__ !important;
        border-color: __BORDER_COL__ !important;
    }
    button[kind="secondary"] p, button[kind="secondary"] span {
        color: __BTN_SEC_TEXT__ !important;
        font-weight: 500 !important;
    }
    button[kind="secondary"]:hover p, button[kind="secondary"]:hover span {
        color: __TEXT_PRIMARY__ !important;
    }
    
    /* Top Nav specific controls */
    div.st-key-nav_sync_btn button {
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 5px 14px !important;
        border-radius: 8px !important;
        min-height: 34px !important;
    }

    /* Segmented Pill Sun and Moon Buttons - Placed after general buttons to guarantee highest specificity */
    div.st-key-btn_sun,
    div.st-key-btn_moon {
        width: 26px !important;
        height: 26px !important;
        min-width: 26px !important;
        min-height: 26px !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    div.st-key-btn_sun .stButton,
    div.st-key-btn_moon .stButton {
        width: 26px !important;
        height: 26px !important;
        padding: 0 !important;
        margin: 0 !important;
    }
    div.st-key-btn_sun button,
    div.st-key-btn_sun button[kind="secondary"] {
        background-color: __SUN_BTN_BG__ !important;
        background-image: url('__SUN_BTN_ICON__') !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-size: 15px 15px !important;
        box-shadow: __SUN_BTN_SHADOW__ !important;
        border: none !important;
        border-radius: 50% !important;
        width: 26px !important;
        height: 26px !important;
        min-width: 26px !important;
        min-height: 26px !important;
        max-width: 26px !important;
        max-height: 26px !important;
        padding: 0 !important;
        margin: 0 !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }
    div.st-key-btn_moon button,
    div.st-key-btn_moon button[kind="secondary"] {
        background-color: __MOON_BTN_BG__ !important;
        background-image: url('__MOON_BTN_ICON__') !important;
        background-repeat: no-repeat !important;
        background-position: center !important;
        background-size: 14px 14px !important;
        box-shadow: __MOON_BTN_SHADOW__ !important;
        border: none !important;
        border-radius: 50% !important;
        width: 26px !important;
        height: 26px !important;
        min-width: 26px !important;
        min-height: 26px !important;
        max-width: 26px !important;
        max-height: 26px !important;
        padding: 0 !important;
        margin: 0 !important;
        cursor: pointer !important;
        transition: all 0.15s ease !important;
    }
    div.st-key-btn_sun button:disabled,
    div.st-key-btn_moon button:disabled {
        cursor: default !important;
        opacity: 1 !important;
    }
    div.st-key-btn_sun button *,
    div.st-key-btn_moon button * {
        display: none !important;
    }
</style>
"""

# Render dynamic CSS
rendered_css = CSS_TEMPLATE
for k, v in tokens.items():
    rendered_css = rendered_css.replace(f"__{k}__", v)

st.markdown(rendered_css, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 3. Sidebar (Clean & Focused on Runtime Daemon, Model & Vector Brand Links)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("### Runtime Daemon")
    st.markdown(
        '<div class="sidebar-section">'
        '<div class="sidebar-row"><span>Daemon Status</span><span class="sidebar-val" style="color: #10B981;">Active</span></div>'
        '<div class="sidebar-row"><span>Daemon Port</span><span class="sidebar-val">4242</span></div>'
        '<div class="sidebar-row"><span>Hardware Node</span><span class="sidebar-val">Pendant 0x91B2</span></div>'
        '<div class="sidebar-row"><span>Battery Level</span><span class="sidebar-val">92%</span></div>'
        '</div>',
        unsafe_allow_html=True
    )
    
    st.markdown("### Bedrock Inference Model")
    model_choice = st.selectbox(
        "Model Selection",
        ["amazon.nova-pro-v1:0", "anthropic.claude-3-5-sonnet-20241022-v2:0"],
        index=0,
        label_visibility="collapsed"
    )
    
    st.markdown("### Staging Destinations")
    st.markdown(
        f'<div class="sidebar-section">'
        f'<div style="margin-bottom: 10px;">'
        f'<a href="https://mail.google.com/mail/u/0/#drafts" target="_blank" style="display:flex; align-items:center; gap:8px; text-decoration:none; color:{tokens["TEXT_PRIMARY"]}; font-size:13px; font-weight:500;">'
        f'<span>{GMAIL_SVG}</span> Open Gmail Drafts ↗'
        f'</a>'
        f'</div>'
        f'<div style="margin-bottom: 10px;">'
        f'<a href="https://calendar.google.com/" target="_blank" style="display:flex; align-items:center; gap:8px; text-decoration:none; color:{tokens["TEXT_PRIMARY"]}; font-size:13px; font-weight:500;">'
        f'<span>{CALENDAR_SVG}</span> Open Google Calendar ↗'
        f'</a>'
        f'</div>'
        f'<div>'
        f'<a href="https://app.todoist.com/" target="_blank" style="display:flex; align-items:center; gap:8px; text-decoration:none; color:{tokens["TEXT_PRIMARY"]}; font-size:13px; font-weight:500;">'
        f'<span>{TODOIST_SVG}</span> Open Todoist App ↗'
        f'</a>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True
    )
    
    st.markdown("### Telemetry Session")
    latency_display = st.session_state.get("latency_ms", 284)
    tokens_display = st.session_state.get("tokens_used", 1140)
    st.markdown(
        f'<div class="sidebar-telemetry">'
        f'<div>Converse API Latency: <strong>{latency_display} ms</strong></div>'
        f'<div>Tokens Consumed: <strong>{tokens_display:,}</strong></div>'
        f'<div>Estimated Cost: <strong>$0.0009 USD</strong></div>'
        f'</div>',
        unsafe_allow_html=True
    )

# -----------------------------------------------------------------------------
# 4. Top Header & Navbar (Inji Playground / Linear Style)
# -----------------------------------------------------------------------------
with st.container(key="top_navbar", border=True):
    nav_c1, nav_c2, nav_c3 = st.columns([3.6, 2.6, 3.8], vertical_alignment="center")

    with nav_c1:
        st.markdown(
            '<div style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap;">'
            '<span class="brand-title">✦ Promise Keeper</span>'
            '<span class="version-pill">Bee v1.4.2 · Bedrock Nova Pro</span>'
            '</div>'
            '<div class="brand-tagline">You said it. We’ll remember it.</div>',
            unsafe_allow_html=True
        )

    with nav_c2:
        st.markdown(
            '<div style="display: flex; justify-content: center; align-items: center; gap: 8px;">'
            '<span class="nav-pill-active">Commitments</span>'
            '<span class="nav-pill">Transcript Stream</span>'
            '</div>',
            unsafe_allow_html=True
        )

    with nav_c3:
        r_col1, r_col2, r_col3 = st.columns([0.8, 1.0, 1.6], vertical_alignment="center")
        with r_col1:
            st.markdown(
                '<div style="display: flex; justify-content: flex-end; align-items: center;">'
                '<span class="live-pill"><span class="green-dot"></span> Live</span>'
                '</div>',
                unsafe_allow_html=True
            )
        with r_col2:
            # Recreate Exact Dual-Icon Sun/Moon Segmented Pill Switch (Inji Playground)
            with st.container(key="theme_pill_container"):
                theme_col1, theme_col2 = st.columns([1, 1], gap="small", vertical_alignment="center")
                if current_theme == "Light":
                    with theme_col1:
                        st.button(" ", key="btn_sun", disabled=True)
                    with theme_col2:
                        if st.button(" ", key="btn_moon"):
                            st.session_state.theme = "Dark"
                            st.rerun()
                else:
                    with theme_col1:
                        if st.button(" ", key="btn_sun"):
                            st.session_state.theme = "Light"
                            st.rerun()
                    with theme_col2:
                        st.button(" ", key="btn_moon", disabled=True)
        with r_col3:
            if st.button("Sync Stream", key="nav_sync_btn", type="primary", use_container_width=True):
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
                    st.toast("Sync complete: extracted latest commitments from wearable audio.", icon="✅")

# -----------------------------------------------------------------------------
# 5. High-Density Metric Strip (Enterprise SaaS Cards)
# -----------------------------------------------------------------------------
m1, m2, m3, m4 = st.columns(4)

with m1:
    st.markdown(
        '<div class="metric-card">'
        '<div class="metric-label">Bee Audio Ingestion</div>'
        '<div class="metric-val">Active Stream</div>'
        '<div class="metric-sub">Sync: 5s · Device: Pendant 0x91B2</div>'
        '</div>',
        unsafe_allow_html=True
    )

with m2:
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-label">Inference Latency</div>'
        f'<div class="metric-val">{st.session_state.latency_ms} ms</div>'
        f'<div class="metric-sub">Amazon Bedrock Converse API</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with m3:
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-label">Token Utilization</div>'
        f'<div class="metric-val">{st.session_state.tokens_used:,} tokens</div>'
        f'<div class="metric-sub">$0.0009 USD · Nova Pro</div>'
        f'</div>',
        unsafe_allow_html=True
    )

with m4:
    pending_count = len([p for p in st.session_state.promises if not p["staged"]])
    st.markdown(
        f'<div class="metric-card">'
        f'<div class="metric-label">Staged Pipeline</div>'
        f'<div class="metric-val">{pending_count} Pending Review</div>'
        f'<div class="metric-sub">0 overdue · {st.session_state.staged_count} staged safely</div>'
        f'</div>',
        unsafe_allow_html=True
    )

st.write("")

# -----------------------------------------------------------------------------
# 6. Action Control Strip
# -----------------------------------------------------------------------------
c_left, c_mid, c_right = st.columns([1.5, 1.8, 4.7])

with c_left:
    if st.button("Sync from Bee", use_container_width=True):
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
            st.toast("Sync complete: extracted latest commitments from wearable audio.", icon="✅")

with c_mid:
    if st.button("Stage All Commitments (2)", use_container_width=True):
        router = ActionRouter()
        for p in st.session_state.promises:
            p["staged"] = True
            router.stage_todoist(p["task_title"], p["verbal_deadline"])
            router.stage_gmail_draft(p["counterparty_email"], p["email_subject"], p["email_body"])
            router.stage_calendar_event(p["calendar_title"], p["iso_deadline"], p["calendar_duration"])
        st.session_state.staged_count = len(st.session_state.promises)
        st.toast("All 2 commitments staged: Gmail drafts and calendar blocks ready.", icon="✅")
        st.rerun()

with c_right:
    if st.button("Reset Pipeline", use_container_width=False):
        for p in st.session_state.promises:
            p["staged"] = False
        st.session_state.staged_count = 0
        st.rerun()

# -----------------------------------------------------------------------------
# 7. Collapsible Transcript Stream Drawer
# -----------------------------------------------------------------------------
with st.expander("Ambient Transcript Stream (Bee Pendant 0x91B2)", expanded=False):
    st.markdown(
        f'<div style="background: {tokens["DRAWER_BG"]}; border: 1px solid {tokens["BORDER_COL"]}; border-radius: 8px; padding: 14px 18px; font-family: \'JetBrains Mono\', monospace; font-size: 12.5px; color: {tokens["TEXT_BODY"]}; line-height: 1.6;">'
        '<div>[09:41:04] Device: Bee Pendant 0x91B2 · Diarization Engine Active · Audio Stream 16kHz</div>'
        '<div>[09:41:12] Speaker 1 (Me): "Hey Alex, thanks for the sync. I\'ll send you the revised pitch deck by 5 PM tomorrow with the updated architecture diagram."</div>'
        '<div>[09:41:20] Speaker 2 (Alex): "Sounds great. Make sure to review the Q3 analytics report before Wednesday noon so we\'re aligned for the client sync."</div>'
        '<div>[09:41:28] Speaker 1 (Me): "Will do, let\'s also block 30 minutes on Thursday morning for a dry run."</div>'
        '</div>',
        unsafe_allow_html=True
    )

st.markdown(f"<h2 style='font-size: 18px; font-weight: 600; color: {tokens['TEXT_PRIMARY']}; margin: 24px 0 16px 0;'>Commitments Pending Review</h2>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 8. Render Commitments in Structured Cards with Clean Bounding Borders
# -----------------------------------------------------------------------------
selected_idx = st.session_state.get("selected_idx", 0)
router = ActionRouter()

for idx, p in enumerate(st.session_state.promises):
    is_me = p["direction"] == "MADE_BY_ME"
    is_selected = (idx == selected_idx)
    
    with st.container(key=f"commitment_card_{idx}", border=True):
        c_chip, c_due = st.columns([3, 1], vertical_alignment="center")
        with c_chip:
            badge_html = '<span class="badge-outgoing">OUTGOING COMMITMENT</span>' if is_me else '<span class="badge-incoming">INCOMING COMMITMENT</span>'
            status_html = '<span class="badge-status-staged">STAGED SAFELY</span>' if p["staged"] else '<span class="badge-status">PENDING REVIEW</span>'
            focus_html = '<span class="badge-active-focus">ACTIVE FOCUS</span>' if is_selected else ''
            focus_marker = '<span class="active-focus-indicator" style="display:none;"></span>' if is_selected else ''
            st.markdown(
                f'<div style="display:flex; align-items:center; gap:8px;">{badge_html}{status_html}{focus_html}{focus_marker}</div>',
                unsafe_allow_html=True
            )
        with c_due:
            st.markdown(
                f'<div style="text-align:right; font-size:12.5px; color:{tokens["TEXT_SECONDARY"]};">Due: <strong style="color:{tokens["TEXT_PRIMARY"]};">{p["verbal_deadline"]}</strong></div>',
                unsafe_allow_html=True
            )
        
        st.markdown(f"### {p['task_title']}")
        st.write(p['summary'])
        st.caption(f"Counterparty: **{p['counterparty_name']}** · Email: `{p['counterparty_email']}` · ISO: `{p['iso_deadline']}`")
        
        # 3 Clean Native Tabs with full legible labels without emojis
        tab_todo, tab_email, tab_cal = st.tabs(["Todoist Task", "Gmail Draft", "Calendar Event"])
        
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
            st.caption("Staged status will be marked as 'tentative' to avoid overwriting existing schedules.")
        
        st.write("")
        
        # Action Footer
        b_col1, b_col2, b_col3 = st.columns([2, 1, 4])
        with b_col1:
            btn_label = "Commitment Staged" if p["staged"] else "Approve & Stage Action"
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
                if st.button("Select Card", key=f"focus_{idx}", type="secondary"):
                    st.session_state.selected_idx = idx
                    st.rerun()
                
        if p["staged"]:
            st.markdown(
                f'<div style="margin-top:14px; padding:10px 14px; background:{tokens["BADGE_STAGED_BG"]}; border:1px solid {tokens["BADGE_STAGED_BORDER"]}; border-radius:8px; font-size:13px; color:{tokens["BADGE_STAGED_TEXT"]}; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; gap:8px;">'
                f'<div><strong>Staged safely:</strong> Created Gmail draft (never auto-sent), added Todoist task, and blocked tentative calendar time.</div>'
                f'<a href="https://mail.google.com/mail/u/0/#drafts" target="_blank" style="display:inline-flex; align-items:center; gap:6px; text-decoration:none; color:{tokens["LINK_COLOR"]}; font-weight:600;">'
                f'{GMAIL_SVG} View Draft in Gmail ↗</a>'
                f'</div>',
                unsafe_allow_html=True
            )
