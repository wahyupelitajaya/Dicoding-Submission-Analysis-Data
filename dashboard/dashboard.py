import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Karena file .py saya berada di folder yang berbeda dengan file .csv jadi saya pake metode ini
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Lokasi file script
DATA_DIR = os.path.join(BASE_DIR, "../data")  # Folder 'data' di luar folder script

# Path ke dataset
DAY_CSV_PATH = os.path.join(DATA_DIR, "day.csv")
HOUR_CSV_PATH = os.path.join(DATA_DIR, "hour.csv")

# Load dataset
df_day = pd.read_csv(DAY_CSV_PATH)
df_hour = pd.read_csv(HOUR_CSV_PATH)

# Konversi kolom tanggal menjadi datetime
df_day['dteday'] = pd.to_datetime(df_day['dteday'])
df_hour['dteday'] = pd.to_datetime(df_hour['dteday'])

# Judul
st.markdown("""
    <h1 style='text-align: center; font-size: 48px; font-weight: bold;'>Dashboard 📊</h1>
""", unsafe_allow_html=True)

st.markdown("""
    <h2 style='text-align: center; font-size: 24px; margin-top: -20px;'>Analisis Penyewaan Sepeda 🚲</h2>
""", unsafe_allow_html=True)

st.markdown("---")
st.write("""
Eksplorasi tersedia dengan berbagai parameter seperti waktu, cuaca, dan musim.  
Gunakan fitur interaktif di sidebar untuk menyesuaikan visualisasi sesuai kebutuhan Anda.
""")

# Sidebar untuk interaktivitas
st.sidebar.header("Filter Data")

# Fungsi untuk mendapatkan rentang tanggal berdasarkan musim
def get_date_range_for_season(season_key):
    season_filtered_df = df_day[df_day['season'] == season_key]
    if season_filtered_df.empty:
        return None, None
    min_date = season_filtered_df['dteday'].min().date()
    max_date = season_filtered_df['dteday'].max().date()
    return min_date, max_date

# Fungsi untuk mendapatkan musim berdasarkan tanggal
def get_season_for_date(date):
    season_mapping = {
        1: "Musim Semi",
        2: "Musim Panas",
        3: "Musim Gugur",
        4: "Musim Dingin"
    }
    season_key = df_day[df_day['dteday'].dt.date == date]['season'].values[0]
    return season_mapping.get(season_key, "Tidak Diketahui")

# Filter berdasarkan musim atau tanggal
seasons = {1: "Musim Semi", 2: "Musim Panas", 3: "Musim Gugur", 4: "Musim Dingin"}

# State untuk menyimpan pilihan terakhir
if 'selected_season' not in st.session_state:
    st.session_state.selected_season = "Musim Semi"
if 'start_date' not in st.session_state:
    st.session_state.start_date = df_day['dteday'].min().date()
if 'end_date' not in st.session_state:
    st.session_state.end_date = df_day['dteday'].max().date()

# Pilihan musim
selected_season = st.sidebar.selectbox(
    "Pilih Musim:",
    "Tekan sekali lagi apabila musim tidak berubah",
    list(seasons.values()),
    index=list(seasons.values()).index(st.session_state.selected_season)    
)

# Update state musim
st.session_state.selected_season = selected_season
season_key = [k for k, v in seasons.items() if v == selected_season][0]

# Dapatkan rentang tanggal berdasarkan musim yang dipilih
min_date, max_date = get_date_range_for_season(season_key)

# Jika rentang tanggal valid, atur tanggal awal dan akhir
if min_date and max_date:
    start_date, end_date = st.sidebar.date_input(
        "Pilih Rentang Tanggal:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date
    )
    st.session_state.start_date = start_date
    st.session_state.end_date = end_date

# Jika tanggal dipilih, atur musim berdasarkan tanggal pertama
if 'start_date' in st.session_state:
    selected_date = st.session_state.start_date
    detected_season = get_season_for_date(selected_date)
    if detected_season != st.session_state.selected_season:
        st.session_state.selected_season = detected_season
        selected_season = detected_season
        season_key = [k for k, v in seasons.items() if v == selected_season][0]

# Filter dataset berdasarkan musim dan rentang tanggal
filtered_df = df_day[
    (df_day['season'] == season_key) &
    (df_day['dteday'].dt.date >= st.session_state.start_date) &
    (df_day['dteday'].dt.date <= st.session_state.end_date)
]

# Filter berdasarkan hari kerja atau hari libur
workingday_options = {0: "Hari Libur", 1: "Hari Kerja"}
selected_workingday = st.sidebar.selectbox("Pilih Hari Kerja:", list(workingday_options.values()))
workingday_key = [k for k, v in workingday_options.items() if v == selected_workingday][0]

