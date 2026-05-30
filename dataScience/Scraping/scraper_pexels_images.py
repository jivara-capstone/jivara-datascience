# -*- coding: utf-8 -*-
"""
=======================================================
SCRAPER GAMBAR DARI PEXELS
=======================================================
Download gambar dari halaman search Pexels untuk class tertentu.

Default target:
    - biskuit_choco_chips dari URL Pexels yang dilampirkan

Install:
    pip install requests beautifulsoup4 pillow selenium

Jalankan:
    python scraper_pexels_images.py --per-class 200

Catatan:
    Pexels sering menolak requests HTML biasa, jadi script ini memakai
    Selenium untuk merender halaman, lalu requests untuk download gambar.
    Dedup dilakukan dengan photo ID Pexels, hash byte, dan perceptual hash.
=======================================================
"""

from __future__ import annotations

import argparse
import hashlib
import html
import random
import re
import time
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Iterable
from urllib.parse import parse_qsl, unquote, urlencode, urlparse, urlunparse

import requests
from PIL import Image, ImageOps


DEFAULT_OUTPUT_DIR = (
    Path(__file__).resolve().parents[1]
    / "data_mentah"
    / "Scraping Image Data Imbalance"
    / "pexels_extra"
)

DEFAULT_TARGETS = {
    "biskuit_choco_chips": "https://www.pexels.com/id-id/pencarian/choco%20chip%20cookies/",
}

PEXELS_IMAGE_PATTERN = re.compile(
    r"https?://images\.pexels\.com/photos/\d+/[^\"'\\\s<>]+",
    flags=re.IGNORECASE,
)
PHOTO_ID_PATTERN = re.compile(r"/photos/(\d+)/", flags=re.IGNORECASE)

DELAY_MIN = 0.6
DELAY_MAX = 1.6
MAX_RETRIES = 3
MIN_IMAGE_SIZE = 220


@dataclass(frozen=True)
class ScrapeTarget:
    class_name: str
    search_url: str


@dataclass(frozen=True)
class ImageCandidate:
    photo_id: str
    url: str
    width_hint: int


def get_session() -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            "Accept": "image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8",
            "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
            "Referer": "https://www.pexels.com/",
        }
    )
    return session


def delay_random() -> None:
    time.sleep(random.uniform(DELAY_MIN, DELAY_MAX))


def safe_class_name(value: str) -> str:
    safe_name = value.lower().strip()
    safe_name = re.sub(r"[^a-z0-9]+", "_", safe_name)
    return "_".join(part for part in safe_name.split("_") if part)


def clean_url(value: str) -> str:
    value = html.unescape(value)
    value = value.replace("\\u002F", "/").replace("\\/", "/")
    return unquote(value.strip())


def extract_photo_id(image_url: str) -> str | None:
    match = PHOTO_ID_PATTERN.search(image_url)
    return match.group(1) if match else None


def width_from_url(image_url: str) -> int:
    parsed = urlparse(image_url)
    params = dict(parse_qsl(parsed.query))
    try:
        return int(params.get("w", "0"))
    except ValueError:
        return 0


def normalize_download_url(image_url: str, download_width: int) -> str:
    parsed = urlparse(clean_url(image_url))
    params = dict(parse_qsl(parsed.query))
    params["auto"] = "compress"
    params["cs"] = "tinysrgb"
    params["w"] = str(download_width)
    params.pop("dpr", None)
    return urlunparse(parsed._replace(query=urlencode(params)))


def parse_srcset(srcset: str) -> list[str]:
    urls = []
    for item in srcset.split(","):
        src = item.strip().split(" ")[0]
        if "images.pexels.com/photos/" in src:
            urls.append(clean_url(src))
    return urls


def collect_pexels_urls_from_text(text: str) -> list[str]:
    urls = []
    decoded_text = clean_url(text)
    for match in PEXELS_IMAGE_PATTERN.findall(decoded_text):
        image_url = clean_url(match).rstrip("\\")
        if image_url not in urls:
            urls.append(image_url)
    return urls


def candidates_from_urls(image_urls: Iterable[str], download_width: int) -> list[ImageCandidate]:
    by_photo_id: dict[str, ImageCandidate] = {}

    for image_url in image_urls:
        if "images.pexels.com/photos/" not in image_url:
            continue
        photo_id = extract_photo_id(image_url)
        if not photo_id:
            continue

        normalized_url = normalize_download_url(image_url, download_width=download_width)
        candidate = ImageCandidate(
            photo_id=photo_id,
            url=normalized_url,
            width_hint=max(width_from_url(image_url), download_width),
        )
        current = by_photo_id.get(photo_id)
        if current is None or candidate.width_hint > current.width_hint:
            by_photo_id[photo_id] = candidate

    return list(by_photo_id.values())


