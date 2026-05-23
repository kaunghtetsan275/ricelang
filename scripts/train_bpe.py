"""Train a Byte-Pair Encoding (BPE) tokenizer on Burmese text.

Reads all ``mya_*.txt`` files from the corpus directory, trains a BPE
tokenizer with the HuggingFace ``tokenizers`` library, and saves the
resulting tokenizer to ``pyidaungsu/model/bpe.json``.

Usage::

    uv run python scripts/train_bpe.py \\
        --corpus ../corpus/data \\
        --output pyidaungsu/model/bpe.json \\
        --vocab-size 16000
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tokenizers import Regex, Tokenizer, models, pre_tokenizers, trainers


def _iter_texts(corpus_dir: Path, glob: str):
    """Yield one text per training example (label stripped)."""
    for path in sorted(corpus_dir.glob(glob)):
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if not line.startswith("__label__"):
                    continue
                _, _, text = line.partition(" ")
                if text:
                    yield text


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--corpus", default="../corpus/data",
                   help="corpus directory (default: ../corpus/data)")
    p.add_argument("--glob", default="mya_*.txt",
                   help="glob pattern for training files (default: mya_*.txt)")
    p.add_argument("--output", default="pyidaungsu/model/bpe.json",
                   help="path to write the tokenizer JSON (default: pyidaungsu/model/bpe.json)")
    p.add_argument("--vocab-size", type=int, default=16000)
    p.add_argument("--min-frequency", type=int, default=2)
    args = p.parse_args(argv)

    corpus_dir = Path(args.corpus).resolve()
    out_path = Path(args.output).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    files = sorted(str(p) for p in corpus_dir.glob(args.glob))
    if not files:
        print(f"[error] no files matching {args.glob!r} in {corpus_dir}", file=sys.stderr)
        return 2
    print(f"[bpe] training on {len(files)} file(s):")
    for f in files:
        print(f"  {f}")

    tokenizer = Tokenizer(models.BPE(unk_token="<unk>"))
    # Burmese has no whitespace word boundaries. Split only on whitespace
    # and on transitions between Burmese and ASCII so each "word" the
    # trainer sees is a coherent unit. Operate on raw Unicode characters
    # (not bytes) so the resulting subword tokens are human-readable.
    tokenizer.pre_tokenizer = pre_tokenizers.Sequence([
        pre_tokenizers.Whitespace(),
        pre_tokenizers.Split(pattern=Regex(r"(?<=[က-႟])(?=[A-Za-z0-9])|(?<=[A-Za-z0-9])(?=[က-႟])"),
                             behavior="isolated"),
    ])

    trainer = trainers.BpeTrainer(
        vocab_size=args.vocab_size,
        min_frequency=args.min_frequency,
        special_tokens=["<pad>", "<unk>", "<s>", "</s>"],
        show_progress=True,
    )

    # Stream lines from the labeled files so we don't materialize the
    # whole corpus in memory.
    def iterator():
        yield from _iter_texts(corpus_dir, args.glob)

    tokenizer.train_from_iterator(iterator(), trainer=trainer)
    tokenizer.save(str(out_path))
    print(f"\n[bpe] vocab size: {tokenizer.get_vocab_size():,}")
    print(f"[bpe] saved -> {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
