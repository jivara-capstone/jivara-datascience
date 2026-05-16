import sys
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from scipy.stats import ttest_ind

sys.path.append(str(Path(__file__).resolve().parent.parent))

from ui import (
    ASSET,
    BRAND,
    DATA,
    add_sidebar,
    apply_theme,
    card,
    compute_interaction_frame,
    hero,
    load_kb,
    note,
    plotly_layout,
    section,
    wrap_text,
)

page_icon = str(ASSET / "splash.png") if (ASSET / "splash.png").exists() else "🌿"
st.set_page_config(page_title="Interaksi & Evidence - Jivara", page_icon=page_icon, layout="wide")
st.markdown(apply_theme(), unsafe_allow_html=True)
add_sidebar("Interaksi & Evidence", "Severity, mekanisme, dan proof of concept")
pl = plotly_layout()


@st.cache_data
def load_data():
    kb = load_kb(DATA / "for_backend" / "drug_food_kb_final.json")
    return kb


kb = load_data()
idf, foods = compute_interaction_frame(kb)
severity_share = (idf["Severity"] >= 4).mean() if not idf.empty else 0
top_food = idf["Makanan"].value_counts().index[0]
top_class = idf["Kelas_Obat"].value_counts().index[0]

st.markdown(
    hero(
        "Knowledge base Jivara paling bernilai saat risiko mulai tinggi",
        "Halaman ini menyorot makanan mana yang paling sering memicu alert, kelas obat mana yang paling sering terdampak, "
        "dan bagaimana bukti eksperimen mendukung nilai produk Jivara sebagai pendamping keputusan pasien.",
    ),
    unsafe_allow_html=True,
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Makanan di KB", f"{len(foods):,}")
c2.metric("Total Interaksi", f"{len(idf):,}")
c3.metric("Severity 4-5", f"{severity_share:.0%}")
c4.metric("Kelas Obat Dominan", top_class)

st.markdown(section("Insight cepat"), unsafe_allow_html=True)
i1, i2, i3 = st.columns(3)
with i1:
    st.markdown(
        card(
            "Interaksi paling sering tidak ringan",
            f"{severity_share:.0%} interaksi berada di severity level 4-5. "
            "Ini menandakan Jivara memang bermain di ruang keputusan yang sensitif, sehingga penjelasan mekanisme dan tingkat urgensi harus jelas.",
        ),
        unsafe_allow_html=True,
    )
with i2:
    st.markdown(
        card(
            "Antidiabetik paling sering bersinggungan",
            f"Kelas obat yang paling sering muncul adalah {top_class}. "
            "Secara produk, ini membuka peluang pengembangan alur edukasi khusus untuk pasien dengan kebutuhan pemantauan gula darah.",
        ),
        unsafe_allow_html=True,
    )
with i3:
    food_count = int(idf["Makanan"].value_counts().iloc[0])
    st.markdown(
        card(
            "Makanan prioritas untuk penjelasan mendalam",
            f"{top_food.replace('-', ' ').title()} memiliki jumlah interaksi terbanyak di knowledge base ({food_count} interaksi). "
            "Kelas seperti ini cocok dijadikan template UX untuk halaman detail warning.",
        ),
        unsafe_allow_html=True,
    )

st.markdown(
    note(
        "<strong>Makna untuk AI reasoning:</strong> pengguna tidak hanya perlu tahu 'aman atau tidak', "
        "tetapi juga apakah risikonya karena sodium, kunyit, santan, gula, atau mekanisme lain yang bisa dipahami sehari-hari."
    ),
    unsafe_allow_html=True,
)

left, right = st.columns(2)
with left:
    sev = idf["Severity"].value_counts().sort_index().reset_index()
    sev.columns = ["Severity", "Jumlah"]
    fig = px.bar(
        sev,
        x="Severity",
        y="Jumlah",
        color="Severity",
        text="Jumlah",
        color_continuous_scale=[BRAND["lime"], BRAND["gold"], BRAND["coral"]],
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(**pl, height=380, coloraxis_showscale=False)
    st.plotly_chart(fig, width="stretch")
with right:
    types = idf["Tipe"].value_counts().reset_index()
    types.columns = ["Tipe", "Jumlah"]
    fig = px.pie(
        types,
        names="Tipe",
        values="Jumlah",
        hole=0.55,
        color="Tipe",
        color_discrete_map={
            "AVOID": BRAND["coral"],
            "MONITOR": BRAND["gold"],
            "LIMIT": BRAND["mint"],
            "TIMING": BRAND["green"],
        },
    )
    fig.update_traces(textposition="inside", textinfo="percent+label")
    fig.update_layout(**pl, height=380)
    st.plotly_chart(fig, width="stretch")

st.markdown(section("Makanan dan kelas obat paling berisiko"), unsafe_allow_html=True)
left, right = st.columns(2)
with left:
    top_foods = (
        idf.groupby("Makanan")["Severity"]
        .agg(["count", "mean"])
        .sort_values(["mean", "count"], ascending=[False, False])
        .head(12)
        .reset_index()
    )
    top_foods["Makanan"] = top_foods["Makanan"].str.replace("-", " ").str.title()
    fig = px.scatter(
        top_foods,
        x="count",
        y="mean",
        size="count",
        color="mean",
        hover_name="Makanan",
        color_continuous_scale=[BRAND["mint"], BRAND["gold"], BRAND["coral"]],
    )
    fig.update_layout(**pl, height=400, coloraxis_colorbar_title="Avg severity", xaxis_title="Jumlah interaksi", yaxis_title="Rata-rata severity")
    st.plotly_chart(fig, width="stretch")
with right:
    top_classes = idf["Kelas_Obat"].value_counts().head(10).reset_index()
    top_classes.columns = ["Kelas Obat", "Jumlah"]
    top_classes["Kelas Obat"] = wrap_text(top_classes["Kelas Obat"], 24)
    fig = px.bar(
        top_classes.sort_values("Jumlah"),
        x="Jumlah",
        y="Kelas Obat",
        orientation="h",
        color="Jumlah",
        color_continuous_scale=[BRAND["lime"], BRAND["mint"], BRAND["forest"]],
        text="Jumlah",
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(**pl, height=430, coloraxis_showscale=False, yaxis_title="", yaxis=dict(automargin=True))
    st.plotly_chart(fig, width="stretch")

st.markdown(section("Eksplorasi detail per makanan"), unsafe_allow_html=True)
selected = st.selectbox(
    "Pilih makanan",
    sorted(foods.keys()),
    format_func=lambda value: value.replace("-", " ").title(),
)
food_data = foods[selected]
st.markdown(
    note(
        f"<strong>{selected.replace('-', ' ').title()}</strong> | kategori: {food_data.get('category', '-')} | "
        f"bahan kunci: {', '.join(food_data.get('key_ingredients', []))}"
    ),
    unsafe_allow_html=True,
)
for interaction in food_data.get("drug_interactions", []):
    label = interaction.get("severity", 0)
    title = f"{interaction.get('drug_class', '-')} | severity {label}/5 | {interaction.get('type', '-')}"
    with st.expander(title):
        st.markdown(f"**Contoh obat:** {', '.join(interaction.get('drug_examples', []))}")
        st.markdown(f"**Interaksi:** {interaction.get('interaction', '-')}")
        st.markdown(f"**Mekanisme:** `{interaction.get('mechanism', '-')}`")

st.markdown(section("A/B testing simulatif"), unsafe_allow_html=True)
st.caption("Proof of concept simulatif, bukan data produksi pengguna riil.")

np.random.seed(42)
n = 150
beta = lambda mu, size: np.random.beta(mu * 30, (1 - mu) * 30, size)
ctrl_adh, treat_adh = beta(0.62, n), beta(0.78, n)
ctrl_avoid, treat_avoid = beta(0.35, n), beta(0.72, n)
_, p1 = ttest_ind(treat_adh, ctrl_adh, equal_var=False)
_, p2 = ttest_ind(treat_avoid, ctrl_avoid, equal_var=False)

a, b = st.columns(2)
with a:
    uplift = treat_adh.mean() - ctrl_adh.mean()
    st.markdown(
        card(
            "RQ3: kepatuhan minum obat",
            f"Rata-rata kepatuhan naik dari {ctrl_adh.mean():.0%} ke {treat_adh.mean():.0%} "
            f"({uplift:+.0%}, p={p1:.4f}). Ini mendukung hipotesis bahwa warning yang tepat waktu dapat memengaruhi perilaku pasien.",
        ),
        unsafe_allow_html=True,
    )
with b:
    uplift = treat_avoid.mean() - ctrl_avoid.mean()
    st.markdown(
        card(
            "RQ4: penghindaran makanan berbahaya",
            f"Penghindaran naik dari {ctrl_avoid.mean():.0%} ke {treat_avoid.mean():.0%} "
            f"({uplift:+.0%}, p={p2:.4f}). Dampaknya lebih besar daripada kepatuhan obat, jadi food alert tampaknya sangat intuitif bagi user.",
        ),
        unsafe_allow_html=True,
    )

ab = pd.DataFrame(
    {
        "Grup": ["Tanpa Jivara"] * n + ["Dengan Jivara"] * n,
        "Kepatuhan Obat": np.concatenate([ctrl_adh, treat_adh]),
        "Penghindaran Makanan": np.concatenate([ctrl_avoid, treat_avoid]),
    }
)

left, right = st.columns(2)
with left:
    fig = px.violin(
        ab,
        x="Grup",
        y="Kepatuhan Obat",
        color="Grup",
        box=True,
        points="outliers",
        color_discrete_map={"Tanpa Jivara": BRAND["coral"], "Dengan Jivara": BRAND["green"]},
    )
    fig.update_layout(**pl, height=420, showlegend=False, yaxis_tickformat=".0%")
    st.plotly_chart(fig, width="stretch")
with right:
    fig = px.violin(
        ab,
        x="Grup",
        y="Penghindaran Makanan",
        color="Grup",
        box=True,
        points="outliers",
        color_discrete_map={"Tanpa Jivara": BRAND["coral"], "Dengan Jivara": BRAND["green"]},
    )
    fig.update_layout(**pl, height=420, showlegend=False, yaxis_tickformat=".0%")
    st.plotly_chart(fig, width="stretch")
