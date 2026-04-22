"""Shared styles, helpers, and ML utilities for RetailIQ."""
import pandas as pd
import numpy as np
import streamlit as st

# ── COLOURS ─────────────────────────────────────────────────
COLORS   = ["#6366f1","#10b981","#f59e0b","#ef4444","#8b5cf6","#14b8a6","#f97316","#ec4899","#3b82f6","#84cc16"]
CHART_BG = "#0d1117"
GRID_COL = "#1e2740"
TEXT_COL = "#8b9dc3"
ACCENT   = "#6366f1"

BASE_LAYOUT = dict(
    paper_bgcolor=CHART_BG,
    plot_bgcolor =CHART_BG,
    font=dict(family="Inter, DM Sans, sans-serif", color=TEXT_COL, size=12),
    xaxis=dict(gridcolor=GRID_COL, zeroline=False, tickfont=dict(size=11), linecolor=GRID_COL),
    yaxis=dict(gridcolor=GRID_COL, zeroline=False, tickfont=dict(size=11), linecolor=GRID_COL),
    margin=dict(l=12, r=12, t=36, b=12),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=11), bordercolor=GRID_COL),
    colorway=COLORS,
)

def fmt_inr(v):
    if v >= 1e7: return f"₹{v/1e7:.2f}Cr"
    if v >= 1e5: return f"₹{v/1e5:.1f}L"
    if v >= 1e3: return f"₹{v/1e3:.1f}K"
    return f"₹{v:,.0f}"

# ── SHARED CSS ───────────────────────────────────────────────
GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

html, body, [class*="css"], .stMarkdown { font-family: 'Inter', sans-serif !important; }

