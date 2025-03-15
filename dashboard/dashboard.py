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
df_day = pd.read_csv(DAY_CSV_PATH)
df_hour = pd.read_csv(HOUR_CSV_PATH)

st.title("📊 Dashboard Analisis Penyewaan Sepeda 🚲")

# Sidebar untuk interaktivitas
st.sidebar.header("Filter Data")

# Filter berdasarkan musim
seasons = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
selected_season = st.sidebar.selectbox("Pilih Musim:", list(seasons.values()))
season_key = [k for k, v in seasons.items() if v == selected_season][0]
filtered_df = df_day[df_day['season'] == season_key]

# Filter berdasarkan tahun
years = {0: "2011", 1: "2012"}
selected_year = st.sidebar.selectbox("Pilih Tahun:", list(years.values()))
year_key = [k for k, v in years.items() if v == selected_year][0]
filtered_df = filtered_df[filtered_df['yr'] == year_key]

# Filter berdasarkan hari kerja
workingday_options = {0: "Hari Libur", 1: "Hari Kerja"}
selected_workingday = st.sidebar.selectbox("Pilih Hari Kerja:", list(workingday_options.values()))
workingday_key = [k for k, v in workingday_options.items() if v == selected_workingday][0]
filtered_df = filtered_df[filtered_df['workingday'] == workingday_key]

# Slider untuk rentang suhu
st.sidebar.subheader("Rentang Suhu (Normalisasi)")
min_temp, max_temp = st.sidebar.slider("Pilih Rentang Suhu:", 0.0, 1.0, (0.2, 0.8))
temp_filtered_df = filtered_df[(filtered_df['temp'] >= min_temp) & (filtered_df['temp'] <= max_temp)]

# Sidebar untuk pilih analisis
analysis = st.sidebar.selectbox("Pilih Analisis:", ["Pola Harian", "Pengaruh Cuaca", "RFM"])

if analysis == "Pola Harian":
    st.header("📈 Pola Penyewaan per Jam")

    # Filter df_hour berdasarkan parameter yang dipilih
    filtered_hour = df_hour[
        (df_hour['season'] == season_key) &
        (df_hour['yr'] == year_key) &
        (df_hour['workingday'] == workingday_key) &
        (df_hour['temp'] >= min_temp) &
        (df_hour['temp'] <= max_temp)
    ]

    # Hitung rata-rata penyewaan per jam berdasarkan data yang difilter
    hourly_rentals = filtered_hour.groupby('hr')['cnt'].mean().reset_index()

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
    st.header("🌧️ Korelasi Cuaca dengan Penyewaan")
    # Ambil kolom relevan untuk korelasi
    corr = temp_filtered_df[['temp', 'hum', 'windspeed', 'cnt']].corr()

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
    st.header("📊 RFM Analysis")
    st.write("Segmentasi hari berdasarkan Recency, Frequency, Monetary")

    # Hitung RFM
    latest_date = pd.to_datetime(temp_filtered_df['dteday']).max()
    temp_filtered_df['recency'] = (latest_date - pd.to_datetime(temp_filtered_df['dteday'])).dt.days

    frequency = temp_filtered_df.groupby('dteday')['cnt'].sum().reset_index()
    frequency.rename(columns={'cnt': 'frequency'}, inplace=True)

    monetary = temp_filtered_df.groupby('dteday')['cnt'].sum().reset_index()
    monetary.rename(columns={'cnt': 'monetary'}, inplace=True)

    rfm = temp_filtered_df[['dteday', 'recency']].merge(frequency, on='dteday').merge(monetary, on='dteday')

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
