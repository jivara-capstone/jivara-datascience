"""
A/B Testing — Jivara (CC26-PSU090)
====================================
Drug-Food Interaction Detection System

Dua Pertanyaan Utama:
  1. Apakah Jivara meningkatkan kepatuhan minum obat pasien?
  2. Apakah Jivara membantu pasien menghindari makanan yang berbahaya
     bagi obat mereka?

Cara menjalankan:
    python AB_Testing_Adherence_Analysis.py

Output:
    Visualisasi PNG di folder ../data_output/ab_testing/

CATATAN: Menggunakan data simulasi sebagai proof-of-concept.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind, mannwhitneyu
from pathlib import Path
import warnings

warnings.filterwarnings("ignore")

# ============================================================
# KONFIGURASI
# ============================================================
SEED = 42
N_PER_GROUP = 150
ALPHA = 0.05
N_BOOTSTRAP = 5000

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data_output" / "ab_testing"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

COLOR_CONTROL = "#FF6B6B"
COLOR_JIVARA = "#4ECDC4"


# ============================================================
# FUNGSI STATISTIK
# ============================================================
def bootstrap_ci(t, c, n=N_BOOTSTRAP):
    """95% Confidence Interval via Bootstrap."""
    t, c = np.asarray(t), np.asarray(c)
    diffs = [np.random.choice(t, len(t), True).mean() -
             np.random.choice(c, len(c), True).mean() for _ in range(n)]
    return np.percentile(diffs, 2.5), np.percentile(diffs, 97.5)


def cohens_d(t, c):
    """Cohen's d effect size."""
    n1, n2 = len(t), len(c)
    pooled = np.sqrt(((n1-1)*t.var() + (n2-1)*c.var()) / (n1+n2-2))
    return (t.mean() - c.mean()) / pooled


def label_d(d):
    """Interpretasi Cohen's d."""
    d = abs(d)
    if d < 0.2: return "Kecil"
    if d < 0.5: return "Sedang"
    if d < 0.8: return "Besar"
    return "Sangat Besar"


def ab_test(treat, ctrl):
    """Jalankan semua uji statistik A/B."""
    _, p_welch = ttest_ind(treat, ctrl, equal_var=False)
    _, p_mw = mannwhitneyu(treat, ctrl, alternative="greater")
    ci = bootstrap_ci(treat, ctrl)
    d = cohens_d(treat, ctrl)
    return {
        "ctrl_mean": ctrl.mean(), "treat_mean": treat.mean(),
        "diff": treat.mean() - ctrl.mean(),
        "p_welch": p_welch, "p_mw": p_mw,
        "significant": p_welch < ALPHA,
        "ci_lo": ci[0], "ci_hi": ci[1],
        "d": d, "d_label": label_d(d),
    }


# ============================================================
# GENERATE DATA SIMULASI
# ============================================================
def generate_data():
    """Membuat dataset simulasi untuk kedua pertanyaan A/B."""
    np.random.seed(SEED)
    beta = lambda mu, n: np.random.beta(mu*30, (1-mu)*30, n)

    # --- Pertanyaan 1: Kepatuhan Minum Obat ---
    # Control: pasien pakai pengingat biasa -> adherence ~62%
    # Jivara:  pasien pakai Jivara          -> adherence ~78%
    adh_ctrl = beta(0.62, N_PER_GROUP)
    adh_treat = beta(0.78, N_PER_GROUP)

    # --- Pertanyaan 2: Penghindaran Makanan Berbahaya ---
    # Control: pasien tanpa Jivara -> ~35% makanan berbahaya dihindari
    # Jivara:  pasien dengan Jivara -> ~72% makanan berbahaya dihindari
    avoid_ctrl = beta(0.35, N_PER_GROUP)
    avoid_treat = beta(0.72, N_PER_GROUP)

    df = pd.DataFrame({
        "patient_id": [f"P{i:03d}" for i in range(1, 2*N_PER_GROUP+1)],
        "group": ["Tanpa Jivara"]*N_PER_GROUP + ["Dengan Jivara"]*N_PER_GROUP,
        "kepatuhan_obat": np.concatenate([adh_ctrl, adh_treat]),
        "penghindaran_makanan": np.concatenate([avoid_ctrl, avoid_treat]),
    })
    return df


