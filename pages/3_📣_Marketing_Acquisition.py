import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots   # ← imported correctly here
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import *

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("<style>.stTabs [aria-selected='true']{background:#2d1b69!important;color:#c4b5fd!important;}</style>", unsafe_allow_html=True)

@st.cache_data
def load():
    camp = pd.read_excel("Marketing_Dataset.xlsx", sheet_name="Campaigns")
    traf = pd.read_excel("Marketing_Dataset.xlsx", sheet_name="Daily_Traffic")
    traf["Date"] = pd.to_datetime(traf["Date"])
    return camp, traf

df_camp, df_traf = load()

with st.sidebar:
    st.markdown('<div class="sidebar-logo"><div class="sidebar-logo-text">📣 Marketing</div><div class="sidebar-logo-sub">Acquisition Dashboard</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section">Filters</div>', unsafe_allow_html=True)
    years     = st.multiselect("Year",     sorted(df_camp["Year"].unique()),    default=sorted(df_camp["Year"].unique()))
    channels  = st.multiselect("Channel",  sorted(df_camp["Channel"].unique()), default=sorted(df_camp["Channel"].unique()))
    platforms = st.multiselect("Platform", sorted(df_camp["Platform"].unique()),default=sorted(df_camp["Platform"].unique()))
    min_roas  = st.slider("Min ROAS", 0.0, 15.0, 0.0, 0.5)

camp = df_camp[df_camp["Year"].isin(years)&df_camp["Channel"].isin(channels)&df_camp["Platform"].isin(platforms)&(df_camp["ROAS"]>=min_roas)]
traf = df_traf[df_traf["Year"].isin(years)&df_traf["Channel"].isin(channels)]

ts   = camp["Spend"].sum(); tr  = camp["Revenue"].sum()
roas = round(tr/ts,2) if ts else 0
conv = camp["Conversions"].sum(); nc = camp["New_Customers"].sum()
cac  = round(ts/nc,0) if nc else 0
imp  = camp["Impressions"].sum(); ctr = camp["CTR_%"].mean(); cvr = camp["Conv_Rate_%"].mean()

st.markdown('<div class="page-hero"><div class="page-hero-tag">RetailIQ · Marketing Intelligence</div><div class="page-hero-title">Marketing & Customer Acquisition</div><div class="page-hero-sub">Campaign ROAS · CAC optimisation · Conversion funnel · Traffic analytics · AI attribution</div></div>', unsafe_allow_html=True)

c1,c2,c3,c4,c5,c6 = st.columns(6)
kpi(c1,"💸","Total Ad Spend",   fmt_inr(ts),          f"{len(camp)} campaigns",  None, "#8b5cf6")
kpi(c2,"💰","Revenue Generated",fmt_inr(tr),          f"ROAS: {roas}x",          None, "#10b981")
kpi(c3,"📈","Blended ROAS",     f"{roas}x",           "revenue per ₹1 spent",    None, "#6366f1")
kpi(c4,"🎯","Avg CAC",          fmt_inr(cac),         f"{nc:,} new customers",   None, "#f59e0b")
kpi(c5,"👁️","Avg CTR",          f"{ctr:.2f}%",        f"{imp/1e6:.1f}M impress.",None, "#14b8a6")
kpi(c6,"🔁","Avg Conv. Rate",   f"{cvr:.2f}%",        f"{conv:,} conversions",   None, "#ef4444")
hr()

t1,t2,t3,t4 = st.tabs(["🎯 Campaign Performance","📊 Channel Analytics","🔁 Conversion Funnel","🤖 AI Insights"])

