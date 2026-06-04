import sys
from collections import Counter
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
    clean_ingredient,
    compute_recipe_insights,
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
st.set_page_config(page_title="Nutrisi & Resep - Jivara", page_icon=page_icon, layout="wide")
st.markdown(apply_theme(), unsafe_allow_html=True)
add_sidebar("Nutrisi & Resep", "Memahami pola makanan dan konteks masakan")
pl = plotly_layout()


@st.cache_data
def load_data():
    return (
        pd.read_csv(PROC / "unified_nutrition.csv"),
        pd.read_csv(PROC / "61_kelas_resep_cleaned.csv"),
    )


df_nutrisi, df_resep = load_data()
recipe_insight = compute_recipe_insights(df_resep)
ingredient_counts = recipe_insight["ingredient_counts"]

st.markdown(
    hero(
        "Nutrisi makanan dan konteks resep perlu dibaca bersama",
        "Nutrisi memberi gambaran apa yang dikonsumsi, sedangkan resep menjelaskan bagaimana makanan itu terbentuk. "
        "Di Jivara, kombinasi keduanya penting untuk memberi warning yang terasa relevan bagi pengguna Indonesia.",
    ),
    unsafe_allow_html=True,
)

top_calorie = df_nutrisi.loc[df_nutrisi["calories"].idxmax()]
protein_dense = (
    df_nutrisi.assign(protein_density=df_nutrisi["proteins"] / df_nutrisi["calories"].replace(0, pd.NA))
    .dropna(subset=["protein_density"])
    .sort_values("protein_density", ascending=False)
    .iloc[0]
)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Kelas Makanan", f"{len(df_nutrisi):,}")
c2.metric("Total Resep", f"{len(df_resep):,}")
c3.metric("Bahan per Resep", f"{recipe_insight['avg_ingredients']:.1f}")
c4.metric("Langkah per Resep", f"{recipe_insight['avg_steps']:.1f}")

st.markdown(section("Insight cepat"), unsafe_allow_html=True)
ic1, ic2, ic3 = st.columns(3)
with ic1:
    st.markdown(
        card(
            "Makanan dengan kalori tertinggi",
            f"{top_calorie['food_name']} paling tinggi kalorinya ({top_calorie['calories']:.0f} kkal per 100g). "
            "Penting untuk diketahui saat memberikan rekomendasi kepada pengguna.",
        ),
        unsafe_allow_html=True,
    )
with ic2:
    st.markdown(
        card(
            "Makanan berprotein tinggi",
            f"{protein_dense['food_name']} paling kaya protein dibanding kalorinya. "
            "Cocok untuk edukasi nutrisi dan pilihan makanan yang lebih sehat.",
        ),
        unsafe_allow_html=True,
    )
with ic3:
    top_ing, top_ing_count = ingredient_counts.most_common(1)[0]
    st.markdown(
        card(
            "Bahan paling sering digunakan",
            f"'{top_ing}' muncul {top_ing_count} kali di berbagai resep. "
            "Bahan populer seperti ini penting untuk dipantau kalau ada risiko interaksi.",
        ),
        unsafe_allow_html=True,
    )

st.markdown(
    note(
        "<strong>Kenapa ini penting?</strong>Warning obat-makanan akan jauh lebih masuk akal jika dikaitkan dengan bahan dominan "
        "dan pola masak nyata, bukan hanya nama hidangan.</strong> "
    ),
    unsafe_allow_html=True,
)

tab1, tab2 = st.tabs(["Analisis Nutrisi", "Database Resep"])

