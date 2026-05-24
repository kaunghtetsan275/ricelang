"""Build a fastText-format training corpus from kaunghtetsan275/corpus.

Consolidates the heterogeneous source files (already-labeled .txt, raw
single-blob .txt, and .xlsx exports) into ``data/train.txt`` and
``data/valid.txt`` ready for ``scripts/train_detector.py``.

Corpus file convention
----------------------
``<iso-639-3>_<source>.<ext>`` — language code prefix, source as postfix.
The Burmese files are tagged ``mya`` even though the model emits ``uni``
(Unicode) vs ``zg`` (Zawgyi) labels; the model's ``zg`` examples are
synthesized at corpus-build time from the ``mya`` Unicode text.

Sources handled
---------------
Every file in the corpus directory is in fastText format
(``__label__X text``). The convention is ``<iso-639-3>_<source>.txt``.
- ``cnh_jsw.txt``       — Hakha Chin (JW.org)
- ``ksw_werribee.txt``  — S'gaw Karen (Werribee Karen Bible)
- ``ksw_jsw.txt``       — S'gaw Karen (JW.org)
- ``eky_kayahli.txt``   — Eastern Kayah (small sample)
- ``eky_youversion.txt``— Eastern Kayah NT (YouVersion 3649)
- ``mya_jsw.txt``       — Burmese Unicode (JW.org)
- ``mya_mmtimes.txt``   — Burmese Unicode (Myanmar Times)
- ``shn_shannews.txt``  — Shan (shannews.org)
- (skipped) Mon         — no data available in this corpus

Optional ``zgi`` synthesis
--------------------------
The detector distinguishes Burmese Unicode (``mya``) from Zawgyi
(``zgi``). The corpus has no Zawgyi text, so by default we synthesize a
matched set by running ``ricelang.cvt2zg`` over every ``mya`` example
(plus a sampled portion to keep classes balanced). Disable with
``--no-synthesize-zg``.
"""

from __future__ import annotations

import argparse
import random
import sys
from pathlib import Path

from ricelang.convert import cvt2zg

LABEL_PREFIX = "__label__"
MIN_LEN = 8  # drop trivially-short fragments


def _clean(text: str) -> str:
    """Collapse whitespace; fastText needs one example per line."""
    return " ".join(text.split())


def _emit(label: str, text: str) -> tuple[str, str] | None:
    text = _clean(text)
    if len(text) < MIN_LEN:
        return None
    return label, text


def _read_labeled_file(path: Path) -> list[tuple[str, str]]:
    """Read a file that's already in fastText format (``__label__x  text``)."""
    out: list[tuple[str, str]] = []
    with path.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line.startswith(LABEL_PREFIX):
                continue
            head, _, text = line.partition("\t")
            if not text:
                head, _, text = line.partition(" ")
            label = head[len(LABEL_PREFIX):]
            example = _emit(label, text)
            if example:
                out.append(example)
    return out


def collect(corpus_dir: Path, synthesize_zg: bool, zg_ratio: float) -> list[tuple[str, str]]:
    examples: list[tuple[str, str]] = []

    # Read every <lang>_<source>.txt file in the corpus directory.
    # Filename language code matches the label (e.g. mya_*.txt ->
    # __label__mya). The zgi label (Zawgyi-encoded Burmese) is synthesized
    # from mya text below since the corpus has no native Zawgyi data.
    for path in sorted(corpus_dir.glob("*.txt")):
        examples += _read_labeled_file(path)

    if synthesize_zg:
        mya_examples = [t for lbl, t in examples if lbl == "mya"]
        # Sample to control class balance; default 1.0 = match mya count.
        target_n = int(len(mya_examples) * zg_ratio)
        sampled = random.sample(mya_examples, min(target_n, len(mya_examples)))
        for text in sampled:
            zg = cvt2zg(text)
            if zg and zg != text:
                examples.append(("zgi", zg))

    return examples


