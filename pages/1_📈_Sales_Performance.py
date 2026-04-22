import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from utils import *

st.markdown(GLOBAL_CSS, unsafe_allow_html=True)
st.markdown("<style>.stTabs [aria-selected='true']{background:#1a1f4a!important;color:#818cf8!important;}</style>", unsafe_allow_html=True)

@st.cache_data
def load():
    df = pd.read_excel("Sales_Performance_Dataset.xlsx", sheet_name="Orders_Data")
    tg = pd.read_excel("Sales_Performance_Dataset.xlsx", sheet_name="Monthly_Targets")
    cu = pd.read_excel("Sales_Performance_Dataset.xlsx", sheet_name="Customer_Segments")
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    return df, tg, cu

df_full, df_targets, df_customers = load()

with st.sidebar:
    st.markdown('<div class="sidebar-logo"><div class="sidebar-logo-text">📈 Sales</div><div class="sidebar-logo-sub">Performance Dashboard</div></div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-section">Date</div>', unsafe_allow_html=True)
    years    = st.multiselect("Year",    sorted(df_full["Year"].unique()),     default=sorted(df_full["Year"].unique()))
    quarters = st.multiselect("Quarter", ["Q1","Q2","Q3","Q4"],               default=["Q1","Q2","Q3","Q4"])
    st.markdown('<div class="sidebar-section">Filters</div>', unsafe_allow_html=True)
    cats     = st.multiselect("Category",     sorted(df_full["Category"].unique()), default=sorted(df_full["Category"].unique()))
    regions  = st.multiselect("Region",       sorted(df_full["Region"].unique()),   default=sorted(df_full["Region"].unique()))
    channels = st.multiselect("Channel",      sorted(df_full["Channel"].unique()),  default=sorted(df_full["Channel"].unique()))
    cust_t   = st.multiselect("Customer Type",["New","Returning"],                  default=["New","Returning"])

df = df_full[df_full["Year"].isin(years)&df_full["Quarter"].isin(quarters)&df_full["Category"].isin(cats)&df_full["Region"].isin(regions)&df_full["Channel"].isin(channels)&df_full["Customer_Type"].isin(cust_t)].copy()
if df.empty: st.warning("No data for selected filters."); st.stop()

rev  = df["Net_Revenue"].sum(); prof = df["Gross_Profit"].sum(); ords = len(df)
aov  = df["Net_Revenue"].mean(); gm = prof/rev*100 if rev else 0
ret_r= (df["Order_Status"]=="Returned").mean()*100; units=df["Units_Sold"].sum(); disc=df["Discount_Amount"].sum()

def yoy(col):
    if len(years)<2: return None
    ys=sorted(years); c=df[df["Year"]==ys[-1]][col].sum(); p=df[df["Year"]==ys[-2]][col].sum()
    return (c-p)/p*100 if p else None

st.markdown('<div class="page-hero"><div class="page-hero-tag">RetailIQ · E-Commerce Analytics</div><div class="page-hero-title">Sales Performance Dashboard</div><div class="page-hero-sub">Revenue intelligence · Margin analytics · Customer RFM · AI-powered forecasting</div></div>', unsafe_allow_html=True)

c1,c2,c3,c4,c5,c6 = st.columns(6)
kpi(c1,"💰","Net Revenue",    fmt_inr(rev),                        f"{units:,} units",        yoy("Net_Revenue"), "#6366f1")
kpi(c2,"📊","Gross Profit",   fmt_inr(prof),                       f"{gm:.1f}% margin",       yoy("Gross_Profit"),"#10b981")
kpi(c3,"🛒","Total Orders",   f"{ords:,}",                         f"AOV {fmt_inr(aov)}",     None,               "#f59e0b")
kpi(c4,"🎯","Avg Order Value",fmt_inr(aov),                        "per order",               None,               "#8b5cf6")
kpi(c5,"↩️","Return Rate",    f"{ret_r:.1f}%",                     f"₹{disc/1e5:.1f}L disc.", None,               "#ef4444")
kpi(c6,"⭐","Avg Rating",     f"{df['Customer_Rating'].mean():.2f}",f"{ords:,} reviews",      None,               "#14b8a6")
hr()