with tab1:
    left, right = st.columns(2)
    with left:
        macro_counts = df_nutrisi["macro_category"].value_counts().reset_index()
        macro_counts.columns = ["Kategori", "Jumlah"]
        fig = px.pie(
            macro_counts,
            names="Kategori",
            values="Jumlah",
            hole=0.52,
            color="Kategori",
            color_discrete_sequence=[BRAND["green"], BRAND["gold"], BRAND["mint"], BRAND["coral"]],
        )
        fig.update_traces(textposition="inside", textinfo="percent+label", textfont=dict(size=14, color=BRAND["forest"]))
        fig.update_layout(**pl, title="Komposisi Kategori Makronutrien", height=400)
        st.plotly_chart(fig, width="stretch")
    with right:
        source_counts = df_nutrisi["source"].value_counts().reset_index()
        source_counts.columns = ["Sumber", "Jumlah"]
        source_counts["Sumber"] = source_counts["Sumber"].map(
            {
                "manual_curated_tkpi": "TKPI Manual Curated",
                "nutrition1_indonesia": "Nutrition Indonesia",
                "food101_global": "Food-101 Global",
            }
        ).fillna(source_counts["Sumber"])
        source_counts["Sumber"] = wrap_text(source_counts["Sumber"], 16)
        fig = px.bar(
            source_counts,
            x="Sumber",
            y="Jumlah",
            text="Jumlah",
            color_discrete_sequence=[BRAND["green"], BRAND["gold"], BRAND["mint"]],
        )
        fig.update_traces(textposition="outside")
        style_bar_labels(fig)
        fig.update_layout(**pl, title="Sumber Data Nutrisi")
        style_figure(fig, height=420, x_title="Sumber Data", y_title="Jumlah Data", legend=False)
        add_bar_headroom(fig, source_counts["Jumlah"])
        st.plotly_chart(fig, width="stretch")

    st.markdown(section("Peta makanan padat energi"), unsafe_allow_html=True)
    top = df_nutrisi.nlargest(12, "calories")[["food_name", "calories", "proteins", "fat", "carbohydrate", "macro_category"]]
    fig = px.bar(
        top.sort_values("calories"),
        x="calories",
        y="food_name",
        orientation="h",
        color="macro_category",
        text="calories",
        color_discrete_sequence=[BRAND["green"], BRAND["gold"], BRAND["coral"], BRAND["mint"]],
    )
    fig.update_traces(texttemplate="%{text:.0f} kkal", textposition="outside")
    style_bar_labels(fig)
    fig.update_layout(**pl, title="Makanan dengan Kalori Tertinggi")
    style_figure(fig, height=520, x_title="Kalori per 100g", y_title="Nama Makanan")
    add_bar_headroom(fig, top["calories"], orientation="h")
    st.plotly_chart(fig, width="stretch")

    st.markdown(section("Kalori vs protein"), unsafe_allow_html=True)
    fig = px.scatter(
        df_nutrisi,
        x="calories",
        y="proteins",
        color="macro_category",
        size="fat",
        hover_data=["food_name", "carbohydrate"],
        color_discrete_sequence=[BRAND["green"], BRAND["gold"], BRAND["coral"], BRAND["mint"]],
    )
    fig.update_layout(**pl, title="Korelasi Kalori dan Protein")
    style_figure(fig, height=450, x_title="Kalori", y_title="Protein")
    st.plotly_chart(fig, width="stretch")

    query = st.text_input("Cari makanan", placeholder="contoh: rendang, gudeg, sate")
    if query:
        result = df_nutrisi[df_nutrisi["food_name"].str.contains(query, case=False, na=False)]
        table_df = result[
            ["food_name", "calories", "proteins", "fat", "carbohydrate", "macro_category", "source"]
        ].rename(
                columns={
                    "food_name": "Makanan",
                    "calories": "Kalori",
                    "proteins": "Protein",
                    "fat": "Lemak",
                    "carbohydrate": "Karbohidrat",
                    "macro_category": "Kategori",
                    "source": "Sumber",
                }
        )
        table_df["Sumber"] = table_df["Sumber"].replace(
            {
                "manual_curated_tkpi": "TKPI Manual Curated",
                "nutrition1_indonesia": "Nutrition Indonesia",
                "food101_global": "Food-101 Global",
            }
        )
        st.markdown(render_search_table(table_df, max_rows=80), unsafe_allow_html=True)