/* App background */
.stApp { background: #070b14 !important; color: #c9d4f0; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080e1d 0%, #0a1020 100%) !important;
    border-right: 1px solid #141e35 !important;
}
section[data-testid="stSidebar"] * { color: #6b7fa8 !important; font-family: 'Inter', sans-serif !important; }
section[data-testid="stSidebar"] .stSelectbox > label,
section[data-testid="stSidebar"] .stMultiSelect > label { color: #3d5080 !important; font-size: 10px !important; letter-spacing: 1.2px; text-transform: uppercase; }
[data-testid="stSidebar"] [data-baseweb="select"] { background: #0e1828 !important; border-color: #1a2d4a !important; }
[data-testid="stSidebar"] [data-baseweb="tag"] { background: #1a2d4a !important; }

/* Hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 2rem !important; max-width: 1400px !important; }

/* KPI Cards */
.kpi-wrap { display: grid; gap: 14px; }
.kpi { 
    background: linear-gradient(145deg, #0d1424 0%, #111c30 100%);
    border: 1px solid #1a2740;
    border-radius: 18px; padding: 22px 20px;
    position: relative; overflow: hidden;
    transition: box-shadow 0.3s;
}
.kpi:hover { box-shadow: 0 0 30px rgba(99,102,241,0.08); }
.kpi::after {
    content: ''; position: absolute; bottom: -20px; right: -20px;
    width: 80px; height: 80px; border-radius: 50%;
    opacity: 0.04;
}
.kpi-accent { position: absolute; top: 0; left: 0; right: 0; height: 2px; border-radius: 18px 18px 0 0; }
.kpi-icon  { font-size: 22px; margin-bottom: 12px; opacity: 0.9; }
.kpi-label { font-size: 10px; font-weight: 600; letter-spacing: 1.8px; text-transform: uppercase; color: #3d5080; margin-bottom: 6px; }
.kpi-value { font-size: 30px; font-weight: 800; color: #e8edf8; line-height: 1; letter-spacing: -1px; }
.kpi-sub   { font-size: 11px; color: #3d5080; margin-top: 6px; }
.kpi-delta { display: inline-flex; align-items: center; gap: 4px; font-size: 11px; font-weight: 600; padding: 3px 9px; border-radius: 20px; margin-top: 10px; }
.kpi-delta.up   { background: rgba(16,185,129,0.12); color: #34d399; border: 1px solid rgba(16,185,129,0.2); }
.kpi-delta.down { background: rgba(239,68,68,0.12);  color: #f87171; border: 1px solid rgba(239,68,68,0.2); }
.kpi-delta.neu  { background: rgba(107,114,128,0.12); color: #9ca3af; border: 1px solid rgba(107,114,128,0.2);}

/* Section headers */
.sh {
    display: flex; align-items: center; gap: 10px;
    font-size: 14px; font-weight: 700; color: #d4daf0;
    letter-spacing: 0.2px; margin: 4px 0 14px;
}
.sh-bar { width: 3px; height: 18px; border-radius: 2px; }

/* Chart card wrapper */
.chart-card {
    background: #0d1424; border: 1px solid #141e35;
    border-radius: 16px; padding: 20px 18px; margin-bottom: 6px;
}

/* Page title area */
.page-hero {
    background: linear-gradient(135deg, #0d1424 0%, #101828 100%);
    border: 1px solid #141e35; border-radius: 20px;
    padding: 28px 32px; margin-bottom: 24px;
    position: relative; overflow: hidden;
}
.page-hero::before {
    content: ''; position: absolute; top: -40px; right: -40px;
    width: 200px; height: 200px; border-radius: 50%;
    background: radial-gradient(circle, rgba(99,102,241,0.08) 0%, transparent 70%);
}
.page-hero-tag { font-size: 10px; letter-spacing: 2.5px; text-transform: uppercase; color: #4f5faa; font-weight: 600; margin-bottom: 8px; }
.page-hero-title { font-size: 28px; font-weight: 800; color: #e8edf8; line-height: 1.15; letter-spacing: -0.5px; }
.page-hero-sub   { font-size: 13px; color: #3d5080; margin-top: 6px; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    background: #0d1424; border-radius: 12px; padding: 5px;
    border: 1px solid #141e35; gap: 3px; overflow-x: auto;
}
.stTabs [data-baseweb="tab"] {
    background: transparent; color: #4a5a7a; border-radius: 9px;
    font-family: 'Inter', sans-serif !important; font-size: 12px; font-weight: 500;
    padding: 8px 16px !important; white-space: nowrap;
}
.stTabs [aria-selected="true"] { color: #e8edf8 !important; font-weight: 600 !important; }
.stTabs [data-baseweb="tab-panel"] { padding-top: 18px; }

/* ML Insight cards */
.insight-box {
    background: linear-gradient(135deg, #0f1a2e 0%, #101828 100%);
    border: 1px solid #1a2d4a; border-radius: 14px;
    padding: 18px 20px; margin-bottom: 10px;
}
.insight-title { font-size: 12px; font-weight: 700; color: #7c8fc4; letter-spacing: 0.5px; margin-bottom: 10px; }
.insight-row { display: flex; justify-content: space-between; align-items: center; padding: 6px 0; border-bottom: 1px solid #141e35; }
.insight-row:last-child { border-bottom: none; }
.insight-key { font-size: 12px; color: #5a6a8a; }
.insight-val { font-size: 13px; font-weight: 600; color: #c9d4f0; }
.insight-val.green { color: #34d399; }
.insight-val.orange { color: #fb923c; }
.insight-val.red { color: #f87171; }
.insight-val.purple { color: #a78bfa; }

/* Alert pills */
.pill { display:inline-block; font-size:10px; font-weight:600; padding:3px 10px; border-radius:20px; }
.pill-red    { background:rgba(239,68,68,0.15);    color:#f87171;  border:1px solid rgba(239,68,68,0.3);    }
.pill-yellow { background:rgba(245,158,11,0.15);   color:#fbbf24;  border:1px solid rgba(245,158,11,0.3);   }
.pill-green  { background:rgba(16,185,129,0.15);   color:#34d399;  border:1px solid rgba(16,185,129,0.3);   }
.pill-blue   { background:rgba(99,102,241,0.15);   color:#818cf8;  border:1px solid rgba(99,102,241,0.3);   }
.pill-purple { background:rgba(139,92,246,0.15);   color:#c4b5fd;  border:1px solid rgba(139,92,246,0.3);   }

/* Divider */
.hr { border:none; border-top:1px solid #141e35; margin:22px 0; }

/* Dataframe override */
[data-testid="stDataFrame"] { border: 1px solid #141e35 !important; border-radius: 12px !important; overflow: hidden; }

/* Sidebar logo */
.sidebar-logo {
    text-align: center; padding: 24px 0 16px;
    border-bottom: 1px solid #141e35; margin-bottom: 20px;
}
.sidebar-logo-text { font-size: 18px; font-weight: 800; color: #e8edf8; letter-spacing: -0.5px; }
.sidebar-logo-sub  { font-size: 9px; letter-spacing: 2.5px; color: #2a3a5a; text-transform: uppercase; margin-top: 3px; }
.sidebar-section   { font-size: 9px; letter-spacing: 1.8px; text-transform: uppercase; color: #2a3a5a; font-weight: 700; margin: 16px 0 8px; padding: 0 4px; }

/* Recommendation card */
.rec-card {
    background: linear-gradient(135deg, #0f1829 0%, #131e35 100%);
    border: 1px solid #1e2d4a; border-radius: 14px;
    padding: 16px 18px; margin-bottom: 10px;
    border-left: 3px solid;
    transition: transform 0.15s;
}
.rec-card:hover { transform: translateX(3px); }
.rec-card.urgent  { border-left-color: #ef4444; }
.rec-card.warning { border-left-color: #f59e0b; }
.rec-card.success { border-left-color: #10b981; }
.rec-card.info    { border-left-color: #6366f1; }
.rec-title { font-size: 13px; font-weight: 700; color: #d4daf0; margin-bottom: 4px; }
.rec-body  { font-size: 12px; color: #4a5a7a; line-height: 1.6; }
.rec-badge { display:inline-block; font-size:10px; font-weight:600; padding:2px 8px; border-radius:10px; margin-bottom:6px; }
.rec-badge.urgent  { background:rgba(239,68,68,0.15); color:#f87171; }
.rec-badge.warning { background:rgba(245,158,11,0.15); color:#fbbf24; }
.rec-badge.success { background:rgba(16,185,129,0.15); color:#34d399; }
.rec-badge.info    { background:rgba(99,102,241,0.15);  color:#818cf8; }

/* Funnel step */
.funnel-step { 
    background: #0d1424; border: 1px solid #141e35; border-radius: 10px;
    padding: 14px 20px; margin-bottom: 6px;
    display: flex; justify-content: space-between; align-items: center;
}
.f-label { font-size: 12px; color: #5a6a8a; }
.f-val   { font-family: 'Inter'; font-size: 20px; font-weight: 800; color: #e8edf8; }
.f-pct   { font-size: 11px; color: #3d5080; }
</style>
"""

def kpi(col, icon, label, value, sub="", delta=None, accent="#6366f1"):
    badge = ""
    if delta is not None:
        sign = "▲" if delta >= 0 else "▼"
        cls  = "up" if delta >= 0 else "down"
        badge = f'<span class="kpi-delta {cls}">{sign} {abs(delta):.1f}%</span>'
    col.markdown(f"""
    <div class="kpi">
        <div class="kpi-accent" style="background:{accent};"></div>
        <div class="kpi-icon">{icon}</div>
        <div class="kpi-label">{label}</div>
        <div class="kpi-value">{value}</div>
        <div class="kpi-sub">{sub}</div>
        {badge}
    </div>
    """, unsafe_allow_html=True)

def section(title, color="#6366f1"):
    st.markdown(f"""
    <div class="sh">
        <div class="sh-bar" style="background:{color};"></div>
        {title}
    </div>""", unsafe_allow_html=True)

def hr():
    st.markdown('<div class="hr"></div>', unsafe_allow_html=True)

def rec_card(badge_label, badge_cls, title, body):
    st.markdown(f"""
    <div class="rec-card {badge_cls}">
        <div class="rec-badge {badge_cls}">{badge_label}</div>
        <div class="rec-title">{title}</div>
        <div class="rec-body">{body}</div>
    </div>""", unsafe_allow_html=True)
