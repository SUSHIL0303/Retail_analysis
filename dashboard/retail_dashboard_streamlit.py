
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

st.set_page_config(page_title="Retail Analytics Dashboard", page_icon="🛍️", layout="wide")

# ---- Dark Theme styling ----
st.markdown('''
    <style>
        .block-container { padding-top: 1rem; }
        /* Card look */
        .metric-card {
            background: #111827;
            border: 1px solid #1f2937;
            border-radius: 14px;
            padding: 16px;
        }
        .metric-val { font-size: 28px; font-weight: 700; color: #e5e7eb; }
        .metric-lbl { font-size: 12px; color: #9ca3af; text-transform: uppercase; letter-spacing: .08em; }
        .section-title { font-size: 18px; font-weight: 700; color: #e5e7eb; margin: 8px 0 0 0; }
        .subtle { color: #9ca3af; }
    </style>
''', unsafe_allow_html=True)

# ---- Load data ----
df = pd.read_excel(r"C:\Users\SUSHIL KUMAR\Desktop\retailsales_analysis\data\Online Retail.xlsx")


# minimal clean (for app)
df = df.dropna(subset=['CustomerID'])
df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
df['CustomerID'] = df['CustomerID'].astype(int)
df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
df['Month'] = df['InvoiceDate'].dt.to_period('M').dt.to_timestamp()

# ---- Sidebar filters ----
st.sidebar.title("Filters")
countries = ["All"] + sorted(df['Country'].dropna().unique().tolist())
country_sel = st.sidebar.selectbox("Country", countries, index=0)

date_min, date_max = df['InvoiceDate'].min(), df['InvoiceDate'].max()
date_range = st.sidebar.date_input("Date range", (date_min, date_max), min_value=date_min, max_value=date_max)

if country_sel != "All":
    df = df[df['Country'] == country_sel]

df = df[(df['InvoiceDate'] >= pd.Timestamp(date_range[0])) & (df['InvoiceDate'] <= pd.Timestamp(date_range[1]))]

# ---- KPIs ----
total_revenue = df['TotalPrice'].sum()
total_orders  = df['InvoiceNo'].nunique()
total_customers = df['CustomerID'].nunique()
avg_order_value = total_revenue / total_orders if total_orders else 0

col1, col2, col3, col4 = st.columns(4)
for col, val, lbl in [
    (col1, f"£{total_revenue:,.0f}", "Revenue"),
    (col2, f"{total_orders:,}", "Orders"),
    (col3, f"{total_customers:,}", "Customers"),
    (col4, f"£{avg_order_value:,.2f}", "Avg. Order Value"),
]:
    with col:
        st.markdown(f'<div class="metric-card"><div class="metric-lbl">{lbl}</div><div class="metric-val">{val}</div></div>', unsafe_allow_html=True)

st.markdown("<div class='section-title'>Sales Trend</div>", unsafe_allow_html=True)
rev_m = df.groupby('Month', as_index=False)['TotalPrice'].sum()
line = px.line(rev_m, x='Month', y='TotalPrice', markers=True)
line.update_layout(template='plotly_dark', height=360, margin=dict(l=10,r=10,b=10,t=30))
st.plotly_chart(line, use_container_width=True)

# ---- Top products & Countries ----
c1, c2 = st.columns(2)
with c1:
    st.markdown("<div class='section-title'>Top 10 Products (Quantity)</div>", unsafe_allow_html=True)
    top_prod = (df.groupby('Description')['Quantity'].sum()
                  .sort_values(ascending=False).head(10).reset_index())
    bar1 = px.bar(top_prod, x='Quantity', y='Description', orientation='h')
    bar1.update_layout(template='plotly_dark', height=420, margin=dict(l=10,r=10,b=10,t=30))
    bar1.update_yaxes(autorange='reversed')
    st.plotly_chart(bar1, use_container_width=True)

with c2:
    st.markdown("<div class='section-title'>Top 10 Countries (Revenue)</div>", unsafe_allow_html=True)
    top_cty = (df.groupby('Country')['TotalPrice'].sum()
                 .sort_values(ascending=False).head(10).reset_index())
    bar2 = px.bar(top_cty, x='Country', y='TotalPrice')
    bar2.update_layout(template='plotly_dark', height=420, margin=dict(l=10,r=10,b=10,t=30))
    st.plotly_chart(bar2, use_container_width=True)

# ---- Geo Map ----
st.markdown("<div class='section-title'>Global Revenue Map</div>", unsafe_allow_html=True)
country_map = df.groupby('Country', as_index=False)['TotalPrice'].sum()
geo = px.choropleth(country_map, locations="Country", locationmode="country names",
                    color="TotalPrice", title="", template='plotly_dark')
geo.update_layout(height=420, margin=dict(l=10,r=10,b=10,t=10))
st.plotly_chart(geo, use_container_width=True)

# ---- Table: Recent Orders ----
st.markdown("<div class='section-title'>Recent Orders</div>", unsafe_allow_html=True)
recent = (df.sort_values('InvoiceDate', ascending=False)
            [['InvoiceDate','InvoiceNo','CustomerID','Country','Description','Quantity','UnitPrice','TotalPrice']]
            .head(300))
st.dataframe(recent, use_container_width=True, hide_index=True)
