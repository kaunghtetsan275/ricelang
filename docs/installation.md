# Installation

ricelang requires **Python 3.10+** and runs on Linux, macOS, and Windows. The
package ships a bundled fastText detector model and 25 BPE tokenizers, totalling
~13 MB.

## From PyPI

=== "pip"

    ```sh
    pip install ricelang
    ```

=== "uv"

    ```sh
    uv add ricelang
    ```

This installs both the importable `ricelang` Python package and the `ricelang`
command-line tool.

## Verify

```sh
ricelang version
# 0.5.0

python -c "import ricelang as rl; print(rl.detect('မင်္ဂလာပါ'))"
# mya
```

## What gets installed

| Component | Size | Purpose |
|---|---:|---|
| `ricelang/model/pdsdetect.ftz` | ~1.8 MB | fastText classifier (25 trained labels) |
| `ricelang/model/tokenizer.crfsuite` | ~1.4 MB | Burmese word-segmentation CRF |
| `ricelang/model/bpe_*.json` (×25) | ~10 MB | per-language + multilingual BPE tokenizers |
| Runtime deps | varies | `fasttext-wheel`, `python-crfsuite`, `tokenizers`, `numpy<2` |

## Optional groups

ricelang's `pyproject.toml` declares two optional dependency groups for
development / running the demo. Most users won't need them:

```sh
# to run the FastAPI demo server in demo/
uv sync --group demo

# to develop / run tests / scrape corpora
uv sync --group dev

# to build the docs site (this site)
uv sync --group docs
```

## From source

```sh
git clone https://github.com/kaunghtetsan275/ricelang.git
cd ricelang
uv sync
uv run pytest
```

To build a wheel locally:

```sh
uv build
ls dist/
```

## Python compatibility

| Version | Status |
|---|---|
| 3.13 | ⚠ untested — fasttext-wheel has no 3.13 Linux wheel yet |
| 3.12 | ✓ tested in CI |
| 3.11 | ✓ tested in CI |
| 3.10 | ✓ tested in CI (minimum) |
| ≤ 3.9 | ✗ unsupported — EOL October 2025, and patched dep versions don't backport |