# ═══ TAB 1 ═══════════════════════════════════════════════════
with t1:
    ca,cb = st.columns([3,2])
    with ca:
        section("ROAS by Campaign (Bubble = Revenue)","#8b5cf6")
        fig=px.scatter(camp,x="Spend",y="ROAS",size="Revenue",color="Channel",color_discrete_sequence=COLORS,
            hover_name="Campaign_Name",hover_data={"Spend":True,"Revenue":True,"ROAS":True,"New_Customers":True},size_max=55,
            labels={"Spend":"Ad Spend (₹)"})
        fig.add_hline(y=1,line_dash="dot",line_color="#ef4444",annotation_text="Break-even (ROAS=1)",annotation_font_color="#ef4444",annotation_font_size=10)
        fig.add_hline(y=camp["ROAS"].mean(),line_dash="dot",line_color="#f59e0b",annotation_text=f"Avg {camp['ROAS'].mean():.1f}x",annotation_font_color="#f59e0b",annotation_font_size=10)
        fig.update_layout(**BASE_LAYOUT,height=360)
        st.plotly_chart(fig,use_container_width=True)

    with cb:
        section("Top Campaigns by ROAS","#10b981")
        top=camp.nlargest(8,"ROAS")
        for _,row in top.iterrows():
            rc="10b981" if row["ROAS"]>=3 else "f59e0b" if row["ROAS"]>=1.5 else "ef4444"
            st.markdown(f"""<div style="background:#0d1424;border:1px solid #141e35;border-left:3px solid #{rc};border-radius:10px;padding:12px 16px;margin-bottom:8px;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-size:13px;font-weight:600;color:#d4daf0;">{row['Campaign_Name']}</div>
                    <div style="font-size:11px;color:#3d5080;margin-top:2px;">{row['Channel']} · {fmt_inr(row['Spend'])} · {int(row['New_Customers'])} new customers</div>
                </div>
                <div style="font-size:22px;font-weight:800;color:#{rc};">{row['ROAS']}x</div>
            </div>""", unsafe_allow_html=True)

    hr()
    cc,cd = st.columns(2)
    with cc:
        section("Spend vs Revenue Overlay","#6366f1")
        cs=camp.sort_values("Spend",ascending=True).tail(12)
        fig2=go.Figure()
        fig2.add_trace(go.Bar(y=cs["Campaign_Name"],x=cs["Spend"],name="Spend",orientation="h",marker_color=COLORS[0],opacity=0.7,marker_line_width=0))
        fig2.add_trace(go.Bar(y=cs["Campaign_Name"],x=cs["Revenue"],name="Revenue",orientation="h",marker_color=COLORS[2],opacity=0.85,marker_line_width=0))
        fig2.update_layout(**BASE_LAYOUT,height=340,barmode="overlay")
        st.plotly_chart(fig2,use_container_width=True)
    with cd:
        section("Budget Utilization %","#f59e0b")
        bu=camp.sort_values("Budget_Utilization_%").tail(12)
        buc=["#ef4444" if v>100 else "#10b981" if v>80 else "#f59e0b" for v in bu["Budget_Utilization_%"]]
        fig3=go.Figure(go.Bar(x=bu["Budget_Utilization_%"],y=bu["Campaign_Name"],orientation="h",marker_color=buc,text=bu["Budget_Utilization_%"].map(lambda x:f"{x:.0f}%"),textposition="outside",textfont=dict(size=10,color=TEXT_COL)))
        fig3.add_vline(x=100,line_dash="dot",line_color="#ef4444",annotation_text="100%",annotation_font_color="#ef4444",annotation_font_size=10)
        fig3.update_layout(**BASE_LAYOUT,height=340)
        st.plotly_chart(fig3,use_container_width=True)