# ============================================================
# VISUALISASI
# ============================================================
def plot_rq1(df, result):
    """
    Pertanyaan 1: Apakah Jivara meningkatkan kepatuhan minum obat?
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # --- Panel Kiri: Perbandingan Mean ---
    ax = axes[0]
    groups = ["Tanpa Jivara", "Dengan Jivara"]
    means = [result["ctrl_mean"], result["treat_mean"]]
    colors = [COLOR_CONTROL, COLOR_JIVARA]

    bars = ax.bar(groups, means, color=colors, alpha=0.85,
                  edgecolor="black", linewidth=1.5, width=0.5)
    for bar, m in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, m + 0.02,
                f"{m:.0%}", ha="center", fontsize=16, fontweight="bold")

    # Annotasi improvement
    ax.annotate(f'+{result["diff"]:.0%}', xy=(0.5, sum(means)/2),
                fontsize=18, fontweight="bold", color="green", ha="center",
                bbox=dict(boxstyle="round,pad=0.4", fc="lightgreen", alpha=0.8))

    ax.set_ylabel("Kepatuhan Minum Obat (%)", fontsize=13)
    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.set_title("Rata-rata Kepatuhan Obat", fontsize=14, fontweight="bold")

    # --- Panel Kanan: Distribusi ---
    ax = axes[1]
    for grp, clr in zip(groups, colors):
        data = df[df["group"] == grp]["kepatuhan_obat"]
        ax.hist(data, bins=20, alpha=0.55, label=grp, color=clr, edgecolor="black")
    ax.set_xlabel("Kepatuhan Minum Obat (%)", fontsize=12)
    ax.set_ylabel("Jumlah Pasien", fontsize=12)
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{x:.0%}"))
    ax.legend(fontsize=11)
    ax.set_title("Distribusi Per Grup", fontsize=14, fontweight="bold")

    # Verdict
    sig = "SIGNIFIKAN" if result["significant"] else "TIDAK SIGNIFIKAN"
    fig.suptitle(
        "Pertanyaan 1: Apakah Jivara Meningkatkan Kepatuhan Minum Obat?",
        fontsize=17, fontweight="bold", y=1.04
    )
    fig.text(0.5, -0.03,
             f"Hasil: Perbedaan {sig} (p = {result['p_welch']:.4f}) | "
             f"Effect size: {result['d']:.2f} ({result['d_label']}) | "
             f"95% CI: [{result['ci_lo']:.0%}, {result['ci_hi']:.0%}]",
             ha="center", fontsize=11, style="italic",
             bbox=dict(boxstyle="round", fc="#F0F0F0", alpha=0.8))

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "RQ1_kepatuhan_obat.png", dpi=300, bbox_inches="tight")
    plt.close()


def plot_rq2(df, result):
    """
    Pertanyaan 2: Apakah Jivara membantu pasien menghindari makanan berbahaya?
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # --- Panel Kiri: Perbandingan Mean ---
    ax = axes[0]
    groups = ["Tanpa Jivara", "Dengan Jivara"]
    means = [result["ctrl_mean"], result["treat_mean"]]
    colors = [COLOR_CONTROL, COLOR_JIVARA]

    bars = ax.bar(groups, means, color=colors, alpha=0.85,
                  edgecolor="black", linewidth=1.5, width=0.5)
    for bar, m in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, m + 0.02,
                f"{m:.0%}", ha="center", fontsize=16, fontweight="bold")

    ax.annotate(f'+{result["diff"]:.0%}', xy=(0.5, sum(means)/2),
                fontsize=18, fontweight="bold", color="green", ha="center",
                bbox=dict(boxstyle="round,pad=0.4", fc="lightgreen", alpha=0.8))

    ax.set_ylabel("Makanan Berbahaya Berhasil Dihindari (%)", fontsize=12)
    ax.set_ylim(0, 1.05)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.set_title("Rata-rata Penghindaran", fontsize=14, fontweight="bold")

    # --- Panel Kanan: Box Plot ---
    ax = axes[1]
    sns.boxplot(data=df, x="group", y="penghindaran_makanan", ax=ax,
                palette={"Tanpa Jivara": COLOR_CONTROL, "Dengan Jivara": COLOR_JIVARA},
                width=0.5, linewidth=1.5)
    ax.set_xlabel("")
    ax.set_ylabel("Penghindaran Makanan Berbahaya (%)", fontsize=12)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f"{y:.0%}"))
    ax.set_title("Distribusi Per Grup", fontsize=14, fontweight="bold")

    sig = "SIGNIFIKAN" if result["significant"] else "TIDAK SIGNIFIKAN"
    fig.suptitle(
        "Pertanyaan 2: Apakah Jivara Membantu Menghindari Makanan Berbahaya?",
        fontsize=17, fontweight="bold", y=1.04
    )
    fig.text(0.5, -0.03,
             f"Hasil: Perbedaan {sig} (p = {result['p_welch']:.4f}) | "
             f"Effect size: {result['d']:.2f} ({result['d_label']}) | "
             f"95% CI: [{result['ci_lo']:.0%}, {result['ci_hi']:.0%}]",
             ha="center", fontsize=11, style="italic",
             bbox=dict(boxstyle="round", fc="#F0F0F0", alpha=0.8))

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "RQ2_penghindaran_makanan.png", dpi=300, bbox_inches="tight")
    plt.close()


