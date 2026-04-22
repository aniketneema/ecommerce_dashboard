# 🏪 RetailIQ — Analytics Suite v2

Advanced 3-dashboard Streamlit app with **ML-powered insights**.

## 📊 Dashboards

| Page | Tabs | ML Features |
|------|------|-------------|
| 📈 Sales Performance | Revenue · Geo · Products · Customers · AI | Revenue Forecast, Churn Risk, K-Means Clustering, Random Forest |
| 📦 Inventory & Ops | Stock · POs · Returns · AI | Isolation Forest Anomaly Detection, Returns Forecast, Supplier Scoring |
| 📣 Marketing | Campaigns · Channels · Funnel · AI | ROAS Forecast, Campaign Clustering, Budget Optimiser |

## 🚀 Run Locally

```bash
pip install -r requirements.txt
streamlit run Home.py
```

## ☁️ Deploy Free on Streamlit Cloud

1. Push this folder to GitHub
2. Go to https://share.streamlit.io → Sign in with GitHub
3. New app → Select repo → **Main file: `Home.py`**
4. Deploy → Share the public URL

## 📁 Structure

```
Home.py
pages/
  1_📈_Sales_Performance.py
  2_📦_Inventory_Operations.py
  3_📣_Marketing_Acquisition.py
utils.py                      ← Shared styles, colors, helpers
Sales_Performance_Dataset.xlsx
Inventory_Operations_Dataset.xlsx
Marketing_Dataset.xlsx
requirements.txt
```