t1,t2,t3,t4,t5 = st.tabs(["📈 Revenue & Trends","🗺️ Geo & Channel","📦 Product Mix","👥 Customers","🤖 AI Insights"])

with t1:
    monthly = df.groupby(["Year","Month_Number","Month"]).agg(Revenue=("Net_Revenue","sum"),Profit=("Gross_Profit","sum"),Orders=("Order_ID","count")).reset_index().sort_values(["Year","Month_Number"])
    monthly["Period"] = monthly["Month"].str[:3]+" "+monthly["Year"].astype(str)
    tgt2 = df_targets.copy(); tgt2["Period"]=tgt2["Month"].str[:3]+" "+tgt2["Year"].astype(str)
    monthly = monthly.merge(tgt2[["Period","Revenue_Target"]],on="Period",how="left")
    monthly["Margin_pct"] = monthly["Profit"]/monthly["Revenue"]*100

    ca,cb = st.columns([3,2])
    with ca:
        section("Monthly Revenue vs Target","#6366f1")
        fig=go.Figure()
        for i,yr in enumerate(sorted(monthly["Year"].unique())):
            sub=monthly[monthly["Year"]==yr]
            fig.add_trace(go.Bar(x=sub["Period"],y=sub["Revenue"],name=f"Revenue {yr}",marker_color=COLORS[i],opacity=0.85,marker_line_width=0))
        fig.add_trace(go.Scatter(x=monthly["Period"],y=monthly["Revenue_Target"],name="Target",mode="lines+markers",line=dict(color="#ef4444",dash="dot",width=2),marker=dict(size=6,symbol="diamond")))
        fig.update_layout(**BASE_LAYOUT,height=300,barmode="group",xaxis_tickangle=-30,xaxis_tickfont=dict(size=9))
        st.plotly_chart(fig,use_container_width=True)
    with cb:
        section("Revenue Waterfall","#10b981")
        gross=df["Gross_Revenue"].sum(); disc_amt=df["Discount_Amount"].sum(); ship=df["Shipping_Cost"].sum()
        fig2=go.Figure(go.Waterfall(orientation="v",measure=["absolute","relative","relative","total","relative","total"],
            x=["Gross","Discounts","Shipping","Net Revenue","COGS","Gross Profit"],
            y=[gross,-disc_amt,-ship,0,-df["COGS"].sum(),0],
            connector=dict(line=dict(color=GRID_COL,width=1)),
            increasing=dict(marker_color="#10b981"),decreasing=dict(marker_color="#ef4444"),totals=dict(marker_color="#6366f1"),
            text=[fmt_inr(gross),f"-{fmt_inr(disc_amt)}",f"-{fmt_inr(ship)}",fmt_inr(rev),f"-{fmt_inr(df['COGS'].sum())}",fmt_inr(prof)],
            textposition="outside",textfont=dict(size=9,color=TEXT_COL)))
        fig2.update_layout(**BASE_LAYOUT,height=300,showlegend=False)
        st.plotly_chart(fig2,use_container_width=True)

    cc,cd = st.columns(2)
    with cc:
        section("Weekly Revenue Trend","#f59e0b")
        weekly=df.groupby(["Year","Week_Number"])["Net_Revenue"].sum().reset_index()
        fig3=px.line(weekly,x="Week_Number",y="Net_Revenue",color="Year",color_discrete_sequence=[COLORS[0],COLORS[2]],labels={"Net_Revenue":"Revenue","Week_Number":"Week"})
        fig3.update_traces(line_width=2); fig3.update_layout(**BASE_LAYOUT,height=260)
        st.plotly_chart(fig3,use_container_width=True)
    with cd:
        section("Gross Margin % Trend","#8b5cf6")
        fig4=go.Figure(); fig4.add_trace(go.Scatter(x=monthly["Period"],y=monthly["Margin_pct"],fill="tozeroy",mode="lines+markers",line=dict(color="#8b5cf6",width=2),fillcolor="rgba(139,92,246,0.08)",marker=dict(size=5,color="#8b5cf6")))
        fig4.add_hline(y=monthly["Margin_pct"].mean(),line_dash="dot",line_color="#f59e0b",annotation_text=f"Avg {monthly['Margin_pct'].mean():.1f}%",annotation_font_color="#f59e0b",annotation_font_size=10)
        fig4.update_layout(**BASE_LAYOUT,height=260,xaxis_tickangle=-30,xaxis_tickfont=dict(size=9))
        st.plotly_chart(fig4,use_container_width=True)

