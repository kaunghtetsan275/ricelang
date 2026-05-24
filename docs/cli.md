# Command-line tool

`pip install ricelang` registers a `ricelang` command. Every subcommand
accepts text as a positional argument, **or** `-` to read from stdin (for
pipes). Add `--json` to any subcommand for machine-parseable output.

## `ricelang detect`

Identify the language of `text`. Returns one ISO 639-3 label, or `None` if
the text is out of scope (emoji, unsupported script, etc.).

```sh
ricelang detect "ထမင်းစားပြီးပြီလား"        # mya
ricelang detect "안녕하세요"                  # kor
ricelang detect "🎉"                          # None
ricelang --json detect "Pathian nih van"     # {"label": "cnh"}
```

## `ricelang predict`

Top-k labels with probabilities, tab-separated by default.

```sh
ricelang predict "Pathian nih van" -k 5
# cnh   1.0000
# cfm   0.0000
# ...

ricelang --json predict "你好" -k 3
# {"predictions":[{"label":"zho","prob":1.0},...]}
```

## `ricelang convert`

Burmese encoding conversion (Zawgyi ↔ Unicode). The `--to` flag picks the
target encoding.

```sh
ricelang convert --to zg  "ထမင်းစားပြီးပြီလား"   # → Zawgyi
ricelang convert --to uni "ထမင္းစားၿပီးၿပီလား"   # → Unicode
```

## `ricelang tokenize`

Tokenize text. The `--form` flag picks the algorithm; `--lang` picks the
target language.

```sh
# syllable (default) — Burmese/Karen/Mon/Shan
ricelang tokenize "ဖေဖေနဲ့မေမေ"
# ဖေ
# ဖေ
# နဲ့
# မေ
# မေ

# word — CRF segmentation, Burmese only
ricelang tokenize --form word "ဖေဖေနဲ့မေမေ၏ကျေးဇူး"
# ဖေဖေ
# နဲ့
# မေမေ
# ၏
# ကျေးဇူး

# bpe — multilingual subwords (default)
ricelang tokenize --form bpe "Pathian nih van"

# bpe with a per-language model
ricelang tokenize --form bpe --lang mya "ဖေဖေနဲ့မေမေ"
```

The `--lang` accepts:

- For `--form syllable`: `mm`, `karen`, `mon`, `shan` (legacy codes)
- For `--form bpe`: any ISO 639-3 code with a bundled BPE
  (`multi`, `mya`, `ksw`, `pwo`, `kvq`, `cnh`, `cfm`, `ctd`, `eky`, `shn`,
  `eng`, `hin`, `khm`, `lao`, `msa`, `tam`, `tgl`, `tha`, `vie`, `zho`,
  `ban`, `hnn`, `kac`, `mnw`, `sun`). Unknown lang silently falls back to
  `multi`.

## Stdin / pipes

Pass `-` instead of a positional argument:

```sh
cat docs.txt | ricelang detect -
echo "ထမင်းစားပြီးပြီလား" | ricelang tokenize --form bpe --lang mya -

# detect every URL in a file (with curl)
while read url; do
  echo "$url $(curl -s "$url" | ricelang detect -)"
done < urls.txt
```

## `--json` output

Add to any subcommand:

```sh
ricelang --json detect "မင်္ဂလာပါ"
# {"label":"mya"}

ricelang --json tokenize --form bpe --lang mya "ဖေဖေ"
# {"tokens":["ဖေ","ဖေ"],"count":2}
```

## `ricelang version` / `ricelang --help`

```sh
ricelang version       # print library version
ricelang --help        # list subcommands
ricelang detect --help # subcommand-specific help
```
