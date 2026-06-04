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


def pct(part: int, total: int) -> str:
    return f"{(part / total):.0%}" if total else "0%"


def map_prescription_label(value):
    return {1: "Perlu resep", 0: "Tanpa resep"}.get(value, "-")


df = load_data()
total_products = len(df)

# Compute insights
df_with_category = df[df['drug_category'].notna()]
top_category = df_with_category["drug_category"].value_counts().index[0] if len(df_with_category) > 0 else "-"
top_category_count = int(df_with_category["drug_category"].value_counts().iloc[0]) if len(df_with_category) > 0 else 0
needs_prescription = (df["perlu_resep"] == 1).sum()
non_prescription = total_products - needs_prescription
active_products = int((df["status_masa_berlaku"] == "aktif").sum())
expired_products = int((df["status_masa_berlaku"] == "kedaluwarsa").sum())
multi_active_count = int((df["jumlah_zat_aktif"] > 1).sum())
single_active_count = total_products - multi_active_count
expiring_1y = int(
    (
        (df["masa_berlaku_sd"] >= pd.Timestamp.today().normalize())
        & ((df["masa_berlaku_sd"] - pd.Timestamp.today().normalize()).dt.days <= 365)
    ).fillna(False).sum()
)
top_dosage = df["kelompok_bentuk_sediaan"].fillna("lainnya").value_counts()
top_dosage_name = top_dosage.index[0] if len(top_dosage) > 0 else "-"
top_dosage_count = int(top_dosage.iloc[0]) if len(top_dosage) > 0 else 0

