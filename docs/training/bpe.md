# Reproduce the BPE tokenizers

The bundled BPE models live in `ricelang/model/bpe_*.json`. There are 24
per-language tokenizers (16k vocab each, ~1 MB each) plus one multilingual
model (`bpe_multi.json`, 32k vocab, ~2 MB).

## Retrain all

```sh
uv run python scripts/train_bpe.py --all
```

This trains every per-language BPE (using corpus files matching
`<lang>_*.txt`) plus the multilingual one (trained on every `*.txt`).
Takes ~5 minutes total.

## Retrain one

```sh
# Per-language: globs <lang>_*.txt in the corpus dir
uv run python scripts/train_bpe.py --lang mya

# Multilingual: trains on every *.txt
uv run python scripts/train_bpe.py --lang multi
```

## What the pre-tokenizer does

For Burmese / Karen / Khmer / Thai / Lao / CJK, BPE training has a
chicken-and-egg problem: the script has no whitespace, so the whole
sentence becomes one giant "word" before BPE even sees it.

ricelang's pre-tokenizer splits on two boundaries:

1. **Whitespace** — for languages that actually use it (English, Latin
   Karen/Chin variants, Vietnamese, Tagalog, etc.).
2. **Script transitions** — `(?<=[<Asian-script>])(?=[A-Za-z0-9])` and the
   reverse. This isolates loanwords. `Pathian` and `ဖေဖေ` end up in
   separate pre-tokens.

The supported Asian-script ranges include Devanagari, Tamil, Thai, Lao,
Myanmar, Khmer, CJK, and Kayah Li.

## Tuning knobs

| Flag | Default | Effect |
|---|---|---|
| `--vocab-size` | 16000 | Vocabulary size for per-language BPEs |
| `--multi-vocab-size` | 32000 | Vocabulary size for the multilingual BPE |
| `--min-frequency` | 2 | Minimum count for a merge to be added |
| `--corpus DIR` | `../corpus/data` | Where to read `*.txt` from |
| `--out-dir DIR` | `ricelang/model` | Where to write `bpe_*.json` |

Tiny corpora (e.g. `kvq` Geba Karen at 8k verses) will naturally plateau
below the target vocab. That's fine.

## Add a new BPE

To add a BPE for a language not currently in `LANGS`, edit
`scripts/train_bpe.py`:

```python
LANGS = [
    ..., "shn",
    "your_lang",   # add here
]
```

Then drop a `your_lang_youversion.txt` (or whatever source) into the
corpus dir and run `--lang your_lang`. The new BPE auto-bundles into
wheels via the `[tool.hatch.build.targets.wheel.force-include]` block in
`pyproject.toml` once you add the entry there too.