with t2:
    ca,cb = st.columns(2)
    with ca:
        section("Revenue by Region","#6366f1")
        rg=df.groupby("Region").agg(Revenue=("Net_Revenue","sum"),Profit=("Gross_Profit","sum")).reset_index()
        rg["Margin"]=rg["Profit"]/rg["Revenue"]*100
        fig=px.bar(rg.sort_values("Revenue"),x="Revenue",y="Region",orientation="h",color="Margin",color_continuous_scale=["#1e3a5f","#6366f1","#10b981"],text=rg.sort_values("Revenue")["Revenue"].map(fmt_inr))
        fig.update_traces(textposition="outside",textfont=dict(size=11,color=TEXT_COL))
        fig.update_layout(**BASE_LAYOUT,height=260,coloraxis_showscale=False)
        st.plotly_chart(fig,use_container_width=True)
    with cb:
        section("City Revenue Treemap","#10b981")
        city=df.groupby("City")["Net_Revenue"].sum().nlargest(12).reset_index()
        fig2=px.treemap(city,path=["City"],values="Net_Revenue",color="Net_Revenue",color_continuous_scale=["#0a0e1a","#6366f1","#10b981"])
        fig2.update_layout(paper_bgcolor=CHART_BG,margin=dict(l=0,r=0,t=0,b=0),height=260,coloraxis_showscale=False)
        st.plotly_chart(fig2,use_container_width=True)

    cc,cd = st.columns(2)
    with cc:
        section("Revenue by Channel","#f59e0b")
        ch=df.groupby("Channel").agg(Revenue=("Net_Revenue","sum"),Orders=("Order_ID","count"),CAC=("CAC","mean")).reset_index()
        ch["RPO"]=ch["Revenue"]/ch["Orders"]
        fig3=px.bar(ch.sort_values("Revenue"),x="Revenue",y="Channel",orientation="h",color="Channel",color_discrete_sequence=COLORS,text=ch.sort_values("Revenue")["Revenue"].map(fmt_inr))
        fig3.update_traces(textposition="outside",textfont=dict(size=10),showlegend=False)
        fig3.update_layout(**BASE_LAYOUT,height=270)
        st.plotly_chart(fig3,use_container_width=True)
    with cd:
        section("CAC vs Revenue per Order","#8b5cf6")
        fig4=px.scatter(ch,x="CAC",y="RPO",size="Orders",color="Channel",color_discrete_sequence=COLORS,text="Channel",size_max=42,labels={"RPO":"Revenue / Order"})
        fig4.update_traces(textposition="top center",textfont=dict(size=9))
        fig4.update_layout(**BASE_LAYOUT,height=270,showlegend=False)
        st.plotly_chart(fig4,use_container_width=True)

    ce,cf = st.columns(2)
    with ce:
        section("Payment Method Split","#ef4444")
        pay=df.groupby("Payment_Method")["Net_Revenue"].sum().reset_index()
        fig5=px.pie(pay,names="Payment_Method",values="Net_Revenue",hole=0.58,color_discrete_sequence=COLORS)
        fig5.update_traces(textinfo="percent+label",marker=dict(line=dict(color=CHART_BG,width=2)),textfont=dict(size=11))
        fig5.update_layout(paper_bgcolor=CHART_BG,height=260,showlegend=False,margin=dict(l=5,r=5,t=5,b=5),font=dict(family="Inter",color=TEXT_COL))
        st.plotly_chart(fig5,use_container_width=True)
    with cf:
        section("Channel Share Over Time","#14b8a6")
        ct=df.groupby(["Month_Number","Channel"])["Net_Revenue"].sum().reset_index()
        ct["share"]=ct["Net_Revenue"]/ct.groupby("Month_Number")["Net_Revenue"].transform("sum")*100
        fig6=px.area(ct,x="Month_Number",y="share",color="Channel",color_discrete_sequence=COLORS,groupnorm="percent",labels={"share":"Share %","Month_Number":"Month"})
        fig6.update_layout(**BASE_LAYOUT,height=260)
        st.plotly_chart(fig6,use_container_width=True)

