import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.append(str(Path(__file__).resolve().parent.parent))

from ui import (
    ASSET,
    BRAND,
    DATA,
    add_bar_headroom,
    add_sidebar,
    apply_theme,
    card,
    compute_interaction_frame,
    hero,
    load_kb,
    note,
    plotly_layout,
    render_search_table,
    section,
    style_bar_labels,
    style_figure,
    wrap_text,
)

DRUG_CLASS_LABELS = {
    "ace_arb": "ACE inhibitor / ARB",
    "antibiotik_fluorokuinolon": "Antibiotik fluorokuinolon",
    "antibiotik_tetrasiklin": "Antibiotik tetrasiklin",
    "antidiabetes": "Antidiabetes",
    "antikoagulan": "Antikoagulan",
    "antikonvulsan": "Antikonvulsan",
    "ccb": "Calcium channel blocker (CCB)",
    "diuretik_hemat_kalium": "Diuretik hemat kalium",
    "dopaminergik_parkinson": "Dopaminergik Parkinson",
    "glikosida_jantung": "Glikosida jantung",
    "imunosupresan": "Imunosupresan",
    "kortikosteroid": "Kortikosteroid",
    "maoi": "MAOI",
    "nsaid": "NSAID",
    "statin": "Statin",
    "tiroid": "Obat tiroid",
    "xantin": "Xantin",
}


def format_food_name(value: str):
    return str(value).replace("-", " ").title()


def format_drug_class(value: str):
    normalized = str(value or "").strip().lower()
    if not normalized:
        return "-"
    return DRUG_CLASS_LABELS.get(normalized, normalized.replace("_", " ").title())


def split_ingredients(value: object):
    if pd.isna(value):
        return []
    return [item.strip() for item in str(value).split("|") if item and item.strip()]


def build_food_view(interactions_df: pd.DataFrame, base_foods: dict):
    filtered_foods = {}
    sorted_df = interactions_df.sort_values(["Makanan", "Severity", "Kelas_Obat"], ascending=[True, False, True])
    for food_name, group in sorted_df.groupby("Makanan"):
        base = base_foods.get(food_name, {})
        key_ingredients = base.get("key_ingredients") or sorted(
            {
                ingredient
                for ingredients in group["Bahan_Pemicu"].tolist()
                for ingredient in split_ingredients(ingredients)
            }
        )
        interactions = []
        for _, row in group.iterrows():
            interactions.append(
                {
                    "drug_class": row["Kelas_Obat"],
                    "severity": int(row["Severity"]),
                    "type": row["Tipe"],
                    "type_label": row["Tipe_Label"],
                    "mechanism": row["Mekanisme"] or "-",
                    "interaction": row["Interaksi"] or row["Mekanisme"] or "-",
                    "matched_ingredients": split_ingredients(row["Bahan_Pemicu"]),
                    "source": row["Sumber"] or "-",
                    "source_label": row["Label_Sumber"] or "-",
                    "is_fact_based": bool(row["Basis_Faktual"]),
                }
            )
        filtered_foods[food_name] = {
            "category": base.get("category", ""),
            "key_ingredients": key_ingredients,
            "drug_interactions": interactions,
        }
    return filtered_foods


page_icon = str(ASSET / "splash.png") if (ASSET / "splash.png").exists() else "J"
st.set_page_config(page_title="Interaksi Obat-Makanan - Jivara", page_icon=page_icon, layout="wide")
st.markdown(apply_theme(), unsafe_allow_html=True)
add_sidebar("Interaksi Obat-Makanan", "Pisahkan kurasi literatur dari inferensi deterministik")
pl = plotly_layout()


@st.cache_data
def load_data():
    return load_kb(DATA / "for_backend" / "drug_food_kb_final_v3.json")


@st.cache_data
def load_drug_examples():
    lookup_path = DATA / "processed" / "drug_name_complete_category_lookup.csv"
    if not lookup_path.exists():
        return {}

    lookup_df = pd.read_csv(lookup_path)
    lookup_df = lookup_df[(lookup_df["matched"] == 1) & (lookup_df["primary_drug_category"] != "UNKNOWN")].copy()
    examples = {}
    for category, group in lookup_df.groupby("primary_drug_category"):
        names = list(dict.fromkeys(group["nama_produk"].dropna().astype(str).tolist()))
        examples[category] = names[:5]
    return examples


kb = load_data()
drug_examples_lookup = load_drug_examples()
idf, foods = compute_interaction_frame(kb)

st.markdown(
    hero(
        "Ringkasan rule interaksi obat-makanan yang dipakai sistem",
        "Halaman ini menampilkan hasil integrasi data makanan, bahan penyusun, kategori obat, dan rule interaksi yang digunakan dalam sistem Jivara. "
        "Tujuannya adalah membantu stakeholder memahami pola interaksi yang dikenali sistem, bukan menggantikan validasi klinis akhir.",
    ),
    unsafe_allow_html=True,
)

if idf.empty:
    st.warning("Data interaksi belum tersedia untuk ditampilkan.")
    st.stop()

