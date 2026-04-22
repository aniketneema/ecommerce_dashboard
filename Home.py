import streamlit as st

st.set_page_config(
    page_title="RetailIQ — Analytics Suite",
    page_icon="🏪",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,300&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background: #080c18; color: #e2e8f0; }

section[data-testid="stSidebar"] {
    background: #0c1022 !important;
    border-right: 1px solid #1a2340;
}
section[data-testid="stSidebar"] * { color: #94a3b8 !important; }

.hero {
    text-align: center;
    padding: 60px 20px 40px;
}
.hero-tag {
    display: inline-block;
    font-size: 11px; letter-spacing: 3px; text-transform: uppercase;
    color: #3b82f6; font-weight: 600; margin-bottom: 20px;
    border: 1px solid #1e3a6e; border-radius: 20px; padding: 4px 16px;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 58px; font-weight: 800; line-height: 1.05;
    background: linear-gradient(135deg, #f1f5f9 30%, #3b82f6 70%, #10b981 100%);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 20px;
}
.hero-sub {
    font-size: 18px; color: #64748b; max-width: 560px; margin: 0 auto 40px;
    line-height: 1.7; font-weight: 300;
}

.card-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; max-width: 960px; margin: 0 auto 60px; }
.dash-card {
    background: linear-gradient(145deg, #0f1729 0%, #131e35 100%);
    border: 1px solid #1a2d50;
    border-radius: 20px; padding: 32px 28px;
    transition: all 0.3s ease; cursor: pointer; position: relative; overflow: hidden;
}
.dash-card::before {
    content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; border-radius: 20px 20px 0 0;
}
.dash-card.blue::before   { background: linear-gradient(90deg, #3b82f6, #06b6d4); }
.dash-card.green::before  { background: linear-gradient(90deg, #10b981, #84cc16); }
.dash-card.purple::before { background: linear-gradient(90deg, #8b5cf6, #ec4899); }

.card-icon { font-size: 36px; margin-bottom: 14px; }
.card-title { font-family: 'Syne', sans-serif; font-size: 18px; font-weight: 700; color: #e2e8f0; margin-bottom: 8px; }
.card-desc  { font-size: 13px; color: #475569; line-height: 1.6; }
.card-tags  { margin-top: 16px; display: flex; flex-wrap: wrap; gap: 6px; }
.tag {
    font-size: 10px; letter-spacing: 0.5px; padding: 3px 10px;
    border-radius: 20px; font-weight: 500;
}
.tag.blue   { background: #0f2444; color: #60a5fa; }
.tag.green  { background: #052e16; color: #4ade80; }
.tag.purple { background: #2d1b69; color: #c4b5fd; }

.stats-bar {
    display: grid; grid-template-columns: repeat(4, 1fr);
    gap: 1px; background: #1a2340;
    border: 1px solid #1a2340; border-radius: 14px;
    overflow: hidden; max-width: 760px; margin: 0 auto 60px;
}
.stat-box {
    background: #0f1729; padding: 24px 20px; text-align: center;
}
.stat-num { font-family: 'Syne', sans-serif; font-size: 26px; font-weight: 800; color: #f1f5f9; }
.stat-lbl { font-size: 11px; color: #475569; letter-spacing: 1px; text-transform: uppercase; margin-top: 4px; }

.nav-hint {
    text-align: center; color: #334155; font-size: 13px;
    padding: 20px; border-top: 1px solid #1a2340; margin-top: 20px;
}
</style>
""", unsafe_allow_html=True)

# ── HERO ──────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-tag">🏪 E-Commerce Intelligence Suite</div>
    <div class="hero-title">RetailIQ<br>Analytics Hub</div>
    <div class="hero-sub">
        Three powerful dashboards. One unified platform.
        Built to showcase what modern data storytelling looks like.
    </div>
</div>
""", unsafe_allow_html=True)

# ── STATS BAR ─────────────────────────────────────────────────
st.markdown("""
<div class="stats-bar">
    <div class="stat-box"><div class="stat-num">5,000+</div><div class="stat-lbl">Orders Analysed</div></div>
    <div class="stat-box"><div class="stat-num">₹11.3Cr</div><div class="stat-lbl">Revenue Tracked</div></div>
    <div class="stat-box"><div class="stat-num">20</div><div class="stat-lbl">Campaigns</div></div>
    <div class="stat-box"><div class="stat-num">15</div><div class="stat-lbl">SKUs Monitored</div></div>
</div>
""", unsafe_allow_html=True)

# ── DASHBOARD CARDS ───────────────────────────────────────────
st.markdown("""
<div class="card-grid">

  <div class="dash-card blue">
    <div class="card-icon">📈</div>
    <div class="card-title">Sales Performance</div>
    <div class="card-desc">Revenue vs targets, profit waterfall, weekly trends, regional breakdown, and customer segmentation — all in one view.</div>
    <div class="card-tags">
      <span class="tag blue">Revenue</span>
      <span class="tag blue">Margins</span>
      <span class="tag blue">Trends</span>
      <span class="tag blue">RFM</span>
    </div>
  </div>

  <div class="dash-card green">
    <div class="card-icon">📦</div>
    <div class="card-title">Inventory & Operations</div>
    <div class="card-desc">Stock health by warehouse, supplier on-time delivery, reorder alerts, return analysis, and purchase order tracking.</div>
    <div class="card-tags">
      <span class="tag green">Stock Levels</span>
      <span class="tag green">Suppliers</span>
      <span class="tag green">Returns</span>
      <span class="tag green">POs</span>
    </div>
  </div>

  <div class="dash-card purple">
    <div class="card-icon">📣</div>
    <div class="card-title">Marketing & Acquisition</div>
    <div class="card-desc">Campaign ROAS, CAC by channel, conversion funnel, traffic trends, and spend vs revenue attribution.</div>
    <div class="card-tags">
      <span class="tag purple">ROAS</span>
      <span class="tag purple">CAC</span>
      <span class="tag purple">Funnel</span>
      <span class="tag purple">Channels</span>
    </div>
  </div>

</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="nav-hint">
    👈 Use the sidebar to navigate between dashboards &nbsp;·&nbsp;
    All dashboards share the same date & region filters
</div>
""", unsafe_allow_html=True)
