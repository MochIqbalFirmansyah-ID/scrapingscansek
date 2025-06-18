import streamlit as st
from pymongo import MongoClient
import pandas as pd
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS
import nltk

# Unduh stopwords untuk WordCloud
nltk.download('stopwords')

# Konfigurasi halaman
st.set_page_config(page_title="Dashboard ScanSek", layout="wide")

# Koneksi ke MongoDB
client = MongoClient('mongodb://iqbal:passwordkuaman@70.153.17.43:27017/beritascansek_db?authSource=beritascansek_db')
db = client['beritascansek_db']
collection = db['berita_kesehatan']

# Ambil data dari MongoDB
data = list(collection.find())
df = pd.DataFrame(data)

# Tambahkan kolom default jika tidak ada
for col in ['judul', 'description', 'link', 'source', 'category']:
    if col not in df.columns:
        df[col] = None

# Judul Aplikasi
st.markdown("""
    <h1 style='text-align: center; color: #007acc;'>📊 Dashboard Berita Kesehatan</h1>
    <p style='text-align: center;'>Visualisasi hasil scraping dari berbagai sumber berita bertema kesehatan.</p>
""", unsafe_allow_html=True)

# ====================
# 🔍 Sidebar Filter
# ====================
with st.sidebar:
    st.header("🔍 Filter & Info")
    st.markdown(f"Total Artikel: **{len(df)}**")

    # Filter sumber berita
    sumber_unik = df['source'].dropna().unique()
    sumber_filter = st.multiselect("Pilih sumber berita:", sumber_unik.tolist(), default=sumber_unik.tolist())

    # Filter kategori
    kategori_unik = df['category'].dropna().unique()
    kategori_filter = st.multiselect("Pilih kategori:", kategori_unik.tolist(), default=kategori_unik.tolist())

    # Pencarian judul
    search_query = st.text_input("Cari judul artikel...")

# ====================
# 🔄 Filter DataFrame
# ====================
filtered_df = df[
    df['source'].isin(sumber_filter) &
    df['category'].isin(kategori_filter)
]

if search_query:
    filtered_df = filtered_df[filtered_df['judul'].str.contains(search_query, case=False, na=False)]

# ====================
# 📰 Daftar Berita
# ====================
st.subheader("📰 Daftar Berita Kesehatan")

berita_per_halaman = 9
total_berita = len(filtered_df)
total_halaman = max(1, (total_berita - 1) // berita_per_halaman + 1)

if 'halaman' not in st.session_state:
    st.session_state.halaman = 1

col1, col2, col3 = st.columns([1, 2, 1])
with col1:
    if st.button("⬅️ Sebelumnya") and st.session_state.halaman > 1:
        st.session_state.halaman -= 1
with col3:
    if st.button("➡️ Selanjutnya") and st.session_state.halaman < total_halaman:
        st.session_state.halaman += 1

start_idx = (st.session_state.halaman - 1) * berita_per_halaman
end_idx = start_idx + berita_per_halaman
page_data = filtered_df.iloc[start_idx:end_idx]

cols = st.columns(3)
for idx, (_, row) in enumerate(page_data.iterrows()):
    with cols[idx % 3]:
        st.markdown(f"""
        <div style='border: 1px solid #ccc; border-radius: 12px; padding: 15px; margin-bottom: 15px; background-color: #f9f9f9;'>
            <h4 style='margin-bottom: 10px;'>{row.get('judul', '-')}</h4>
            <p style='font-size: 14px; color: #555;'>{row.get('description', '-')[:100]}...</p>
            <a href='{row.get('link', '#')}' target='_blank'>🔗 Baca selengkapnya</a>
        </div>
        """, unsafe_allow_html=True)

st.markdown(f"<p style='text-align:center;'>Halaman {st.session_state.halaman} dari {total_halaman}</p>", unsafe_allow_html=True)
