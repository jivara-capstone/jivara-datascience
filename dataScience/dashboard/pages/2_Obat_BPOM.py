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
    compute_drug_insights,
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
st.set_page_config(page_title="Obat BPOM - Jivara", page_icon=page_icon, layout="wide")
st.markdown(apply_theme(), unsafe_allow_html=True)
add_sidebar("Obat BPOM", "Peta produk obat yang jadi basis reasoning")
pl = plotly_layout()


@st.cache_data
def load_data():
    df = pd.read_csv(PROC / "obat_bpom_cleaned_dedup.csv")
    df["Tanggal Terbit"] = pd.to_datetime(df["Tanggal Terbit"], errors="coerce")
    df["Masa Berlaku s/d"] = pd.to_datetime(df["Masa Berlaku s/d"], errors="coerce")
    return df


df = load_data()
insight = compute_drug_insights(df)

st.markdown(
    hero(
        "Data obat BPOM adalah fondasi keputusan medis yang aman",
        "Semakin lengkap data obat (nama, komposisi, zat aktif), semakin akurat sistem Jivara mendeteksi risiko interaksi. "
        "Halaman ini menunjukkan pola obat apa yang paling banyak terdaftar dan bagaimana strukturnya.",
    ),
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Produk Terdaftar", f"{len(df):,}")
c2.metric("Obat Keras", f"{(df['Golongan_Obat'] == 'Obat Keras').sum():,}")
c3.metric("Pangsa Lokal", f"{insight['local_share']:.0%}")
c4.metric("Multi Zat Aktif", f"{insight['multi_active_share']:.0%}")

st.markdown(section("Insight cepat"), unsafe_allow_html=True)
i1, i2, i3 = st.columns(3)
with i1:
    st.markdown(
        card(
            "Jenis obat terbanyak",
            f"{insight['top_group']} paling banyak ({insight['top_group_count']:,} produk). "
            "Ini adalah prioritas utama untuk sistem deteksi risiko Jivara.",
        ),
        unsafe_allow_html=True,
    )
with i2:
    st.markdown(
        card(
            "Banyak obat dengan beberapa zat aktif",
            f"{insight['multi_active_share']:.0%} obat memiliki lebih dari satu zat aktif. "
            "Sistem harus bisa mencocokkan kombinasi zat aktif, bukan hanya satu obat.",
        ),
        unsafe_allow_html=True,
    )
with i3:
    st.markdown(
        card(
            "Beberapa obat akan segera expired",
            f"Sekitar {insight['expiring_1y']:,} produk berakhir masa berlakunya dalam 12 bulan. "
            "Data perlu diperbarui secara berkala agar tetap akurat.",
        ),
        unsafe_allow_html=True,
    )

st.markdown(
    note(
        "<strong>Catatan:</strong> Data obat tidak hanya daftar nama, tapi juga komposisi, zat aktif, dan status regulasi. "
        "Semua ini mempengaruhi akurasi deteksi risiko interaksi."
    ),
    unsafe_allow_html=True,
)

left, right = st.columns(2)
with left:
    group_counts = df["Golongan_Obat"].value_counts().reset_index()
    group_counts.columns = ["Golongan", "Jumlah"]
    group_counts["Golongan"] = wrap_text(group_counts["Golongan"], 14)
    fig = px.bar(
        group_counts,
        x="Golongan",
        y="Jumlah",
        color="Golongan",
        text="Jumlah",
        color_discrete_sequence=[BRAND["green"], BRAND["mint"], BRAND["gold"], BRAND["coral"], "#7FB069", "#52796F", "#E5989B"],
    )
    fig.update_traces(textposition="outside")
    style_bar_labels(fig)
    fig.update_layout(**pl, title="Distribusi Golongan Obat")
    style_figure(fig, height=440, x_title="Golongan Obat", y_title="Jumlah Produk", legend=False)
    add_bar_headroom(fig, group_counts["Jumlah"])
    st.plotly_chart(fig, width="stretch")
with right:
    dosage = df["Bentuk Sediaan"].value_counts().head(12).reset_index()
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

st.markdown(section("Asal produk dan kompleksitas formulasi"), unsafe_allow_html=True)
left, right = st.columns(2)
with left:
    origin = df["Asal_Obat"].value_counts().reset_index()
    origin.columns = ["Asal", "Jumlah"]
    fig = px.pie(
        origin,
        names="Asal",
        values="Jumlah",
        hole=0.55,
        color="Asal",
        color_discrete_map={"Lokal/Lainnya": BRAND["green"], "Impor": BRAND["gold"]},
    )
    fig.update_traces(textposition="inside", textinfo="percent+label", textfont=dict(size=14, color=BRAND["forest"]))
    fig.update_layout(**pl, title="Asal Produk Obat", height=380)
    st.plotly_chart(fig, width="stretch")
with right:
    active_dist = (
        df["Jumlah_Zat_Aktif"]
        .fillna(0)
        .clip(upper=6)
        .value_counts()
        .sort_index()
        .reset_index()
    )
    active_dist.columns = ["Jumlah Zat Aktif", "Produk"]
    active_dist["Jumlah Zat Aktif"] = active_dist["Jumlah Zat Aktif"].astype(int).astype(str)
    fig = px.bar(
        active_dist,
        x="Jumlah Zat Aktif",
        y="Produk",
        color="Produk",
        text="Produk",
        color_continuous_scale=[BRAND["lime"], BRAND["mint"], BRAND["forest"]],
    )
    fig.update_traces(textposition="outside")
    style_bar_labels(fig)
    fig.update_layout(**pl, title="Kompleksitas Jumlah Zat Aktif", coloraxis_showscale=False)
    style_figure(fig, height=400, x_title="Jumlah Zat Aktif", y_title="Jumlah Produk")
    add_bar_headroom(fig, active_dist["Produk"])
    st.plotly_chart(fig, width="stretch")

st.markdown(section("Pencarian produk"), unsafe_allow_html=True)
query = st.text_input("Cari nama produk atau komposisi", placeholder="contoh: paracetamol, amlodipine, vitamin")
if query:
    result = df[
        df["Nama Produk"].str.contains(query, case=False, na=False)
        | df["Komposisi"].str.contains(query, case=False, na=False)
    ]
    st.caption(f"Ditemukan {len(result)} produk.")
    table_df = result[
        ["Nama Produk", "Komposisi", "Bentuk Sediaan", "Golongan_Obat", "Perusahaan", "Asal_Obat"]
    ]
    st.markdown(render_search_table(table_df, max_rows=100), unsafe_allow_html=True)
