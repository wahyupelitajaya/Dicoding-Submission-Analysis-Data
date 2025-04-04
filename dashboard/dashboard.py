import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Load dataset
day_df = pd.read_csv("https://raw.githubusercontent.com/wahyupelitajaya/Dicoding-Submission-Analysis-Data/refs/heads/main/data/day.csv")
hour_df = pd.read_csv("https://raw.githubusercontent.com/wahyupelitajaya/Dicoding-Submission-Analysis-Data/refs/heads/main/data/hour.csv")

# Rename kolom untuk kemudahan
day_df.rename(columns={
    'dteday': 'tanggal',
    'weathersit': 'cuaca',
    'temp': 'suhu',
    'hum': 'kelembaban',
    'windspeed': 'kecepatan_angin',
    'cnt': 'total_sewa'
}, inplace=True)

hour_df.rename(columns={
    'dteday': 'tanggal',
    'hr': 'jam',
    'weathersit': 'cuaca',
    'temp': 'suhu',
    'hum': 'kelembaban',
    'windspeed': 'kecepatan_angin',
    'cnt': 'total_sewa'
}, inplace=True)

# Konversi kolom tanggal ke datetime
day_df['tanggal'] = pd.to_datetime(day_df['tanggal'])
hour_df['tanggal'] = pd.to_datetime(hour_df['tanggal'])

# Judul
st.markdown("""<h1 style='text-align: center; font-size: 48px; font-weight: bold;'>Dashboard 📊</h1>""", unsafe_allow_html=True)
st.markdown("""<h2 style='text-align: center; font-size: 24px; margin-top: -20px;'>Analisis Penyewaan Sepeda 🚴‍♂️</h2>""", unsafe_allow_html=True)
st.markdown("---")
st.write("""
Eksplorasi tersedia dengan berbagai parameter seperti waktu, cuaca, dan musim.
Gunakan fitur interaktif di sidebar untuk menyesuaikan visualisasi sesuai kebutuhan Anda.
""")

# Sidebar untuk interaktivitas
st.sidebar.header("Filter Data")

# Filter berdasarkan jam
st.sidebar.subheader("Rentang Jam")
min_hour, max_hour = st.sidebar.slider("Pilih Rentang Jam:", 0, 23, (6, 18))

# Filter berdasarkan cuaca (suhu, kelembaban, kecepatan angin)
st.sidebar.subheader("Rentang Suhu (Normalisasi)")
min_temp, max_temp = st.sidebar.slider("Pilih Rentang Suhu:", 0.0, 1.0, (0.2, 0.8))

st.sidebar.subheader("Rentang Kelembaban (%)")
min_humidity, max_humidity = st.sidebar.slider("Pilih Rentang Kelembaban:", 0.0, 1.0, (0.2, 0.8))

st.sidebar.subheader("Rentang Kecepatan Angin (Normalisasi)")
min_windspeed, max_windspeed = st.sidebar.slider("Pilih Rentang Kecepatan Angin:", 0.0, 1.0, (0.1, 0.5))

# Filter berdasarkan hari libur atau hari kerja
workingday_options = {0: "Hari Libur", 1: "Hari Kerja"}
selected_workingday = st.sidebar.selectbox("Pilih Hari Kerja/Libur:", list(workingday_options.values()))
workingday_key = [k for k, v in workingday_options.items() if v == selected_workingday][0]

# Filter dataset berdasarkan parameter yang dipilih
filtered_hour = hour_df[
    (hour_df['jam'] >= min_hour) & (hour_df['jam'] <= max_hour) &
    (hour_df['suhu'] >= min_temp) & (hour_df['suhu'] <= max_temp) &
    (hour_df['kelembaban'] >= min_humidity) & (hour_df['kelembaban'] <= max_humidity) &
    (hour_df['kecepatan_angin'] >= min_windspeed) & (hour_df['kecepatan_angin'] <= max_windspeed) &
    (hour_df['workingday'] == workingday_key)
]

# Sidebar untuk pilih analisis
analysis = st.sidebar.selectbox("Pilih Analisis:", ["Pola Harian", "Pengaruh Cuaca", "Hari Kerja vs Libur"])

# Analisis Pola Harian
if analysis == "Pola Harian":
    st.header("📊 Pola Penyewaan per Jam")
    
    # Agregasi rata-rata penyewaan per jam berdasarkan data yang difilter
    hourly_rentals = filtered_hour.groupby('jam')['total_sewa'].mean().reset_index()

    # Visualisasi
    plt.figure(figsize=(12, 6))
    sns.lineplot(x='jam', y='total_sewa', data=hourly_rentals, marker='o')
    plt.title('Pola Penyewaan Sepeda per Jam 🕕')
    plt.xlabel('Jam')
    plt.ylabel('Rata-Rata Penyewaan')
    plt.grid(True)
    st.pyplot(plt)

    # Insight untuk Pola Harian
    st.write("""
    - **Grafik ini menunjukkan pola penyewaan sepeda setiap jam dalam sehari.**
    - Terlihat bahwa penyewaan meningkat pada pagi hari (sekitar jam 7–9) dan sore hari (sekitar jam 17–19). 
      Ini biasanya terjadi karena banyak orang menggunakan sepeda untuk pergi ke kantor atau sekolah.
    - Pada malam hari (setelah jam 21), jumlah penyewaan menurun drastis karena aktivitas masyarakat umumnya berkurang.
    - Anda bisa memanfaatkan informasi ini untuk memastikan jumlah sepeda tersedia cukup di jam-jam sibuk!
    """)

