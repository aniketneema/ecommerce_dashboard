import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.linear_model import LinearRegression
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import *

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("<style>.stTabs [aria-selected='true']{background:#052e16!important;color:#34d399!important;}</style>", unsafe_allow_html=True)

@st.cache_data
def load():
    inv = pd.read_excel("Inventory_Operations_Dataset.xlsx", sheet_name="Inventory_Snapshot")
    po  = pd.read_excel("Inventory_Operations_Dataset.xlsx", sheet_name="Purchase_Orders")
    ret = pd.read_excel("Inventory_Operations_Dataset.xlsx", sheet_name="Returns_Refunds")
    po["Order_Date"]   = pd.to_datetime(po["Order_Date"])
    ret["Return_Date"] = pd.to_datetime(ret["Return_Date"])
    return inv, po, ret

df_inv, df_po, df_ret = load()

with st.sidebar:
    st.markdown('<div class="sidebar-logo"><div class="sidebar-logo-text">📦 Inventory</div><div class="sidebar-logo-sub">Operations Dashboard</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section">Filters</div>', unsafe_allow_html=True)
    cats      = st.multiselect("Category",     sorted(df_inv["Category"].unique()),  default=sorted(df_inv["Category"].unique()))
    whs       = st.multiselect("Warehouse",    sorted(df_inv["Warehouse"].unique()), default=sorted(df_inv["Warehouse"].unique()))
    years     = st.multiselect("Year",         sorted(df_po["Year"].unique()),        default=sorted(df_po["Year"].unique()))
    statuses  = st.multiselect("Stock Status", ["Healthy","Low","Critical","Overstocked"], default=["Healthy","Low","Critical","Overstocked"])

inv = df_inv[df_inv["Category"].isin(cats)&df_inv["Warehouse"].isin(whs)&df_inv["Stock_Status"].isin(statuses)]
po  = df_po[df_po["Year"].isin(years)&df_po["Category"].isin(cats)]
ret = df_ret[df_ret["Year"].isin(years)&df_ret["Category"].isin(cats)]

sv   = inv["Stock_Value"].sum()
crit = (inv["Stock_Status"]=="Critical").sum()
low  = (inv["Stock_Status"]=="Low").sum()
over = (inv["Stock_Status"]=="Overstocked").sum()
otr  = (po["On_Time"]=="Yes").mean()*100 if len(po) else 0
adel = po[po["Delay_Days"]>0]["Delay_Days"].mean()
tref = ret["Refund_Amount"].sum()

st.markdown('<div class="page-hero"><div class="page-hero-tag">RetailIQ · Operations Intelligence</div><div class="page-hero-title">Inventory & Operations Dashboard</div><div class="page-hero-sub">Stock health · Reorder alerts · Supplier performance · Returns analysis · Anomaly detection</div></div>', unsafe_allow_html=True)

c1,c2,c3,c4,c5,c6 = st.columns(6)
kpi(c1,"📦","Stock Value",        fmt_inr(sv),                      f"{len(inv)} SKU-WH pairs",  None, "#10b981")
kpi(c2,"🔴","Critical SKUs",      str(crit),                        f"{low} low stock",           None, "#ef4444")
kpi(c3,"📊","Overstocked SKUs",   str(over),                        "excess inventory",           None, "#f59e0b")
kpi(c4,"🚚","Supplier On-Time",   f"{otr:.1f}%",                    f"{len(po)} POs tracked",     None, "#6366f1")
kpi(c5,"⏱️","Avg Delay",          f"{adel:.1f}d" if not pd.isna(adel) else "0d", "when late",    None, "#8b5cf6")
kpi(c6,"↩️","Total Refunds",      fmt_inr(tref),                    f"{len(ret)} returns",        None, "#14b8a6")
hr()

t1,t2,t3,t4 = st.tabs(["🏪 Stock Health","🚚 Purchase Orders","↩️ Returns","🤖 AI Insights"])