with tab2:
    left, right = st.columns(2)
    with left:
        complexity = df_resep["Kompleksitas"].value_counts().reset_index()
        complexity.columns = ["Kompleksitas", "Jumlah"]
        fig = px.bar(
            complexity,
            x="Kompleksitas",
            y="Jumlah",
            color="Kompleksitas",
            text="Jumlah",
            color_discrete_map={"Sederhana": BRAND["mint"], "Menengah": BRAND["gold"], "Kompleks": BRAND["coral"]},
        )
        fig.update_traces(textposition="outside")
        style_bar_labels(fig)
        fig.update_layout(**pl, title="Distribusi Kompleksitas Resep")
        style_figure(fig, height=420, x_title="Kompleksitas", y_title="Jumlah Resep", legend=False)
        add_bar_headroom(fig, complexity["Jumlah"])
        st.plotly_chart(fig, width="stretch")
    with right:
        top_classes = df_resep["Kelas_YOLO"].value_counts().head(12).reset_index()
        top_classes.columns = ["Kelas", "Jumlah"]
        top_classes["Kelas"] = wrap_text(top_classes["Kelas"].str.replace("-", " ").str.title(), 18)
        fig = px.bar(
            top_classes.sort_values("Jumlah"),
            x="Jumlah",
            y="Kelas",
            orientation="h",
            color="Jumlah",
            color_continuous_scale=[BRAND["lime"], BRAND["mint"], BRAND["green"]],
            text="Jumlah",
        )
        fig.update_traces(textposition="outside")
        style_bar_labels(fig)
        fig.update_layout(**pl, title="Kelas Resep dengan Jumlah Terbanyak", coloraxis_showscale=False)
        style_figure(fig, height=430, x_title="Jumlah Resep", y_title="Kelas Makanan")
        add_bar_headroom(fig, top_classes["Jumlah"], orientation="h")
        st.plotly_chart(fig, width="stretch")

    st.markdown(section("Bahan paling sering muncul"), unsafe_allow_html=True)
    ing_df = pd.DataFrame(ingredient_counts.most_common(20), columns=["Bahan", "Frekuensi"])
    ing_df["Bahan"] = wrap_text(ing_df["Bahan"], 20)
    fig = px.bar(
        ing_df.sort_values("Frekuensi"),
        x="Frekuensi",
        y="Bahan",
        orientation="h",
        color="Frekuensi",
        color_continuous_scale=[BRAND["lime"], BRAND["mint"], BRAND["forest"]],
        text="Frekuensi",
    )
    fig.update_traces(textposition="outside")
    style_bar_labels(fig)
    fig.update_layout(**pl, title="Bahan yang Paling Sering Digunakan", coloraxis_showscale=False)
    style_figure(fig, height=600, x_title="Frekuensi", y_title="Nama Bahan")
    add_bar_headroom(fig, ing_df["Frekuensi"], orientation="h")
    st.plotly_chart(fig, width="stretch")

    st.markdown(section("Eksplorasi kelas resep"), unsafe_allow_html=True)
    selected_class = st.selectbox(
        "Pilih kelas makanan",
        sorted(df_resep["Kelas_YOLO"].unique()),
        format_func=lambda value: value.replace("-", " ").title(),
    )
    filtered = df_resep[df_resep["Kelas_YOLO"] == selected_class].reset_index(drop=True)
    st.caption(f"{len(filtered)} resep tersedia untuk {selected_class.replace('-', ' ').title()}.")

    class_ingredients = Counter()
    for bahan in filtered["Bahan-bahan"].dropna():
        for item in str(bahan).split("|"):
            cleaned = clean_ingredient(item)
            if len(cleaned) > 1:
                class_ingredients[cleaned] += 1

    preview = ", ".join(f"{name} ({count})" for name, count in class_ingredients.most_common(10))
    st.markdown(note(f"<strong>Bahan dominan kelas ini:</strong> {preview}"), unsafe_allow_html=True)

    for _, row in filtered.head(20).iterrows():
        title = (
            f"{row['Nama Resep']} | {row['Kompleksitas']} | "
            f"{int(row['Jumlah_Bahan'])} bahan | {int(row['Jumlah_Langkah'])} langkah"
        )
        with st.expander(title):
            a, b = st.columns(2)
            with a:
                st.markdown("**Bahan-bahan**")
                for item in str(row["Bahan-bahan"]).split("|"):
                    st.markdown(f"- {item.strip()}")
            with b:
                st.markdown("**Langkah memasak**")
                for idx, item in enumerate(str(row["Langkah Memasak"]).split("||"), start=1):
                    st.markdown(f"{idx}. {item.strip()}")