with t3:
    ca,cb = st.columns(2)
    with ca:
        section("Category Revenue vs Margin Bubble","#6366f1")
        cat=df.groupby("Category").agg(Revenue=("Net_Revenue","sum"),Profit=("Gross_Profit","sum"),Units=("Units_Sold","sum")).reset_index()
        cat["Margin"]=cat["Profit"]/cat["Revenue"]*100
        fig=px.scatter(cat,x="Revenue",y="Margin",size="Units",color="Category",color_discrete_sequence=COLORS,text="Category",size_max=55)
        fig.update_traces(textposition="top center",textfont=dict(size=10))
        fig.update_layout(**BASE_LAYOUT,height=320,showlegend=False)
        st.plotly_chart(fig,use_container_width=True)
    with cb:
        section("Top 10 Sub-Categories","#10b981")
        sub=df.groupby(["Category","Sub_Category"]).agg(Revenue=("Net_Revenue","sum")).reset_index().nlargest(10,"Revenue")
        fig2=px.bar(sub,x="Revenue",y="Sub_Category",orientation="h",color="Category",color_discrete_sequence=COLORS,text=sub["Revenue"].map(fmt_inr))
        fig2.update_traces(textposition="outside",textfont=dict(size=10))
        fig2.update_layout(**BASE_LAYOUT,height=320)
        st.plotly_chart(fig2,use_container_width=True)

    section("Brand × Category Revenue Heatmap","#f59e0b")
    bc=df.groupby(["Brand","Category"])["Net_Revenue"].sum().reset_index()
    pivot=bc.pivot(index="Brand",columns="Category",values="Net_Revenue").fillna(0)
    top_b=df.groupby("Brand")["Net_Revenue"].sum().nlargest(14).index
    pivot=pivot.loc[pivot.index.isin(top_b)]
    fig3=px.imshow(pivot,color_continuous_scale=["#070b14","#1a2d4a","#6366f1","#10b981"],aspect="auto")
    fig3.update_layout(paper_bgcolor=CHART_BG,font=dict(family="Inter",color=TEXT_COL),height=360,margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig3,use_container_width=True)

    cc,cd = st.columns(2)
    with cc:
        section("Discount % vs Revenue","#8b5cf6")
        dsc=df.groupby("Discount_%").agg(Revenue=("Net_Revenue","sum"),Orders=("Order_ID","count")).reset_index()
        fig4=px.bar(dsc,x="Discount_%",y="Revenue",color="Orders",color_continuous_scale=["#1a2d4a","#6366f1"],labels={"Discount_%":"Discount %"})
        fig4.update_layout(**BASE_LAYOUT,height=250,coloraxis_showscale=False)
        st.plotly_chart(fig4,use_container_width=True)
    with cd:
        section("Category Revenue Trend","#14b8a6")
        ct2=df.groupby(["Month_Number","Category"])["Net_Revenue"].sum().reset_index()
        fig5=px.line(ct2,x="Month_Number",y="Net_Revenue",color="Category",color_discrete_sequence=COLORS,labels={"Month_Number":"Month"})
        fig5.update_traces(line_width=2); fig5.update_layout(**BASE_LAYOUT,height=250)
        st.plotly_chart(fig5,use_container_width=True)