st.markdown(
    hero(
        "Ringkasan obat BPOM untuk kebutuhan interaksi obat-makanan",
        "Halaman ini membantu stakeholder membaca profil obat yang sudah tervalidasi untuk sistem Jivara, mulai dari kebutuhan resep, status registrasi, bentuk sediaan, hingga kategori interaksi yang paling dominan. "
        "Tujuannya adalah memberi gambaran cepat tentang kualitas dan karakter katalog obat yang dipakai sistem, tanpa harus membaca data mentah satu per satu.",
    ),
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Produk Tervalidasi", f"{total_products:,}")
c2.metric("Registrasi Aktif", f"{active_products:,}", pct(active_products, total_products))
c3.metric("Perlu Resep", f"{needs_prescription:,}", pct(needs_prescription, total_products))
c4.metric("Multi Zat Aktif", f"{multi_active_count:,}", pct(multi_active_count, total_products))

st.markdown(section("Insight cepat"), unsafe_allow_html=True)
i1, i2, i3 = st.columns(3)
with i1:
    st.markdown(
        card(
            "Apa yang paling menonjol di katalog ini",
            f"Kategori {top_category.replace('_', ' ')} adalah yang paling dominan dengan {top_category_count:,} produk atau {pct(top_category_count, total_products)} dari seluruh katalog. "
            "Ini memberi sinyal area interaksi yang paling sering muncul saat sistem melakukan pengecekan.",
        ),
        unsafe_allow_html=True,
    )
with i2:
    st.markdown(
        card(
            "Apa yang perlu diperhatikan sejak awal",
            f"{needs_prescription:,} produk atau {pct(needs_prescription, total_products)} termasuk obat yang memerlukan resep. "
            "Saat halaman ini diakses, insight terpentingnya adalah mayoritas katalog berisi obat yang butuh perhatian klinis lebih tinggi.",
        ),
        unsafe_allow_html=True,
    )
with i3:
    st.markdown(
        card(
            "Apa yang relevan untuk monitoring data",
            f"{expired_products:,} produk sudah berstatus kedaluwarsa, sementara {expiring_1y:,} produk aktif akan habis masa berlaku dalam 12 bulan ke depan. "
            "Artinya, halaman ini juga bisa dipakai untuk melihat apakah katalog perlu diperbarui secara berkala.",
        ),
        unsafe_allow_html=True,
    )

st.markdown(
    note(
        f"<strong>Cara membaca halaman ini:</strong> katalog ini berisi produk tervalidasiyang sudah dimapping ke kategori interaksi. "
        f"Jadi angka di dashboard merepresentasikan subset operasional untuk sistem Jivara, bukan seluruh populasi obat BPOM nasional.</strong>"
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

st.markdown(section("Status registrasi dan kebutuhan resep"), unsafe_allow_html=True)
left, right = st.columns(2)
with left:
    status_dist = (
        df["status_masa_berlaku"]
        .fillna("tidak diketahui")
        .value_counts()
        .rename_axis("Status")
        .reset_index(name="Jumlah")
    )
    status_dist["Status"] = status_dist["Status"].replace(
        {"aktif": "Registrasi aktif", "kedaluwarsa": "Registrasi kedaluwarsa", "tidak diketahui": "Tidak diketahui"}
    )
    fig = px.pie(
        status_dist,
        names="Status",
        values="Jumlah",
        hole=0.55,
        color="Status",
        color_discrete_map={
            "Registrasi aktif": BRAND["green"],
            "Registrasi kedaluwarsa": BRAND["coral"],
            "Tidak diketahui": BRAND["gold"],
        },
    )
    fig.update_traces(textposition="inside", textinfo="percent+label", textfont=dict(size=14, color=BRAND["forest"]))
    fig.update_layout(**pl, title="Status Registrasi Produk", height=380)
    st.plotly_chart(fig, width="stretch")
with right:
    resep_dist = df["perlu_resep"].value_counts().reset_index()
    resep_dist.columns = ["Status", "Jumlah"]
    resep_dist["Status"] = resep_dist["Status"].map({1: "Perlu resep", 0: "Tanpa resep"})
    fig = px.pie(
        resep_dist,
        names="Status",
        values="Jumlah",
        hole=0.55,
        color="Status",
        color_discrete_map={"Perlu resep": BRAND["coral"], "Tanpa resep": BRAND["mint"]},
    )
    fig.update_traces(textposition="inside", textinfo="percent+label", textfont=dict(size=14, color=BRAND["forest"]))
    fig.update_layout(**pl, title="Kebutuhan Resep Dokter", height=380)
    st.plotly_chart(fig, width="stretch")

st.markdown(section("Apa arti data ini untuk stakeholder"), unsafe_allow_html=True)
s1, s2, s3 = st.columns(3)
with s1:
    st.markdown(
        card(
            "Untuk tim produk",
            f"Mayoritas produk di katalog ini adalah obat yang membutuhkan resep ({pct(needs_prescription, total_products)}). "
            "Warning interaksi sebaiknya dibuat singkat, tegas, dan mudah dicari saat tenaga kesehatan melakukan pengecekan cepat.",
        ),
        unsafe_allow_html=True,
    )
with s2:
    st.markdown(
        card(
            "Untuk tim klinis",
            f"{multi_active_count:,} produk ({pct(multi_active_count, total_products)}) mengandung lebih dari satu zat aktif. "
            "Artinya, pengecekan interaksi tidak cukup berhenti di nama dagang dan perlu mempertimbangkan komposisinya.",
        ),
        unsafe_allow_html=True,
    )
with s3:
    st.markdown(
        card(
            "Untuk tim data",
            f"Bentuk sediaan paling umum adalah {top_dosage_name} dengan {top_dosage_count:,} produk. "
            "Informasi ini membantu menentukan prioritas normalisasi data, filter dashboard, dan contoh use case untuk demo.",
        ),
        unsafe_allow_html=True,
    )

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
    table_df["perlu_resep"] = table_df["perlu_resep"].map(map_prescription_label)
    table_df["status_masa_berlaku"] = table_df["status_masa_berlaku"].replace(
        {"aktif": "Registrasi aktif", "kedaluwarsa": "Registrasi kedaluwarsa"}
    )
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
