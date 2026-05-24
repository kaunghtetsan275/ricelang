# Hierarchical detector

`rl.detect()` doesn't always invoke the trained model. It runs a two-stage
hybrid: a Unicode-block rule first, then the fastText classifier only when
the script is genuinely ambiguous.

```
detect(text)
 │
 ├─ script_detect(text)  →  dominant Unicode block
 │
 │   ├─ Hangul present       →  "kor"          (script-rule, no ML)
 │   ├─ Hiragana present     →  "jpn"
 │   ├─ Devanagari           →  "hin"
 │   ├─ Tamil                →  "tam"
 │   ├─ Thai                 →  "tha"
 │   ├─ Lao                  →  "lao"
 │   ├─ Khmer                →  "khm"
 │   ├─ Kayah Li             →  "eky"
 │   ├─ CJK (no kana/hangul) →  "zho"
 │   ├─ Greek, Hebrew, ...   →  "ell", "heb", ...   (script-rule freebies)
 │   ├─ Shan-tone subrange   →  "shn"          (sub-block rule inside Myanmar)
 │   │
 │   ├─ Myanmar block        →  _ml_predict(text)   (8-class fastText)
 │   ├─ Latin                →  _ml_predict(text)   (11-class fastText)
 │   │
 │   └─ none of the above    →  fallback (default None)
```

## Why this design

A 7B-parameter LLM doesn't need to load to tell you that text in Hangul is
Korean — a 5-line Unicode-range check is faster, smaller, and 100% accurate
by construction. The trained model only runs when the script is genuinely
shared by multiple supported languages.

Two consequences:

- **Free coverage for ~27 languages**: any script that's used by exactly
  one language we care about gets a rule, no training data needed.
- **Honest out-of-scope handling**: if the text contains *no* characters in
  any supported script, the rule returns `None`. The model is never
  invoked. No more confidently-wrong predictions on Korean, Russian,
  Arabic, emoji, etc.

## The Shan sub-block case

Shan and Burmese both use the Myanmar block (U+1000–U+109F). They're
linguistically distinct but share the same Unicode codepoints — at least
for most characters.

The Myanmar block carves out a **Shan subrange** at U+1075–U+108A
("Myanmar Letter Shan Ka", "Myanmar Sign Shan Tone-2", etc.) that Burmese
and Karen never use. ricelang's rule:

- Any of `U+1022`, `U+1079`, `U+1084` (Shan-only — verified zero usage in
  mya/zgi/ksw/pwo/kvq/mnw corpora) → `shn`
- ≥ 20% of Myanmar-block chars in U+1075–U+108A → `shn`

The distributions are cleanly bimodal: real Shan text clusters at 25–40%
density in that range; Zawgyi clusters at 1–5%. The 20% threshold gives:

- 99.34% of Shan paragraphs caught by the rule
- 0.07% false-positive rate on Zawgyi

## What the trained model actually does

Just two real classification jobs:

| Family | Labels | Why ML is needed |
|---|---|---|
| **Latin** | `eng`, `cnh`, `cfm`, `ctd`, `msa`, `tgl`, `vie`, `ban`, `sun`, `hnn`, `kac` | 11 languages all share Latin script |
| **Myanmar block** | `mya`, `zgi`, `ksw`, `pwo`, `kvq`, `mnw` | 6 languages share the same Unicode block (Shan now handled by rule) |

The detector is a fastText supervised model trained on character n-grams
(min=2, max=5). 25 labels total in the model (the 17 shared-script ones
plus 7 already-monopoly ones kept for fallback safety, plus `zgi`).

Held-out validation: **99.85% P@1** overall.

## The full set of script rules

The rule table is in [`ricelang/scripts.py`](https://github.com/kaunghtetsan275/ricelang/blob/master/ricelang/scripts.py).
Each entry is:

```python
(label, [(lo, hi), ...], min_fraction, extra_predicate)
```

Adding a new monopoly-script language is one row — find the Unicode block
(e.g. Adlam at U+1E900–U+1E95F) and add:

```python
("ff",  [(0x1E900, 0x1E95F)], 0.30, None),    # Fulani (Adlam)
```