with t4:
    ca,cb = st.columns(2)
    seg_c={"Champions":"#10b981","Loyal":"#6366f1","At Risk":"#ef4444","New":"#f59e0b","Hibernating":"#6b7280"}
    with ca:
        section("New vs Returning Revenue","#6366f1")
        cm=df.groupby(["Month_Number","Customer_Type"])["Net_Revenue"].sum().reset_index()
        fig=px.bar(cm,x="Month_Number",y="Net_Revenue",color="Customer_Type",color_discrete_map={"New":COLORS[0],"Returning":COLORS[1]},barmode="stack",labels={"Net_Revenue":"Revenue","Month_Number":"Month"})
        fig.update_layout(**BASE_LAYOUT,height=270)
        st.plotly_chart(fig,use_container_width=True)
    with cb:
        section("RFM Customer Segments","#10b981")
        seg=df_customers.groupby("Segment").agg(Customers=("Customer_ID","count")).reset_index()
        fig2=px.bar(seg,x="Segment",y="Customers",color="Segment",color_discrete_map=seg_c,text="Customers")
        fig2.update_traces(textposition="outside"); fig2.update_layout(**BASE_LAYOUT,height=270,showlegend=False)
        st.plotly_chart(fig2,use_container_width=True)

    cc,cd = st.columns(2)
    with cc:
        section("Segment Lifetime Spend","#f59e0b")
        fig3=px.box(df_customers,x="Segment",y="Total_Spend",color="Segment",color_discrete_map=seg_c,labels={"Total_Spend":"Lifetime Spend (₹)"})
        fig3.update_layout(**BASE_LAYOUT,height=270,showlegend=False)
        st.plotly_chart(fig3,use_container_width=True)
    with cd:
        section("Customer Rating by Category","#8b5cf6")
        rd=df[df["Customer_Rating"].notna()]
        fig4=px.violin(rd,x="Category",y="Customer_Rating",color="Category",box=True,points=False,color_discrete_sequence=COLORS)
        fig4.update_layout(**BASE_LAYOUT,height=270,showlegend=False)
        st.plotly_chart(fig4,use_container_width=True)

