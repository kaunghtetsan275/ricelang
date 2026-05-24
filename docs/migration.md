# Migrating from pyidaungsu

ricelang is a revamp of [pyidaungsu](https://pypi.org/project/pyidaungsu/).
If you're coming from `pyidaungsu` 0.1.x, here's everything that changed.

## TL;DR

```python
# before
import pyidaungsu as pds
pds.detect("...")   # returns 'karen', 'mm_uni', 'mm_zg'

# after
import ricelang as pds
pds.detect("...")   # returns ISO 639-3: 'ksw', 'mya', 'zgi'
```

Most function calls work as-is. The package name, import path, and label
strings changed. The function names (`detect`, `tokenize`, `cvt2zg`,
`cvt2uni`) are preserved.

## Install change

```sh
pip uninstall pyidaungsu
pip install ricelang
```

## Label changes

| pyidaungsu | ricelang | notes |
|---|---|---|
| `mm_uni` | `mya` | Burmese Unicode (ISO 639-3) |
| `mm_zg` | `zgi` | Burmese Zawgyi encoding |
| `karen` | `ksw` | Now specifically S'gaw Karen (ISO 639-3); ricelang also distinguishes `pwo` (Pwo) and `kvq` (Geba) |
| `mon` | `mnw` | Mon (ISO 639-3) |
| `shan` | `shn` | Shan (ISO 639-3) |
| (none) | `cnh`, `cfm`, `ctd` | Hakha / Falam / Tedim Chin (new) |
| (none) | `eky` | Eastern Kayah (new) |
| (none) | `kac` | Jingphaw / Kachin (new) |
| (none) | `eng`, `hin`, `khm`, `lao`, `msa`, `tam`, `tgl`, `tha`, `vie`, `zho`, `ban`, `sun`, `hnn` | broader regional + South Asian (new) |
| (none) | 27 script-rule freebies (`kor`, `jpn`, `ell`, `heb`, `hye`, `kat`, `amh`, `sin`, `bod`, …) | new via Unicode-block rules |

## API differences

### `detect()` returns `None` for out-of-scope

```python
# pyidaungsu
pds.detect("🎉")   # returned some confidently-wrong label

# ricelang
rl.detect("🎉")    # None
```

Callers that relied on `detect()` always returning a string can pass
`fallback="..."` to keep that behavior:

```python
rl.detect(text, fallback="unknown")
```

### Tokenization

`tokenize()` signature is unchanged for `form="syllable"` and `form="word"`.
Legacy `lang` codes `"mm"`, `"karen"`, `"mon"`, `"shan"` still work.

New in ricelang:

```python
rl.tokenize(text, form="bpe")               # multilingual BPE (default)
rl.tokenize(text, form="bpe", lang="mya")   # per-language BPE
```

### `cvt2zgi` is now an alias

`cvt2zgi` was documented in pyidaungsu's README but not actually exported.
ricelang exports it as an alias for `cvt2zg` so any documentation copy-paste
works.

## What else is new

- **CLI**: `pip install ricelang` registers a `ricelang` command. See
  [CLI reference](cli.md).
- **Hierarchical detector**: a Unicode-script rule runs before the trained
  classifier. See [How it works](architecture/detector.md).
- **BPE tokenizers**: 24 per-language + 1 multilingual. See
  [Tokenization](guide/tokenization.md).
- **Demo server**: a FastAPI app under `demo/` exposes every endpoint with a
  form UI.
- **Reproducible training**: scripts under `scripts/` let you rebuild every
  bundled model from scratch using the
  [corpus repo](https://github.com/kaunghtetsan275/corpus). See
  [Training](training/detector.md).
- **`uv`-native**: `pyproject.toml`, no `setup.py`, `uv.lock` checked in.

## What's gone

- `download_model()` — no longer needed. Models ship with the package.
- The "syllable + word level" output dictionary structure — replaced by
  plain lists, same as before but cleaner.