def collect_from_selenium(
    search_url: str,
    scroll_rounds: int,
    download_width: int,
    headless: bool = True,
) -> list[ImageCandidate]:
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
    options.add_argument("--window-size=1440,2400")
    options.add_argument("--lang=id-ID")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    )

    image_urls: list[str] = []
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.get(search_url)
        time.sleep(5)

        stagnant_rounds = 0
        last_scroll_height = 0
        for round_idx in range(1, scroll_rounds + 1):
            added = 0

            for image in driver.find_elements(By.TAG_NAME, "img"):
                found = []
                for attr_name in ("src", "currentSrc", "data-src"):
                    value = image.get_attribute(attr_name)
                    if value and "images.pexels.com/photos/" in value:
                        found.append(clean_url(value))

                srcset = image.get_attribute("srcset") or ""
                found.extend(parse_srcset(srcset))

                for image_url in found:
                    if image_url not in image_urls:
                        image_urls.append(image_url)
                        added += 1

            for image_url in collect_pexels_urls_from_text(driver.page_source):
                if image_url not in image_urls:
                    image_urls.append(image_url)
                    added += 1

            print(f"    Scroll {round_idx}: +{added} URL (total {len(image_urls)})")
            scroll_height = driver.execute_script("return document.documentElement.scrollHeight;")
            driver.execute_script("window.scrollBy(0, Math.floor(window.innerHeight * 0.75));")
            time.sleep(random.uniform(2.2, 3.8))

            if added == 0 and scroll_height == last_scroll_height:
                stagnant_rounds += 1
            else:
                stagnant_rounds = 0
            last_scroll_height = scroll_height

            if stagnant_rounds >= 6:
                break

    except Exception as exc:
        print(f"  [!] Selenium gagal membuka Pexels: {exc}")
    finally:
        if driver:
            driver.quit()

    return candidates_from_urls(image_urls, download_width=download_width)


def image_hash(content: bytes) -> str:
    return hashlib.md5(content).hexdigest()


def dhash_from_image(image: Image.Image, hash_size: int = 8) -> int:
    image = ImageOps.exif_transpose(image).convert("L").resize((hash_size + 1, hash_size))
    pixels = list(image.getdata())
    value = 0
    for row in range(hash_size):
        for col in range(hash_size):
            left = pixels[row * (hash_size + 1) + col]
            right = pixels[row * (hash_size + 1) + col + 1]
            value = (value << 1) | int(left > right)
    return value


def hamming_distance(left: int, right: int) -> int:
    return (left ^ right).bit_count()


def existing_fingerprints(paths: Iterable[Path]) -> tuple[set[str], set[int]]:
    byte_hashes: set[str] = set()
    visual_hashes: set[int] = set()

    for folder in paths:
        if not folder.exists():
            continue
        for image_path in folder.glob("*"):
            if not image_path.is_file():
                continue
            try:
                content = image_path.read_bytes()
                byte_hashes.add(image_hash(content))
                with Image.open(BytesIO(content)) as image:
                    visual_hashes.add(dhash_from_image(image))
            except Exception:
                continue

    return byte_hashes, visual_hashes


def is_visual_duplicate(candidate_hash: int, known_hashes: set[int], threshold: int) -> bool:
    return any(hamming_distance(candidate_hash, known_hash) <= threshold for known_hash in known_hashes)


def download_image(session: requests.Session, image_url: str) -> tuple[bytes, str, int] | None:
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.get(image_url, timeout=40)
            response.raise_for_status()
            content = response.content

            with Image.open(BytesIO(content)) as image:
                image = ImageOps.exif_transpose(image)
                width, height = image.size
                if width < MIN_IMAGE_SIZE or height < MIN_IMAGE_SIZE:
                    return None
                extension = image.format.lower() if image.format else "jpg"
                visual_hash = dhash_from_image(image)

            if extension == "jpeg":
                extension = "jpg"
            return content, extension, visual_hash
        except Exception:
            if attempt == MAX_RETRIES:
                return None
            time.sleep(DELAY_MAX * attempt)

    return None