literature_available = bool(idf["Basis_Faktual"].fillna(False).any())
view_mode = st.radio(
    "Mode tampilan data",
    ["Kurasi literatur", "Semua interaksi tersedia"],
    index=0 if literature_available else 1,
    horizontal=True,
    help="Mode default hanya menampilkan entri yang pada dataset diberi label kurasi literatur.",
)
min_severity = st.select_slider("Severity minimum", options=[2, 3, 4, 5], value=2)

view_df = idf.copy()
if literature_available and view_mode == "Kurasi literatur":
    view_df = view_df[view_df["Basis_Faktual"].fillna(False)].copy()
view_df = view_df[view_df["Severity"] >= min_severity].copy()

if view_df.empty:
    st.warning("Tidak ada interaksi yang cocok dengan filter saat ini.")
    st.stop()

visible_foods = build_food_view(view_df, foods)
severity_share = (view_df["Severity"] >= 4).mean()
top_food = view_df["Makanan"].value_counts().index[0]
top_class = view_df["Kelas_Obat"].value_counts().index[0]
top_food_count = int(view_df["Makanan"].value_counts().iloc[0])
hidden_foods = sorted(set(idf["Makanan"].unique()) - set(view_df["Makanan"].unique()))

c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Kelas Makanan", f"{idf['Makanan'].nunique():,}")
c2.metric("Kelas pada Filter", f"{view_df['Makanan'].nunique():,}")
c3.metric("Interaksi Ditampilkan", f"{len(view_df):,}")
c4.metric("Severity Tinggi (4-5)", f"{severity_share:.0%}")

st.markdown(
    note(
        "<strong>Catatan penting:</strong> halaman ini membaca rule interaksi dari `drug_food_interactions.csv` dan menggabungkannya "
        "dengan mapping bahan makanan serta kategori obat. Karena itu, insight yang tampil merepresentasikan <strong>rule operasional yang dikenali sistem</strong>, "
        "bukan klaim klinis final untuk semua kondisi penggunaan obat dan makanan."
    ),
    unsafe_allow_html=True,
)
if hidden_foods:
    st.caption(
        "Filter aktif sedang menyembunyikan "
        f"{len(hidden_foods)} kelas makanan: {', '.join(format_food_name(item) for item in hidden_foods)}."
    )

st.markdown(section("Insight cepat"), unsafe_allow_html=True)
i1, i2, i3 = st.columns(3)
with i1:
    st.markdown(
        card(
            "Apa yang paling cepat terbaca dari rule sistem",
            f"{severity_share:.0%} entri pada tampilan ini berada di severity 4-5. "
            "Ini membantu melihat porsi warning yang perlu perhatian lebih tinggi pada rule yang sedang ditampilkan.",
        ),
        unsafe_allow_html=True,
    )
with i2:
    st.markdown(
        card(
            "Kelas obat yang paling sering muncul: " + format_drug_class(top_class),
            f"{format_drug_class(top_class)} paling sering muncul pada entri yang sedang ditampilkan. "
            "Ini menunjukkan pola rule pada dataset yang dipakai sistem, bukan ranking risiko universal lintas semua obat.",
        ),
        unsafe_allow_html=True,
    )
with i3:
    st.markdown(
        card(
            "Makanan yang paling sering punya rule: " + format_food_name(top_food),
            f"{format_food_name(top_food)} muncul dalam {top_food_count} entri pada tampilan ini. "
            "Gunakan ini sebagai contoh pembacaan rule sistem, bukan sebagai label bahwa makanan tersebut pasti paling berisiko secara umum.",
        ),
        unsafe_allow_html=True,
    )

left, right = st.columns(2)
with left:
    sev = view_df["Severity"].value_counts().sort_index().reset_index()
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
    style_bar_labels(fig)
    fig.update_layout(**pl, title="Distribusi Severity pada Hasil Filter", coloraxis_showscale=False)
    style_figure(fig, height=420, x_title="Severity", y_title="Jumlah Interaksi")
    add_bar_headroom(fig, sev["Jumlah"])
    st.plotly_chart(fig, width="stretch")
with right:
    types = view_df["Tipe_Label"].value_counts().reset_index()
    types.columns = ["Tipe Interaksi", "Jumlah"]
    fig = px.pie(
        types,
        names="Tipe Interaksi",
        values="Jumlah",
        hole=0.55,
        color="Tipe Interaksi",
        color_discrete_map={
            "Farmakodinamik": BRAND["green"],
            "Farmakokinetik": BRAND["gold"],
            "Aditif": BRAND["mint"],
            "Pengaturan waktu minum": BRAND["coral"],
        },
    )
    fig.update_traces(textposition="inside", textinfo="percent+label", textfont=dict(size=14, color=BRAND["forest"]))
    fig.update_layout(**pl, title="Proporsi Tipe Interaksi Asli Dataset", height=400)
    st.plotly_chart(fig, width="stretch")