with t5:
    st.markdown("""<div style="background:linear-gradient(135deg,#0d1829,#111e35);border:1px solid #1a2d4a;border-radius:16px;padding:20px 24px;margin-bottom:20px;">
        <div style="font-size:10px;letter-spacing:2px;color:#4f5faa;text-transform:uppercase;margin-bottom:6px;">Machine Learning</div>
        <div style="font-size:18px;font-weight:700;color:#e8edf8;">AI-Powered Insights & Predictions</div>
        <div style="font-size:12px;color:#3d5080;margin-top:4px;">Revenue forecasting · Customer churn risk · Clustering · Feature importance</div>
    </div>""", unsafe_allow_html=True)

    ca,cb = st.columns(2)
    with ca:
        section("📈 Revenue Forecast — Next 6 Months","#6366f1")
        mr=df.groupby(["Year","Month_Number"])["Net_Revenue"].sum().reset_index()
        mr["t"]=(mr["Year"]-mr["Year"].min())*12+mr["Month_Number"]
        model=LinearRegression().fit(mr[["t"]].values,mr["Net_Revenue"].values)
        t_max=mr["t"].max(); ft=np.arange(t_max+1,t_max+7).reshape(-1,1); fc=model.predict(ft)
        r2=model.score(mr[["t"]].values,mr["Net_Revenue"].values)
        fig=go.Figure()
        fig.add_trace(go.Scatter(x=mr["t"],y=mr["Net_Revenue"],mode="lines+markers",name="Actual",line=dict(color=COLORS[0],width=2),marker=dict(size=4)))
        fig.add_trace(go.Scatter(x=ft.flatten(),y=fc,mode="lines+markers",name="Forecast",line=dict(color="#10b981",width=2,dash="dot"),marker=dict(size=8,symbol="diamond",color="#10b981")))
        fig.add_vrect(x0=t_max+0.5,x1=t_max+6.5,fillcolor="rgba(16,185,129,0.05)",line_width=0,annotation_text="Forecast Zone",annotation_position="top left",annotation_font=dict(color="#34d399",size=10))
        fig.update_layout(**BASE_LAYOUT,height=280,xaxis_title="Month Index")
        st.plotly_chart(fig,use_container_width=True)
        st.markdown(f"""<div class="insight-box"><div class="insight-title">🔍 FORECAST SUMMARY</div>
            <div class="insight-row"><span class="insight-key">Model</span><span class="insight-val purple">Linear Regression</span></div>
            <div class="insight-row"><span class="insight-key">R² Score</span><span class="insight-val {'green' if r2>0.6 else 'orange'}">{r2:.3f}</span></div>
            <div class="insight-row"><span class="insight-key">Next Month</span><span class="insight-val green">{fmt_inr(fc[0])}</span></div>
            <div class="insight-row"><span class="insight-key">6-Month Total</span><span class="insight-val green">{fmt_inr(sum(fc))}</span></div>
            <div class="insight-row"><span class="insight-key">Trend</span><span class="insight-val {'green' if model.coef_[0]>0 else 'red'}">{'📈 Upward' if model.coef_[0]>0 else '📉 Downward'}</span></div>
        </div>""", unsafe_allow_html=True)

    with cb:
        section("⚠️ Customer Churn Risk Score","#ef4444")
        cf2=df_customers.copy()
        cf2["churn_score"]=(cf2["Last_Order_Days_Ago"]/cf2["Last_Order_Days_Ago"].max()*50+
            (1-cf2["Total_Orders"]/cf2["Total_Orders"].max())*30+
            (1-cf2["Total_Spend"]/cf2["Total_Spend"].max())*20).clip(0,100).round(1)
        cf2["Risk"]=pd.cut(cf2["churn_score"],bins=[0,30,60,100],labels=["Low Risk","Medium Risk","High Risk"])
        rc2={"Low Risk":"#10b981","Medium Risk":"#f59e0b","High Risk":"#ef4444"}
        rk=cf2["Risk"].value_counts().reset_index(); rk.columns=["Risk","Count"]
        fig2=px.pie(rk,names="Risk",values="Count",hole=0.6,color="Risk",color_discrete_map=rc2)
        fig2.update_traces(textinfo="percent+label",marker=dict(line=dict(color=CHART_BG,width=2)))
        fig2.update_layout(paper_bgcolor=CHART_BG,height=220,showlegend=False,margin=dict(l=5,r=5,t=5,b=5),font=dict(family="Inter",color=TEXT_COL))
        st.plotly_chart(fig2,use_container_width=True)
        hr_c=cf2[cf2["Risk"]=="High Risk"]; mr_c=cf2[cf2["Risk"]=="Medium Risk"]
        st.markdown(f"""<div class="insight-box"><div class="insight-title">🎯 CHURN RISK BREAKDOWN</div>
            <div class="insight-row"><span class="insight-key">🔴 High Risk</span><span class="insight-val red">{len(hr_c)} customers ({len(hr_c)/len(cf2)*100:.0f}%)</span></div>
            <div class="insight-row"><span class="insight-key">🟡 Medium Risk</span><span class="insight-val orange">{len(mr_c)} customers</span></div>
            <div class="insight-row"><span class="insight-key">Revenue at Risk</span><span class="insight-val red">{fmt_inr(hr_c['Total_Spend'].sum())}</span></div>
            <div class="insight-row"><span class="insight-key">Avg Inactive (days)</span><span class="insight-val orange">{hr_c['Last_Order_Days_Ago'].mean():.0f}d</span></div>
        </div>""", unsafe_allow_html=True)

    hr()
    cc,cd = st.columns(2)
    with cc:
        section("🔵 K-Means Customer Clustering","#8b5cf6")
        Xc=df_customers[["Total_Spend","Total_Orders","Avg_Order_Value"]].copy()
        Xn=(Xc-Xc.mean())/Xc.std()
        km=KMeans(n_clusters=4,random_state=42,n_init=10).fit(Xn)
        df_customers["Cluster"]="Cluster "+pd.Series(km.labels_).astype(str).values
        fig3=px.scatter(df_customers,x="Total_Spend",y="Total_Orders",color="Cluster",size="Avg_Order_Value",color_discrete_sequence=COLORS,size_max=22,labels={"Total_Spend":"Lifetime Spend","Total_Orders":"Order Count"})
        fig3.update_layout(**BASE_LAYOUT,height=290)
        st.plotly_chart(fig3,use_container_width=True)
        cs=df_customers.groupby("Cluster").agg(Count=("Customer_ID","count"),Avg_Spend=("Total_Spend","mean"),Avg_Orders=("Total_Orders","mean")).reset_index()
        st.dataframe(cs.style.format({"Avg_Spend":"₹{:,.0f}","Avg_Orders":"{:.1f}"}),use_container_width=True,height=155)

    with cd:
        section("🌲 Revenue Drivers (Random Forest)","#10b981")
        rfd=df[["Category","Channel","Region","Customer_Type","Discount_%","Units_Sold","Net_Revenue"]].copy().dropna()
        for c in ["Category","Channel","Region","Customer_Type"]: rfd[c]=LabelEncoder().fit_transform(rfd[c])
        Xf=rfd.drop("Net_Revenue",axis=1); yf=rfd["Net_Revenue"]
        rf=RandomForestRegressor(n_estimators=60,random_state=42,max_depth=6).fit(Xf,yf)
        imp=pd.DataFrame({"Feature":Xf.columns,"Importance":rf.feature_importances_}).sort_values("Importance")
        fig4=px.bar(imp,x="Importance",y="Feature",orientation="h",color="Importance",color_continuous_scale=["#1a2d4a","#10b981"],text=imp["Importance"].map(lambda x:f"{x:.3f}"))
        fig4.update_traces(textposition="outside",textfont=dict(size=11))
        fig4.update_layout(**BASE_LAYOUT,height=290,coloraxis_showscale=False)
        st.plotly_chart(fig4,use_container_width=True)

    hr()
    section("🎯 AI-Generated Recommendations","#f59e0b")
    ce,cf3,cg = st.columns(3)
    ch2=df.groupby("Channel").agg(Revenue=("Net_Revenue","sum")).reset_index()
    top_ch2=ch2.loc[ch2["Revenue"].idxmax(),"Channel"]
    worst_cat=df.groupby("Category").apply(lambda x:(x["Order_Status"]=="Returned").mean()).idxmax()
    hr_pct=len(hr_c)/len(cf2)*100
    with ce: rec_card("💡 HIGH PRIORITY","urgent",f"Fix Returns in {worst_cat}",f"{worst_cat} has the highest return rate. Improve product descriptions, quality checks, and packaging to recover lost revenue and boost customer satisfaction.")
    with cf3: rec_card("📈 GROWTH","success",f"Scale {top_ch2} Budget",f"{top_ch2} is your top revenue channel with the best return on spend. Increasing budget allocation by 25-30% here is likely to yield the highest incremental revenue.")
    with cg: rec_card("⚠️ RETENTION","warning",f"Re-engage {len(hr_c)} At-Risk Customers",f"{hr_pct:.0f}% of your base shows high churn signals. Launch personalised win-back campaigns with exclusive offers for customers inactive 90+ days.")

st.markdown('<div style="text-align:center;padding:24px 0 8px;color:#1e2d4a;font-size:11px;border-top:1px solid #141e35;margin-top:24px;">RetailIQ Analytics Suite · Sales Performance · Streamlit + Plotly + scikit-learn</div>', unsafe_allow_html=True)
