import json
import re
from collections import Counter
from pathlib import Path
from textwrap import fill

import pandas as pd
from html import escape

BASE = Path(__file__).resolve().parent
DATA = BASE.parent / "data_output"
PROC = DATA / "processed"
ASSET = BASE / "asset"

BRAND = {
    "forest": "#123524",
    "green": "#2F6B43",
    "mint": "#74C69D",
    "lime": "#D8F3DC",
    "sand": "#F6FFF8",
    "gold": "#E9C46A",
    "coral": "#E76F51",
    "ink": "#1F2937",
    "muted": "#5F6F65",
}


def apply_theme():
    css = f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&display=swap');

    *, html, body, [class*="css"] {{
        font-family: 'Manrope', sans-serif;
    }}

    .stApp, [data-testid="stAppViewContainer"], [data-testid="stMain"],
    [data-testid="stAppViewBlockContainer"], .block-container {{
        background:
            radial-gradient(circle at top right, rgba(116,198,157,0.18), transparent 28%),
            linear-gradient(180deg, #fbfff9 0%, #f3fbf4 100%) !important;
    }}

    header[data-testid="stHeader"] {{
        background: rgba(18,53,36,0.9) !important;
        backdrop-filter: blur(10px);
    }}

    [data-testid="stSidebar"] {{
        background: linear-gradient(180deg, #123524 0%, #1E5631 48%, #2F6B43 100%);
    }}

    [data-testid="stSidebar"] * {{
        color: white !important;
    }}

    [data-testid="stSidebar"] hr {{
        border-color: rgba(255,255,255,0.16) !important;
    }}

    [data-testid="stSidebarHeader"] img,
    [data-testid="stSidebarNav"] img {{
        max-height: 92px !important;
        width: auto !important;
    }}

    [data-testid="stSidebarCollapsedControl"] button svg,
    header[data-testid="stHeader"] button svg {{
        color: white !important;
        fill: white !important;
    }}

    [data-testid="stMain"] p, [data-testid="stMain"] li, [data-testid="stMain"] span,
    [data-testid="stMain"] td, [data-testid="stMain"] th, [data-testid="stMain"] label {{
        color: {BRAND["ink"]} !important;
    }}

    [data-testid="stMain"] h1, [data-testid="stMain"] h2, [data-testid="stMain"] h3 {{
        color: {BRAND["forest"]} !important;
    }}

    div[data-testid="stMetric"] {{
        background: linear-gradient(180deg, rgba(255,255,255,0.95), rgba(244,252,246,0.95));
        border: 1px solid rgba(47,107,67,0.10);
        border-radius: 20px;
        padding: 18px 20px;
        box-shadow: 0 12px 30px rgba(18,53,36,0.06);
    }}

    div[data-testid="stMetric"] label {{
        color: {BRAND["muted"]} !important;
        font-weight: 700 !important;
        letter-spacing: 0.02em;
    }}

    div[data-testid="stMetric"] [data-testid="stMetricValue"] {{
        color: {BRAND["forest"]} !important;
        font-weight: 800 !important;
    }}

    [data-testid="stExpander"] {{
        border: none !important;
    }}

    [data-testid="stExpander"] summary {{
        background: rgba(255,255,255,0.88) !important;
        border: 1px solid rgba(47,107,67,0.10) !important;
        border-radius: 16px !important;
    }}

    [data-baseweb="input"], [data-baseweb="select"], textarea {{
        border-radius: 14px !important;
    }}

    .jv-hero {{
        background:
            radial-gradient(circle at top right, rgba(233,196,106,0.28), transparent 26%),
            linear-gradient(135deg, #123524 0%, #1E5631 48%, #2F6B43 100%);
        border-radius: 28px;
        padding: 38px 34px;
        color: white;
        box-shadow: 0 18px 45px rgba(18,53,36,0.18);
        margin-bottom: 1rem;
    }}

    .jv-hero h1, .jv-hero h2 {{
        color: white !important;
        margin-bottom: 0.35rem;
        font-weight: 800;
    }}

    .jv-hero p {{
        color: rgba(255,255,255,0.92) !important;
        margin: 0;
        max-width: 760px;
        line-height: 1.7;
    }}

    .jv-section {{
        margin: 0.5rem 0 1rem;
    }}

    .jv-section h3 {{
        display: inline-block;
        border-bottom: 4px solid {BRAND["mint"]};
        padding-bottom: 0.3rem;
        margin-bottom: 0.35rem;
    }}

    .jv-card {{
        background: linear-gradient(180deg, rgba(255,255,255,0.97), rgba(247,252,248,0.96));
        border: 1px solid rgba(47,107,67,0.16);
        border-radius: 22px;
        padding: 22px 22px 18px;
        box-shadow: 0 12px 24px rgba(18,53,36,0.05);
        height: 100%;
        min-height: 198px;
    }}

    .jv-card h4 {{
        color: {BRAND["forest"]} !important;
        margin: 0 0 0.55rem;
        font-size: 1.05rem;
        line-height: 1.35;
        font-weight: 800;
    }}

    .jv-card p {{
        color: {BRAND["ink"]} !important;
        margin: 0;
        line-height: 1.7;
        font-size: 0.95rem;
    }}

    [data-testid="stDataFrame"] {{
        border: 1px solid rgba(47,107,67,0.14);
        border-radius: 18px;
        overflow: hidden;
        box-shadow: 0 10px 24px rgba(18,53,36,0.05);
    }}

    .jv-badge {{
        display: inline-block;
        margin: 0.5rem 0.35rem 0 0;
        padding: 0.3rem 0.7rem;
        border-radius: 999px;
        background: {BRAND["lime"]};
        color: {BRAND["forest"]};
        font-size: 0.78rem;
        font-weight: 700;
    }}

    .jv-note {{
        background: rgba(216,243,220,0.55);
        border-left: 5px solid {BRAND["green"]};
        border-radius: 16px;
        padding: 16px 18px;
        margin: 0.5rem 0 1rem;
    }}

    .jv-note strong {{
        color: {BRAND["forest"]};
    }}

    .jv-table-wrap {{
        margin-top: 0.75rem;
        border: 1px solid rgba(47,107,67,0.16);
        border-radius: 20px;
        overflow: hidden;
        box-shadow: 0 10px 24px rgba(18,53,36,0.06);
        background: rgba(255,255,255,0.97);
    }}

    .jv-table-scroll {{
        overflow-x: auto;
    }}

    .jv-table {{
        width: 100%;
        border-collapse: collapse;
        min-width: 760px;
    }}

    .jv-table thead th {{
        background: linear-gradient(180deg, #123524 0%, #1E5631 100%);
        color: #ffffff !important;
        text-align: left;
        padding: 12px 14px;
        font-size: 0.9rem;
        font-weight: 700;
        border-right: 1px solid rgba(255,255,255,0.08);
        white-space: nowrap;
    }}

    .jv-table tbody td {{
        padding: 11px 14px;
        color: {BRAND["ink"]} !important;
        border-top: 1px solid #E2F0E7;
        vertical-align: top;
        line-height: 1.55;
        background: rgba(255,255,255,0.98);
    }}

    .jv-table tbody tr:nth-child(even) td {{
        background: #F6FFF8;
    }}

    .jv-table-empty {{
        padding: 20px 16px;
        color: {BRAND["muted"]} !important;
        text-align: center;
        background: rgba(255,255,255,0.98);
    }}
    </style>
    """
    return css


def plotly_layout():
    return dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Manrope", color=BRAND["ink"], size=14),
        margin=dict(l=28, r=28, t=70, b=52),
        title_font=dict(size=18, color=BRAND["forest"], family="Manrope"),
        legend=dict(font=dict(size=13, color=BRAND["ink"]), title=dict(font=dict(size=13, color=BRAND["forest"]))),
    )


def axis_style(title: str):
    return dict(
        title=dict(text=title, font=dict(size=15, color=BRAND["ink"])),
        tickfont=dict(size=13, color=BRAND["forest"]),
        automargin=True,
        title_standoff=10,
        showgrid=True,
        gridcolor="rgba(31,41,55,0.14)",
        zeroline=False,
    )


def style_figure(fig, height: int, x_title: str = "", y_title: str = "", legend: bool = True):
    fig.update_layout(
        height=height,
        showlegend=legend,
        uniformtext_minsize=13,
        uniformtext_mode="show",
    )
    if x_title is not None:
        fig.update_xaxes(**axis_style(x_title))
    if y_title is not None:
        fig.update_yaxes(**axis_style(y_title))
    return fig


def style_bar_labels(fig):
    fig.update_traces(
        textfont=dict(size=15, color=BRAND["forest"]),
        cliponaxis=False,
    )
    return fig


def add_bar_headroom(fig, series: pd.Series, orientation: str = "v", pad: float = 0.18):
    values = pd.to_numeric(series, errors="coerce").dropna()
    if values.empty:
        return fig
    max_value = float(values.max())
    upper = max_value * (1 + pad) if max_value > 0 else 1
    if orientation == "h":
        fig.update_xaxes(range=[0, upper])
    else:
        fig.update_yaxes(range=[0, upper])
    return fig


def add_sidebar(title: str, subtitle: str):
    logo = ASSET / "notext.png"
    import streamlit as st

    if logo.exists():
        st.logo(str(logo), size="large")

    st.sidebar.markdown(f"### {title}")
    st.sidebar.caption(subtitle)
    st.sidebar.markdown("---")
    st.sidebar.markdown("**Tim Jivara**")
    st.sidebar.markdown("Rizki Pangestu")
    st.sidebar.markdown("La Rayan")
    st.sidebar.markdown("Hanif Rifan Ash Shidiq")
    st.sidebar.markdown("Alfito Juanda")
    st.sidebar.markdown("Panji Ihsanudin Fajri")
    st.sidebar.markdown("Rama Danadipa Putra Wijaya")


def hero(title: str, description: str):
    return f"""
    <div class="jv-hero">
        <h2>{title}</h2>
        <p>{description}</p>
    </div>
    """


def section(title: str):
    return f'<div class="jv-section"><h3>{title}</h3></div>'


def card(title: str, body: str, badges=None):
    badge_html = ""
    for badge in badges or []:
        badge_html += f'<span class="jv-badge">{badge}</span>'
    return f'<div class="jv-card"><h4>{title}</h4><p>{body}</p>{badge_html}</div>'


def note(text: str):
    return f'<div class="jv-note">{text}</div>'


def clean_ingredient(item: str):
    cleaned = re.sub(
        r"^\d+[\s/\d]*\s*(sdm|sdt|buah|siung|batang|lembar|porsi|bungkus|butir|ekor|biji|iris|potong|helai|cm|kg|gr|gram|ml|liter|sendok|mangkok|gelas|sachet|bks|bh)\s*",
        "",
        item.strip(),
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"^secukupnya\s*", "", cleaned, flags=re.IGNORECASE).strip().lower()
    return cleaned


def ingredient_counter(df: pd.DataFrame):
    counts = Counter()
    for bahan_str in df["Bahan-bahan"].dropna():
        for item in str(bahan_str).split("|"):
            cleaned = clean_ingredient(item)
            if len(cleaned) > 1:
                counts[cleaned] += 1
    return counts


def compute_recipe_insights(df_resep: pd.DataFrame):
    ingredient_counts = ingredient_counter(df_resep)
    class_counts = df_resep["Kelas_YOLO"].value_counts()
    return {
        "ingredient_counts": ingredient_counts,
        "avg_ingredients": df_resep["Jumlah_Bahan"].mean(),
        "avg_steps": df_resep["Jumlah_Langkah"].mean(),
        "most_common_class": class_counts.index[0],
        "most_common_class_count": int(class_counts.iloc[0]),
    }


def compute_drug_insights(df: pd.DataFrame):
    expiring = 0
    if "Masa Berlaku s/d" in df.columns:
        dates = pd.to_datetime(df["Masa Berlaku s/d"], errors="coerce")
        expiring = int(((dates - pd.Timestamp.today()).dt.days <= 365).fillna(False).sum())
    return {
        "top_group": df["Golongan_Obat"].value_counts().index[0],
        "top_group_count": int(df["Golongan_Obat"].value_counts().iloc[0]),
        "local_share": float((df["Asal_Obat"] == "Lokal/Lainnya").mean()),
        "multi_active_share": float((df["Jumlah_Zat_Aktif"] > 1).mean()),
        "expiring_1y": expiring,
    }


def compute_interaction_frame(kb: dict):
    foods = kb.get("local_ingredient_safety_registry", {})
    rows = []
    for fname, fdata in foods.items():
        for inter in fdata.get("drug_interactions", []):
            rows.append(
                {
                    "Makanan": fname,
                    "Kategori": fdata.get("category", ""),
                    "Severity": inter.get("severity", 0),
                    "Tipe": inter.get("type", ""),
                    "Kelas_Obat": inter.get("drug_class", ""),
                    "Mekanisme": inter.get("mechanism", ""),
                }
            )

    # Fallback: if the JSON KB is empty, load from the CSV instead
    if not rows:
        csv_path = PROC / "drug_food_interactions.csv"
        if csv_path.exists():
            csv_df = pd.read_csv(csv_path)
            # Only keep rows that actually have an interaction
            csv_df = csv_df[csv_df["has_interaction"] == 1].copy()
            csv_df = csv_df.rename(columns={
                "food_class": "Makanan",
                "drug_category": "Kelas_Obat",
                "severity": "Severity",
                "interaction_type": "Tipe",
                "mechanism": "Mekanisme",
            })
            csv_df["Kategori"] = ""
            # Normalize Tipe to the expected labels
            tipe_map = {
                "pharmacokinetic": "AVOID",
                "pharmacodynamic": "MONITOR",
                "additive": "LIMIT",
                "timing": "TIMING",
            }
            csv_df["Tipe"] = csv_df["Tipe"].str.strip().str.lower().map(tipe_map).fillna("MONITOR")
            idf = csv_df[["Makanan", "Kategori", "Severity", "Tipe", "Kelas_Obat", "Mekanisme"]].reset_index(drop=True)
            # Build a synthetic foods dict for downstream compatibility
            foods = {}
            for food_name, group in csv_df.groupby("Makanan"):
                interactions = []
                for _, row in group.iterrows():
                    interactions.append({
                        "drug_class": row["Kelas_Obat"],
                        "severity": int(row["Severity"]),
                        "type": row["Tipe"],
                        "mechanism": row.get("Mekanisme", ""),
                        "interaction": row.get("Mekanisme", ""),
                        "drug_examples": [],
                    })
                foods[food_name] = {
                    "category": "",
                    "key_ingredients": [],
                    "drug_interactions": interactions,
                }
            return idf, foods

    idf = pd.DataFrame(rows)
    # Ensure expected columns exist even when empty
    for col in ["Makanan", "Kategori", "Severity", "Tipe", "Kelas_Obat", "Mekanisme"]:
        if col not in idf.columns:
            idf[col] = pd.Series(dtype="object")
    return idf, foods


def load_kb(path: Path):
    with open(path, "r", encoding="utf-8") as file:
        return json.load(file)


def wrap_text(values, width=18):
    return [fill(str(value), width=width) for value in values]


def style_search_dataframe(df: pd.DataFrame):
    return (
        df.style.hide(axis="index")
        .set_table_styles(
            [
                {
                    "selector": "thead th",
                    "props": [
                        ("background-color", BRAND["forest"]),
                        ("color", "white"),
                        ("font-weight", "700"),
                        ("border", f"1px solid {BRAND['green']}"),
                        ("padding", "10px 12px"),
                    ],
                },
                {
                    "selector": "tbody td",
                    "props": [
                        ("padding", "9px 12px"),
                        ("border-bottom", f"1px solid {BRAND['lime']}"),
                        ("color", BRAND["ink"]),
                        ("background-color", "rgba(255,255,255,0.95)"),
                    ],
                },
                {
                    "selector": "tbody tr:nth-child(even) td",
                    "props": [("background-color", BRAND["sand"])],
                },
            ]
        )
        .set_properties(**{"text-align": "left"})
    )


def render_search_table(df: pd.DataFrame, max_rows: int = 100):
    table_df = df.head(max_rows).copy()
    if table_df.empty:
        return """
        <div class="jv-table-wrap">
            <div class="jv-table-empty">Data tidak ditemukan untuk kata kunci tersebut.</div>
        </div>
        """

    headers = "".join(f"<th>{escape(str(col))}</th>" for col in table_df.columns)
    rows = []
    for _, row in table_df.iterrows():
        cells = "".join(f"<td>{escape('' if pd.isna(value) else str(value))}</td>" for value in row.tolist())
        rows.append(f"<tr>{cells}</tr>")
    body = "".join(rows)
    return f"""
    <div class="jv-table-wrap">
        <div class="jv-table-scroll">
            <table class="jv-table">
                <thead><tr>{headers}</tr></thead>
                <tbody>{body}</tbody>
            </table>
        </div>
    </div>
    """
