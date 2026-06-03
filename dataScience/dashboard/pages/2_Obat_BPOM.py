import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))

from ui import (
    ASSET,
    BRAND,
    PROC,
    add_bar_headroom,
    add_sidebar,
    apply_theme,
    card,
    hero,
    note,
    plotly_layout,
    render_search_table,
    section,
    style_bar_labels,
    style_figure,
    wrap_text,
)

page_icon = str(ASSET / "splash.png") if (ASSET / "splash.png").exists() else "🌿"
st.set_page_config(page_title="Data Obat - Jivara", page_icon=page_icon, layout="wide")
st.markdown(apply_theme(), unsafe_allow_html=True)
add_sidebar("Data Obat", "Katalog produk obat lengkap dengan kategori interaksi")
pl = plotly_layout()


@st.cache_data
def load_data():
    df = pd.read_csv(PROC / "obat_backend_perawat_one_composition_mapped.csv")
    df["tanggal_terbit"] = pd.to_datetime(df["tanggal_terbit"], errors="coerce")
    df["masa_berlaku_sd"] = pd.to_datetime(df["masa_berlaku_sd"], errors="coerce")
    return df


df = load_data()

# Compute insights
df_with_category = df[df['drug_category'].notna()]
top_category = df_with_category["drug_category"].value_counts().index[0] if len(df_with_category) > 0 else "-"
top_category_count = int(df_with_category["drug_category"].value_counts().iloc[0]) if len(df_with_category) > 0 else 0
local_share = (df["negara_asal"] == "Indonesia").mean()
multi_active_share = (df["jumlah_zat_aktif"] > 1).mean()
expiring_1y = int(((df["masa_berlaku_sd"] - pd.Timestamp.today()).dt.days <= 365).fillna(False).sum())
needs_prescription = (df["perlu_resep"] == 1).sum()

