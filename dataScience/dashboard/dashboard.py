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

logo = ASSET / "text.png"
if logo.exists():
    left, center, right = st.columns([1.2, 1.6, 1.2])
    with center:
        st.image(str(logo), width=360)

st.markdown(
    hero(
        "Jivara: dari makanan yang terlihat ke keputusan medis yang lebih aman",
        "Dashboard ini merangkum bagaimana project Jivara menyatukan 4 aset inti: katalog nutrisi makanan, "
        "resep Indonesia, registrasi obat BPOM, dan knowledge base interaksi obat-makanan. Fokus utamanya bukan "
        "sekadar visualisasi, tetapi menunjukkan titik risiko dan peluang insight yang benar-benar relevan untuk produk.",
    ),
    unsafe_allow_html=True,
)

col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Kelas Makanan", f"{len(df_nutrisi):,}")
col2.metric("Resep", f"{len(df_resep):,}")
col3.metric("Produk BPOM", f"{len(df_obat):,}")
col4.metric("Makanan di KB", f"{len(foods):,}")
col5.metric("Interaksi KB", f"{len(idf):,}")

st.markdown(
    note(
        f"<strong>Insight kunci: Jivara menghubungkan {len(df_nutrisi)} kelas makanan, "
        f"{len(df_resep):,} resep lokal, dan {len(df_obat):,} produk obat BPOM ke dalam {len(idf):,} interaksi obat-makanan "
        f"yang terdeteksi. Artinya setiap makanan rata-rata terhubung ke "
        f"{len(idf) / max(len(foods), 1):.1f} potensi risiko obat — cukup untuk memberikan warning yang bermakna di level hidangan sehari-hari.</strong>"
    ),
    unsafe_allow_html=True,
)

st.markdown(section("Apa yang paling menonjol?"), unsafe_allow_html=True)
row1, row2, row3 = st.columns(3)
with row1:
    st.markdown(
        card(
            "Makanan inti project sangat resep-driven",
            f"Dataset resep berisi {len(df_resep):,} resep untuk {df_resep['Kelas_YOLO'].nunique()} kelas makanan. "
            f"Kelas paling sering muncul adalah {recipe_insight['most_common_class'].replace('-', ' ').title()} "
            f"dengan {recipe_insight['most_common_class_count']} resep, memberi sinyal kelas ini penting untuk prioritas model dan UX.",
            ["Cookpad", "61 kelas", "resep lokal"],
        ),
        unsafe_allow_html=True,
    )
with row2:
    st.markdown(
        card(
            "Portofolio BPOM sangat didominasi obat keras",
            f"{drug_insight['top_group']} mencakup {drug_insight['top_group_count']:,} produk. "
            f"Selain itu, {drug_insight['local_share']:.0%} produk berasal dari kategori lokal/lainnya, jadi coverage registrasi domestik adalah kekuatan data ini.",
            ["BPOM", "regulatory", "lokal dominan"],
        ),
        unsafe_allow_html=True,
    )
with row3:
    st.markdown(
        card(
            "Risiko interaksi paling sering tidak ringan",
            f"Dari {len(idf):,} interaksi di knowledge base, severity level 3-5 mendominasi. "
            f"Ini berarti value Jivara lebih kuat sebagai sistem pencegahan keputusan berisiko daripada sekadar edukasi nutrisi umum.",
            ["severity 3-5", "clinical alert", "safety first"],
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
            "Prioritas pengalaman pengguna",
            f"Resep rata-rata membutuhkan {recipe_insight['avg_ingredients']:.1f} bahan dan {recipe_insight['avg_steps']:.1f} langkah. "
            "Artinya penjelasan risiko sebaiknya dibuat sesingkat mungkin, karena konteks penggunaan sangat mungkin terjadi saat pengguna sedang memasak atau memilih makanan.",
            ["UX", "mobile-first", "short alerts"],
        ),
        unsafe_allow_html=True,
    )
with ins2:
    st.markdown(
        card(
            "Prioritas reasoning engine",
            f"{drug_insight['multi_active_share']:.0%} produk BPOM memiliki lebih dari satu zat aktif. "
            "Ini memberi sinyal bahwa reasoning engine Jivara perlu siap menangani kombinasi komposisi, bukan hanya pencocokan satu obat ke satu makanan.",
            ["knowledge graph", "multi-ingredient", "backend"],
        ),
        unsafe_allow_html=True,
    )

st.markdown(section("Arah eksplorasi halaman"), unsafe_allow_html=True)
nav1, nav2, nav3 = st.columns(3)
with nav1:
    st.markdown(
        card(
            "Nutrisi & Resep",
            "Lihat makanan yang padat kalori, kelas resep paling kompleks, dan bahan yang paling sering berulang untuk memahami pola konsumsi serta konteks masakan Indonesia.",
        ),
        unsafe_allow_html=True,
    )
with nav2:
    st.markdown(
        card(
            "Obat BPOM",
            "Telusuri dominasi golongan obat, bentuk sediaan utama, komposisi multi-zat aktif, dan profil produk lokal versus impor.",
        ),
        unsafe_allow_html=True,
    )
with nav3:
    st.markdown(
        card(
            "Interaksi Obat-Makanan",
            "Eksplorasi makanan dengan severity tertinggi, kelas obat paling sering terdampak, serta mekanisme interaksi yang paling penting untuk dijelaskan ke pengguna.",
        ),
        unsafe_allow_html=True,
    )