# ═══ TAB 2 ═══════════════════════════════════════════════════
with t2:
    ch2=camp.groupby("Channel").agg(Spend=("Spend","sum"),Revenue=("Revenue","sum"),
        Conversions=("Conversions","sum"),New_Cust=("New_Customers","sum")).reset_index()
    ch2["ROAS"]=(ch2["Revenue"]/ch2["Spend"]).round(2)
    ch2["CAC"]=(ch2["Spend"]/ch2["New_Cust"]).round(0)

    ca,cb = st.columns(2)
    with ca:
        section("Revenue & ROAS by Channel (Dual Axis)","#8b5cf6")
        # FIX: make_subplots is now correctly imported at top of file
        fig=make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(go.Bar(x=ch2["Channel"],y=ch2["Revenue"],name="Revenue",marker_color=COLORS[0],opacity=0.85,marker_line_width=0),secondary_y=False)
        fig.add_trace(go.Scatter(x=ch2["Channel"],y=ch2["ROAS"],name="ROAS",mode="markers+lines",marker=dict(color=COLORS[2],size=11,symbol="diamond"),line=dict(color=COLORS[2],width=2)),secondary_y=True)
        fig.update_layout(**BASE_LAYOUT,height=290)
        fig.update_yaxes(title_text="Revenue (₹)",secondary_y=False,gridcolor=GRID_COL,tickfont=dict(size=10,color=TEXT_COL))
        fig.update_yaxes(title_text="ROAS",secondary_y=True,gridcolor=GRID_COL,tickfont=dict(size=10,color=TEXT_COL),showgrid=False)
        st.plotly_chart(fig,use_container_width=True)
    with cb:
        section("CAC vs ROAS Efficiency Matrix","#10b981")
        fig2=px.scatter(ch2,x="CAC",y="ROAS",size="Spend",color="Channel",color_discrete_sequence=COLORS,text="Channel",size_max=50,labels={"CAC":"Customer Acquisition Cost (₹)"})
        fig2.update_traces(textposition="top center",textfont=dict(size=10))
        fig2.update_layout(**BASE_LAYOUT,height=290,showlegend=False)
        st.plotly_chart(fig2,use_container_width=True)

    cc,cd = st.columns(2)
    with cc:
        section("Platform Spend Split","#6366f1")
        pl=camp.groupby("Platform")["Spend"].sum().reset_index()
        fig3=px.pie(pl,names="Platform",values="Spend",hole=0.58,color_discrete_sequence=COLORS)
        fig3.update_traces(textinfo="percent+label",marker=dict(line=dict(color=CHART_BG,width=2)),textfont=dict(size=11))
        fig3.update_layout(paper_bgcolor=CHART_BG,height=270,showlegend=False,margin=dict(l=5,r=5,t=5,b=5),font=dict(family="Inter",color=TEXT_COL))
        st.plotly_chart(fig3,use_container_width=True)
    with cd:
        section("CTR vs Conv. Rate by Channel","#f59e0b")
        cr=camp.groupby("Channel").agg(CTR=("CTR_%","mean"),ConvRate=("Conv_Rate_%","mean"),CPC=("CPC","mean")).reset_index()
        fig4=px.scatter(cr,x="CTR",y="ConvRate",color="Channel",color_discrete_sequence=COLORS,text="Channel",size="CPC",size_max=35,labels={"CTR":"Avg CTR %","ConvRate":"Avg Conv. Rate %"})
        fig4.update_traces(textposition="top center",textfont=dict(size=10))
        fig4.update_layout(**BASE_LAYOUT,height=270,showlegend=False)
        st.plotly_chart(fig4,use_container_width=True)

    section("📋 Channel Performance Scorecard","#14b8a6")
    sc2=ch2.copy(); sc2["Spend"]=sc2["Spend"].map(fmt_inr); sc2["Revenue"]=sc2["Revenue"].map(fmt_inr)
    sc2["CAC"]=sc2["CAC"].map(lambda x:f"₹{x:,.0f}"); sc2["ROAS"]=sc2["ROAS"].map(lambda x:f"{x}x")
    sc2.columns=["Channel","Ad Spend","Revenue","Conversions","New Customers","ROAS","CAC"]
    st.dataframe(sc2,use_container_width=True)

