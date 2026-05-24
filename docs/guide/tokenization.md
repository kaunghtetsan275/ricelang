# Tokenization

ricelang exposes three tokenization modes via the same `tokenize()` function:

| `form` | Algorithm | Languages |
|---|---|---|
| `"syllable"` (default) | Regex-based syllable split | Burmese (`mm`), Karen (`karen`), Mon (`mon`), Shan (`shan`) |
| `"word"` | CRF word segmentation | Burmese only |
| `"bpe"` | Byte-pair encoding subwords | Per-language model (24 langs) + multilingual (`multi`) |

## Syllable (default)

Splits on regex rules that respect each language's consonant + virama
patterns. Cheap, fast, good for text statistics and downstream ML inputs.

```python
import ricelang as rl

rl.tokenize("Alan Turingကို Artificial Intelligence")
# ['Alan', 'Turing', 'ကို', 'Artificial', 'Intelligence']

rl.tokenize("ဖေဖေနဲ့မေမေ၏ကျေးဇူး")
# ['ဖေ', 'ဖေ', 'နဲ့', 'မေ', 'မေ', '၏', 'ကျေး', 'ဇူး']

rl.tokenize("လူၤစံယၤ အခီၣ်စ့ၣ်တကပၤ", lang="karen")
# ['လူၤ', 'စံ', 'ယၤ', 'အ', 'ခီၣ်', 'စ့ၣ်', 'တ', 'က', 'ပၤ']
```

## Word (Burmese only, CRF-based)

Segments Burmese into linguistic words using a trained CRF model
(`tokenizer.crfsuite`, ~1.4 MB). Slower than syllable but much closer to
what a human reader would produce.

```python
rl.tokenize("ဖေဖေနဲ့မေမေ၏ကျေးဇူးတရားမှာကြီးမားလှပေသည်", form="word")
# ['ဖေဖေ', 'နဲ့', 'မေမေ', '၏', 'ကျေးဇူးတရား', 'မှာ',
#  'ကြီးမား', 'လှ', 'ပေ', 'သည်']
```

## BPE subwords

Byte-pair encoding via [HuggingFace tokenizers](https://github.com/huggingface/tokenizers).
Useful as input to downstream LLM / embedding pipelines that expect subword
units.

Two flavors are bundled:

- **`multi`** (default): 32k-vocab tokenizer trained on the full corpus.
  Handles every supported script in one model. Best for code-switching or
  unknown-language input.
- **Per-language** (24 of them): 16k-vocab tokenizer trained on one
  language's corpus. Tighter splits on the target language at the cost of
  not handling other scripts well.

```python
# multilingual (default for form="bpe")
rl.tokenize("Pathian nih van", form="bpe")
# ['Pathian', 'nih', 'van']

# per-language Burmese
rl.tokenize("ဖေဖေနဲ့မေမေ၏ကျေးဇူး", form="bpe", lang="mya")
# ['ဖေ', 'ဖေ', 'နဲ့', 'မေ', 'မေ', '၏', 'ကျေးဇူး']

# per-language Thai
rl.tokenize("สวัสดีครับ ขอบคุณมากครับ", form="bpe", lang="tha")
```

### Available per-language BPE models

`mya`, `ksw`, `pwo`, `kvq`, `cnh`, `cfm`, `ctd`, `eky`, `shn`,
`eng`, `hin`, `khm`, `lao`, `msa`, `tam`, `tgl`, `tha`, `vie`, `zho`,
`ban`, `hnn`, `kac`, `mnw`, `sun`.

(No `zgi` BPE — Zawgyi text should be normalized to Unicode via
[`cvt2uni()`](conversion.md) before tokenizing.)

Unknown lang silently falls back to `multi`.

## Retraining BPEs

Both the per-language and multilingual BPEs can be retrained from your own
corpus — see [Training BPEs](../training/bpe.md).

## Choosing the right form

| Use case | Recommended |
|---|---|
| Quick word count / text statistics | `syllable` |
| Search index / phrase matching for Burmese | `word` |
| Feeding into an LLM / embedding model | `bpe` (multi or per-language) |
| Building a non-Burmese SE Asian word-level pipeline | `syllable` + custom rules |
