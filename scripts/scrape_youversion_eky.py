"""Scrape Eastern Kayah Shadaw Dialect NT (+ Genesis) from YouVersion.

YouVersion version 3649 (``eky-Kali-MM``, published by The Seed Company) is
the only sizable freely-readable Eastern Kayah text on the open web.
The pages are server-rendered HTML with ``data-usfm`` verse markers, so we
can extract one verse per line without JavaScript execution.

Note: the text is copyright by Christian Far East Ministry; this is a
research-use scrape only, mirroring how the existing ``jsw_*.txt`` files in
the corpus repo were sourced.

Usage::

    uv run python scripts/scrape_youversion_eky.py \\
        --out ../corpus/data/eky_youversion.txt
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

VERSION_ID = 3649
BASE = f"https://www.bible.com/bible/{VERSION_ID}"
USER_AGENT = "Mozilla/5.0 (research scraping; pyidaungsu corpus build)"

# Chapter counts for the books we expect this translation to include
# (NT plus Genesis per the YouVersion listing). We iterate optimistically
# and skip any book/chapter that 404s, so over-listing is harmless.
BOOKS: dict[str, int] = {
    "GEN": 50,
    "MAT": 28, "MRK": 16, "LUK": 24, "JHN": 21, "ACT": 28,
    "ROM": 16, "1CO": 16, "2CO": 13, "GAL": 6, "EPH": 6,
    "PHP": 4, "COL": 4, "1TH": 5, "2TH": 3, "1TI": 6,
    "2TI": 4, "TIT": 3, "PHM": 1, "HEB": 13, "JAS": 5,
    "1PE": 5, "2PE": 3, "1JN": 5, "2JN": 1, "3JN": 1,
    "JUD": 1, "REV": 22,
}


def fetch(session: requests.Session, book: str, chapter: int) -> str | None:
    url = f"{BASE}/{book}.{chapter}"
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
    p.add_argument("--out", required=True, help="output .txt path (fastText format, __label__eky per line)")
    p.add_argument("--label", default="eky", help="label to prefix each verse with (default: eky)")
    p.add_argument("--sleep", type=float, default=0.5, help="seconds between requests (be polite)")
    p.add_argument("--books", nargs="*", help="restrict to these book codes (default: all NT + GEN)")
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
                html = fetch(session, book, ch)
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