# ═══ TAB 3 ═══════════════════════════════════════════════════
with t3:
    funnel_vals=[int(camp["Impressions"].sum()),int(camp["Clicks"].sum()),int(camp["Sessions"].sum()),int(camp["Conversions"].sum()),int(camp["New_Customers"].sum())]
    funnel_labels=["Impressions","Clicks","Sessions","Conversions","New Customers"]

    ca,cb = st.columns([1,2])
    with ca:
        section("Acquisition Funnel","#8b5cf6")
        for i,(label,val) in enumerate(zip(funnel_labels,funnel_vals)):
            pct=f"{val/funnel_vals[0]*100:.2f}% of impressions" if i>0 else "Top of funnel"
            drop=f"↓ {(1-val/funnel_vals[i-1])*100:.0f}% drop-off" if i>0 else ""
            bar_w=max(15,int(val/funnel_vals[0]*100))
            colors_f=["#8b5cf6","#6d28d9","#4c1d95","#10b981","#059669"]
            st.markdown(f"""<div class="funnel-step">
                <div>
                    <div class="f-label">{label}</div>
                    <div class="f-pct">{pct}</div>
                    <div style="font-size:10px;color:#ef4444;margin-top:2px;">{drop}</div>
                </div>
                <div class="f-val">{val:,}</div>
            </div>""", unsafe_allow_html=True)

    with cb:
        section("Funnel Drop-off Visualisation","#6366f1")
        fig=go.Figure(go.Funnel(
            y=funnel_labels, x=funnel_vals,
            textinfo="value+percent initial+percent previous",
            marker=dict(color=["#8b5cf6","#6d28d9","#4c1d95","#10b981","#059669"]),
            connector=dict(line=dict(color=GRID_COL,dash="dot",width=2)),
            textfont=dict(family="Inter",size=12,color="#f1f5f9")))
        fig.update_layout(paper_bgcolor=CHART_BG,plot_bgcolor=CHART_BG,font=dict(family="Inter",color=TEXT_COL),margin=dict(l=10,r=10,t=10,b=10),height=380)
        st.plotly_chart(fig,use_container_width=True)

    hr()
    cc,cd = st.columns(2)
    with cc:
        section("Conversion Rate by Channel","#10b981")
        cv2=camp.groupby("Channel").agg(Sessions=("Sessions","sum"),Conversions=("Conversions","sum")).reset_index()
        cv2["Conv_Rate"]=cv2["Conversions"]/cv2["Sessions"]*100
        fig2=px.bar(cv2.sort_values("Conv_Rate"),x="Conv_Rate",y="Channel",orientation="h",color="Conv_Rate",color_continuous_scale=["#1e3a5f","#8b5cf6","#10b981"],text=cv2.sort_values("Conv_Rate")["Conv_Rate"].map(lambda x:f"{x:.2f}%"))
        fig2.update_traces(textposition="outside",textfont=dict(size=11)); fig2.update_layout(**BASE_LAYOUT,height=270,coloraxis_showscale=False)
        st.plotly_chart(fig2,use_container_width=True)
    with cd:
        section("CPC vs Conv. Rate — Efficiency Quadrant","#f59e0b")
        ef=camp.groupby("Channel").agg(CPC=("CPC","mean"),ConvRate=("Conv_Rate_%","mean"),Spend=("Spend","sum")).reset_index()
        fig3=px.scatter(ef,x="CPC",y="ConvRate",size="Spend",color="Channel",color_discrete_sequence=COLORS,text="Channel",size_max=45,labels={"CPC":"CPC (₹)","ConvRate":"Conv. Rate %"})
        fig3.add_vline(x=ef["CPC"].mean(),line_dash="dot",line_color=GRID_COL)
        fig3.add_hline(y=ef["ConvRate"].mean(),line_dash="dot",line_color=GRID_COL)
        fig3.update_traces(textposition="top center",textfont=dict(size=10))
        fig3.update_layout(**BASE_LAYOUT,height=270,showlegend=False)
        st.plotly_chart(fig3,use_container_width=True)

