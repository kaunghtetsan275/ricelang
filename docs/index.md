# ricelang

[![PyPI](https://img.shields.io/pypi/v/ricelang.svg)](https://pypi.org/project/ricelang/)
[![Python](https://img.shields.io/pypi/pyversions/ricelang.svg)](https://pypi.org/project/ricelang/)
[![tests](https://github.com/kaunghtetsan275/ricelang/actions/workflows/test.yml/badge.svg)](https://github.com/kaunghtetsan275/ricelang/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Language identification, tokenization, and Zawgyi/Unicode conversion for 50+ Southeast and South Asian languages.**

Revamp of [pyidaungsu](https://pypi.org/project/pyidaungsu/) — ISO 639-3 labels, 17× more languages, reproducible training, `uv`-native.

## At a glance

- **50+ languages**: 25 trained labels + 27 script-rule freebies
- **99.85% P@1** on held-out validation
- **1.8 MB** detection model, ~13 MB full bundle
- **Local & offline**: no API key, no GPU, no network
- **Returns `None`** for out-of-scope text — no hallucinated answers
- **`ricelang` CLI** ships with the Python package

## Install

=== "pip"

    ```sh
    pip install ricelang
    ```

=== "uv"

    ```sh
    uv add ricelang
    ```

## One-minute taste

```python
import ricelang as rl

rl.detect("ထမင်းစားပြီးပြီလား")       # 'mya'   (Burmese)
rl.detect("안녕하세요")                # 'kor'   (Korean — via script rule)
rl.detect("🎉")                       #  None    (out of scope)

rl.tokenize("ဖေဖေနဲ့မေမေ၏ကျေးဇူး", form="word")
# ['ဖေဖေ', 'နဲ့', 'မေမေ', '၏', 'ကျေးဇူး']

rl.cvt2zg("ထမင်းစားပြီးပြီလား")        # → Zawgyi
rl.cvt2uni("ထမင္းစားၿပီးၿပီလား")        # → Unicode
```

…or from the shell:

```sh
ricelang detect "ထမင်းစားပြီးပြီလား"      # mya
echo "hello" | ricelang detect -          # None  (no rule for English-only short text)
```

## When to use ricelang

ricelang is the right tool when you have **text from Southeast or South Asia** and need:

- **Language identification** for routing/filtering pipelines
- **Tokenization** that respects script and morphology (Burmese syllables, BPE subwords for downstream embeddings)
- **Zawgyi → Unicode** normalization of legacy Burmese text
- A **small, deterministic, offline** building block that's not an LLM

## When *not* to use ricelang

- **Generic worldwide language detection** — ricelang is specialised for SE/South Asia + East Asian script families. Use [`fasttext lid.176`](https://fasttext.cc/docs/en/language-identification.html) or [`cld3`](https://github.com/google/cld3) as an upstream router if you process arbitrary global text.
- **Anything requiring reasoning** — translation, summarization, structured extraction. That's LLM territory.

## Next steps

- [**Install**](installation.md) — pip / uv / from source
- [**CLI**](cli.md) — every subcommand with examples
- [**Detection guide**](guide/detection.md) — Python API
- [**How the detector works**](architecture/detector.md) — script rule + ML hybrid
- [**Supported languages**](guide/languages.md) — full label table
- [**Migrating from pyidaungsu**](migration.md)