st.markdown(
    hero(
        "Data obat tervalidasi untuk sistem Jivara",
        "Katalog ini berisi SEMUA obat yang sudah di-validasi dengan kategori interaksi lengkap. "
        "Setiap obat sudah melalui mapping dan dikurasi untuk memastikan akurasi deteksi risiko interaksi dengan makanan.",
    ),
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Produk Tervalidasi", f"{len(df):,}")
c2.metric("Dengan Kategori", f"{len(df_with_category):,}")
c3.metric("Pangsa Lokal", f"{local_share:.0%}")
c4.metric("Perlu Resep", f"{needs_prescription:,}")

st.markdown(section("Insight cepat"), unsafe_allow_html=True)
i1, i2, i3 = st.columns(3)
with i1:
    st.markdown(
        card(
            "Kategori obat terbanyak",
            f"{top_category} paling banyak ({top_category_count:,} produk). "
            "Kategori ini adalah fokus utama untuk pencegahan risiko interaksi dengan makanan.",
        ),
        unsafe_allow_html=True,
    )
with i2:
    st.markdown(
        card(
            "Obat yang memerlukan resep",
            f"{needs_prescription:,} obat memerlukan resep dokter. "
            "Jenis obat ini perlu lebih diperhatikan dalam checking interaksi.",
        ),
        unsafe_allow_html=True,
    )
with i3:
    st.markdown(
        card(
            "Beberapa obat akan segera expired",
            f"Sekitar {expiring_1y:,} produk berakhir masa berlakunya dalam 12 bulan. "
            "Database perlu diperbaharui untuk menjaga akurasi sistem.",
        ),
        unsafe_allow_html=True,
    )

st.markdown(
    note(
        f"<strong>Catatan penting:</strong> Data ini berisi {len(df)} obat yang telah di-validasi dengan kategori interaksi lengkap. "
        f"Setiap obat sudah dimap untuk sistem checking interaksi obat-makanan."
    ),
    unsafe_allow_html=True,
)

left, right = st.columns(2)
with left:
    # Show drug category distribution
    category_counts = df["drug_category"].value_counts().reset_index()
    category_counts.columns = ["Kategori Interaksi", "Jumlah"]
    category_counts["Kategori Interaksi"] = wrap_text(category_counts["Kategori Interaksi"], 14)
    fig = px.bar(
        category_counts.head(12),
        x="Jumlah",
        y="Kategori Interaksi",
        orientation="h",
        color="Jumlah",
        color_continuous_scale=[BRAND["lime"], BRAND["mint"], BRAND["forest"]],
        text="Jumlah",
    )
    fig.update_traces(textposition="outside")
    style_bar_labels(fig)
    fig.update_layout(**pl, title="Kategori Interaksi Obat - TOP 12", coloraxis_showscale=False)
    style_figure(fig, height=440, x_title="Jumlah Produk", y_title="Kategori")
    add_bar_headroom(fig, category_counts.head(12)["Jumlah"], orientation="h")
    st.plotly_chart(fig, width="stretch")
with right:
    dosage = df["bentuk_sediaan"].value_counts().head(12).reset_index()
    dosage.columns = ["Bentuk Sediaan", "Jumlah"]
    dosage["Bentuk Sediaan"] = wrap_text(dosage["Bentuk Sediaan"], 20)
    fig = px.bar(
        dosage.sort_values("Jumlah"),
        x="Jumlah",
        y="Bentuk Sediaan",
        orientation="h",
        color="Jumlah",
        color_continuous_scale=[BRAND["lime"], BRAND["mint"], BRAND["forest"]],
        text="Jumlah",
    )
    fig.update_traces(textposition="outside")
    style_bar_labels(fig)
    fig.update_layout(**pl, title="Bentuk Sediaan Terbanyak", coloraxis_showscale=False)
    style_figure(fig, height=440, x_title="Jumlah Produk", y_title="Bentuk Sediaan")
    add_bar_headroom(fig, dosage["Jumlah"], orientation="h")
    st.plotly_chart(fig, width="stretch")

st.markdown(section("Status obat dan keperluan resep"), unsafe_allow_html=True)
left, right = st.columns(2)
with left:
    origin = df["negara_asal"].value_counts().reset_index()
    origin.columns = ["Asal", "Jumlah"]
    fig = px.pie(
        origin,
        names="Asal",
        values="Jumlah",
        hole=0.55,
        color="Asal",
        color_discrete_map={"Indonesia": BRAND["green"], "Impor": BRAND["gold"]},
    )
    fig.update_traces(textposition="inside", textinfo="percent+label", textfont=dict(size=14, color=BRAND["forest"]))
    fig.update_layout(**pl, title="Asal Produk Obat", height=380)
    st.plotly_chart(fig, width="stretch")
with right:
    resep_dist = df["perlu_resep"].value_counts().reset_index()
    resep_dist.columns = ["Status", "Jumlah"]
    resep_dist["Status"] = resep_dist["Status"].map({1: "Perlu Resep", 0: "Bebas"})
    fig = px.pie(
        resep_dist,
        names="Status",
        values="Jumlah",
        hole=0.55,
        color="Status",
        color_discrete_map={"Perlu Resep": BRAND["coral"], "Bebas": BRAND["mint"]},
    )
    fig.update_traces(textposition="inside", textinfo="percent+label", textfont=dict(size=14, color=BRAND["forest"]))
    fig.update_layout(**pl, title="Distribusi Perlu Resep", height=380)
    st.plotly_chart(fig, width="stretch")

st.markdown(section("Pencarian produk"), unsafe_allow_html=True)
query = st.text_input("Cari nama produk, komposisi, atau kategori interaksi", placeholder="contoh: paracetamol, amlodipine, nsaid, antidiabetes")
if query:
    result = df[
        df["nama_produk"].str.contains(query, case=False, na=False)
        | df["komposisi"].str.contains(query, case=False, na=False)
        | df["drug_category"].str.contains(query, case=False, na=False)
        | df["kategori_interaksi_obat"].str.contains(query, case=False, na=False)
    ]
    st.caption(f"Ditemukan {len(result)} produk.")
    table_df = result[
        ["nama_produk", "komposisi", "drug_category", "kategori_interaksi_obat", "bentuk_sediaan", 
         "perlu_resep", "status_masa_berlaku", "sisa_hari_berlaku", "golongan_obat"]
    ].copy()
    table_df = table_df.rename(columns={
        "nama_produk": "Nama Produk",
        "komposisi": "Komposisi",
        "drug_category": "Kategori",
        "kategori_interaksi_obat": "Kategori Interaksi",
        "bentuk_sediaan": "Bentuk",
        "perlu_resep": "Perlu Resep",
        "status_masa_berlaku": "Status",
        "sisa_hari_berlaku": "Hari Berlaku",
        "golongan_obat": "Golongan"
    })
    st.markdown(render_search_table(table_df, max_rows=100), unsafe_allow_html=True)