# ═══ TAB 4 — AI INSIGHTS ═════════════════════════════════════
with t4:
    st.markdown("""<div style="background:linear-gradient(135deg,#150d29,#1a1035);border:1px solid #2d1b69;border-radius:16px;padding:20px 24px;margin-bottom:20px;">
        <div style="font-size:10px;letter-spacing:2px;color:#4c1d95;text-transform:uppercase;margin-bottom:6px;">Machine Learning</div>
        <div style="font-size:18px;font-weight:700;color:#e8edf8;">Marketing Intelligence</div>
        <div style="font-size:12px;color:#2d1b69;margin-top:4px;">ROAS forecasting · Campaign clustering · Attribution modelling · Spend optimisation</div>
    </div>""", unsafe_allow_html=True)

    ca,cb = st.columns(2)

    # ── ML 1: ROAS Forecast ─────────────────────────────────
    with ca:
        section("📈 ROAS Trend & Forecast","#8b5cf6")
        camp_t=camp.copy()
        camp_t["t"]=(camp_t["Year"]-camp_t["Year"].min())*12+camp_t["Month_Number"]
        mon_roas=camp_t.groupby("t").apply(lambda x:(x["Revenue"].sum()/x["Spend"].sum())).reset_index(name="ROAS")
        mdl=LinearRegression().fit(mon_roas[["t"]].values,mon_roas["ROAS"].values)
        t_max=mon_roas["t"].max(); ft=np.arange(t_max+1,t_max+5).reshape(-1,1); fc=mdl.predict(ft)
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=mon_roas["t"],y=mon_roas["ROAS"],mode="lines+markers",name="Actual ROAS",line=dict(color=COLORS[0],width=2),marker=dict(size=6)))
        fig.add_trace(go.Scatter(x=ft.flatten(),y=fc,mode="lines+markers",name="Forecast",line=dict(color="#10b981",width=2,dash="dot"),marker=dict(size=8,symbol="diamond",color="#10b981")))
        fig.add_hline(y=1,line_dash="dot",line_color="#ef4444",annotation_text="Break-even",annotation_font_color="#ef4444",annotation_font_size=10)
        fig.update_layout(**BASE_LAYOUT,height=280,xaxis_title="Month Index",yaxis_title="ROAS")
        st.plotly_chart(fig,use_container_width=True)
        st.markdown(f"""<div class="insight-box"><div class="insight-title">🔍 ROAS FORECAST</div>
            <div class="insight-row"><span class="insight-key">Next Month ROAS</span><span class="insight-val {'green' if fc[0]>1 else 'red'}">{fc[0]:.2f}x</span></div>
            <div class="insight-row"><span class="insight-key">Trend</span><span class="insight-val {'green' if mdl.coef_[0]>0 else 'red'}">{'📈 Improving' if mdl.coef_[0]>0 else '📉 Declining'}</span></div>
            <div class="insight-row"><span class="insight-key">Avg Blended ROAS</span><span class="insight-val purple">{mon_roas['ROAS'].mean():.2f}x</span></div>
        </div>""", unsafe_allow_html=True)

    # ── ML 2: Campaign Clustering ────────────────────────────
    with cb:
        section("🔵 Campaign Clustering (K-Means)","#6366f1")
        Xc=camp[["Spend","Revenue","ROAS","CTR_%","Conv_Rate_%"]].copy()
        Xn=MinMaxScaler().fit_transform(Xc)
        km=KMeans(n_clusters=3,random_state=42,n_init=10).fit(Xn)
        camp2=camp.copy(); camp2["Cluster"]=["Cluster "+str(l+1) for l in km.labels_]
        cluster_labels={
            camp2.groupby("Cluster")["ROAS"].mean().idxmax(): "🏆 Star Performers",
            camp2.groupby("Cluster")["Spend"].mean().idxmax(): "💰 High Spenders",
        }
        camp2["Cluster_Name"]=camp2["Cluster"].map(lambda x: cluster_labels.get(x, "📊 Average"))
        fig2=px.scatter(camp2,x="Spend",y="ROAS",color="Cluster_Name",size="Revenue",
            color_discrete_sequence=COLORS,text="Campaign_Name",size_max=30,
            labels={"Spend":"Ad Spend (₹)"})
        fig2.update_traces(textposition="top center",textfont=dict(size=8))
        fig2.update_layout(**BASE_LAYOUT,height=280)
        st.plotly_chart(fig2,use_container_width=True)
        cs=camp2.groupby("Cluster_Name").agg(Campaigns=("Campaign_Name","count"),Avg_ROAS=("ROAS","mean"),Avg_Spend=("Spend","mean")).reset_index()
        st.dataframe(cs.style.format({"Avg_ROAS":"{:.2f}x","Avg_Spend":"₹{:,.0f}"}),use_container_width=True,height=120)

    hr()

    # ── ML 3: Spend Optimisation Score ──────────────────────
    section("💡 AI Budget Allocation Optimiser","#10b981")
    camp3=camp.copy()
    camp3["Efficiency_Score"]=(
        MinMaxScaler().fit_transform(camp3[["ROAS"]])*40 +
        MinMaxScaler().fit_transform(camp3[["Conv_Rate_%"]])*30 +
        (1-MinMaxScaler().fit_transform(camp3[["CPC"]]))*20 +
        MinMaxScaler().fit_transform(camp3[["New_Customers"]])*10
    ).round(1)
    camp3["Recommended_Action"]=camp3["Efficiency_Score"].apply(
        lambda s: "🚀 Scale Up (↑ Budget)" if s>=70 else "✅ Maintain" if s>=45 else "⚠️ Optimise" if s>=25 else "🛑 Review / Pause")
    camp3=camp3.sort_values("Efficiency_Score",ascending=False)

    cc2,cd2 = st.columns(2)
    with cc2:
        fig3=px.bar(camp3.head(12).sort_values("Efficiency_Score"),x="Efficiency_Score",y="Campaign_Name",orientation="h",
            color="Efficiency_Score",color_continuous_scale=["#ef4444","#f59e0b","#10b981"],
            text=camp3.head(12).sort_values("Efficiency_Score")["Efficiency_Score"].map(lambda x:f"{x:.0f}"),
            labels={"Efficiency_Score":"Efficiency Score"})
        fig3.update_traces(textposition="outside",textfont=dict(size=10))
        fig3.add_vline(x=70,line_dash="dot",line_color="#10b981",annotation_text="Scale Up",annotation_font_color="#10b981",annotation_font_size=10)
        fig3.add_vline(x=25,line_dash="dot",line_color="#ef4444",annotation_text="Pause Risk",annotation_font_color="#ef4444",annotation_font_size=10)
        fig3.update_layout(**BASE_LAYOUT,height=320,coloraxis_showscale=False)
        st.plotly_chart(fig3,use_container_width=True)
    with cd2:
        disp=camp3[["Campaign_Name","Channel","ROAS","Efficiency_Score","Recommended_Action"]].head(12)
        disp.columns=["Campaign","Channel","ROAS","Score","Recommendation"]
        disp["ROAS"]=disp["ROAS"].map(lambda x:f"{x}x")
        st.dataframe(disp,use_container_width=True,height=340)

    hr()
    section("🎯 AI-Generated Marketing Recommendations","#f59e0b")
    ce2,cf2,cg2 = st.columns(3)
    scale_up=camp3[camp3["Efficiency_Score"]>=70]
    pause=camp3[camp3["Efficiency_Score"]<25]
    best_ch=ch2.loc[ch2["ROAS"].idxmax(),"Channel"]
    worst_ch=ch2.loc[ch2["CAC"].idxmax(),"Channel"]
    with ce2: rec_card("🚀 SCALE","success",f"Scale {len(scale_up)} High-Efficiency Campaigns",f"{len(scale_up)} campaigns scored 70+ on the efficiency index. Reallocating 20-30% more budget to these campaigns could significantly improve overall ROAS without increasing total spend.")
    with cf2: rec_card("🛑 PAUSE","urgent",f"Review {len(pause)} Under-Performing Campaigns",f"{len(pause)} campaigns scored below 25. Pause these and redirect spend to high-performing campaigns — especially {best_ch} which delivers the best ROAS across all channels.")
    with cg2: rec_card("💰 CAC","warning",f"Reduce CAC on {worst_ch}",f"{worst_ch} has the highest customer acquisition cost. A/B test new creatives, refine audience targeting, and optimise landing page conversion to bring CAC closer to your blended average.")

st.markdown('<div style="text-align:center;padding:24px 0 8px;color:#1e2d4a;font-size:11px;border-top:1px solid #141e35;margin-top:24px;">RetailIQ Analytics Suite · Marketing & Acquisition · Streamlit + Plotly + scikit-learn</div>', unsafe_allow_html=True)