# ═══ TAB 1 ═══════════════════════════════════════════════════
with t1:
    ca,cb = st.columns([2,1])
    with ca:
        section("Stock Levels by Product & Warehouse","#10b981")
        fig=px.bar(inv.sort_values("Current_Stock"),x="Current_Stock",y="Product_Name",color="Warehouse",orientation="h",barmode="group",color_discrete_sequence=COLORS,labels={"Current_Stock":"Units in Stock","Product_Name":"Product"})
        fig.update_layout(**BASE_LAYOUT,height=420)
        st.plotly_chart(fig,use_container_width=True)

    with cb:
        section("Stock Status Breakdown","#6366f1")
        sc=inv["Stock_Status"].value_counts().reset_index(); sc.columns=["Status","Count"]
        scm={"Healthy":"#10b981","Low":"#f59e0b","Critical":"#ef4444","Overstocked":"#8b5cf6"}
        fig2=px.pie(sc,names="Status",values="Count",hole=0.6,color="Status",color_discrete_map=scm)
        fig2.update_traces(textinfo="percent+label",marker=dict(line=dict(color=CHART_BG,width=2)),textfont=dict(size=11))
        fig2.update_layout(paper_bgcolor=CHART_BG,height=200,showlegend=False,margin=dict(l=5,r=5,t=5,b=5),font=dict(family="Inter",color=TEXT_COL))
        st.plotly_chart(fig2,use_container_width=True)

        section("🚨 Reorder Alerts","#ef4444")
        alerts=inv[inv["Stock_Status"].isin(["Critical","Low"])].drop_duplicates("SKU").head(6)
        for _,row in alerts.iterrows():
            color="#ef4444" if row["Stock_Status"]=="Critical" else "#f59e0b"
            icon="🔴" if row["Stock_Status"]=="Critical" else "🟡"
            fill="#2d0707" if row["Stock_Status"]=="Critical" else "#1a0f00"
            pct=int(row["Current_Stock"]/row["Reorder_Point"]*100)
            st.markdown(f"""<div style="background:{fill};border:1px solid {color}33;border-left:3px solid {color};border-radius:10px;padding:10px 14px;margin-bottom:8px;">
                <div style="display:flex;justify-content:space-between;align-items:center;">
                    <div>
                        <div style="font-size:12px;font-weight:600;color:#d4daf0;">{icon} {row['Product_Name']}</div>
                        <div style="font-size:10px;color:#4a5a7a;margin-top:2px;">{row['SKU']} · {row['Warehouse']}</div>
                    </div>
                    <div style="text-align:right;">
                        <div style="font-size:15px;font-weight:800;color:{color};">{row['Current_Stock']}</div>
                        <div style="font-size:9px;color:#4a5a7a;">/ {row['Reorder_Point']} ROP</div>
                    </div>
                </div>
                <div style="background:#0d1424;border-radius:4px;height:4px;margin-top:8px;overflow:hidden;">
                    <div style="background:{color};width:{min(pct,100)}%;height:100%;border-radius:4px;"></div>
                </div>
            </div>""", unsafe_allow_html=True)

    hr()
    cc,cd = st.columns(2)
    with cc:
        section("Stock Value by Category (Treemap)","#f59e0b")
        cv=inv.groupby("Category")["Stock_Value"].sum().reset_index()
        fig3=px.treemap(cv,path=["Category"],values="Stock_Value",color="Stock_Value",color_continuous_scale=["#0a0e1a","#10b981","#84cc16"])
        fig3.update_layout(paper_bgcolor=CHART_BG,margin=dict(l=0,r=0,t=0,b=0),height=260,coloraxis_showscale=False)
        st.plotly_chart(fig3,use_container_width=True)
    with cd:
        section("Inventory Coverage Ratio","#8b5cf6")
        ic=inv.groupby("Product_Name").agg(Stock=("Current_Stock","sum"),ROP=("Reorder_Point","mean")).reset_index()
        ic["Coverage"]=ic["Stock"]/ic["ROP"]
        ic=ic.sort_values("Coverage")
        cc2=[("#ef4444" if v<1 else "#f59e0b" if v<2 else "#10b981") for v in ic["Coverage"]]
        fig4=go.Figure(go.Bar(x=ic["Coverage"],y=ic["Product_Name"],orientation="h",marker_color=cc2,text=ic["Coverage"].map(lambda x:f"{x:.1f}x"),textposition="outside",textfont=dict(size=10,color=TEXT_COL)))
        fig4.add_vline(x=1,line_dash="dot",line_color="#ef4444",annotation_text="Reorder",annotation_font_color="#ef4444",annotation_font_size=10)
        fig4.update_layout(**BASE_LAYOUT,height=260)
        st.plotly_chart(fig4,use_container_width=True)

    section("📋 Full Inventory Table","#14b8a6")
    di=inv[["SKU","Product_Name","Category","Warehouse","Current_Stock","Reorder_Point","Max_Stock","Stock_Status","Stock_Value"]].copy()
    di["Stock_Value"]=di["Stock_Value"].map(fmt_inr)
    st.dataframe(di.style.applymap(lambda v:"color:#ef4444;font-weight:600" if v=="Critical" else "color:#fbbf24;font-weight:600" if v=="Low" else "color:#a78bfa" if v=="Overstocked" else "color:#34d399",subset=["Stock_Status"]),use_container_width=True,height=300)

