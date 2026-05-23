# Pyidaungsu

Python library for Myanmar language. Useful in Natural Language Processing and text preprocessing for Myanmar language.

## Installation

```sh
pip install pyidaungsu
# or, with uv
uv add pyidaungsu
```

## Usage

### Language detection

Detects Burmese (Unicode and Zawgyi encodings), S'gaw Karen, Hakha Chin,
and Kayah Li. Labels follow ISO 639-3 codes (note: `karen` was renamed to
`ksw` in 0.2.0).

| Label  | Language                  |
| ------ | ------------------------- |
| `uni`  | Burmese (Unicode)         |
| `zg`   | Burmese (Zawgyi)          |
| `ksw`  | S'gaw Karen               |
| `cnh`  | Hakha Chin                |
| `eky`  | Eastern Kayah             |

Mon and Shan detection were disabled in 0.1.3 due to dirty training data
and remain disabled in 0.2.0.

```sh
import pyidaungsu as pds

pds.detect("ထမင်းစားပြီးပြီလား")
>> "uni"
pds.detect("ထမင္းစားၿပီးၿပီလား")
>> "zg"
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

## Training the language detector

The bundled `pyidaungsu/model/pdsdetect.ftz` is a fastText supervised
classifier (char n-grams with word n-grams, quantized to ~1.2 MB).

### Reproduce the bundled model

Clone the corpus repo next to this one and run the two scripts:

```sh
# at the same level as pyidaungsu/
git clone git@github.com:kaunghtetsan275/corpus.git

# build train/valid splits from the corpus
uv run python scripts/build_corpus.py --corpus ../corpus/scraped_data --out data

# train, evaluate, quantize, and save into the package
uv run python scripts/train_detector.py \
    --train-file data/train.txt --valid-file data/valid.txt \
    --output pyidaungsu/model/pdsdetect.ftz \
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

## Future work

- [x] Add tokenizer for Burmese (Syllabel and word-level tokenization)
- [ ] Add more tokenizer (BPE, WordPiece etc.)
- [ ] Add Part-of-Speech (POS) tagger for Burmese
- [ ] Add Named-entities Recognition (NER) classifier for Burmese
- [ ] Add thorough documentation