def plot_summary(rq1, rq2):
    """Visualisasi ringkasan kedua pertanyaan."""
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.axis("off")

    ax.text(0.5, 0.96, "RINGKASAN A/B TESTING — JIVARA",
            fontsize=22, fontweight="bold", ha="center", transform=ax.transAxes)
    ax.text(0.5, 0.91, "(Data Simulasi - Proof of Concept)",
            fontsize=11, ha="center", color="#999", style="italic",
            transform=ax.transAxes)

    rows = [
        ["", "Tanpa Jivara", "Dengan Jivara", "Peningkatan", "Signifikan?", "Effect Size"],
        ["RQ1: Kepatuhan Obat",
         f"{rq1['ctrl_mean']:.0%}", f"{rq1['treat_mean']:.0%}",
         f"+{rq1['diff']:.0%}", "YA" if rq1["significant"] else "TIDAK",
         f"{rq1['d']:.1f} ({rq1['d_label']})"],
        ["RQ2: Hindari Makanan\nBerbahaya",
         f"{rq2['ctrl_mean']:.0%}", f"{rq2['treat_mean']:.0%}",
         f"+{rq2['diff']:.0%}", "YA" if rq2["significant"] else "TIDAK",
         f"{rq2['d']:.1f} ({rq2['d_label']})"],
    ]

    table = ax.table(cellText=rows[1:], colLabels=rows[0],
                     cellLoc="center", loc="center",
                     bbox=[0.02, 0.28, 0.96, 0.55])
    table.auto_set_font_size(False)
    table.set_fontsize(13)
    table.scale(1, 2.5)

    # Style header
    for j in range(6):
        table[0, j].set_facecolor("#2C3E50")
        table[0, j].set_text_props(color="white", fontweight="bold", fontsize=11)

    # Style data
    for i in [1, 2]:
        table[i, 0].set_text_props(fontweight="bold")
        table[i, 0].set_facecolor("#ECF0F1")
        # Kolom "Signifikan?"
        val = rows[i][4]
        if val == "YA":
            table[i, 4].set_facecolor("#D5F5E3")
        else:
            table[i, 4].set_facecolor("#FADBD8")
        # Kolom "Peningkatan"
        table[i, 3].set_facecolor("#D5F5E3")
        table[i, 3].set_text_props(fontweight="bold", color="#27AE60")

    # Kesimpulan
    both_sig = rq1["significant"] and rq2["significant"]
    if both_sig:
        verdict = "JIVARA TERBUKTI EFEKTIF (dalam simulasi)"
        vcolor = "#27AE60"
    else:
        verdict = "PERLU EVALUASI LEBIH LANJUT"
        vcolor = "#E67E22"

    ax.text(0.5, 0.18, f"KESIMPULAN: {verdict}",
            fontsize=16, fontweight="bold", ha="center", color="white",
            transform=ax.transAxes,
            bbox=dict(boxstyle="round,pad=0.6", fc=vcolor, alpha=0.9))

    ax.text(0.5, 0.08,
            "Jivara secara signifikan meningkatkan kepatuhan minum obat\n"
            "DAN membantu pasien menghindari makanan yang berinteraksi dengan obat mereka.",
            fontsize=12, ha="center", color="#555", transform=ax.transAxes)

    ax.text(0.5, 0.01,
            "Catatan: Perlu validasi dengan data pengguna real sebelum deployment.",
            fontsize=10, ha="center", color="#999", style="italic",
            transform=ax.transAxes)

    plt.savefig(OUTPUT_DIR / "00_ringkasan_ab_testing.png", dpi=300, bbox_inches="tight")
    plt.close()


