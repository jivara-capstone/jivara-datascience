# -*- coding: utf-8 -*-
"""
=======================================================
SCRAPER GAMBAR RESEP MAKANAN DARI COOKPAD INDONESIA
=======================================================
Download gambar resep dari Cookpad berdasarkan kategori makanan.
Gambar disimpan dalam folder per kategori untuk training dataset.

Install:
    pip install requests beautifulsoup4 pandas pillow lxml

Jalankan:
    python scraper_cookpad_images.py --per-category 50

=======================================================
"""

import os
import sys
import time
import random
import requests
import argparse
from pathlib import Path
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
from PIL import Image
from io import BytesIO
import hashlib

# ===================== CONFIG =====================
BASE_URL = "https://cookpad.com"
SEARCH_URL = "https://cookpad.com/id/cari/{keyword}"
DELAY_MIN = 1.0
DELAY_MAX = 2.5
MAX_RETRIES = 3
MAX_PAGES_PER_KEYWORD = 5
MAX_IMAGES_PER_CATEGORY = 100  # Default, bisa di-override
DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data_mentah" / "cookpad_images_selected_classes"

# Default class yang akan dicari saja.
DEFAULT_CATEGORIES = [
    "kunyit-asam",
    "gudeg",
    "bir pletok",
    "papeda",
    "sate lilit",
    "ayam goreng lengkuas",
    "sate meranggi",
    "soerabi",
    "es dawet",
    "sate ayam lamongan",
    "gulai ikan mas",
    "kerak telor",
    "kalppertart",
]

CATEGORY_QUERY_ALIASES = {
    "biskuit choco chips": ["biskuit choco chips", "cookies choco chips", "kue kering choco chips"],
    "sate umum": ["sate ayam", "sate daging", "sate"],
    "gulai ikan-mas": ["gulai ikan mas", "gulai ikan-mas"],
    "gulai ikan mas": ["gulai ikan mas", "gulai ikan-mas"],
    "kunyit-asam": ["kunyit asam", "kunyit-asam"],
    "kunyit asam": ["kunyit asam", "kunyit-asam"],
    "sate meranggi": ["sate meranggi", "sate maranggi"],
    "sate maranggi": ["sate maranggi", "sate meranggi"],
    "soerabi": ["soerabi", "serabi", "surabi"],
    "sperabi": ["soerabi", "serabi", "surabi"],
    "sate ayam lamongan": ["sate ayam lamongan", "sate lamongan"],
    "sate ayam a]lamongan": ["sate ayam lamongan", "sate lamongan"],
    "klappertaart": ["klappertaart", "klappertart"],
    "klappertart": ["klappertart", "klappertaart"],
    "kalppertart": ["kalppertart", "klappertart"],
    "mie aceh": ["mie aceh", "mi aceh"],
    "gado-gado": ["gado gado", "gado-gado"],
    "rawon surabaya": ["rawon surabaya", "rawon"],
    "soto ayam lamongan": ["soto ayam lamongan", "soto lamongan"],
}
# ==================================================


def safe_class_name(category: str) -> str:
    """Ubah nama class menjadi nama folder/file yang aman."""
    safe_name = category.lower().strip()
    safe_name = safe_name.replace("a]lamongan", "lamongan")
    for old, new in (("-", "_"), (" ", "_"), ("]", ""), ("[", "")):
        safe_name = safe_name.replace(old, new)
    return "_".join(part for part in safe_name.split("_") if part)


def get_search_queries(category: str) -> list[str]:
    """Return query Cookpad untuk satu class, termasuk alias typo/ejaan lama."""
    normalized = category.lower().strip()
    queries = CATEGORY_QUERY_ALIASES.get(normalized, [category])
    unique_queries = []
    for query in queries:
        if query not in unique_queries:
            unique_queries.append(query)
    return unique_queries

def get_session() -> requests.Session:
    """Buat session dengan headers browser."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        ),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Referer": "https://cookpad.com/id",
    })

    try:
        resp = session.get(f"{BASE_URL}/id", timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"[!] Warning akses homepage: {e}")

    return session


def delay_random():
    """Random delay agar tidak terdeteksi sebagai bot."""
    wait = random.uniform(DELAY_MIN, DELAY_MAX)
    time.sleep(wait)


def fetch_page(session: requests.Session, url: str) -> BeautifulSoup | None:
    """Fetch halaman dan return BeautifulSoup object."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            resp = session.get(url, timeout=30)
            if resp.status_code == 429:
                print(f"    [!] Rate limited (429), tunggu 5 detik...")
                time.sleep(5)
                continue
            resp.raise_for_status()
            return BeautifulSoup(resp.text, "lxml")
        except Exception as e:
            if attempt < MAX_RETRIES:
                time.sleep(DELAY_MAX * 2)
    return None


def get_recipe_links_from_search(session: requests.Session, keyword: str,
                                  max_pages: int = MAX_PAGES_PER_KEYWORD) -> list[str]:
    """Ambil daftar link resep dari halaman pencarian Cookpad."""
    recipe_links = []
    encoded_keyword = quote(keyword)

    for page in range(1, max_pages + 1):
        if page == 1:
            url = SEARCH_URL.format(keyword=encoded_keyword)
        else:
            url = SEARCH_URL.format(keyword=encoded_keyword) + f"?page={page}"

        soup = fetch_page(session, url)
        if not soup:
            break

        found_count = 0
        for a_tag in soup.find_all("a", href=True):
            href = a_tag.get("href", "")
            if "/id/resep/" in href and "/resep/baru" not in href:
                title = a_tag.get_text(strip=True)
                if not title or len(title) < 3:
                    continue
                if title.lower() in ("cetak", "edit resep", "hapus", "laporkan resep"):
                    continue

                full_url = urljoin(BASE_URL, href)
                full_url = full_url.split("?")[0]

                if full_url not in recipe_links:
                    recipe_links.append(full_url)
                    found_count += 1

        print(f"    Halaman {page}: {found_count} link ditemukan (total: {len(recipe_links)})")

        if found_count == 0:
            break

        delay_random()

    return recipe_links


