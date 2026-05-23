# Pyidaungsu

Python library for Myanmar language. Useful in Natural Language Processing and text preprocessing for Myanmar language.

## Installation

```sh
pip install pyidaungsu
# or, with uv
uv add pyidaungsu
```

## Usage

### ~~Zawgyi-Unicode detection~~ Language detection (Myanmar <Zawgyi, Unicode>, Karen, Mon, Shan)
Starting from the pyidaungsu 0.0.9, it does not only detect Zawgyi and Unicode for Myanmar language but also other languages such as Mon, Karen, Shan as well.

Language detection for Mon and Shan is temporarily disabled starting from 0.1.3 as the accuracy for those languages wasn't as good.
Supported languages ATM: English, Spanish, French, Chinese, Japanese, Korean, Myanmar (unicode), Myanmar (zawgyi), Karen

```sh
import pyidaungsu as pds

# language detection
pds.detect("ထမင်းစားပြီးပြီလား")
>> "uni"
pds.detect("ထမင္းစားၿပီးၿပီလား")
>> "zg"
pds.detect("တၢ်သိၣ်လိတၢ်ဖးလံာ် ကွဲးလံာ်အိၣ်လၢ မ့ရ့ၣ်အစုပူၤလီၤ.")
>> "karen"
pds.detect("ဇၟာပ်မၞိဟ်ဂှ် ကတဵုဒှ်ကၠုင် ပ္ဍဲကဵုဂကောံမွဲ ဖအိုတ်ရ၊၊")
>> "mon"   # (Mon detection disabled since 0.1.3 due to low accuracy)
pds.detect("ၼႂ်းဢိူင်ႇမိူင်းၽူင်း ၸႄႈဝဵင်းတႃႈၶီႈလဵၵ်း ၾႆးမႆႈႁိူၼ်း ၵူၼ်းဝၢၼ်ႈ လင်ၼိုင်ႈ")
>> "shan"  # (Shan detection disabled since 0.1.3)
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

The bundled `pyidaungsu/model/pdsdetect.ftz` is a fastText supervised classifier.
To retrain it on your own corpus:

```sh
# Layout: data/train/<lang>/*.txt with one example per line
uv run python scripts/train_detector.py \
    --train-dir data/train \
    --valid-dir data/valid \
    --output pyidaungsu/model/pdsdetect.ftz \
    --epoch 25 --lr 1.0 --dim 16
```

Alternatively, pass `--train-file` with a file already in fastText format
(`__label__<lang> <text>` per line). See `scripts/train_detector.py --help`
for tuning knobs (`--word-ngrams`, `--loss`, `--no-quantize`, ...).

## Future work

- [x] Add tokenizer for Burmese (Syllabel and word-level tokenization)
- [ ] Add more tokenizer (BPE, WordPiece etc.)
- [ ] Add Part-of-Speech (POS) tagger for Burmese
- [ ] Add Named-entities Recognition (NER) classifier for Burmese
- [ ] Add thorough documentation
