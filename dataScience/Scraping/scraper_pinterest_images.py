# -*- coding: utf-8 -*-
"""
=======================================================
SCRAPER GAMBAR DARI PINTEREST
=======================================================
Download gambar dari halaman search Pinterest untuk class tertentu.

Default target:
    - stroberi dari URL "buah stroberry"
    - apel dari URL "apple red fruit"

Install:
    pip install requests beautifulsoup4 pillow

Jalankan:
    python scraper_pinterest_images.py --per-class 200

Custom:
    python scraper_pinterest_images.py \
        --per-class 100 \
        --output "../data_mentah/Scraping Image Data Imbalance/pinterest_fruits"

Catatan:
    Pinterest kadang membatasi akses publik. Script ini dibuat dengan retry,
    delay, validasi gambar, dan resume agar bisa dijalankan ulang.
=======================================================
"""

from __future__ import annotations

import argparse
import hashlib
import html
import json
import random
import re
import time
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Iterable
from urllib.parse import quote, unquote, urlparse

import requests
from PIL import Image


DEFAULT_OUTPUT_DIR = (
    Path(__file__).resolve().parents[1]
    / "data_mentah"
    / "Scraping Image Data Imbalance"
    / "pinterest_fruits"
)

DEFAULT_TARGETS = {
    "stroberi": "https://id.pinterest.com/search/pins/?q=buah%20stroberry&rs=typed",
    "apel": (
        "https://id.pinterest.com/search/pins/?q=apple%20red%20fruit&rs=ac&len=13"
        "&source_id=ac_ANduFnnT&eq=apple%20red%20fru&etslf=4656"
    ),
}

PINIMG_PATTERN = re.compile(
    r"https?://i\.pinimg\.com/[^\"'\\\s<>]+?\.(?:jpg|jpeg|png|webp)",
    flags=re.IGNORECASE,
)
PINTEREST_RESOURCE_URL = "https://www.pinterest.com/resource/BaseSearchResource/get/"

DELAY_MIN = 1.0
DELAY_MAX = 2.5
MAX_RETRIES = 3
MIN_IMAGE_SIZE = 180


@dataclass(frozen=True)
class ScrapeTarget:
    class_name: str
    search_url: str


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://id.pinterest.com/",
        }
    )
    return session


def delay_random() -> None:
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))


def safe_class_name(value: str) -> str:
    safe_name = value.lower().strip()
    safe_name = re.sub(r"[^a-z0-9]+", "_", safe_name)
    return "_".join(part for part in safe_name.split("_") if part)


def upgrade_pinimg_url(image_url: str) -> str:
    """Gunakan resolusi tinggi jika URL Pinterest memakai ukuran thumbnail."""
    cleaned_url = image_url.split("?")[0]
    cleaned_url = cleaned_url.replace("\\u002F", "/").replace("\\/", "/")
    cleaned_url = unquote(cleaned_url)
    return re.sub(r"/(?:75x75|170x|236x|474x|564x|736x)/", "/originals/", cleaned_url)


