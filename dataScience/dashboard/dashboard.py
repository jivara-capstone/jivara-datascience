import pandas as pd
import plotly.express as px
import streamlit as st

from ui import (
    ASSET,
    BRAND,
    DATA,
    PROC,
    add_bar_headroom,
    add_sidebar,
    apply_theme,
    style_bar_labels,
    style_figure,
    card,
    compute_drug_insights,
    compute_interaction_frame,
    compute_recipe_insights,
    hero,
    load_kb,
    note,
    plotly_layout,
    section,
)

page_icon = str(ASSET / "splash.png") if (ASSET / "splash.png").exists() else "🌿"
st.set_page_config(page_title="Jivara Dashboard", page_icon=page_icon, layout="wide", initial_sidebar_state="expanded")
st.markdown(apply_theme(), unsafe_allow_html=True)
add_sidebar("Dashboard Jivara", "Executive summary project data science")


@st.cache_data
def load_data():
    nutrisi = pd.read_csv(PROC / "unified_nutrition.csv")
    resep = pd.read_csv(PROC / "61_kelas_resep_cleaned.csv")
    obat = pd.read_csv(PROC / "obat_bpom_cleaned_dedup.csv")
    kb = load_kb(DATA / "for_backend" / "drug_food_kb_final_v3.json")
    return nutrisi, resep, obat, kb


df_nutrisi, df_resep, df_obat, kb = load_data()
idf, foods = compute_interaction_frame(kb)
recipe_insight = compute_recipe_insights(df_resep)
drug_insight = compute_drug_insights(df_obat)
pl = plotly_layout()

st.markdown(
    hero(
        "Jivara: dari makanan yang terlihat ke keputusan medis yang lebih aman",
        "Dashboard ini merangkum bagaimana project Jivara menyatukan 4 aset inti: katalog nutrisi makanan, "
        "resep Indonesia, registrasi obat BPOM, dan knowledge base interaksi obat-makanan. Fokus utamanya bukan "
        "sekadar visualisasi, tetapi menunjukkan titik risiko dan peluang insight yang benar-benar relevan untuk produk.",
    ),
    unsafe_allow_html=True,
)

col1, col2, col3, col4 = st.columns(4)
col1.metric("Kelas Makanan", f"{len(df_nutrisi):,}")
col2.metric("Resep", f"{len(df_resep):,}")
col3.metric("Makanan Dipantau", f"{len(foods):,}")
col4.metric("Risiko Interaksi", f"{len(idf):,}")

st.markdown(
    note(
        f"<strong>Snapshot data:</strong> Jivara menghubungkan {len(df_nutrisi)} jenis makanan, "
        f"{len(df_resep):,} resep lokal, dan {len(df_obat):,} produk obat yang terdaftar BPOM. "
        f"Dari data tersebut, sistem mendeteksi {len(idf):,} interaksi potensial antara obat dan makanan. "
        f"Rata-rata setiap makanan terhubung ke {len(idf) / max(len(foods), 1):.1f} risiko—cukup untuk memberikan peringatan bermakna saat pengguna memilih menu atau minum obat.</strong>"
    ),
    unsafe_allow_html=True,
)

st.markdown(section("Apa yang paling menonjol?"), unsafe_allow_html=True)
row1, row2, row3 = st.columns(3)
with row1:
    st.markdown(
        card(
            "Dataset resep sangat beragam",
            f"Ada {len(df_resep):,} resep untuk {df_resep['Kelas_YOLO'].nunique()} jenis makanan. "
            f"Makanan terbanyak adalah {recipe_insight['most_common_class'].replace('-', ' ').title()} "
            f"dengan {recipe_insight['most_common_class_count']} resep—ini makanan penting untuk sistem.",
            ["61 jenis makanan", "dari Cookpad", "lokal Indonesia"],
        ),
        unsafe_allow_html=True,
    )
with row2:
    st.markdown(
        card(
            "Obat keras mendominasi daftar BPOM",
            f"Obat {drug_insight['top_group']} terbanyak dengan {drug_insight['top_group_count']:,} produk. "
            f"Selain itu, {drug_insight['local_share']:.0%} obat lokal atau uncategorized—banyak produk Indonesia terdaftar.",
            ["registrasi lokal", "BPOM regulatory", "keamanan diperhatikan"],
        ),
        unsafe_allow_html=True,
    )
