# Corpus layout

The training corpus lives in a separate repo:
[`kaunghtetsan275/corpus`](https://github.com/kaunghtetsan275/corpus).

## File naming convention

Every file under `corpus/data/` follows:

```
<iso-639-3>_<source>.txt
```

For example:

| File | Language | Source |
|---|---|---|
| `mya_jsw.txt` | Burmese | JW.org |
| `mya_mmtimes.txt` | Burmese | Myanmar Times (xlsx export → txt) |
| `cnh_jsw.txt` | Hakha Chin | JW.org |
| `cnh_youversion.txt` | Hakha Chin | YouVersion Bible v327 |
| `mnw_wikipedia.txt` | Mon | Mon Wikipedia dump |
| `eng_youversion.txt` | English | YouVersion KJV (v1) |

The Burmese files are tagged `mya` even though the detector emits `mya`
(Unicode) and `zgi` (Zawgyi) labels — `zgi` is synthesized at
corpus-build time by running `cvt2zg` over the `mya` text.

## File contents

Every file is in **fastText supervised format**:

```
__label__<iso>  one example per line
__label__<iso>  another example
```

The build script (`scripts/build_corpus.py`) reads every `*.txt`, applies
short-prefix augmentation, caps each label, and emits `data/train.txt`
and `data/valid.txt`.

## Data sources used

| Source | Languages |
|---|---|
| **YouVersion** Bible scrapes | most labels — see `scripts/scrape_youversion.py` |
| **JW.org** scrapes (legacy) | `mya`, `ksw`, `cnh` — inherited from pyidaungsu |
| **Mon Wikipedia** dump | `mnw` (no YouVersion Bible exists) |
| **Myanmar Times** xlsx export | `mya` (non-Bible Burmese register) |
| **shannews.org** xlsx export | `shn` (Shan news) |
| **Werribee Karen Bible** | `ksw` |
| **Kayah Li** (origin unknown) | small `eky` sample |

## Adding a new source

1. Get the text into fastText format:
   ```
   __label__xxx  example 1
   __label__xxx  example 2
   ```
2. Save as `corpus/data/<iso>_<source>.txt`.
3. Run `uv run python scripts/build_corpus.py` to rebuild the
   training/validation split.
4. Run `uv run python scripts/train_detector.py ...` to retrain.

The corpus build script auto-discovers any `*.txt` in the directory — no
list to update.

## Scraping YouVersion

For languages with a YouVersion Bible, the scraper handles the rest:

```sh
uv run python scripts/scrape_youversion.py \
    --version 327 --label cnh \
    --out ../corpus/data/cnh_youversion.txt \
    --sleep 0.4
```

The script walks every chapter of every book (standard Protestant canon),
extracts verses from `data-usfm` markers in the chapter HTML, and writes
fastText-format output. `--sleep 0.4` is the polite delay between
requests.

To find a version's numeric ID: visit `bible.com/languages/<iso>`, click
through to a chapter, and grab the number from the URL
(`bible.com/bible/<ID>/MAT.1`).
