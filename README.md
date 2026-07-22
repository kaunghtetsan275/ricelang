# ricelang

[![PyPI](https://img.shields.io/pypi/v/ricelang.svg)](https://pypi.org/project/ricelang/)
[![Python](https://img.shields.io/pypi/pyversions/ricelang.svg)](https://pypi.org/project/ricelang/)
[![tests](https://github.com/kaunghtetsan275/ricelang/actions/workflows/test.yml/badge.svg)](https://github.com/kaunghtetsan275/ricelang/actions/workflows/test.yml)
[![publish](https://github.com/kaunghtetsan275/ricelang/actions/workflows/publish.yml/badge.svg)](https://github.com/kaunghtetsan275/ricelang/actions/workflows/publish.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![docs](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://kaunghtetsan275.github.io/ricelang/)

NLP library for Southeast Asian and South Asian languages — language
identification, tokenization, and Zawgyi/Unicode conversion.

📖 **Full documentation:** <https://kaunghtetsan275.github.io/ricelang/>

## Revamped from `pyidaungsu`

This project is a revamp of
[pyidaungsu](https://pypi.org/project/pyidaungsu/):

- **Revamped** as `ricelang` (PyPI + GitHub + import path).
- **25 detectable languages** (was 3): added 22 SE/South Asian
  languages, full ISO 639-3 codes throughout.
- **Better detection model**: fastText with character n-grams, retrained
  on a 787k-example corpus (Bible scrapes + Mon Wikipedia). P@1 = 99.85%.
- **Added BPE tokenizers**: 24 per-language + 1 multilingual, all
  bundled, lazy-loaded.
- **uv-based**: `pyproject.toml`, no more `setup.py`.
- **Demo server**: a `/demo` FastAPI app to try every function in a
  browser (`uv run --group demo uvicorn demo.server:app --reload`).
- **Modernized code**: split into focused modules, typed, lazy-loaded
  models, cleaner public API. Existing function names
  (`detect`, `tokenize`, `cvt2zg`, `cvt2uni`) are preserved.

**Migrating from the original `pyidaungsu`**: change `import pyidaungsu as pds` to
`import ricelang as pds` and most calls work as-is. Detector labels
changed from `karen`/`mm_uni`/`mm_zg` to `ksw`/`mya`/`zgi`. New labels
follow ISO 639-3 except `zgi`, which is an encoding marker (Burmese
written in the legacy Zawgyi font, not a separate language).

## Installation

```sh
pip install ricelang
# or, with uv
uv add ricelang
```

## CLI

Installing the package registers a `ricelang` command. Every subcommand
accepts the text as a positional argument **or** `-` to read from
stdin. Add `--json` to any subcommand for machine-parseable output.

```sh
# detect — one ISO 639-3 label (or 'None' for out-of-scope text)
ricelang detect "ထမင်းစားပြီးပြီလား"          # → mya
ricelang detect "안녕하세요"                   # → kor
ricelang detect "🎉"                          # → None

# predict — top-k labels with probabilities (tab-separated, or --json)
ricelang predict "Pathian nih van" -k 5
ricelang --json predict "你好" -k 3

# convert — Burmese Zawgyi ↔ Unicode
ricelang convert --to zg  "ထမင်းစားပြီးပြီလား"
ricelang convert --to uni "ထမင္းစားၿပီးၿပီလား"

# tokenize — syllable | word | bpe
ricelang tokenize "ဖေဖေနဲ့မေမေ"                          # syllable, default lang=mm
ricelang tokenize --form word "ဖေဖေနဲ့မေမေ၏ကျေးဇူး"      # CRF word segmentation (Burmese)
ricelang tokenize --form bpe  "Pathian nih van"            # multilingual BPE (default)
ricelang tokenize --form bpe --lang mya "ဖေဖေနဲ့မေမေ"     # per-language BPE

# stdin — for piping from files / other commands
cat docs.txt | ricelang detect -
echo "ထမင်းစားပြီးပြီလား" | ricelang tokenize --form bpe --lang mya -

ricelang version    # print library version
ricelang --help     # all subcommands
```

The CLI is a thin wrapper over the Python API, so behavior and labels
are identical to `import ricelang as rl` — see below.

## Usage

### Language detection

Detects 25 labels across South and Southeast Asia (full table below).
Labels follow ISO 639-3 codes — with one exception, **`zgi`**, which
isn't a language but an encoding marker for Burmese text written in the
legacy non-Unicode Zawgyi font. The underlying language is `mya`; the
separate label exists so callers can route Zawgyi text through
`cvt2uni()` before any further NLP.

52+ labels in four groups. The first three come from a trained fastText
classifier; the **fourth group is detected by Unicode-block rule alone**
(no training data, no model call — scripts that have one language each).

**Myanmar-region minority languages** (original focus):

| Label  | Language                  | | Label  | Language                  |
| ------ | ------------------------- |-| ------ | ------------------------- |
| `mya`  | Burmese (Unicode)         | | `cnh`  | Hakha Chin (Lai)          |
| `zgi`† | Burmese (Zawgyi encoding) | | `cfm`  | Falam Chin                |
| `ksw`  | S'gaw Karen               | | `ctd`  | Tedim Chin                |
| `pwo`  | Pwo Western Karen         | | `eky`  | Eastern Kayah             |
| `kvq`  | Geba Karen                | | `shn`  | Shan (Tai Yai)            |
| `kac`  | Jingphaw (Kachin)         | | `mnw`  | Mon                       |

**Broader SE / South Asian** (via YouVersion):

| Label  | Language     | | Label  | Language          |
| ------ | ------------ |-| ------ | ----------------- |
| `eng`  | English      | | `tam`  | Tamil             |
| `hin`  | Hindi        | | `tgl`  | Tagalog           |
| `khm`  | Khmer        | | `tha`  | Thai              |
| `lao`  | Lao          | | `vie`  | Vietnamese        |
| `msa`  | Malay        | | `zho`  | Chinese           |

**Regional & script variants**:

| Label  | Language                       |
| ------ | ------------------------------ |
| `ban`  | Balinese                       |
| `sun`  | Sundanese                      |
| `hnn`  | Hanunoo                        |

Mon (`mnw`) is sourced from the Mon Wikipedia dump (135k paragraphs);
all other trained labels come from YouVersion Bible scrapes.

**Script-rule freebies** (no training data — Unicode block alone identifies them):

| Label  | Language | | Label  | Language          |
| ------ | -------- |-| ------ | ----------------- |
| `kor`  | Korean   | | `bod`  | Tibetan           |
| `jpn`  | Japanese | | `chr`  | Cherokee          |
| `ell`  | Greek    | | `nqo`  | N'Ko              |
| `heb`  | Hebrew   | | `mon`  | Mongolian (script) |
| `hye`  | Armenian | | `vai`  | Vai               |
| `kat`  | Georgian | | `jav`  | Javanese (script) |
| `amh`  | Amharic  | | `cjm`  | Cham              |
| `sin`  | Sinhala  | | `mni`  | Meetei            |
|        |          | | `nod`  | Lanna (Tai Tham)  |
|        |          | | `sat`  | Santali (Ol Chiki)|
|        |          | | `khb`  | Tai Lue           |
|        |          | | `tdd`  | Tai Nüa           |

…plus Bamum, Lepcha, Limbu, Saurashtra, Buginese, Pahawh Hmong, Adlam
(Fulani). Adding more is a one-line Unicode-range entry in
`ricelang/scripts.py` — see that file's `SCRIPT_RULES` table.

† `zgi` is the only non-ISO-639-3 label. It's not a language but an
encoding marker for Burmese text written in the legacy Zawgyi font
(the underlying language is `mya`). Use `cvt2uni()` to normalize
Zawgyi text to Unicode before any downstream processing.

**Accuracy** (held-out validation, 71,833 examples across the 25
trained labels): overall **P@1 = 99.85%**. 12 labels score 100%, 13
more score 99.2–99.97%. Lowest is `cnh` at 99.22%. The script-rule
freebies are 100% by construction (Unicode-block check is
deterministic).

**Out-of-scope text** (Korean text without Hangul, Russian, Arabic,
emoji-only, garbage) returns `None` from `detect()` — no more
confidently-wrong predictions for languages outside the supported set.
Exception: Latin script is shared with many global languages we don't
support (French, Spanish, German, etc.) — those will still be routed
to whichever in-set Latin label fits best. Use a general-purpose LID
upstream as a router if you need that distinction.

**Languages deliberately not supported** because text-only character-
n-gram detection cannot meaningfully distinguish them from a sibling
language already in the set (the text is often *literally identical*):

- **Indonesian (`ind`)** — shares ~80% vocabulary with `msa`; e.g.
  "Terima kasih" is grammatical in both.
- **Rakhine (`rki`)** — uses the same Myanmar script as `mya` and many
  short phrases are interchangeable.
- **Chinese Traditional (`zho_hant`)** — most characters are identical
  to Simplified; the writing-system difference doesn't show up in
  every text. Use `zho` for both for now.

The right place to disambiguate these is in the calling application
using context the model doesn't have (region, user metadata,
surrounding text).

To keep over-represented classes from biasing short-text decisions,
training caps each label at 40k examples (`--cap-per-label` in
`scripts/build_corpus.py`). Without it, `mnw` (135k paragraphs) would
dominate short Myanmar-script input.

```python
import ricelang as pds

pds.detect("ထမင်းစားပြီးပြီလား")
>> "mya"
pds.detect("ထမင္းစားၿပီးၿပီလား")
>> "zgi"
pds.detect("တၢ်သိၣ်လိတၢ်ဖးလံာ် ကွဲးလံာ်အိၣ်လၢ မ့ရ့ၣ်အစုပူၤလီၤ.")
>> "ksw"
```

### Zawgyi-Unicode conversion

```python
# convert to zawgyi (cvt2zg, or cvt2zgi alias)
pds.cvt2zg("ထမင်းစားပြီးပြီလား")
>> "ထမင္းစားၿပီးၿပီလား"

# convert to unicode
pds.cvt2uni("ထမင္းစားၿပီးၿပီလား")
>> "ထမင်းစားပြီးပြီလား"
```

### Tokenization

```python
# syllable level tokenization for Burmese
pds.tokenize("Alan TuringကိုArtificial Intelligenceနဲ့Computerတွေရဲ့ဖခင်ဆိုပြီးလူသိများပါတယ်") # lang parameter for default function is 'mm'
>> ['Alan', 'Turing', 'ကို', 'Artificial', 'Intelligence', 'နဲ့', 'Computer', 'တွေ', 'ရဲ့', 'ဖ', 'ခင်', 'ဆို', 'ပြီး', 'လူ', 'သိ', 'များ', 'ပါ', 'တယ်']

# syllable level tokenization for Karen
pds.tokenize("သရၣ်,သရၣ်မုၣ် ခဲလၢာ်ဟးထီၣ် (၃၅) ဂၤန့ၣ်လီၤ.", lang="karen")
>> ['ကၠိ', 'သ', 'ရၣ်', ',', 'သ', 'ရၣ်', 'မုၣ်', 'ခဲ', 'လၢာ်', 'ဟး', 'ထီၣ်', '(', '၃၅', ')', 'ဂၤ', 'န့ၣ်', 'လီၤ', '.']

# word level tokenization
pds.tokenize("ဖေဖေနဲ့မေမေ၏ကျေးဇူးတရားမှာကြီးမားလှပေသည်", form="word")
>> ['ဖေဖေ', 'နဲ့', 'မေမေ', '၏', 'ကျေးဇူးတရား', 'မှာ', 'ကြီးမား', 'လှ', 'ပေ', 'သည်']

```

Syllable-level tokenization supports 4 languages (Burmese, Karen, Mon, Shan)
via the legacy `lang` argument: `"mm"`, `"karen"`, `"mon"`, `"shan"`.
Word-level tokenization (CRF-based) supports only Burmese.

```python
# Multilingual BPE — handles every supported script. Default for form="bpe".
pds.tokenize("Pathian nih van le vawlei a ser hna tikah", form="bpe")

# Per-language BPE — pass an ISO 639-3 lang code that has a bundled model
pds.tokenize("ဖေဖေနဲ့မေမေ၏ကျေးဇူးတရားမှာကြီးမားလှပေသည်", lang="mya", form="bpe")
>> ['ဖေ', 'ဖေ', 'နဲ့', 'မေ', 'မေ', '၏', 'ကျေးဇူး', 'တရား', 'မှာ', 'ကြီးမား', 'လှ', 'ပေ', 'သည်']
```

BPE tokenizers are bundled for every supported language (24 per-language
models — every label except `zgi`, which shares the Burmese script with
`mya`) plus a multilingual one (`multi`, 32k vocab) that covers every
script in a single tokenizer. Per-language BPEs target 16k vocab
(smaller for tiny corpora like `kvq`, `khm`); `multi` handles
code-switching naturally. Retrain via `scripts/train_bpe.py --all`.

## Demo server

A FastAPI app that exposes every public function with a form UI:

```sh
uv run --group demo uvicorn demo.server:app --reload --port 8000
```

- Form UI: <http://127.0.0.1:8000/>
- Swagger / API explorer: <http://127.0.0.1:8000/docs>

Includes per-language sample buttons that populate the input field with a
random sentence in the chosen language so you can try detection,
conversion, and tokenization without having to find text in 25
languages yourself. See `demo/README.md`.

## Training the language detector

The bundled `ricelang/model/pdsdetect.ftz` is a fastText supervised
classifier (subword character n-grams, no word n-grams; quantized to
~1.8 MB).

### Reproduce the bundled model

Clone the corpus repo next to this one and run the two scripts:

```sh
# at the same level as ricelang/
git clone git@github.com:kaunghtetsan275/corpus.git

# build train/valid splits from the corpus
uv run python scripts/build_corpus.py --corpus ../corpus/data --out data

# train, evaluate, quantize, and save into the package
uv run python scripts/train_detector.py \
    --train-file data/train.txt --valid-file data/valid.txt \
    --output ricelang/model/pdsdetect.ftz \
    --epoch 25 --lr 0.5 --dim 16 --word-ngrams 1 --minn 2 --maxn 5
```

The corpus builder also synthesizes a `zgi` class by running `cvt2zg`
over the Unicode Burmese examples, so the model can distinguish
encodings even though no native Zawgyi text is available in the
corpus. Disable with `--no-synthesize-zg`.

### Train on your own data

`scripts/train_detector.py` also accepts a directory tree of per-language
`.txt` files (`--train-dir <dir>` with subdirs `mya/`, `ksw/`, ...) — see
`scripts/train_detector.py --help` for all knobs.

## Planned / wanted languages

Candidates to add next, grouped by what's blocking them:

**Need a different source than YouVersion**
- **Lanna / Northern Thai** in Tai Tham script (`nod`, U+1A20–U+1AAF) —
  the YouVersion v1907 nod version uses Thai-script transliteration
  which is visually indistinguishable from `tha`; real Tai Tham
  orthography lives mostly in scanned monastery manuscripts and a small
  Wikipedia Incubator project.
- **Batak Toba** (`bbc`) — the only YouVersion bbc version (v17) is a
  catalog placeholder with no published chapter content.
- **Mon (`mnw`)** is shipped from the Mon Wikipedia dump — but more
  modern/news-style Mon text from sources like Independent Mon News
  Agency (mon.monnews.org) would broaden coverage.

**Need source identification**
- **Malay in Jawi script** (`msa_Arab`) — would be a true script variant,
  not just a sibling of Latin-script `msa`.

**Cannot be supported by character-n-gram detection** (see "Languages
deliberately not supported" above): Indonesian (`ind`), Rakhine (`rki`),
Chinese Traditional (`zho_hant`). These would need either external
metadata (region, user profile) or a different model class.

## Future work

- [x] Add tokenizer for Burmese (syllable and word-level tokenization)
- [x] Add BPE tokenizer for every supported language + a multilingual one
- [ ] Add Part-of-Speech (POS) tagger for Burmese
- [ ] Add Named-entities Recognition (NER) classifier for Burmese
- [ ] Add thorough documentation

## Citation

If you use `ricelang` in your research or software, please cite it:

```bibtex
@software{san_ricelang,
  author  = {San, Kaung Htet},
  title   = {ricelang: Language identification and tokenization for Southeast and South Asian languages},
  url     = {https://github.com/kaunghtetsan275/ricelang},
  version = {0.5.0},
  license = {MIT}
}
```

Or in plain text:

> Kaung Htet San. *ricelang: Language identification and tokenization for
> Southeast and South Asian languages.* MIT License.
> <https://github.com/kaunghtetsan275/ricelang>
