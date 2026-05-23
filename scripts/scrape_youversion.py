"""Scrape a YouVersion Bible into fastText format.

Pages are server-rendered HTML with verse text inside the ``__NEXT_DATA__``
JSON blob at ``props.pageProps.chapterInfo.content``. Each verse carries a
``data-usfm`` attribute, so we extract one verse per line without
JavaScript execution.

Note: Bible translations on YouVersion are copyright their publishers
(Seed Company, Bible Society of Myanmar, etc.). This script is for
research use only, mirroring how the existing ``*_jsw.txt`` files in
the corpus repo were sourced.

Usage::

    # Eastern Kayah NT (Seed Company, version 3649)
    uv run python scripts/scrape_youversion.py \\
        --version 3649 --label eky \\
        --out ../corpus/data/eky_youversion.txt

    # Hakha Chin full Bible (Bible Society of Myanmar, version 327)
    uv run python scripts/scrape_youversion.py \\
        --version 327 --label cnh \\
        --out ../corpus/data/cnh_youversion.txt
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup

_NEXT_DATA_RE = re.compile(
    r'<script id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.DOTALL
)

USER_AGENT = "Mozilla/5.0 (research scraping; pyidaungsu corpus build)"

# Chapter counts for every standard Protestant Bible book. We iterate
# optimistically and skip any book/chapter the version doesn't include
# (404 or empty chapterInfo), so over-listing is harmless.
BOOKS: dict[str, int] = {
    # Old Testament
    "GEN": 50, "EXO": 40, "LEV": 27, "NUM": 36, "DEU": 34,
    "JOS": 24, "JDG": 21, "RUT": 4,
    "1SA": 31, "2SA": 24, "1KI": 22, "2KI": 25,
    "1CH": 29, "2CH": 36, "EZR": 10, "NEH": 13, "EST": 10,
    "JOB": 42, "PSA": 150, "PRO": 31, "ECC": 12, "SNG": 8,
    "ISA": 66, "JER": 52, "LAM": 5, "EZK": 48, "DAN": 12,
    "HOS": 14, "JOL": 3, "AMO": 9, "OBA": 1, "JON": 4,
    "MIC": 7, "NAM": 3, "HAB": 3, "ZEP": 3, "HAG": 2,
    "ZEC": 14, "MAL": 4,
    # New Testament
    "MAT": 28, "MRK": 16, "LUK": 24, "JHN": 21, "ACT": 28,
    "ROM": 16, "1CO": 16, "2CO": 13, "GAL": 6, "EPH": 6,
    "PHP": 4, "COL": 4, "1TH": 5, "2TH": 3, "1TI": 6,
    "2TI": 4, "TIT": 3, "PHM": 1, "HEB": 13, "JAS": 5,
    "1PE": 5, "2PE": 3, "1JN": 5, "2JN": 1, "3JN": 1,
    "JUD": 1, "REV": 22,
}


def fetch(session: requests.Session, version_id: int, book: str, chapter: int) -> str | None:
    url = f"https://www.bible.com/bible/{version_id}/{book}.{chapter}"
    resp = session.get(url, timeout=20)
    if resp.status_code == 404:
        return None
    resp.raise_for_status()
    return resp.text


def extract_verses(page_html: str, book: str, chapter: int) -> list[tuple[str, str]]:
    """Return ``[(usfm_ref, text), ...]`` from a YouVersion chapter page.

    The verse HTML lives inside ``__NEXT_DATA__`` JSON at
    ``props.pageProps.chapterInfo.content`` rather than the top-level DOM.
    """
    m = _NEXT_DATA_RE.search(page_html)
    if not m:
        return []
    data = json.loads(m.group(1))
    chapter_info = (data.get("props") or {}).get("pageProps", {}).get("chapterInfo") or {}
    content = chapter_info.get("content")
    if not content:
        return []

    soup = BeautifulSoup(content, "html.parser")
    prefix = f"{book}.{chapter}."

    # Each verse: <span class="verse vN" data-usfm="BOOK.CH.V"> ... </span>.
    # The same usfm can appear across multiple spans when a verse spans
    # paragraph breaks — accumulate text per ref.
    by_ref: dict[str, list[str]] = {}
    for span in soup.find_all("span", attrs={"data-usfm": True}):
        if not hasattr(span, "attrs") or span.attrs is None:
            continue
        usfm = span.attrs.get("data-usfm")
        if not usfm or not usfm.startswith(prefix):
            continue
        # Strip the verse-number label and footnote markers.
        for junk in span.find_all(class_=("label", "note")):
            junk.decompose()
        text = " ".join(span.get_text(" ", strip=True).split())
        if text:
            by_ref.setdefault(usfm, []).append(text)

    out: list[tuple[str, str]] = []
    for ref, parts in by_ref.items():
        text = " ".join(parts)
        out.append((ref, text))
    out.sort(key=lambda kv: int(kv[0].rsplit(".", 1)[1]))
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--version", type=int, required=True, help="YouVersion bible version ID (e.g. 327 for Hakha Chin, 3649 for Eastern Kayah)")
    p.add_argument("--label", required=True, help="ISO 639-3 label to prefix each verse with (e.g. cnh, eky)")
    p.add_argument("--out", required=True, help="output .txt path (fastText format, one verse per line)")
    p.add_argument("--sleep", type=float, default=0.4, help="seconds between requests (be polite)")
    p.add_argument("--books", nargs="*", help="restrict to these USFM book codes (default: all OT+NT)")
    args = p.parse_args(argv)

    books = {b: BOOKS[b] for b in args.books} if args.books else BOOKS
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    session = requests.Session()
    session.headers["User-Agent"] = USER_AGENT

    total_verses = 0
    skipped_books: list[str] = []
    with out_path.open("w", encoding="utf-8") as fh:
        for book, n_chapters in books.items():
            book_count = 0
            book_missing = 0
            for ch in range(1, n_chapters + 1):
                html = fetch(session, args.version, book, ch)
                if html is None:
                    book_missing += 1
                    # If the first chapter of a book is missing, the book
                    # isn't in this translation -- skip rest.
                    if ch == 1:
                        skipped_books.append(book)
                        break
                    continue
                verses = extract_verses(html, book, ch)
                for ref, text in verses:
                    fh.write(f"__label__{args.label} {text}\n")
                book_count += len(verses)
                time.sleep(args.sleep)
            if book_count:
                print(f"  {book:4s}  {book_count:>5d} verses"
                      + (f"  ({book_missing} missing chapters)" if book_missing else ""))
            total_verses += book_count

    print(f"\n[done] {total_verses:,} verses -> {out_path}")
    if skipped_books:
        print(f"[note] not in this translation: {', '.join(skipped_books)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
