"""Train per-language or multilingual BPE tokenizer(s).

Reads corpus files from the corpus directory, trains a BPE tokenizer
with the HuggingFace ``tokenizers`` library, and saves the resulting
tokenizer to ``ricelang/model/bpe_<lang>.json``.

Usage::

    # one per-language BPE (globs <lang>_*.txt in the corpus dir)
    uv run python scripts/train_bpe.py --lang mya
    uv run python scripts/train_bpe.py --lang ksw

    # multilingual BPE over every *.txt
    uv run python scripts/train_bpe.py --lang multi

    # train one BPE per language plus the multilingual one
    uv run python scripts/train_bpe.py --all
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tokenizers import Regex, Tokenizer, models, pre_tokenizers, trainers

# Languages we maintain corpus files for. Zawgyi (zgi) is synthesized from
# mya at corpus-build time and isn't a separate input "language" for BPE.
LANGS = ["cfm", "cnh", "ctd", "eky", "ksw", "kvq", "mya", "pwo", "shn"]


def _resolve_files(corpus_dir: Path, lang: str) -> list[Path]:
    if lang == "multi":
        return sorted(corpus_dir.glob("*.txt"))
    return sorted(corpus_dir.glob(f"{lang}_*.txt"))


def _iter_texts(files: list[Path]):
    """Yield one text per labeled line, stripping the __label__ prefix."""
    for path in files:
        with path.open(encoding="utf-8") as fh:
            for line in fh:
                line = line.rstrip("\n")
                if not line.startswith("__label__"):
                    continue
                _, _, text = line.partition(" ")
                if text:
                    yield text


def train_one(corpus_dir: Path, lang: str, out_dir: Path,
              vocab_size: int, min_frequency: int) -> Path | None:
    files = _resolve_files(corpus_dir, lang)
    if not files:
        print(f"[skip {lang}] no matching corpus files", file=sys.stderr)
        return None

    out_path = out_dir / f"bpe_{lang}.json"
    print(f"\n[bpe {lang}] training on {len(files)} file(s) -> {out_path.name}")

    tokenizer = Tokenizer(models.BPE(unk_token="<unk>"))
    # One pre-tokenizer for every language: whitespace + a script-boundary
    # split that fires only when text transitions between a SE Asian script
    # (Myanmar block + Kayah Li block) and ASCII. For pure-Latin scripts
    # (cnh/cfm/ctd) the boundary rule never fires, so only whitespace
    # splitting applies. For Burmese/Karen/Kayah it isolates loanwords.
    tokenizer.pre_tokenizer = pre_tokenizers.Sequence([
        pre_tokenizers.Whitespace(),
        pre_tokenizers.Split(
            pattern=Regex(
                r"(?<=[က-႟꤀-꤯])(?=[A-Za-z0-9])"
                r"|(?<=[A-Za-z0-9])(?=[က-႟꤀-꤯])"
            ),
            behavior="isolated",
        ),
    ])
    trainer = trainers.BpeTrainer(
        vocab_size=vocab_size,
        min_frequency=min_frequency,
        special_tokens=["<pad>", "<unk>", "<s>", "</s>"],
        show_progress=False,
    )
    tokenizer.train_from_iterator(_iter_texts(files), trainer=trainer)
    tokenizer.save(str(out_path))
    print(f"[bpe {lang}] vocab={tokenizer.get_vocab_size():,}  "
          f"size={out_path.stat().st_size:,} bytes")
    return out_path


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--corpus", default="../corpus/data",
                   help="corpus directory (default: ../corpus/data)")
    p.add_argument("--out-dir", default="ricelang/model",
                   help="directory to write bpe_<lang>.json files (default: ricelang/model)")
    p.add_argument("--lang", help="ISO 639-3 language code, or 'multi' for multilingual")
    p.add_argument("--all", action="store_true",
                   help="train BPE for every supported language plus the multilingual one")
    p.add_argument("--vocab-size", type=int, default=16000)
    p.add_argument("--multi-vocab-size", type=int, default=32000,
                   help="vocab size for the multilingual BPE (default 32000)")
    p.add_argument("--min-frequency", type=int, default=2)
    args = p.parse_args(argv)

    if not args.lang and not args.all:
        p.error("specify --lang <iso> or --all")

    corpus_dir = Path(args.corpus).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.all:
        targets = LANGS + ["multi"]
    else:
        targets = [args.lang]

    for lang in targets:
        vocab = args.multi_vocab_size if lang == "multi" else args.vocab_size
        train_one(corpus_dir, lang, out_dir, vocab, args.min_frequency)

    return 0


if __name__ == "__main__":
    sys.exit(main())