def fetch_text(session: requests.Session, url: str) -> str:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(url, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as exc:
            if attempt == MAX_RETRIES:
                print(f"    [!] Gagal fetch: {url} ({exc})")
                return ""
            time.sleep(DELAY_MAX * 2)

    return ""


def extract_pinimg_urls_from_text(text: str) -> list[str]:
    decoded_text = html.unescape(text)
    decoded_text = decoded_text.replace("\\u002F", "/").replace("\\/", "/")

    urls = []
    for match in PINIMG_PATTERN.findall(decoded_text):
        upgraded_url = upgrade_pinimg_url(match)
        if upgraded_url not in urls:
            urls.append(upgraded_url)
    return urls


def collect_from_search_page(session: requests.Session, search_url: str) -> list[str]:
    print("  Mengambil URL gambar dari halaman search...")
    text = fetch_text(session, search_url)
    urls = extract_pinimg_urls_from_text(text)
    print(f"    Ditemukan {len(urls)} kandidat dari HTML awal")
    return urls


def get_search_query(search_url: str) -> str:
    parsed = urlparse(search_url)
    query_match = re.search(r"(?:^|&)q=([^&]+)", parsed.query)
    if not query_match:
        return ""
    return unquote(query_match.group(1).replace("+", " "))


def build_resource_params(search_url: str, bookmark: str | None = None) -> dict[str, str]:
    query = get_search_query(search_url)
    source_url = f"/search/pins/?q={quote(query)}&rs=typed"
    data = {
        "options": {
            "appliedProductFilters": "---",
            "article": "",
            "auto_correction_disabled": False,
            "corpus": None,
            "customized_rerank_type": None,
            "domains": None,
            "filters": None,
            "journey_depth": None,
            "page_size": 25,
            "price_max": None,
            "price_min": None,
            "query_pin_sigs": None,
            "query": query,
            "redux_normalize_feed": True,
            "rs": "typed",
            "scope": "pins",
            "source_id": None,
        },
        "context": {},
    }
    if bookmark:
        data["options"]["bookmarks"] = [bookmark]

    return {
        "source_url": source_url,
        "data": json.dumps(data, separators=(",", ":")),
        "_": str(int(time.time() * 1000)),
    }


def iter_values(payload: object) -> Iterable[object]:
    if isinstance(payload, dict):
        for value in payload.values():
            yield value
            yield from iter_values(value)
    elif isinstance(payload, list):
        for item in payload:
            yield item
            yield from iter_values(item)


def extract_pinimg_urls_from_json(payload: object) -> list[str]:
    urls = []
    for value in iter_values(payload):
        if isinstance(value, str) and "i.pinimg.com" in value:
            for image_url in extract_pinimg_urls_from_text(value):
                if image_url not in urls:
                    urls.append(image_url)
    return urls


def extract_bookmark(payload: object) -> str | None:
    if isinstance(payload, dict):
        resource = payload.get("resource_response", {})
        if isinstance(resource, dict):
            bookmark = resource.get("bookmark")
            if isinstance(bookmark, str) and bookmark:
                return bookmark

        for value in payload.values():
            bookmark = extract_bookmark(value)
            if bookmark:
                return bookmark
    elif isinstance(payload, list):
        for item in payload:
            bookmark = extract_bookmark(item)
            if bookmark:
                return bookmark

    return None


def collect_from_resource_api(session: requests.Session, search_url: str, rounds: int) -> list[str]:
    urls = []
    bookmark = None

    print("  Mengambil URL gambar dari Pinterest resource API...")
    for round_idx in range(1, rounds + 1):
        try:
            response = session.get(
                PINTEREST_RESOURCE_URL,
                params=build_resource_params(search_url, bookmark=bookmark),
                headers={"Accept": "application/json", "X-Requested-With": "XMLHttpRequest"},
                timeout=30,
            )
            response.raise_for_status()
            payload = response.json()
        except Exception as exc:
            print(f"    [!] Resource API round {round_idx} gagal: {exc}")
            break

        new_urls = extract_pinimg_urls_from_json(payload)
        added = 0
        for image_url in new_urls:
            if image_url not in urls:
                urls.append(image_url)
                added += 1

        bookmark = extract_bookmark(payload)
        print(f"    Round {round_idx}: +{added} kandidat (total {len(urls)})")

        if not bookmark or added == 0:
            break
        delay_random()

    return urls


def image_hash(content: bytes) -> str:
    return hashlib.md5(content).hexdigest()


def existing_hashes(folder: Path) -> set[str]:
    hashes = set()
    for image_path in folder.glob("*"):
        if image_path.is_file():
            try:
                hashes.add(image_hash(image_path.read_bytes()))
            except Exception:
                continue
    return hashes


def download_image(session: requests.Session, image_url: str) -> tuple[bytes, str] | None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(image_url, timeout=30)
            response.raise_for_status()
            content = response.content

            image = Image.open(BytesIO(content))
            width, height = image.size
            if width < MIN_IMAGE_SIZE or height < MIN_IMAGE_SIZE:
                return None

            extension = image.format.lower() if image.format else "jpg"
            if extension == "jpeg":
                extension = "jpg"
            return content, extension
        except Exception:
            if attempt == MAX_RETRIES:
                return None
            time.sleep(DELAY_MAX)

    return None


def collect_candidate_urls(session: requests.Session, search_url: str, api_rounds: int) -> list[str]:
    urls = []
    for image_url in collect_from_search_page(session, search_url):
        if image_url not in urls:
            urls.append(image_url)

    for image_url in collect_from_resource_api(session, search_url, rounds=api_rounds):
        if image_url not in urls:
            urls.append(image_url)

    return urls


def parse_srcset(srcset: str) -> list[str]:
    urls = []
    for item in srcset.split(","):
        src = item.strip().split(" ")[0]
        if src.startswith("http") and "i.pinimg.com" in src:
            urls.append(src.split("?")[0])
            urls.append(upgrade_pinimg_url(src))
    return urls


def collect_from_selenium(search_url: str, scroll_rounds: int, headless: bool = True) -> list[str]:
    """Render Pinterest dengan Selenium lalu ambil URL gambar yang sudah muncul."""
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.common.by import By
    except ImportError:
        print("  [!] Selenium belum terinstall. Install: pip install selenium")
        return []

    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1400,2200")
    options.add_argument("--lang=id-ID")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    urls = []
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(search_url)
        time.sleep(5)

        for round_idx in range(1, scroll_rounds + 1):
            images = driver.find_elements(By.TAG_NAME, "img")
            added = 0
            for image in images:
                candidates = []
                try:
                    for attr_name in ("src", "currentSrc", "data-src"):
                        value = image.get_attribute(attr_name)
                        if value and "i.pinimg.com" in value:
                            candidates.append(value.split("?")[0])
                            candidates.append(upgrade_pinimg_url(value))

                    srcset = image.get_attribute("srcset") or ""
                    candidates.extend(parse_srcset(srcset))
                except Exception:
                    continue

                for candidate in candidates:
                    if candidate not in urls:
                        urls.append(candidate)
                        added += 1

            try:
                page_urls = extract_pinimg_urls_from_text(driver.page_source)
            except Exception:
                page_urls = []
            for page_url in page_urls:
                if page_url not in urls:
                    urls.append(page_url)
                    added += 1

            print(f"    Scroll {round_idx}: +{added} kandidat (total {len(urls)})")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(random.uniform(2.0, 4.0))

            if added == 0 and round_idx >= 3:
                break

    except Exception as exc:
        print(f"  [!] Selenium gagal membuka Pinterest: {exc}")
    finally:
        if driver:
            driver.quit()

    return urls


def scrape_target(
    session: requests.Session,
    target: ScrapeTarget,
    per_class: int,
    output_dir: Path,
    api_rounds: int,
    scroll_rounds: int,
    mode: str,
    headless: bool,
) -> None:
    class_folder = output_dir / safe_class_name(target.class_name)
    class_folder.mkdir(parents=True, exist_ok=True)

    existing_files = [path for path in class_folder.glob("*") if path.is_file()]
    downloaded = len(existing_files)
    seen_hashes = existing_hashes(class_folder)

    print(f"\n[{target.class_name}]")
    print(f"  URL    : {target.search_url}")
    print(f"  Folder : {class_folder}")
    print(f"  Resume : {downloaded}/{per_class}")

    if downloaded >= per_class:
        print("  [OK] Target sudah terpenuhi, skip.")
        return

    candidate_urls = []
    if mode in ("auto", "selenium"):
        print("  Mode browser Selenium...")
        candidate_urls.extend(
            collect_from_selenium(
                search_url=target.search_url,
                scroll_rounds=scroll_rounds,
                headless=headless,
            )
        )

    if mode == "requests" or (mode == "auto" and not candidate_urls):
        print("  Mode requests fallback...")
        candidate_urls.extend(collect_candidate_urls(session, target.search_url, api_rounds=api_rounds))

    unique_candidate_urls = []
    for image_url in candidate_urls:
        if image_url not in unique_candidate_urls:
            unique_candidate_urls.append(image_url)
    candidate_urls = unique_candidate_urls

    print(f"  Total kandidat URL: {len(candidate_urls)}")

    failed = 0
    for image_url in candidate_urls:
        if downloaded >= per_class:
            break

        result = download_image(session, image_url)
        if not result:
            failed += 1
            continue

        content, extension = result
        content_hash = image_hash(content)
        if content_hash in seen_hashes:
            continue

        downloaded += 1
        seen_hashes.add(content_hash)
        filename = f"{safe_class_name(target.class_name)}_{downloaded:03d}.{extension}"
        (class_folder / filename).write_bytes(content)
        print(f"    [{downloaded}/{per_class}] {filename} [OK]")
        delay_random()

    print(f"  Selesai: total={downloaded}, gagal={failed}")


def parse_targets(targets_arg: str | None) -> list[ScrapeTarget]:
    if not targets_arg:
        return [
            ScrapeTarget(class_name=class_name, search_url=url)
            for class_name, url in DEFAULT_TARGETS.items()
        ]

    targets = []
    for item in targets_arg.split(","):
        if not item.strip():
            continue
        if "=" not in item:
            raise ValueError("Format --targets harus class_name=url,class_name=url")
        class_name, url = item.split("=", 1)
        targets.append(ScrapeTarget(class_name=class_name.strip(), search_url=url.strip()))
    return targets


def main() -> None:
    parser = argparse.ArgumentParser(description="Download gambar dari Pinterest search URL.")
    parser.add_argument("--per-class", type=int, default=200, help="Jumlah gambar per class.")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT_DIR), help="Folder output.")
    parser.add_argument(
        "--mode",
        choices=["auto", "selenium", "requests"],
        default="auto",
        help="Mode scraping. Pinterest biasanya perlu selenium.",
    )
    parser.add_argument(
        "--api-rounds",
        type=int,
        default=8,
        help="Jumlah request tambahan ke Pinterest resource API.",
    )
    parser.add_argument(
        "--scroll-rounds",
        type=int,
        default=12,
        help="Jumlah scroll saat memakai Selenium.",
    )
    parser.add_argument(
        "--show-browser",
        action="store_true",
        help="Tampilkan browser Selenium, berguna kalau Pinterest meminta login/captcha.",
    )
    parser.add_argument(
        "--targets",
        type=str,
        default=None,
        help="Format custom: class_name=url,class_name=url",
    )

    args = parser.parse_args()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    targets = parse_targets(args.targets)
    session = get_session()

    print("=" * 70)
    print("SCRAPER PINTEREST IMAGES")
    print(f"Target class: {len(targets)}")
    print(f"Per class   : {args.per_class}")
    print(f"Output      : {output_dir}")
    print("=" * 70)

    for target in targets:
        scrape_target(
            session=session,
            target=target,
            per_class=args.per_class,
            output_dir=output_dir,
            api_rounds=args.api_rounds,
            scroll_rounds=args.scroll_rounds,
            mode=args.mode,
            headless=not args.show_browser,
        )

    print("\nSelesai.")


if __name__ == "__main__":
    main()