# ═══ TAB 2 ═══════════════════════════════════════════════════
with t2:
    ca,cb = st.columns(2)
    with ca:
        section("PO Value by Month","#10b981")
        pm=po.groupby(["Year","Month_Number","Month"]).agg(Orders=("PO_ID","count"),Value=("Total_Cost","sum")).reset_index().sort_values(["Year","Month_Number"])
        pm["Period"]=pm["Month"].str[:3]+" "+pm["Year"].astype(str)
        fig=px.bar(pm,x="Period",y="Value",color="Year",color_discrete_sequence=[COLORS[0],COLORS[2]],labels={"Value":"PO Value (₹)"},barmode="group")
        fig.update_layout(**BASE_LAYOUT,height=270,xaxis_tickangle=-30,xaxis_tickfont=dict(size=9))
        st.plotly_chart(fig,use_container_width=True)
    with cb:
        section("PO Status Distribution","#6366f1")
        ps=po["Status"].value_counts().reset_index(); ps.columns=["Status","Count"]
        pc={"Delivered":"#10b981","In Transit":"#6366f1","Pending":"#f59e0b","Delayed":"#ef4444"}
        fig2=px.bar(ps,x="Status",y="Count",color="Status",color_discrete_map=pc,text="Count")
        fig2.update_traces(textposition="outside"); fig2.update_layout(**BASE_LAYOUT,height=270,showlegend=False)
        st.plotly_chart(fig2,use_container_width=True)

    cc,cd = st.columns(2)
    with cc:
        section("Supplier On-Time Delivery %","#f59e0b")
        so=po.groupby("Supplier").apply(lambda x:(x["On_Time"]=="Yes").mean()*100).reset_index(name="OnTime_%")
        fig3=px.bar(so.sort_values("OnTime_%"),x="OnTime_%",y="Supplier",orientation="h",color="OnTime_%",color_continuous_scale=["#ef4444","#f59e0b","#10b981"],text=so.sort_values("OnTime_%")["OnTime_%"].map(lambda x:f"{x:.0f}%"))
        fig3.add_vline(x=80,line_dash="dot",line_color="#f59e0b",annotation_text="80% SLA",annotation_font_color="#f59e0b")
        fig3.update_traces(textposition="outside",textfont=dict(size=11)); fig3.update_layout(**BASE_LAYOUT,height=270,coloraxis_showscale=False)
        st.plotly_chart(fig3,use_container_width=True)
    with cd:
        section("Delay Distribution (days)","#8b5cf6")
        dl=po[po["Delay_Days"]>0]
        fig4=px.histogram(dl,x="Delay_Days",nbins=12,color_discrete_sequence=[COLORS[3]],labels={"Delay_Days":"Days Delayed"})
        fig4.add_vline(x=dl["Delay_Days"].mean(),line_dash="dot",line_color=COLORS[2],annotation_text=f"Avg {dl['Delay_Days'].mean():.1f}d",annotation_font_color=COLORS[2])
        fig4.update_layout(**BASE_LAYOUT,height=270)
        st.plotly_chart(fig4,use_container_width=True)

    section("📋 Purchase Order Log (Latest 25)","#14b8a6")
    pd2=po.sort_values("Order_Date",ascending=False).head(25)[["PO_ID","Order_Date","Product_Name","Supplier","Warehouse","Qty_Ordered","Total_Cost","Status","Delay_Days","On_Time"]].copy()
    pd2["Total_Cost"]=pd2["Total_Cost"].map(fmt_inr)
    st.dataframe(pd2,use_container_width=True,height=360)

