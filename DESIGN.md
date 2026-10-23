---
name: Promise Keeper
description: Ambient AI staging engine with deterministic human review
colors:
  primary: "#0F172A"
  primary-hover: "#1E293B"
  canvas-dark: "#0B0F17"
  card-dark: "#161B22"
  border-dark: "#262F3D"
  text-main-dark: "#F1F5F9"
  text-muted-dark: "#94A3B8"
  canvas-light: "#F8F9FA"
  card-light: "#FFFFFF"
  border-light: "#E5E7EB"
  text-main-light: "#111827"
  text-muted-light: "#6B7280"
  success-dark: "#10B981"
  success-light: "#059669"
  warning-dark: "#F59E0B"
  warning-light: "#D97706"
  danger-dark: "#EF4444"
  danger-light: "#DC2626"
typography:
  fontFamily: "-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif"
  fontMono: "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
rounded:
  sm: "6px"
  md: "10px"
  lg: "14px"
  full: "9999px"
spacing:
  xs: "4px"
  sm: "8px"
  md: "16px"
  lg: "24px"
  xl: "32px"
components:
  button-primary:
    backgroundColor: "{colors.primary}"
    textColor: "#FFFFFF"
    rounded: "{rounded.md}"
    padding: "8px 18px"
  metric-card:
    backgroundColor: "{colors.card-light}"
    rounded: "{rounded.lg}"
    padding: "18px 22px"
---

# Design System: Promise Keeper

## Overview

Promise Keeper is an executive tool designed for ambient conversation triage and commitment staging. Its interface favors precision, scannability, and high contrast over decoration. The design rejects common AI slop patterns (such as thick colored side-border tabs, generic emoji iconography, nested card bloat, and low-contrast text) in favor of crisp typographic hierarchy, bespoke vector marks, enclosed tinted card structures, and authentic browser surface finishes.

## Colors

The palette is engineered to exceed WCAG AA contrast standards (minimum 4.5:1 for body copy and 3:1 for large display elements) in both Dark and Light modes:

- **Light Mode Canvas & Cards**: `#F8FAFC` background with pure white `#FFFFFF` cards, framed with `#E2E8F0` hairline borders. Main text `#0F172A` (16.2:1 contrast ratio against white) and secondary text `#475569` (5.8:1 contrast).
- **Dark Mode Canvas & Cards**: `#0F141C` deep obsidian canvas with `#161D27` elevated slate cards, framed with `#263040` subtle borders. Main text `#F8FAFC` (15.1:1 contrast) and secondary text `#94A3B8` (7.2:1 contrast).
- **Semantic Accents**:
  - **Commitment / Identity**: Primary blue `#2563EB` (light) / `#3B82F6` (dark).
  - **Live Ingestion / Connected**: Emerald `#059669` (light) / `#10B981` (dark).
  - **Ambiguity Guard**: Amber `#D97706` (light) / `#F59E0B` (dark).
  - **Critical Alert**: Crimson `#DC2626` (light) / `#EF4444` (dark).

## Typography

- **System Font Stack**: Native `-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif` for fast rendering, clean kerning, and zero layout shift.
- **Monospace Stack**: `ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace` strictly reserved for timestamps, hardware telemetry, token counts, and email addresses. Never used as decorative costume.
- **Tabular Numerals**: `font-variant-numeric: tabular-nums` applied to metric counts and latency timers to eliminate jitter during real-time data updates.
- **Hierarchy Scale**:
  - Page Title: 20px / 700 weight / -0.02em tracking.
  - Section Headers: 16px / 650 weight.
  - Card Titles: 15.5px / 650 weight.
  - Body Text: 13.5px–14px / 400 weight / 1.5 line height. Minimum text size is 12px for badges and metadata.

## Layout

- **Container Insets**: Generous padding (18–24px) preventing cramped cards.
- **Grid Structure**: 4-column scannable metric strip followed by vertically bounded commitment cards.
- **Responsive Insets**: Maximum container width bounded to 1200px for optimal reading measure.

## Elevation & Depth

- Elevation is declared once: crisp 1px borders with subtle ambient diffuse drop shadow (`box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04)` in light mode, `box-shadow: 0 1px 3px rgba(0, 0, 0, 0.25)` in dark mode).
- No zero-blur offset block shadows or multi-border ghost effects.

## Shapes

- Small controls (badges, status pills): 9999px (pill).
- Interactive buttons and input fields: 8px.
- Enclosed quote callouts and expanders: 10px.
- Main commitment cards: 14px.

## Components

- **Commitment Cards**: Enclosed bounded containers with distinct metadata header, spoken dialogue quote box, ambiguity warnings (when confidence < 70%), editable staged fields, and atomic staging actions.
- **Spoken Quote Callout**: Replaces AI side-tabs (`border-left: 3px`) with fully enclosed tinted background (`#F1F5F9` light / `#1E2633` dark) and 1px border.
- **Status Indicators**: Clean SVG status dots and badges with explicit semantic color pairings meeting WCAG AA.
- **Vector Icons**: Hand-crafted, pixel-aligned inline SVGs for microphone, audio waveform, Gmail, Calendar, Todoist, sun/moon theme toggle, and checkmarks. Zero unicode emoji iconography.

## Do's and Don'ts

### Do
- Use enclosed tinted containers with 1px hairline borders for callouts and quotes.
- Enforce tabular numbers on all live metrics and timestamps.
- Ensure high contrast for both light and dark themes.
- Implement browser surface craftsmanship (`::selection`, custom scrollbar, `:focus-visible`).
- Preserve strict human review before staging to external APIs.

### Don't
- Never use colored `border-left` / `border-right` side-tabs on cards or alerts.
- Never use raw text emojis as icons (`🎙️`, `⚡`, `⚠️`, `✓`, `☀️`, `🌙`).
- Never use eyebrow / kicker labels above headings.
- Never use low-contrast washed-out text below 4.5:1 ratio.
- Never autonomously send emails or dispatch unapproved actions.
