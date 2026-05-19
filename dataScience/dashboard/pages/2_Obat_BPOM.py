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
    add_sidebar,
    apply_theme,
    card,
    compute_drug_insights,
    hero,
    note,
    plotly_layout,
    render_search_table,
    section,
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
        "BPOM data memberi konteks dunia nyata untuk keputusan medis",
        "Semakin kaya struktur produk obat, semakin realistis sistem Jivara saat menghubungkan nama obat, komposisi, "
        "dan interaksi yang perlu diwaspadai. Halaman ini menonjolkan pola yang paling berpengaruh ke reasoning engine.",
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
            "Golongan dominan",
            f"{insight['top_group']} mendominasi dengan {insight['top_group_count']:,} produk. "
            "Ini memperlihatkan bahwa use case Jivara paling relevan pada area terapi yang memang butuh kehati-hatian klinis lebih tinggi.",
        ),
        unsafe_allow_html=True,
    )
with i2:
    st.markdown(
        card(
            "Komposisi kombinasi bukan kasus kecil",
            f"{insight['multi_active_share']:.0%} produk memiliki lebih dari satu zat aktif. "
            "Artinya mapping komposisi dan normalisasi ingredient obat akan sangat menentukan kualitas alert interaksi.",
        ),
        unsafe_allow_html=True,
    )
with i3:
    st.markdown(
        card(
            "Registrasi juga punya dimensi lifecycle",
            f"Ada sekitar {insight['expiring_1y']:,} produk yang masa berlakunya jatuh dalam 12 bulan ke depan. "
            "Kalau project berkembang ke monitoring operasional, status regulasi bisa menjadi sinyal kualitas data tambahan.",
        ),
        unsafe_allow_html=True,
    )

st.markdown(
    note(
        "<strong>Implikasi produk:data obat di Jivara tidak cukup diperlakukan sebagai daftar nama. "
        "Perusahaan, bentuk sediaan, dan jumlah zat aktif semuanya bisa memengaruhi cara sistem menjelaskan risiko.</strong> "
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
    fig.update_traces(textposition="outside", textfont=dict(size=14, color=BRAND["forest"]))
    fig.update_layout(
        **pl,
        title="Distribusi Golongan Obat",
        height=420,
        showlegend=False,
        xaxis_title="Golongan Obat",
        yaxis_title="Jumlah Produk",
        xaxis=dict(automargin=True, tickfont=dict(size=12, color=BRAND["forest"]), title_font=dict(size=13, color=BRAND["forest"])),
        yaxis=dict(automargin=True, tickfont=dict(size=12, color=BRAND["forest"]), title_font=dict(size=13, color=BRAND["forest"])),
    )
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
    fig.update_traces(textposition="outside", textfont=dict(size=14, color=BRAND["forest"]))
    fig.update_layout(
        **pl,
        title="Bentuk Sediaan Terbanyak",
        height=420,
        coloraxis_showscale=False,
        xaxis_title="Jumlah Produk",
        yaxis_title="Bentuk Sediaan",
        xaxis=dict(automargin=True, tickfont=dict(size=12, color=BRAND["forest"]), title_font=dict(size=13, color=BRAND["forest"])),
        yaxis=dict(automargin=True, tickfont=dict(size=12, color=BRAND["forest"]), title_font=dict(size=13, color=BRAND["forest"])),
    )
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
    fig.update_traces(textposition="inside", textinfo="percent+label", textfont=dict(size=13, color=BRAND["forest"]))
    fig.update_layout(**pl, title="Asal Produk Obat", height=360)
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
    fig.update_traces(textposition="outside", textfont=dict(size=14, color=BRAND["forest"]))
    fig.update_layout(
        **pl,
        title="Kompleksitas Jumlah Zat Aktif",
        height=360,
        coloraxis_showscale=False,
        xaxis_title="Jumlah Zat Aktif",
        yaxis_title="Jumlah Produk",
        xaxis=dict(automargin=True, tickfont=dict(size=12, color=BRAND["forest"]), title_font=dict(size=13, color=BRAND["forest"])),
        yaxis=dict(automargin=True, tickfont=dict(size=12, color=BRAND["forest"]), title_font=dict(size=13, color=BRAND["forest"])),
    )
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