# ═══ TAB 3 ═══════════════════════════════════════════════════
with t3:
    ca,cb = st.columns(2)
    with ca:
        section("Returns by Reason","#ef4444")
        rs=ret["Reason"].value_counts().reset_index(); rs.columns=["Reason","Count"]
        fig=px.bar(rs,x="Count",y="Reason",orientation="h",color="Count",color_continuous_scale=["#1e3a5f","#ef4444"],text="Count",labels={"Count":"Returns"})
        fig.update_traces(textposition="outside",textfont=dict(size=11)); fig.update_layout(**BASE_LAYOUT,height=290,coloraxis_showscale=False)
        st.plotly_chart(fig,use_container_width=True)
    with cb:
        section("Returns by Category (Value vs Volume)","#10b981")
        rc2=ret.groupby("Category").agg(Returns=("Return_ID","count"),Refunds=("Refund_Amount","sum")).reset_index()
        fig2=px.scatter(rc2,x="Returns",y="Refunds",size="Returns",color="Category",color_discrete_sequence=COLORS,text="Category",size_max=45,labels={"Refunds":"Refund Value (₹)"})
        fig2.update_traces(textposition="top center",textfont=dict(size=10))
        fig2.update_layout(**BASE_LAYOUT,height=290,showlegend=False)
        st.plotly_chart(fig2,use_container_width=True)

    cc,cd = st.columns(2)
    with cc:
        section("Monthly Return Volume","#f59e0b")
        rm=ret.groupby(["Year","Month_Number","Month"]).agg(Returns=("Return_ID","count")).reset_index().sort_values(["Year","Month_Number"])
        rm["Period"]=rm["Month"].str[:3]+" "+rm["Year"].astype(str)
        fig3=go.Figure(); fig3.add_trace(go.Bar(x=rm["Period"],y=rm["Returns"],marker_color=COLORS[3],opacity=0.85,marker_line_width=0))
        fig3.update_layout(**BASE_LAYOUT,height=270,xaxis_tickangle=-30,xaxis_tickfont=dict(size=9))
        st.plotly_chart(fig3,use_container_width=True)
    with cd:
        section("Resolution Status","#8b5cf6")
        rv=ret["Resolution"].value_counts().reset_index(); rv.columns=["Resolution","Count"]
        rcm={"Refunded":"#10b981","Replacement":"#6366f1","Pending":"#f59e0b"}
        fig4=px.pie(rv,names="Resolution",values="Count",hole=0.58,color="Resolution",color_discrete_map=rcm)
        fig4.update_traces(textinfo="percent+label",marker=dict(line=dict(color=CHART_BG,width=2)))
        fig4.update_layout(paper_bgcolor=CHART_BG,height=270,showlegend=False,margin=dict(l=5,r=5,t=5,b=5),font=dict(family="Inter",color=TEXT_COL))
        st.plotly_chart(fig4,use_container_width=True)

