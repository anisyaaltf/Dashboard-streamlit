import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import datetime as dt

#config
st.set_page_config(page_title="Dashboard penjualan", layout="wide")
st.title("Dashboard analisis penjualan")

    # load data

@st.cache_data
def load_data():
    df = pd.read_csv('data/main_data.csv')
    df['order_purchase_timestamp'] = pd.to_datetime(df['order_purchase_timestamp'])        
    df['month'] = df['order_purchase_timestamp'].dt.to_period('M').astype(str)
    return df

df = load_data()

#sidebar filter
st.sidebar.header("filter")
month_list = sorted(df['month'].unique())
selected_month = st.sidebar.multiselect(
        "pilih bulan", 
        options=month_list,
        default=month_list
)
df_filtered = df[df['month'].isin(selected_month)]

#KPI
total_revenue = df_filtered['price'].sum()
total_orders = df_filtered['order_id'].nunique()
total_customers = df_filtered['customer_id'].nunique()

col1, col2 , col3 = st.columns(3)

col1.metric("Total Revenue", f"{total_revenue:,.0f}")
col2.metric("Total Orders", total_orders)
col3.metric("Total Customer", total_customers)

# Pertanyaan 1
st.subheader("Performa penjualan & Revenue")
monthly_sales = df.groupby('month').agg({
    'price':'sum',
    'order_id': 'count'
}).reset_index()
col1, col2 = st.columns(2)
with col1:
    st.markdown("Revenue Bulanan")
    st.line_chart(monthly_sales.set_index('month')['price'])
with col2:
    st.markdown("Jumlah order")
    st.line_chart(monthly_sales.set_index('month')['order_id'])

# Pertanyaan 2
st.subheader("Frekuensi Pembelian Customer")
customer_freq = df_filtered.groupby('customer_id')['order_id'].count().reset_index()
customer_freq.columns = ['customer_id', 'frequency']

fig, ax = plt.subplots()
sns.histplot(customer_freq['frequency'], bins=20, ax=ax)
ax.set_title("Distribusi Frekuensi Customer")
ax.set_xlabel("Jumlah Transaksi")
ax.set_ylabel("Jumlah Customer")
st.pyplot(fig)

#RFM ANALYSIS
st.subheader("RFM ANALYSIS")
snapshot_date = df_filtered['order_purchase_timestamp'].max()
rfm = df_filtered.groupby('customer_id').agg({
    'order_purchase_timestamp':lambda x:(snapshot_date - x.max()).days, 
    'order_id':'count',
    'price':'sum'
 })
rfm.columns = ['Regency', 'Frequency', 'Monetary']
rfm = rfm.reset_index()
# tampil top customer
st.markdown("Top Customers(RFM)")
st.dataframe(rfm.sort_values(by='Monetary', ascending=False).head())

# Top state
st.subheader("Top Customer State")
top_state = df_filtered['customer_state'].value_counts().head(10)
st.bar_chart(top_state)

#footer
st.caption("Dashboard by Anisya Lutfiyani")
