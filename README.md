# ricelang

NLP library for Southeast Asian languages — language identification,
tokenization, and Zawgyi/Unicode conversion. Successor to
[pyidaungsu](https://pypi.org/project/pyidaungsu/) with an expanded label
set, full-Bible corpus from YouVersion scrapes, and a BPE tokenizer.

## Installation

```sh
pip install ricelang
# or, with uv
uv add ricelang
```

## Usage

### Language detection

Detects Burmese (Unicode and Zawgyi encodings), three Karen variants
(S'gaw, Pwo, Geba), three Chin variants (Hakha, Falam, Tedim), Eastern
Kayah, and Shan. Labels follow ISO 639-3 codes.

21 labels in two groups:

**Myanmar-region minority languages** (the original focus):

| Label  | Language                  |
| ------ | ------------------------- |
| `mya`  | Burmese (Unicode)         |
| `zgi`  | Burmese (Zawgyi)          |
| `ksw`  | S'gaw Karen               |
| `pwo`  | Pwo Western Karen         |
| `kvq`  | Geba Karen                |
| `cnh`  | Hakha Chin (Lai)          |
| `cfm`  | Falam Chin                |
| `ctd`  | Tedim Chin                |
| `eky`  | Eastern Kayah             |
| `shn`  | Shan (Tai Yai)            |

**Broader SE / South Asian** (added in 0.3.x via YouVersion full-Bible scrapes):

| Label  | Language     | | Label  | Language     |
| ------ | ------------ |-| ------ | ------------ |
| `eng`  | English      | | `msa`  | Malay        |
| `hin`  | Hindi        | | `tam`  | Tamil        |
| `ind`  | Indonesian   | | `tgl`  | Tagalog      |
| `khm`  | Khmer        | | `tha`  | Thai         |
| `lao`  | Lao          | | `vie`  | Vietnamese   |
|        |              | | `zho`  | Chinese      |

Mon detection remains disabled (no training data available). Shan was
disabled in 0.1.3 due to dirty data and re-enabled in 0.2.0 after the
shannews.org export was reprocessed.

**Accuracy** (held-out validation, 59,240 examples across 21 labels):
overall **P@1 = 99.09%**. 17 labels score 100% and 4 score 99.2–99.9%.
The two notable weak spots are **ind ↔ msa** (~91–93%) — Indonesian and
Malay share ~80% of their vocabulary so the model genuinely struggles
to tell them apart on short or scripture-style text; this is a real
linguistic ambiguity rather than a training issue.

```sh
import ricelang as pds

pds.detect("ထမင်းစားပြီးပြီလား")
>> "mya"
pds.detect("ထမင္းစားၿပီးၿပီလား")
>> "zgi"
pds.detect("တၢ်သိၣ်လိတၢ်ဖးလံာ် ကွဲးလံာ်အိၣ်လၢ မ့ရ့ၣ်အစုပူၤလီၤ.")
>> "ksw"
```

### Zawgyi-Unicode conversion

```sh
# convert to zawgyi (cvt2zg, or cvt2zgi alias)
pds.cvt2zg("ထမင်းစားပြီးပြီလား")
>> "ထမင္းစားၿပီးၿပီလား"

# convert to unicode
pds.cvt2uni("ထမင္းစားၿပီးၿပီလား")
>> "ထမင်းစားပြီးပြီလား"
```

### Tokenization

```sh
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

Syllable-level tokenization supports for 4 languages (Burmese, Karen, Shan, Mon). Word-level tokenization supports only Burmese currently.</br>
Available values for `lang` parameter in `tokenize` function: "mm", "karen", "mon", "shan"

```sh
# Multilingual BPE — handles every supported script. Default for form="bpe".
pds.tokenize("Pathian nih van le vawlei a ser hna tikah", form="bpe")

# Per-language BPE — pass an ISO 639-3 lang code that has a bundled model
pds.tokenize("ဖေဖေနဲ့မေမေ၏ကျေးဇူးတရားမှာကြီးမားလှပေသည်", lang="mya", form="bpe")
>> ['ဖေ', 'ဖေ', 'နဲ့', 'မေ', 'မေ', '၏', 'ကျေးဇူး', 'တရား', 'မှာ', 'ကြီးမား', 'လှ', 'ပေ', 'သည်']
```

BPE tokenizers are bundled for every supported language (20 per-language
models — every label except `zgi`, since it shares the Burmese script
with `mya`) plus a multilingual one (`multi`, 32k vocab) that covers
every script in a single tokenizer. Per-language BPEs target 16k vocab
(smaller for tiny corpora like `kvq`, `khm`); `multi` handles
code-switching naturally. Retrain via `scripts/train_bpe.py --all`.

## Training the language detector

The bundled `ricelang/model/pdsdetect.ftz` is a fastText supervised
classifier (char n-grams with word n-grams, quantized to ~1.2 MB).

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

The corpus builder also synthesizes a `zg` class by running `cvt2zg` over
the Unicode Burmese examples, so the model can distinguish encodings even
though no native Zawgyi text is available. Disable with
`--no-synthesize-zg`.

### Train on your own data

`scripts/train_detector.py` also accepts a directory tree of per-language
`.txt` files (`--train-dir <dir>` with subdirs `uni/`, `ksw/`, ...) — see
`scripts/train_detector.py --help` for all knobs.

## Planned languages

Languages to add next, grouped by region. Each needs a sourcing decision
(YouVersion if a Bible exists, otherwise community/literature corpora):

**Myanmar region**
- Rakhine / Arakan (`rki`)
- Mon (`mnw`)
- Jingphaw / Kachin (`kac`)

**Thailand region**
- Lanna / Northern Thai in Tai Tham script (`nod`)
- Malay in Jawi script (`msa_Arab`)

**Philippines region**
- Tagalog in Mangyan / Hanunoo script (`hnn`)

**Indonesia region**
- Balinese (`ban`)
- Sundanese (`sun`)
- Batak (`bbc` Toba; macro-language with multiple ISO codes)

**Script / writing-system variants**
- Chinese Traditional (`zho_Hant` — currently only Simplified `zho` is trained)

## Future work

- [x] Add tokenizer for Burmese (syllable and word-level tokenization)
- [x] Add BPE tokenizer for every supported language + a multilingual one
- [ ] Add Part-of-Speech (POS) tagger for Burmese
- [ ] Add Named-entities Recognition (NER) classifier for Burmese
- [ ] Add thorough documentation
