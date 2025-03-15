import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Dapatkan path absolut ke folder proyek
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Lokasi file script
DATA_DIR = os.path.join(BASE_DIR, "../data")  # Folder 'data' di luar folder script

# Path ke dataset
DAY_CSV_PATH = os.path.join(DATA_DIR, "day.csv")
HOUR_CSV_PATH = os.path.join(DATA_DIR, "hour.csv")

# Load dataset
try:
    df_day = pd.read_csv(DAY_CSV_PATH)
    df_hour = pd.read_csv(HOUR_CSV_PATH)
except FileNotFoundError:
    st.error("Dataset tidak ditemukan! Pastikan file 'day.csv' dan 'hour.csv' ada di folder 'data'.")
    st.stop()

st.title("Dashboard Analisis Penyewaan Sepeda 🚲")

# Sidebar untuk pilih analisis
analysis = st.sidebar.selectbox("Pilih Analisis:",
                                ["Pola Harian", "Pengaruh Cuaca", "RFM"])

if analysis == "Pola Harian":
  st.header("Pola Penyewaan per Jam")
  hourly_rentals = df_hour.groupby('hr')['cnt'].mean().reset_index()

  # Visualisasi
  fig, ax = plt.subplots(figsize=(10, 5))
  sns.lineplot(x='hr', y='cnt', data=hourly_rentals, ax=ax)
  ax.set_title("Rata-rata Penyewaan Sepeda per Jam")
  ax.set_xlabel("Jam")
  ax.set_ylabel("Rata-rata Jumlah Penyewaan")
  st.pyplot(fig)

  # Insight
  st.write("""
    **Insight:**  
    - Grafik menunjukkan bahwa penyewaan sepeda meningkat secara signifikan pada jam-jam sibuk (pagi sekitar jam 7-9 dan sore sekitar jam 17-19).  
    - Hal ini kemungkinan besar terkait dengan aktivitas komuter seperti pergi ke kantor atau sekolah.  
    - Pada malam hari (setelah jam 21), jumlah penyewaan menurun drastis karena aktivitas masyarakat berkurang.
    """)

elif analysis == "Pengaruh Cuaca":
  st.header("Korelasi Cuaca dengan Penyewaan")
  # Ambil kolom relevan untuk korelasi
  corr = df_day[['temp', 'hum', 'windspeed', 'cnt']].corr()

  # Visualisasi
  fig, ax = plt.subplots(figsize=(8, 6))
  sns.heatmap(corr, annot=True, cmap='coolwarm', ax=ax)
  ax.set_title("Heatmap Korelasi")
  st.pyplot(fig)

  # Insight
  st.write("""
    **Insight:**  
    - Suhu (`temp`) memiliki korelasi positif yang cukup kuat dengan jumlah penyewaan sepeda (`cnt`), yang menunjukkan bahwa semakin hangat cuaca, semakin banyak orang yang menyewa sepeda.  
    - Kelembapan (`hum`) memiliki korelasi negatif lemah dengan penyewaan, artinya kelembapan tinggi sedikit mengurangi minat penyewaan sepeda.  
    - Kecepatan angin (`windspeed`) memiliki korelasi positif moderat, yang menunjukkan bahwa angin sepoi-sepoi mungkin membuat berkendara lebih nyaman.
    """)

elif analysis == "RFM":
  st.header("RFM Analysis")
  st.write("Segmentasi hari berdasarkan Recency, Frequency, Monetary")

  # Hitung RFM
  # Recency: Hari terakhir penyewaan (diasumsikan dari tanggal terakhir dataset)
  latest_date = pd.to_datetime(df_day['dteday']).max()
  df_day['recency'] = (latest_date - pd.to_datetime(df_day['dteday'])).dt.days

  # Frequency: Total penyewaan per hari
  frequency = df_day.groupby('dteday')['cnt'].sum().reset_index()
  frequency.rename(columns={'cnt': 'frequency'}, inplace=True)

  # Monetary: Total penyewaan sebagai nilai moneter
  monetary = df_day.groupby('dteday')['cnt'].sum().reset_index()
  monetary.rename(columns={'cnt': 'monetary'}, inplace=True)

  # Gabungkan RFM
  rfm = df_day[['dteday', 'recency']].merge(frequency,
                                            on='dteday').merge(monetary,
                                                               on='dteday')

  # Tampilkan dataframe RFM
  st.dataframe(rfm)

  # Insight
  st.write("""
    **Insight:**  
    - **Recency** menunjukkan seberapa baru suatu hari dalam dataset. Hari-hari dengan recency rendah adalah hari-hari terbaru dalam dataset.  
    - **Frequency** menunjukkan total jumlah penyewaan per hari. Hari-hari dengan frekuensi tinggi adalah hari-hari dengan permintaan tertinggi.  
    - **Monetary** mencerminkan pendapatan atau nilai ekonomi dari penyewaan pada hari tersebut.  
    - Segmentasi RFM dapat digunakan untuk mengidentifikasi hari-hari penting yang memberikan dampak besar pada bisnis, seperti hari libur atau akhir pekan.
    """)