# ============================================================
# MAIN
# ============================================================
def main():
    print("=" * 60)
    print("  A/B TESTING - JIVARA")
    print("  Drug-Food Interaction Detection System")
    print("  (Data Simulasi - Proof of Concept)")
    print("=" * 60)

    # 1. Generate data
    print("\n[1/3] Membuat data simulasi...")
    df = generate_data()
    print(f"  {len(df)} pasien ({N_PER_GROUP} per grup)")

    # 2. Uji statistik
    print("\n[2/3] Menjalankan uji statistik...")

    ctrl = df[df["group"] == "Tanpa Jivara"]
    treat = df[df["group"] == "Dengan Jivara"]

    rq1 = ab_test(treat["kepatuhan_obat"], ctrl["kepatuhan_obat"])
    rq2 = ab_test(treat["penghindaran_makanan"], ctrl["penghindaran_makanan"])

    print("\n  RQ1: Apakah Jivara meningkatkan kepatuhan minum obat?")
    print(f"    Tanpa Jivara: {rq1['ctrl_mean']:.0%}")
    print(f"    Dengan Jivara: {rq1['treat_mean']:.0%}")
    print(f"    Peningkatan: +{rq1['diff']:.0%}")
    print(f"    Signifikan: {'YA' if rq1['significant'] else 'TIDAK'} "
          f"(p={rq1['p_welch']:.4f})")
    print(f"    Effect size: {rq1['d']:.2f} ({rq1['d_label']})")

    print("\n  RQ2: Apakah Jivara membantu menghindari makanan berbahaya?")
    print(f"    Tanpa Jivara: {rq2['ctrl_mean']:.0%}")
    print(f"    Dengan Jivara: {rq2['treat_mean']:.0%}")
    print(f"    Peningkatan: +{rq2['diff']:.0%}")
    print(f"    Signifikan: {'YA' if rq2['significant'] else 'TIDAK'} "
          f"(p={rq2['p_welch']:.4f})")
    print(f"    Effect size: {rq2['d']:.2f} ({rq2['d_label']})")

    # 3. Visualisasi
    print("\n[3/3] Membuat visualisasi...")
    sns.set_theme(style="whitegrid", palette="Set2", font_scale=1.1)
    plt.rcParams["figure.dpi"] = 120

    plot_rq1(df, rq1)
    print("  [OK] RQ1_kepatuhan_obat.png")
    plot_rq2(df, rq2)
    print("  [OK] RQ2_penghindaran_makanan.png")
    plot_summary(rq1, rq2)
    print("  [OK] 00_ringkasan_ab_testing.png")

    # Kesimpulan
    print("\n" + "=" * 60)
    if rq1["significant"] and rq2["significant"]:
        print("  KESIMPULAN: JIVARA TERBUKTI EFEKTIF (dalam simulasi)")
    else:
        print("  KESIMPULAN: PERLU EVALUASI LEBIH LANJUT")
    print(f"\n  Output: {OUTPUT_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