def scrape_target(
    session: requests.Session,
    target: ScrapeTarget,
    per_class: int,
    output_dir: Path,
    reference_dirs: list[Path],
    scroll_rounds: int,
    download_width: int,
    duplicate_threshold: int,
    headless: bool,
) -> None:
    class_folder = output_dir / safe_class_name(target.class_name)
    class_folder.mkdir(parents=True, exist_ok=True)

    existing_files = [path for path in class_folder.glob("*") if path.is_file()]
    downloaded = len(existing_files)
    byte_hashes, visual_hashes = existing_fingerprints([class_folder, *reference_dirs])
    seen_photo_ids: set[str] = set()

    print(f"\n[{target.class_name}]")
    print(f"  URL       : {target.search_url}")
    print(f"  Folder    : {class_folder}")
    print(f"  Resume    : {downloaded}/{per_class}")
    print(f"  Ref dedup : {len(reference_dirs)} folder")

    if downloaded >= per_class:
        print("  [OK] Target sudah terpenuhi, skip.")
        return

    print("  Mode browser Selenium...")
    candidates = collect_from_selenium(
        search_url=target.search_url,
        scroll_rounds=scroll_rounds,
        download_width=download_width,
        headless=headless,
    )
    print(f"  Total kandidat unik berdasarkan photo ID: {len(candidates)}")

    failed = 0
    skipped_duplicate = 0
    for candidate in candidates:
        if downloaded >= per_class:
            break
        if candidate.photo_id in seen_photo_ids:
            skipped_duplicate += 1
            continue
        seen_photo_ids.add(candidate.photo_id)

        result = download_image(session, candidate.url)
        if not result:
            failed += 1
            continue

        content, extension, visual_hash = result
        content_hash = image_hash(content)
        if content_hash in byte_hashes or is_visual_duplicate(
            visual_hash, visual_hashes, threshold=duplicate_threshold
        ):
            skipped_duplicate += 1
            continue

        downloaded += 1
        byte_hashes.add(content_hash)
        visual_hashes.add(visual_hash)
        filename = f"{safe_class_name(target.class_name)}_{downloaded:03d}.{extension}"
        (class_folder / filename).write_bytes(content)
        print(f"    [{downloaded}/{per_class}] {filename} [OK] photo_id={candidate.photo_id}")
        delay_random()

    print(f"  Selesai: total={downloaded}, gagal={failed}, duplikat_skip={skipped_duplicate}")


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


def parse_reference_dirs(values: list[str] | None) -> list[Path]:
    if not values:
        return []
    return [Path(value) for value in values if value.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Download gambar dari Pexels search URL.")
    parser.add_argument("--per-class", type=int, default=200, help="Jumlah gambar per class.")
    parser.add_argument("--output", type=str, default=str(DEFAULT_OUTPUT_DIR), help="Folder output.")
    parser.add_argument(
        "--scroll-rounds",
        type=int,
        default=16,
        help="Jumlah scroll saat memakai Selenium.",
    )
    parser.add_argument(
        "--download-width",
        type=int,
        default=1200,
        help="Lebar gambar yang diminta dari Pexels.",
    )
    parser.add_argument(
        "--duplicate-threshold",
        type=int,
        default=4,
        help="Ambang hamming distance dHash. Kecilkan jika terlalu banyak gambar dianggap duplikat.",
    )
    parser.add_argument(
        "--show-browser",
        action="store_true",
        help="Tampilkan browser Selenium, berguna kalau Pexels meminta verifikasi.",
    )
    parser.add_argument(
        "--targets",
        type=str,
        default=None,
        help="Format custom: class_name=url,class_name=url",
    )
    parser.add_argument(
        "--reference-dir",
        action="append",
        default=[],
        help="Folder tambahan untuk dedup visual terhadap dataset lama. Bisa dipakai berulang.",
    )

    args = parser.parse_args()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    targets = parse_targets(args.targets)
    reference_dirs = parse_reference_dirs(args.reference_dir)
    session = get_session()

    print("=" * 70)
    print("SCRAPER PEXELS IMAGES")
    print(f"Target class : {len(targets)}")
    print(f"Per class    : {args.per_class}")
    print(f"Output       : {output_dir}")
    print("=" * 70)

    for target in targets:
        scrape_target(
            session=session,
            target=target,
            per_class=args.per_class,
            output_dir=output_dir,
            reference_dirs=reference_dirs,
            scroll_rounds=args.scroll_rounds,
            download_width=args.download_width,
            duplicate_threshold=args.duplicate_threshold,
            headless=not args.show_browser,
        )

    print("\nSelesai.")


if __name__ == "__main__":
    main()
