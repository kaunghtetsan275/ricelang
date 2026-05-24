# Reproduce the detector

The bundled `pdsdetect.ftz` is a fastText supervised classifier trained on
~787k examples across 25 labels. The full reproduction takes ~3 minutes on
a modern laptop and requires the corpus repo.

## 1. Get the corpus

The training data lives in a separate GitHub repo so the main package stays
small.

```sh
# at the same level as ricelang/
git clone git@github.com:kaunghtetsan275/corpus.git
```

The corpus has ~13 fastText-format text files, one per language source. See
[Corpus layout](corpus.md) for the file naming convention.

## 2. Build the training set

```sh
cd ricelang
uv run python scripts/build_corpus.py \
    --corpus ../corpus/data \
    --out data
```

This reads every `*.txt` in the corpus dir, synthesizes a `zgi` (Zawgyi)
class by running `cvt2zg` over the `mya` examples, applies short-prefix
augmentation, caps each label at 40k examples for balance, and writes:

- `data/train.txt` — fastText-format training set
- `data/valid.txt` — held-out validation (10%)

Knobs:

| Flag | Default | Effect |
|---|---|---|
| `--cap-per-label N` | 40000 | Subsample any label that exceeds N |
| `--no-short-augment` | (off) | Disable short-prefix augmentation |
| `--augment-lengths L L L` | 10 20 40 | Prefix character lengths to emit |
| `--no-synthesize-zg` | (off) | Skip `mya` → `zgi` synthesis |
| `--zg-ratio R` | 1.0 | Fraction of `mya` to convert (1.0 = match `mya` count) |
| `--valid-fraction F` | 0.1 | Held-out split size |

## 3. Train the detector

```sh
uv run python scripts/train_detector.py \
    --train-file data/train.txt \
    --valid-file data/valid.txt \
    --output ricelang/model/pdsdetect.ftz \
    --epoch 25 --lr 0.5 --dim 16 --word-ngrams 1 \
    --minn 2 --maxn 5 --quantize-cutoff 100000
```

What matters here:

- `--minn 2 --maxn 5` — **character n-grams**. Without these, fastText
  tokenizes on whitespace, which means Burmese text becomes one giant
  "word" and the model can't learn anything.
- `--word-ngrams 1` — no word n-grams (they don't help for scripts without
  whitespace).
- `--dim 16` — small embeddings; the task is simple enough that bigger
  hurts more than it helps.
- `--quantize-cutoff 100000` — keep the model under 2 MB.

Training prints per-label accuracy on the validation set at the end.

## 4. Verify

```sh
uv run pytest -q
```

The smoke tests will exercise the new model file in place.

## Train on your own data

`scripts/train_detector.py` can also take a directory tree of per-language
`.txt` files:

```sh
uv run python scripts/train_detector.py \
    --train-dir data/raw \
    --valid-dir data/raw_valid \
    --output ricelang/model/pdsdetect.ftz \
    --epoch 25
```

Expected layout:

```
data/raw/
  mya/        ← Unicode Burmese .txt files (one example per line)
  ksw/        ← S'gaw Karen
  cnh/        ← Hakha Chin
  ...
```

See `scripts/train_detector.py --help` for the full list of fastText flags
exposed.
