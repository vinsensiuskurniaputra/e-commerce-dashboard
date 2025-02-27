import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
df = pd.read_csv("./main_data.csv")
# Convert order_purchase_timestamp to datetime
df['order_purchase_timestamp'] = pd.to_datetime(df['"order_purchase_timestamp"'])

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard Analisis E-Commerce", layout="wide")

# Sidebar untuk filter data
st.sidebar.header("Filter Data")
min_date = df['order_purchase_timestamp'].min().date()
max_date = df['order_purchase_timestamp'].max().date()
start_date, end_date = st.sidebar.date_input(
    "Pilih Rentang Waktu",
    [min_date, max_date],
    min_value=min_date,
    max_value=max_date
)

# Filter data berdasarkan range tanggal
filtered_df = df[
    (df['order_purchase_timestamp'].dt.date >= start_date) &
    (df['order_purchase_timestamp'].dt.date <= end_date)
]

st.title("📊 Dashboard Analisis E-Commerce")
st.markdown("Dashboard ini menampilkan berbagai analisis untuk membantu pengambilan keputusan bisnis.")

# Sebaran Pelanggan
st.subheader("📍 Sebaran Pelanggan Berdasarkan Lokasi")
customer_geo = filtered_df.groupby(["customer_city"])["order_id"].count().sort_values(ascending=False).head(10)
fig_review = px.bar(x=customer_geo.index, y=customer_geo.values, 
                    labels={"x": "Kota", "y": "Jumlah Pelanggan"},
                    title="Top 10 Kota dengan Pelanggan Terbanyak", 
                    color=customer_geo.index)
st.plotly_chart(fig_review)

# Distribusi Ulasan
st.subheader("⭐ Distribusi Ulasan Pelanggan")
review_counts = filtered_df["review_score"].value_counts().sort_index()
fig_review = px.bar(x=review_counts.index, y=review_counts.values, 
                    labels={"x": "Skor Review", "y": "Jumlah"},
                    title="Distribusi Ulasan", 
                    color=review_counts.index)
st.plotly_chart(fig_review)

# Analisis Metode Pembayaran
st.subheader("💳 Metode Pembayaran")
col1, col2 = st.columns(2)

with col1:
    payment_counts = filtered_df["payment_type"].value_counts()
    fig_payment_pie = px.pie(values=payment_counts.values, 
                            names=payment_counts.index, 
                            title="Metode Pembayaran Terpopuler")
    st.plotly_chart(fig_payment_pie)

with col2:
    payment_sums = filtered_df.groupby("payment_type")["payment_value"].sum()
    fig_payment_bar = px.bar(x=payment_sums.index, y=payment_sums.values, 
                            labels={"x": "Metode Pembayaran", "y": "Total Transaksi"},
                            title="Total Transaksi per Metode Pembayaran", 
                            color=payment_sums.index)
    st.plotly_chart(fig_payment_bar)

# Kategori Produk
st.subheader("🛍️ Kategori Produk dengan Penjualan Tertinggi")
top_categories = filtered_df["product_category_name_english"].value_counts().nlargest(10)
fig_category = px.bar(x=top_categories.index, y=top_categories.values, 
                      labels={"x": "Kategori Produk", "y": "Jumlah"},
                      title="Top 10 Kategori Produk dengan Order Terbanyak", 
                      color=top_categories.index)
st.plotly_chart(fig_category)

# RFM Analysis
st.subheader("📊 RFM Analysis (Segmentasi Pelanggan)")
col1, col2, col3 = st.columns(3)

# RFM Score Calculation
latest_date = filtered_df['order_purchase_timestamp'].max()
rfm = filtered_df.groupby('customer_id').agg({
    'order_purchase_timestamp': lambda x: (latest_date - x.max()).days,  # Recency
    'order_id': 'count',  # Frequency
    'payment_value': 'sum'  # Monetary
}).reset_index()
rfm.columns = ['customer_id', 'Recency', 'Frequency', 'Monetary']

avg_recency = round(rfm["Recency"].mean(), 1)
avg_frequency = round(rfm["Frequency"].mean(), 1)
avg_monetary = round(rfm["Monetary"].mean(), 2)

col1.metric("Average Recency (days)", avg_recency)
col2.metric("Average Frequency", avg_frequency)
col3.metric("Average Monetary", f"AUD {avg_monetary:,}")

# RFM Visualization
fig_rfm, ax = plt.subplots(1, 3, figsize=(15, 5))
sns.histplot(data=rfm, x='Recency', ax=ax[0])
ax[0].set_title("Recency Distribution")
sns.histplot(data=rfm, x='Frequency', ax=ax[1])
ax[1].set_title("Frequency Distribution")
sns.histplot(data=rfm, x='Monetary', ax=ax[2])
ax[2].set_title("Monetary Distribution")
st.pyplot(fig_rfm)

# Footer
st.markdown("Create with 🧡 by Vinsensius Kurnia Putra")
