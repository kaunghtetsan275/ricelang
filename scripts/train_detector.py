"""Train the ricelang language-detection model.

Trains a fastText supervised classifier, evaluates it (optional), and saves
a quantized ``.ftz`` model ready to drop into ``ricelang/model/``.

Two ways to supply data:

1.  ``--train-file path/to/train.txt`` — already in fastText format, one
    example per line: ``__label__<lang> <text>``. Lines must not contain
    embedded newlines.

2.  ``--train-dir path/to/dir`` — a directory of per-language subdirectories,
    each containing ``.txt`` files where every line is one example. Labels
    are taken from the subdirectory names. The script converts this into
    a temporary fastText file before training. Example layout::

        train-dir/
          uni/burmese_news_2024.txt
          zg/burmese_blogs_2020.txt
          karen/karen_bible.txt

Usage::

    uv run python scripts/train_detector.py \\
        --train-dir data/train \\
        --valid-dir data/valid \\
        --output ricelang/model/pdsdetect.ftz
"""

from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

import fasttext

LABEL_PREFIX = "__label__"


def _iter_examples(directory: Path):
    """Yield ``(label, text)`` pairs from a directory tree of per-lang subdirs."""
    if not directory.is_dir():
        raise FileNotFoundError(f"not a directory: {directory}")
    found_any = False
    for lang_dir in sorted(p for p in directory.iterdir() if p.is_dir()):
        label = lang_dir.name
        for txt in sorted(lang_dir.rglob("*.txt")):
            with txt.open(encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    found_any = True
                    yield label, line
    if not found_any:
        raise ValueError(f"no .txt examples found under {directory}")


def _dir_to_fasttext_file(directory: Path, out_path: Path) -> int:
    """Materialize a per-lang directory into a fastText-format file. Returns line count."""
    n = 0
    with out_path.open("w", encoding="utf-8") as out:
        for label, text in _iter_examples(directory):
            # Collapse any embedded whitespace runs so each example fits on one line.
            text = " ".join(text.split())
            out.write(f"{LABEL_PREFIX}{label} {text}\n")
            n += 1
    return n


def _resolve_train_path(args, stack: list[Path]) -> Path:
    if args.train_file:
        return Path(args.train_file)
    tmp = Path(tempfile.mkstemp(prefix="pds_train_", suffix=".txt")[1])
    stack.append(tmp)
    n = _dir_to_fasttext_file(Path(args.train_dir), tmp)
    print(f"[train] wrote {n:,} examples from {args.train_dir} -> {tmp}")
    return tmp


def _resolve_valid_path(args, stack: list[Path]) -> Path | None:
    if args.valid_file:
        return Path(args.valid_file)
    if args.valid_dir:
        tmp = Path(tempfile.mkstemp(prefix="pds_valid_", suffix=".txt")[1])
        stack.append(tmp)
        n = _dir_to_fasttext_file(Path(args.valid_dir), tmp)
        print(f"[valid] wrote {n:,} examples from {args.valid_dir} -> {tmp}")
        return tmp
    return None


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--train-file", help="fastText-format training file (__label__lang text per line)")
    src.add_argument("--train-dir", help="directory tree of per-language subdirs")
    p.add_argument("--valid-file", help="optional fastText-format validation file")
    p.add_argument("--valid-dir", help="optional directory tree for validation")
    p.add_argument("--output", required=True, help="path to write the quantized .ftz model")
    p.add_argument("--epoch", type=int, default=25)
    p.add_argument("--lr", type=float, default=1.0)
    p.add_argument("--dim", type=int, default=16)
    p.add_argument("--word-ngrams", type=int, default=2)
    p.add_argument("--min-count", type=int, default=1)
    p.add_argument("--minn", type=int, default=2,
                   help="min char n-gram length (subword features); essential for whitespace-poor scripts")
    p.add_argument("--maxn", type=int, default=5, help="max char n-gram length")
    p.add_argument("--loss", default="softmax", choices=["softmax", "ns", "hs", "ova"])
    p.add_argument("--quantize-cutoff", type=int, default=50_000,
                   help="vocab cutoff during quantization; lower = smaller model (default 50000)")
    p.add_argument("--no-quantize", action="store_true", help="save full .bin instead of quantized .ftz")
    args = p.parse_args(argv)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    cleanup: list[Path] = []
    try:
        train_path = _resolve_train_path(args, cleanup)
        valid_path = _resolve_valid_path(args, cleanup)

        print(f"[train] fastText supervised: epoch={args.epoch} lr={args.lr} "
              f"dim={args.dim} wordNgrams={args.word_ngrams} loss={args.loss}")
        model = fasttext.train_supervised(
            input=str(train_path),
            epoch=args.epoch,
            lr=args.lr,
            dim=args.dim,
            wordNgrams=args.word_ngrams,
            minCount=args.min_count,
            loss=args.loss,
            minn=args.minn,
            maxn=args.maxn,
        )
        print(f"[train] labels: {sorted(l[len(LABEL_PREFIX):] for l in model.get_labels())}")

        if valid_path is not None:
            n, p_at_1, r_at_1 = model.test(str(valid_path))
            print(f"[eval] N={n}  P@1={p_at_1:.4f}  R@1={r_at_1:.4f}")
            # Per-label confusion summary so class imbalance is visible.
            per_label: dict[str, list[int]] = {}
            with open(valid_path, encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line:
                        continue
                    true_label, _, text = line.partition(" ")
                    true_label = true_label[len(LABEL_PREFIX):]
                    pred = model.predict(text)[0][0][len(LABEL_PREFIX):]
                    bucket = per_label.setdefault(true_label, [0, 0])
                    bucket[0] += 1
                    if pred == true_label:
                        bucket[1] += 1
            print("[eval] per-label accuracy:")
            for label in sorted(per_label):
                total, correct = per_label[label]
                print(f"         {label:6s}  {correct:>5d}/{total:<5d}  {correct/total*100:5.1f}%")

        if args.no_quantize:
            model.save_model(str(output))
            print(f"[save] wrote unquantized model to {output} ({output.stat().st_size:,} bytes)")
        else:
            # Quantize so we ship a small .ftz like the bundled one (~1.2 MB).
            model.quantize(input=str(train_path), retrain=True,
                           cutoff=args.quantize_cutoff, qnorm=True)
            model.save_model(str(output))
            print(f"[save] wrote quantized model to {output} ({output.stat().st_size:,} bytes)")
    finally:
        for path in cleanup:
            path.unlink(missing_ok=True)

    return 0


if __name__ == "__main__":
    sys.exit(main())