def extract_image_from_recipe(session: requests.Session, recipe_url: str) -> str | None:
    """Extract gambar utama resep dari halaman Cookpad."""
    soup = fetch_page(session, recipe_url)
    if not soup:
        return None

    try:
        # Cari og:image meta tag (gambar preview resep)
        og_image = soup.find("meta", attrs={"property": "og:image"})
        if og_image and og_image.get("content"):
            return og_image["content"]

        # Fallback: cari img tag dengan class recipe-hero atau hero
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if "recipe" in src.lower() or "hero" in img.get("class", []):
                return urljoin(BASE_URL, src)

        # Fallback lagi: cari img pertama yang ukurannya besar
        for img in soup.find_all("img"):
            src = img.get("src", "")
            if src and "cookpad" in src.lower():
                return urljoin(BASE_URL, src)

        return None
    except Exception as e:
        print(f"    [!] Error extract image: {e}")
        return None


def download_image(session: requests.Session, image_url: str, output_path: Path) -> bool:
    """Download dan simpan gambar."""
    try:
        resp = session.get(image_url, timeout=30)
        resp.raise_for_status()

        # Validate image
        img = Image.open(BytesIO(resp.content))
        if img.size[0] < 200 or img.size[1] < 200:
            print(f"      [!] Image terlalu kecil ({img.size}), skip")
            return False

        # Save image
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'wb') as f:
            f.write(resp.content)

        return True
    except Exception as e:
        print(f"      [!] Error download image: {e}")
        return False


def scrape_cookpad_images(
    categories: list[str],
    per_category: int,
    output_dir: str,
    max_pages: int = MAX_PAGES_PER_KEYWORD,
):
    """Download gambar resep dari Cookpad per kategori."""
    print(f"\n{'='*70}")
    print(f"  SCRAPER GAMBAR RESEP - COOKPAD INDONESIA")
    print(f"  Kategori: {len(categories)} jenis")
    print(f"  Target per kategori: {per_category} gambar")
    print(f"  Output: {output_dir}")
    print(f"{'='*70}\n")

    session = get_session()
    output_base = Path(output_dir)

    for cat_idx, category in enumerate(categories, 1):
        class_name = safe_class_name(category)
        search_queries = get_search_queries(category)
        cat_folder = output_base / class_name
        cat_folder.mkdir(parents=True, exist_ok=True)

        print(f"[{cat_idx}/{len(categories)}] Kategori: '{category}'")
        print(f"  Query: {', '.join(search_queries)}")
        print(f"  Folder: {cat_folder}")

        existing_count = len(list(cat_folder.glob(f"{class_name}_*.jpg")))
        if existing_count >= per_category:
            print(f"  [OK] Sudah ada {existing_count}/{per_category} gambar, skip\n")
            continue
        if existing_count:
            print(f"  Resume dari {existing_count}/{per_category} gambar")

        # Cari link resep
        print(f"  Mengumpulkan link resep...")
        recipe_links = []
        for query in search_queries:
            for recipe_url in get_recipe_links_from_search(session, query, max_pages=max_pages):
                if recipe_url not in recipe_links:
                    recipe_links.append(recipe_url)
        print(f"  Total link: {len(recipe_links)}")

        if not recipe_links:
            print(f"  [!] Tidak ada resep ditemukan\n")
            continue

        # Download gambar
        downloaded = existing_count
        new_downloaded = 0
        failed = 0
        print(f"  Mengunduh gambar...")

        for link_idx, recipe_url in enumerate(recipe_links, 1):
            if downloaded >= per_category:
                print(f"  Target tercapai ({downloaded}/{per_category})")
                break

            # Extract image URL
            image_url = extract_image_from_recipe(session, recipe_url)
            if not image_url:
                failed += 1
                continue

            # Download image
            filename = f"{class_name}_{downloaded+1:03d}.jpg"
            filepath = cat_folder / filename

            if download_image(session, image_url, filepath):
                downloaded += 1
                new_downloaded += 1
                print(f"    [{downloaded}/{per_category}] {filename} [OK]")
            else:
                failed += 1

            delay_random()

        print(f"  [OK] Baru: {new_downloaded}, Total: {downloaded}, Gagal: {failed}\n")

    print(f"{'='*70}")
    print(f"  SELESAI!")
    print(f"{'='*70}\n")


def main():
    parser = argparse.ArgumentParser(description='Download gambar resep dari Cookpad')
    parser.add_argument('--categories', type=str, default=None,
                        help='Comma-separated class names (default: 13 selected classes only)')
    parser.add_argument('--per-category', type=int, default=50,
                        help='Number of images per category (default: 50)')
    parser.add_argument('--output', type=str, default=str(DEFAULT_OUTPUT_DIR),
                        help=f'Output directory (default: {DEFAULT_OUTPUT_DIR})')
    parser.add_argument('--max-pages', type=int, default=MAX_PAGES_PER_KEYWORD,
                        help=f'Maximum search pages per query (default: {MAX_PAGES_PER_KEYWORD})')

    args = parser.parse_args()

    # Tentukan kategori
    if args.categories:
        categories = [c.strip() for c in args.categories.split(',') if c.strip()]
    else:
        categories = DEFAULT_CATEGORIES

    # Run scraper
    scrape_cookpad_images(categories, args.per_category, args.output, args.max_pages)


if __name__ == '__main__':
    main()