st.markdown(section("Makanan dan kelas obat paling sering tercatat"), unsafe_allow_html=True)
left, right = st.columns(2)
with left:
    top_foods = (
        view_df.groupby("Makanan")["Severity"]
        .agg(["count", "mean"])
        .sort_values(["mean", "count"], ascending=[False, False])
        .head(12)
        .reset_index()
    )
    top_foods["Makanan"] = top_foods["Makanan"].map(format_food_name)
    fig = px.scatter(
        top_foods,
        x="count",
        y="mean",
        size="count",
        color="mean",
        hover_name="Makanan",
        color_continuous_scale=[BRAND["mint"], BRAND["gold"], BRAND["coral"]],
    )
    fig.update_layout(**pl, title="Makanan dengan Rata-rata Severity Tertinggi", coloraxis_colorbar_title="Rata-rata severity")
    style_figure(fig, height=430, x_title="Jumlah Interaksi", y_title="Rata-rata Severity")
    st.plotly_chart(fig, width="stretch")
with right:
    top_classes = view_df["Kelas_Obat"].value_counts().head(10).reset_index()
    top_classes.columns = ["Kelas Obat", "Jumlah"]
    top_classes["Kelas Obat"] = top_classes["Kelas Obat"].map(format_drug_class)
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
    style_bar_labels(fig)
    fig.update_layout(**pl, title="Kelas Obat yang Paling Sering Terdampak", coloraxis_showscale=False)
    style_figure(fig, height=450, x_title="Jumlah Interaksi", y_title="Kelas Obat")
    add_bar_headroom(fig, top_classes["Jumlah"], orientation="h")
    st.plotly_chart(fig, width="stretch")

st.markdown(section("Eksplorasi detail per makanan"), unsafe_allow_html=True)
selected = st.selectbox(
    "Pilih makanan",
    sorted(visible_foods.keys()),
    format_func=format_food_name,
)
food_data = visible_foods[selected]
st.markdown(
    note(
        f"<strong>{format_food_name(selected)}</strong> | kategori: {food_data.get('category') or '-'} | "
        f"bahan pemicu yang cocok: {', '.join(food_data.get('key_ingredients', [])) if food_data.get('key_ingredients') else '-'}"
    ),
    unsafe_allow_html=True,
)
for interaction in food_data.get("drug_interactions", []):
    label = interaction.get("severity", 0)
    drug_class = interaction.get("drug_class", "-")
    title = f"{format_drug_class(drug_class)} | severity {label}/5 | {interaction.get('type_label', '-')}"
    with st.expander(title):
        examples = drug_examples_lookup.get(drug_class, [])
        st.markdown(f"**Contoh obat BPOM yang terpetakan:** {', '.join(examples) if examples else '-'}")
        st.markdown(
            f"**Bahan pemicu di makanan ini:** "
            f"{', '.join(interaction.get('matched_ingredients', [])) if interaction.get('matched_ingredients') else '-'}"
        )
        st.markdown(f"**Ringkasan interaksi:** {interaction.get('interaction', '-')}")
        st.markdown(f"**Mekanisme:** {interaction.get('mechanism', '-')}")
        st.markdown(f"**Kelas evidensi dataset:** {interaction.get('source_label', '-')}")
        st.caption(f"Sumber rule pada dataset: {interaction.get('source', '-')}")
        if not interaction.get("is_fact_based", False):
            st.warning(
                "Entri ini berasal dari inferensi deterministik berbasis ingredient mapping dan masih memerlukan verifikasi farmakologi klinis."
            )

st.markdown(section("Pencarian interaksi"), unsafe_allow_html=True)
query = st.text_input(
    "Cari makanan, kelas obat, bahan pemicu, atau mekanisme interaksi",
    placeholder="contoh: kiwi, warfarin, kalsium, tyramine, levothyroxine",
)
if query:
    search_df = view_df[
        view_df["Makanan"].str.contains(query, case=False, na=False)
        | view_df["Kelas_Obat"].map(format_drug_class).str.contains(query, case=False, na=False)
        | view_df["Mekanisme"].str.contains(query, case=False, na=False)
        | view_df["Bahan_Pemicu"].str.contains(query, case=False, na=False)
        | view_df["Tipe_Label"].str.contains(query, case=False, na=False)
    ].copy()
    st.caption(f"Ditemukan {len(search_df)} interaksi.")
    table_df = search_df[
        ["Makanan", "Kelas_Obat", "Severity", "Tipe_Label", "Bahan_Pemicu", "Label_Sumber"]
    ].rename(
        columns={
            "Makanan": "Makanan",
            "Kelas_Obat": "Kelas Obat",
            "Severity": "Severity",
            "Tipe_Label": "Tipe Interaksi",
            "Bahan_Pemicu": "Bahan Pemicu",
            "Label_Sumber": "Evidensi",
        }
    )
    table_df["Makanan"] = table_df["Makanan"].map(format_food_name)
    table_df["Kelas Obat"] = table_df["Kelas Obat"].map(format_drug_class)
    table_df["Bahan Pemicu"] = table_df["Bahan Pemicu"].replace("", "-").str.replace("|", ", ", regex=False)
    st.markdown(render_search_table(table_df, max_rows=100), unsafe_allow_html=True)