def cap_per_label(examples: list[tuple[str, str]], cap: int) -> list[tuple[str, str]]:
    """Subsample any label that exceeds ``cap``. Keeps the class distribution
    closer to balanced so over-represented sources (e.g. the 135k-paragraph
    Mon Wikipedia) don't bias the model toward predicting them by default
    on short or ambiguous input."""
    by_label: dict[str, list[tuple[str, str]]] = {}
    for ex in examples:
        by_label.setdefault(ex[0], []).append(ex)
    out: list[tuple[str, str]] = []
    for label, exs in by_label.items():
        if len(exs) > cap:
            out += random.sample(exs, cap)
        else:
            out += exs
    return out


def write_fasttext(path: Path, examples: list[tuple[str, str]]) -> None:
    with path.open("w", encoding="utf-8") as fh:
        for label, text in examples:
            fh.write(f"{LABEL_PREFIX}{label} {text}\n")


def summarize(examples: list[tuple[str, str]]) -> str:
    counts: dict[str, int] = {}
    for label, _ in examples:
        counts[label] = counts.get(label, 0) + 1
    width = max(len(l) for l in counts)
    lines = [f"  {label.ljust(width)}  {n:>7,}" for label, n in sorted(counts.items())]
    lines.append(f"  {'total'.ljust(width)}  {len(examples):>7,}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--corpus", default="../corpus/data",
                   help="path to corpus data directory (default: ../corpus/data)")
    p.add_argument("--out", default="data", help="output directory (default: data/)")
    p.add_argument("--valid-fraction", type=float, default=0.1)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--no-synthesize-zg", dest="synthesize_zg", action="store_false",
                   help="don't synthesize zg examples from uni text via cvt2zg")
    p.add_argument("--zg-ratio", type=float, default=1.0,
                   help="number of synthetic zg examples relative to uni count (default 1.0)")
    p.add_argument("--no-short-augment", dest="short_augment", action="store_false",
                   help="don't augment training set with truncated copies of each example")
    p.add_argument("--augment-lengths", type=int, nargs="+", default=[10, 20, 40],
                   help="character lengths to truncate to (default: 10 20 40)")
    p.add_argument("--cap-per-label", type=int, default=40_000,
                   help="subsample any label with more than this many examples "
                        "(default 40_000; 0 = no cap)")
    args = p.parse_args(argv)

    random.seed(args.seed)
    corpus_dir = Path(args.corpus).resolve()
    out_dir = Path(args.out).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"[corpus] reading from {corpus_dir}")
    examples = collect(corpus_dir, args.synthesize_zg, args.zg_ratio)
    print(f"[corpus] collected:")
    print(summarize(examples))

    if args.cap_per_label:
        examples = cap_per_label(examples, args.cap_per_label)
        print(f"[cap] subsampled each over-represented label to {args.cap_per_label:,}:")
        print(summarize(examples))

    random.shuffle(examples)
    split = int(len(examples) * (1 - args.valid_fraction))
    train, valid = examples[:split], examples[split:]

    # Short-snippet augmentation: for each training example, also emit
    # truncated copies so the model learns that short prefixes carry the
    # signal too. Validation set is left untouched so we keep measuring
    # full-length accuracy. Only applied to training.
    if args.short_augment:
        augmented = []
        for label, text in train:
            augmented.append((label, text))
            for cap in args.augment_lengths:
                if len(text) > cap:
                    augmented.append((label, text[:cap]))
        train = augmented
        random.shuffle(train)
        print(f"[augment] short-snippet augmentation produced {len(train):,} training lines "
              f"(was {split:,})")

    train_path = out_dir / "train.txt"
    valid_path = out_dir / "valid.txt"
    write_fasttext(train_path, train)
    write_fasttext(valid_path, valid)
    print(f"[write] train -> {train_path}  ({len(train):,} lines)")
    print(f"[write] valid -> {valid_path}  ({len(valid):,} lines)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