# Analisis Pengaruh Cuaca
elif analysis == "Pengaruh Cuaca":
    st.header("🌤️ Pengaruh Cuaca terhadap Penyewaan")

    # Scatterplot 1: Hubungan antara suhu & cuaca dengan total penyewaan
    plt.figure(figsize=(18, 6))

    plt.subplot(1, 3, 1)  # 1 baris, 3 kolom, plot pertama
    sns.scatterplot(x='suhu', y='total_sewa', hue='cuaca', data=filtered_hour)
    plt.title('Pengaruh Suhu dan Cuaca terhadap Penyewaan')
    plt.xlabel('Suhu (°C)')
    plt.ylabel('Total Penyewaan Sepeda')

    # Scatterplot 2: Hubungan antara kelembapan dengan total penyewaan
    plt.subplot(1, 3, 2)  # 1 baris, 3 kolom, plot kedua
    sns.scatterplot(x='kelembaban', y='total_sewa', hue='cuaca', data=filtered_hour)
    plt.title('Pengaruh Kelembapan terhadap Penyewaan')
    plt.xlabel('Kelembapan (%)')
    plt.ylabel('Total Penyewaan Sepeda')

    # Scatterplot 3: Hubungan antara kecepatan angin dengan total penyewaan
    plt.subplot(1, 3, 3)  # 1 baris, 3 kolom, plot ketiga
    sns.scatterplot(x='kecepatan_angin', y='total_sewa', hue='cuaca', data=filtered_hour)
    plt.title('Pengaruh Kecepatan Angin terhadap Penyewaan')
    plt.xlabel('Kecepatan Angin (km/h)')
    plt.ylabel('Total Penyewaan Sepeda')

    # Tampilkan semua plot
    plt.tight_layout()
    st.pyplot(plt)

    # Insight untuk Pengaruh Cuaca
    st.write("""
    - **Grafik ini menunjukkan pengaruh cuaca terhadap pola penyewaan sepeda.**
    - Suhu hangat cenderung meningkatkan jumlah penyewaan, sementara suhu dingin menurunkannya.
    - Kelembapan tinggi sedikit mengurangi minat penyewaan, kemungkinan karena kondisi lembap kurang nyaman untuk bersepeda.
    - Kecepatan angin rendah hingga sedang membuat berkendara lebih nyaman, sehingga jumlah penyewaan cenderung meningkat.
    - Informasi ini bisa membantu Anda memprediksi lonjakan penyewaan berdasarkan kondisi cuaca!
    """)

# Analisis Hari Kerja vs Libur
elif analysis == "Hari Kerja vs Libur":
    st.header("📅 Rata-rata Penyewaan Berdasarkan Hari Kerja/Libur")

    # Filter dataset hari (day_df) berdasarkan parameter yang dipilih di sidebar
    filtered_day = day_df[
        (day_df['suhu'] >= min_temp) & (day_df['suhu'] <= max_temp) &
        (day_df['kelembaban'] >= min_humidity) & (day_df['kelembaban'] <= max_humidity) &
        (day_df['kecepatan_angin'] >= min_windspeed) & (day_df['kecepatan_angin'] <= max_windspeed)
    ]

    # Hitung rata-rata total penyewaan berdasarkan hari kerja/libur dari dataset yang sudah difilter
    workday_analysis = filtered_day.groupby('workingday')['total_sewa'].mean().reset_index()
    workday_analysis['workingday'] = workday_analysis['workingday'].map({0: "Hari Libur", 1: "Hari Kerja"})

    # Visualisasi
    plt.figure(figsize=(8, 5))
    sns.barplot(x='workingday', y='total_sewa', data=workday_analysis)
    plt.title("Rata-rata Penyewaan Sepeda Berdasarkan Hari Kerja/Libur")
    plt.xlabel("Hari")
    plt.ylabel("Rata-rata Jumlah Penyewaan")
    st.pyplot(plt)

    # Insight untuk Hari Kerja vs Libur
    st.write("""
    - **Grafik ini menunjukkan perbandingan rata-rata penyewaan antara hari kerja dan hari libur.**
    - Penyewaan lebih tinggi pada hari kerja dibandingkan hari libur.
    - Hal ini menunjukkan bahwa sepeda lebih sering digunakan untuk komuter di hari kerja.
    - Namun, hari libur juga memiliki potensi besar untuk meningkatkan penyewaan melalui promosi khusus.
    """)
