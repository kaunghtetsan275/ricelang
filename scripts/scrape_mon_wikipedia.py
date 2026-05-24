"""Download Mon Wikipedia and extract one paragraph per line.

Mon (mnw) has no YouVersion Bible, but the Mon Wikipedia has ~3,700
content articles available as a CC-BY-SA dump from Wikimedia.

Pipeline:
    1. Download mnwwiki-latest-pages-articles.xml.bz2 from Wikimedia.
    2. Stream-parse the XML, run each ``<text>`` through mwparserfromhell
       to strip wiki markup down to plain Mon text.
    3. Split into paragraphs, trim, write each as ``__label__mnw <text>``.

We use mwparserfromhell rather than wikiextractor because the latter has
a Python 3.12 regex incompatibility (``global flags not at the start``).

Usage::

    uv run python scripts/scrape_mon_wikipedia.py \\
        --out ../corpus/data/mnw_wikipedia.txt
"""

from __future__ import annotations

import argparse
import bz2
import re
import sys
import tempfile
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import mwparserfromhell

DUMP_URL = "https://dumps.wikimedia.org/mnwwiki/latest/mnwwiki-latest-pages-articles.xml.bz2"
LABEL = "mnw"
MIN_LEN = 20
# MediaWiki XML uses an xmlns prefix; the local-name we want is "page".
NS = "{http://www.mediawiki.org/xml/export-0.11/}"

# Drop pages whose title prefix marks them as non-article (talk, files, etc.)
_NON_ARTICLE_PREFIXES = (
    "ဆွေးနွေး:", "ဝီကီပိဒိယာ:", "ဖိုင်:", "မီဒီယာဝီကီ:", "နမူနာ:", "အသုံးပြုသူ:",
    "ဂမျိုၚ်:", "ဝီကီပီဒိယာ:",  # alt mnw forms
    "Talk:", "Wikipedia:", "File:", "MediaWiki:", "Template:", "User:",
    "Category:", "Help:", "Portal:",
)


def download(url: str, dest: Path) -> None:
    print(f"[download] {url}")
    with urllib.request.urlopen(url) as resp, dest.open("wb") as out:
        n = 0
        while True:
            buf = resp.read(1 << 16)
            if not buf:
                break
            out.write(buf)
            n += len(buf)
    print(f"[download] {n:,} bytes -> {dest}")


def iter_pages(dump_path: Path):
    """Yield (title, wikitext) per <page>. Streams the bz2 XML."""
    with bz2.open(dump_path, "rb") as fh:
        for _event, elem in ET.iterparse(fh, events=("end",)):
            if elem.tag != f"{NS}page":
                continue
            title = (elem.findtext(f"{NS}title") or "").strip()
            text_el = elem.find(f"{NS}revision/{NS}text")
            text = (text_el.text if text_el is not None else "") or ""
            yield title, text
            elem.clear()  # free memory


def strip_to_plain(wikitext: str) -> str:
    """Wikitext -> plain text. Drops templates, refs, files, headings."""
    code = mwparserfromhell.parse(wikitext)
    # strip_code drops templates, html comments, link targets, etc.
    plain = code.strip_code(normalize=True, collapse=True)
    # Remove leftover heading marks and excessive whitespace.
    plain = re.sub(r"^\s*=+.*?=+\s*$", "", plain, flags=re.MULTILINE)
    return plain


def write_fasttext(dump_path: Path, out_path: Path) -> tuple[int, int]:
    n_articles = 0
    n_lines = 0
    with out_path.open("w", encoding="utf-8") as out:
        for title, wikitext in iter_pages(dump_path):
            if not wikitext or any(title.startswith(p) for p in _NON_ARTICLE_PREFIXES):
                continue
            # Redirect pages are short and just contain #REDIRECT [[Target]]
            if wikitext.lstrip().lower().startswith(("#redirect", "#ပြန်ညွှန်း")):
                continue
            try:
                plain = strip_to_plain(wikitext)
            except Exception:  # mwparserfromhell can choke on malformed pages
                continue
            n_articles += 1
            for para in plain.split("\n"):
                para = " ".join(para.split())
                if len(para) < MIN_LEN or para.isascii():
                    continue
                out.write(f"__label__{LABEL} {para}\n")
                n_lines += 1
    return n_articles, n_lines


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", required=True, help="output .txt path (fastText format)")
    p.add_argument("--dump", help="path to an existing local dump (skips download)")
    args = p.parse_args(argv)

    out_path = Path(args.out).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory(prefix="mnw_wiki_") as tmp:
        dump_path = Path(args.dump) if args.dump else Path(tmp) / "mnwwiki.xml.bz2"
        if not args.dump:
            download(DUMP_URL, dump_path)

        print(f"[extract] parsing {dump_path.name}...")
        n_articles, n_lines = write_fasttext(dump_path, out_path)
        print(f"[done] {n_articles:,} articles -> {n_lines:,} paragraphs -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