with row3:
    st.markdown(
        card(
            "Mayoritas interaksi termasuk kategori serius",
            f"Dari {len(idf):,} interaksi yang terdaftar, sebagian besar level 3-5 (serius). "
            f"Ini berarti Jivara penting untuk pencegahan, bukan sekadar informasi nutrisi biasa.",
            ["severe interactions", "clinical alerts", "safety system"],
        ),
        unsafe_allow_html=True,
    )

st.markdown(section("Distribusi aset data"), unsafe_allow_html=True)
left, right = st.columns([1.2, 1])
with left:
    source_counts = (
        df_nutrisi["macro_category"]
        .value_counts()
        .rename_axis("Kategori")
        .reset_index(name="Jumlah")
    )
    fig = px.bar(
        source_counts,
        x="Kategori",
        y="Jumlah",
        color="Kategori",
        text="Jumlah",
        color_discrete_sequence=[BRAND["green"], BRAND["gold"], BRAND["mint"], BRAND["coral"]],
    )
    fig.update_traces(textposition="outside")
    style_bar_labels(fig)
    fig.update_layout(**pl, title="Distribusi Kategori Makronutrien")
    style_figure(fig, height=420, x_title="Kategori", y_title="Jumlah Kelas Makanan", legend=False)
    add_bar_headroom(fig, source_counts["Jumlah"])
    st.plotly_chart(fig, width="stretch")
with right:
    type_counts = idf["Tipe"].value_counts().reset_index()
    type_counts.columns = ["Tipe", "Jumlah"]
    fig = px.pie(
        type_counts,
        names="Tipe",
        values="Jumlah",
        hole=0.52,
        color="Tipe",
        color_discrete_map={
            "AVOID": BRAND["coral"],
            "MONITOR": BRAND["gold"],
            "LIMIT": BRAND["mint"],
            "TIMING": BRAND["green"],
        },
    )
    fig.update_traces(textposition="inside", textinfo="percent+label", textfont=dict(size=14, color=BRAND["forest"]))
    fig.update_layout(**pl, title="Komposisi Tipe Interaksi", height=400)
    st.plotly_chart(fig, width="stretch")

st.markdown(section("Insight untuk product direction"), unsafe_allow_html=True)
ins1, ins2 = st.columns(2)
with ins1:
    st.markdown(
        card(
            "Desain untuk pengguna yang sibuk",
            f"Setiap resep rata-rata butuh {recipe_insight['avg_ingredients']:.1f} bahan dan {recipe_insight['avg_steps']:.1f} langkah memasak. "
            "Artinya warning obat-makanan harus singkat dan jelas, karena pengguna kemungkinan besar sedang memasak atau memilih menu makan.",
            ["UX priority", "mobile-first", "alert design"],
        ),
        unsafe_allow_html=True,
    )
with ins2:
    st.markdown(
        card(
            "Sistem butuh mengenali kombinasi obat",
            f"{drug_insight['multi_active_share']:.0%} obat BPOM memiliki lebih dari satu zat aktif. "
            "Ini berarti sistem tidak bisa hanya mencocokkan satu obat ke satu makanan—harus bisa handle kombinasi zat aktif yang kompleks.",
            ["kompleks composition", "multi-zat", "reasoning"],
        ),
        unsafe_allow_html=True,
    )

st.markdown(section("Halaman lain yang bisa dijelajahi"), unsafe_allow_html=True)
nav1, nav2, nav3 = st.columns(3)
with nav1:
    st.markdown(
        card(
            "Nutrisi & Resep",
            "Lihat makanan berkalori tinggi, resep paling kompleks, bahan yang sering digunakan, dan pola konsumsi makanan Indonesia.",
        ),
        unsafe_allow_html=True,
    )
with nav2:
    st.markdown(
        card(
            "Daftar Obat BPOM",
            "Telusuri jenis obat, bentuk sediaan, zat aktif dalam produk, serta obat lokal versus impor.",
        ),
        unsafe_allow_html=True,
    )
with nav3:
    st.markdown(
        card(
            "Interaksi Obat-Makanan",
            "Cari makanan berbahaya, obat yang sering berinteraksi, dan cara interaksi terjadi untuk edukasi pengguna.",
        ),
        unsafe_allow_html=True,
    )