# Sesuaikan filter untuk hari libur atau hari kerja
filtered_df = filtered_df[filtered_df['workingday'] == workingday_key]

# Slider untuk rentang suhu
st.sidebar.subheader("Rentang Suhu (Normalisasi)")
min_temp, max_temp = st.sidebar.slider("Pilih Rentang Suhu:", 0.0, 1.0, (0.2, 0.8))
temp_filtered_df = filtered_df[(filtered_df['temp'] >= min_temp) & (filtered_df['temp'] <= max_temp)]

# Cek apakah ada data yang tersedia setelah filter hari kerja/libur
if temp_filtered_df.empty:
    # Jika tidak ada data, tampilkan keterangan untuk membantu pengguna
    if workingday_key == 1:
        st.warning("""
            **Tidak ada data yang tersedia untuk rentang tanggal ini sebagai hari kerja.**
            - Tampaknya tanggal yang dipilih bukan termasuk hari kerja.
            - Cobalah memilih rentang tanggal yang mencakup hari Senin hingga Jumat.
        """)
    else:
        st.warning("""
            **Tidak ada data yang tersedia untuk rentang tanggal ini sebagai hari libur.**
            - Tampaknya tanggal yang dipilih bukan termasuk hari libur.
            - Cobalah memilih rentang tanggal yang mencakup akhir pekan (Sabtu/Minggu) atau hari libur nasional.
        """)
else:
    # Tampilkan keterangan tambahan jika data tersedia
    avg_temp = temp_filtered_df['temp'].mean()
    avg_atemp = temp_filtered_df['atemp'].mean()
    st.info(f"""
        **Informasi Tambahan:**
        - Suhu rata-rata pada rentang tanggal ini: **{avg_temp:.2f}** (normalisasi).
        - Sensasi suhu rata-rata: **{avg_atemp:.2f}** (normalisasi).
    """)

# Sidebar untuk pilih analisis
analysis = st.sidebar.selectbox("Pilih Analisis:", ["Pola Harian", "Pengaruh Cuaca", "RFM"])

if analysis == "Pola Harian":
    st.header("📈 Pola Penyewaan per Jam")

    # Filter df_hour berdasarkan parameter yang dipilih
    filtered_hour = df_hour[
        (df_hour['season'] == season_key) &
        (df_hour['dteday'].dt.date >= st.session_state.start_date) &
        (df_hour['dteday'].dt.date <= st.session_state.end_date) &
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

    # Insight untuk Pola Harian
    st.write("""
    - **Grafik ini menunjukkan pola penyewaan sepeda setiap jam dalam sehari.**
    - Terlihat bahwa penyewaan meningkat pada pagi hari (sekitar jam 7–9) dan sore hari (sekitar jam 17–19). Ini biasanya terjadi karena banyak orang menggunakan sepeda untuk pergi ke kantor atau sekolah.
    - Pada malam hari (setelah jam 21), jumlah penyewaan menurun drastis karena aktivitas masyarakat umumnya berkurang.
    - Anda bisa memanfaatkan informasi ini untuk memastikan jumlah sepeda tersedia cukup di jam-jam sibuk!
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

    # Insight untuk Korelasi Cuaca
    st.write("""
    - **Heatmap ini menunjukkan hubungan antara cuaca dan jumlah penyewaan sepeda.**
    - Suhu hangat membuat lebih banyak orang tertarik menyewa sepeda. Semakin tinggi suhu, semakin tinggi pula jumlah penyewaan.
    - Kelembapan tinggi sedikit mengurangi minat penyewaan, mungkin karena cuaca lembap kurang nyaman untuk bersepeda.
    - Angin sepoi-sepoi justru membuat berkendara lebih nyaman, sehingga jumlah penyewaan cenderung meningkat saat angin tidak terlalu kencang.
    - Informasi ini bisa membantu Anda memprediksi lonjakan penyewaan berdasarkan kondisi cuaca!
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

    # Insight untuk RFM
    st.write("""
    - **Tabel ini membantu kita memahami performa hari-hari tertentu berdasarkan tiga faktor: Recency, Frequency, dan Monetary.**
    - **Recency:** Menunjukkan seberapa baru hari tersebut dalam dataset. Hari-hari dengan nilai rendah adalah hari-hari terbaru.
    - **Frequency:** Menunjukkan berapa kali sepeda disewa dalam satu hari. Hari-hari dengan frekuensi tinggi biasanya merupakan hari-hari sibuk seperti akhir pekan atau hari libur.
    - **Monetary:** Mencerminkan total pendapatan dari penyewaan sepeda pada hari tersebut. Hari-hari dengan nilai tinggi memberikan kontribusi besar bagi bisnis.
    - Anda bisa menggunakan analisis ini untuk fokus pada hari-hari penting yang memberikan dampak besar pada bisnis, seperti akhir pekan atau musim liburan!
    """)