# ═══ TAB 4 — AI INSIGHTS ═════════════════════════════════════
with t4:
    st.markdown("""<div style="background:linear-gradient(135deg,#051a0f,#081a12);border:1px solid #0d3320;border-radius:16px;padding:20px 24px;margin-bottom:20px;">
        <div style="font-size:10px;letter-spacing:2px;color:#145a32;text-transform:uppercase;margin-bottom:6px;">Machine Learning</div>
        <div style="font-size:18px;font-weight:700;color:#e8edf8;">Inventory Intelligence</div>
        <div style="font-size:12px;color:#1a4028;margin-top:4px;">Anomaly detection · Demand forecasting · Reorder prediction · Supplier scoring</div>
    </div>""", unsafe_allow_html=True)

    ca,cb = st.columns(2)

    # ── ML 1: Anomaly Detection on POs ─────────────────────
    with ca:
        section("🔍 PO Cost Anomaly Detection (Isolation Forest)","#ef4444")
        po_feat=po[["Qty_Ordered","Total_Cost","Delay_Days"]].fillna(0)
        iso=IsolationForest(contamination=0.08,random_state=42).fit(po_feat)
        po2=po.copy(); po2["Anomaly"]=iso.predict(po_feat)
        po2["Label"]=po2["Anomaly"].map({1:"Normal",-1:"Anomaly"})
        po2["Score"]=iso.score_samples(po_feat)
        fig=px.scatter(po2,x="Qty_Ordered",y="Total_Cost",color="Label",symbol="Label",
            color_discrete_map={"Normal":COLORS[0],"Anomaly":"#ef4444"},
            size_max=12,opacity=0.75,
            labels={"Qty_Ordered":"Qty Ordered","Total_Cost":"Total Cost (₹)"},
            hover_data={"Product_Name":True,"Supplier":True,"Status":True})
        fig.update_layout(**BASE_LAYOUT,height=300)
        st.plotly_chart(fig,use_container_width=True)
        n_anom=len(po2[po2["Label"]=="Anomaly"])
        st.markdown(f"""<div class="insight-box"><div class="insight-title">🚨 ANOMALY DETECTION RESULTS</div>
            <div class="insight-row"><span class="insight-key">Model</span><span class="insight-val purple">Isolation Forest</span></div>
            <div class="insight-row"><span class="insight-key">Total POs Scanned</span><span class="insight-val">{len(po2)}</span></div>
            <div class="insight-row"><span class="insight-key">Anomalous POs Flagged</span><span class="insight-val red">{n_anom} ({n_anom/len(po2)*100:.1f}%)</span></div>
            <div class="insight-row"><span class="insight-key">Potential Overcharging</span><span class="insight-val orange">Review flagged orders</span></div>
        </div>""", unsafe_allow_html=True)

    # ── ML 2: Demand / Returns Forecast ────────────────────
    with cb:
        section("📈 Monthly Returns Forecast","#10b981")
        rm2=ret.groupby(["Year","Month_Number"])["Return_ID"].count().reset_index(name="Returns")
        rm2["t"]=(rm2["Year"]-rm2["Year"].min())*12+rm2["Month_Number"]
        mdl=LinearRegression().fit(rm2[["t"]].values,rm2["Returns"].values)
        t_max=rm2["t"].max(); ft=np.arange(t_max+1,t_max+7).reshape(-1,1); fc=mdl.predict(ft)
        fig2=go.Figure()
        fig2.add_trace(go.Scatter(x=rm2["t"],y=rm2["Returns"],mode="lines+markers",name="Actual",line=dict(color=COLORS[3],width=2),marker=dict(size=5)))
        fig2.add_trace(go.Scatter(x=ft.flatten(),y=np.maximum(fc,0),mode="lines+markers",name="Forecast",line=dict(color="#10b981",width=2,dash="dot"),marker=dict(size=8,symbol="diamond",color="#10b981")))
        fig2.add_vrect(x0=t_max+0.5,x1=t_max+6.5,fillcolor="rgba(16,185,129,0.05)",line_width=0)
        fig2.update_layout(**BASE_LAYOUT,height=300,xaxis_title="Month Index",yaxis_title="Returns")
        st.plotly_chart(fig2,use_container_width=True)
        trend_dir="📈 Increasing — Action Needed" if mdl.coef_[0]>0 else "📉 Decreasing — Good Trend"
        trend_col="red" if mdl.coef_[0]>0 else "green"
        st.markdown(f"""<div class="insight-box"><div class="insight-title">📊 RETURNS FORECAST</div>
            <div class="insight-row"><span class="insight-key">Next Month Forecast</span><span class="insight-val orange">{int(max(fc[0],0))} returns</span></div>
            <div class="insight-row"><span class="insight-key">6-Month Total</span><span class="insight-val orange">{int(sum(np.maximum(fc,0)))} returns</span></div>
            <div class="insight-row"><span class="insight-key">Trend Direction</span><span class="insight-val {trend_col}">{trend_dir}</span></div>
        </div>""", unsafe_allow_html=True)

    hr()

    # ── ML 3: Supplier Scoring ──────────────────────────────
    section("🏭 AI Supplier Scorecard","#6366f1")
    sup=po.groupby("Supplier").agg(
        Total_POs=("PO_ID","count"),
        Total_Value=("Total_Cost","sum"),
        OnTime_Rate=("On_Time",lambda x:(x=="Yes").mean()*100),
        Avg_Delay=("Delay_Days","mean"),
        Num_Delayed=("Delay_Days",lambda x:(x>0).sum()),
    ).reset_index()
    sup["Performance_Score"]=(
        sup["OnTime_Rate"]*0.50 +
        (1-sup["Avg_Delay"]/sup["Avg_Delay"].max())*30 +
        (sup["Total_POs"]/sup["Total_POs"].max())*20
    ).clip(0,100).round(1)
    sup["Grade"]=pd.cut(sup["Performance_Score"],bins=[0,50,70,85,101],labels=["D","C","B","A"])

    cc3,cd3 = st.columns(2)
    with cc3:
        fig3=px.bar(sup.sort_values("Performance_Score"),x="Performance_Score",y="Supplier",orientation="h",
            color="Performance_Score",color_continuous_scale=["#ef4444","#f59e0b","#10b981"],
            text=sup.sort_values("Performance_Score")["Performance_Score"].map(lambda x:f"{x:.0f}"),
            labels={"Performance_Score":"Performance Score"})
        fig3.update_traces(textposition="outside",textfont=dict(size=11))
        fig3.add_vline(x=70,line_dash="dot",line_color="#f59e0b",annotation_text="Min Threshold",annotation_font_color="#f59e0b",annotation_font_size=10)
        fig3.update_layout(**BASE_LAYOUT,height=280,coloraxis_showscale=False)
        st.plotly_chart(fig3,use_container_width=True)
    with cd3:
        fig4=px.scatter(sup,x="OnTime_Rate",y="Avg_Delay",size="Total_Value",color="Performance_Score",
            text="Supplier",size_max=45,color_continuous_scale=["#ef4444","#f59e0b","#10b981"],
            labels={"OnTime_Rate":"On-Time Rate %","Avg_Delay":"Avg Delay (days)"})
        fig4.update_traces(textposition="top center",textfont=dict(size=9))
        fig4.update_layout(**BASE_LAYOUT,height=280)
        st.plotly_chart(fig4,use_container_width=True)

    hr()
    section("🎯 AI-Generated Operations Recommendations","#f59e0b")
    ce3,cf3,cg3 = st.columns(3)
    worst_sup=sup.loc[sup["Performance_Score"].idxmin(),"Supplier"]
    best_sup =sup.loc[sup["Performance_Score"].idxmax(),"Supplier"]
    top_ret_reason=ret["Reason"].value_counts().index[0]
    with ce3: rec_card("🚨 URGENT","urgent",f"Review Supplier: {worst_sup}",f"{worst_sup} has the lowest performance score with poor on-time delivery. Consider renegotiating SLAs, adding backup suppliers, or switching vendors for critical SKUs.")
    with cf3: rec_card("📦 INVENTORY","warning",f"Reorder {crit} Critical SKUs Immediately",f"{crit} SKUs are below reorder point across warehouses. Initiate emergency POs to avoid stockouts during peak demand periods. Prioritise high-margin categories.")
    with cg3: rec_card("↩️ RETURNS","info",f"Reduce '{top_ret_reason}' Returns",f"'{top_ret_reason}' is the #1 return reason. Investigate root cause — product quality, packaging, or delivery handling — and implement corrective action to reduce refund costs.")

st.markdown('<div style="text-align:center;padding:24px 0 8px;color:#1e2d4a;font-size:11px;border-top:1px solid #141e35;margin-top:24px;">RetailIQ Analytics Suite · Inventory & Operations · Streamlit + Plotly + scikit-learn</div>', unsafe_allow_html=True)
