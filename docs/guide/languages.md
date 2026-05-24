# Supported languages

ricelang detects **50+ labels** in total. Some come from a trained fastText
classifier (Latin and Myanmar block — shared scripts); the rest come from
Unicode-script rules (one language per script — no ML needed).

## Trained classifier (25 labels)

These use the bundled `pdsdetect.ftz` model (~1.8 MB). All scored 99.2–100%
on held-out validation.

### Myanmar region

| Label | Language | Notes |
|---|---|---|
| `mya` | Burmese (Unicode) | Myanmar script |
| `zgi` | Burmese (Zawgyi) | Legacy encoding — not a separate language; use [`cvt2uni()`](conversion.md) |
| `ksw` | S'gaw Karen | Myanmar script |
| `pwo` | Pwo Western Karen | Myanmar script |
| `kvq` | Geba Karen | Myanmar script (non-Roman version) |
| `cnh` | Hakha Chin (Lai) | Latin script |
| `cfm` | Falam Chin | Latin script |
| `ctd` | Tedim Chin | Latin script |
| `eky` | Eastern Kayah | Kayah Li script (also handled by Unicode rule) |
| `shn` | Shan (Tai Yai) | Myanmar block, Shan extension subrange |
| `kac` | Jingphaw (Kachin) | Latin script |
| `mnw` | Mon | Myanmar script |

### Broader SE / South Asia

| Label | Language |
|---|---|
| `eng` | English |
| `hin` | Hindi |
| `khm` | Khmer |
| `lao` | Lao |
| `msa` | Malay |
| `tam` | Tamil |
| `tgl` | Tagalog |
| `tha` | Thai |
| `vie` | Vietnamese |
| `zho` | Chinese |

### Regional & script variants

| Label | Language |
|---|---|
| `ban` | Balinese (Latin) |
| `hnn` | Hanunoo |
| `sun` | Sundanese (Latin) |

## Script-rule freebies (27 labels)

These are detected by **Unicode-block check alone** — no ML, no training data
needed. Accurate by construction (deterministic).

### Already in the trained set, but caught by rule first (faster)

`hin` Devanagari · `tam` Tamil · `tha` Thai · `lao` Lao · `khm` Khmer · `eky` Kayah Li · `zho` CJK

### New labels added via script rule

| Label | Language | Script block |
|---|---|---|
| `kor` | Korean | Hangul (U+AC00–D7AF) |
| `jpn` | Japanese | Hiragana + Katakana |
| `ell` | Greek | Greek + Greek Extended |
| `heb` | Hebrew | Hebrew + presentation forms |
| `hye` | Armenian | Armenian |
| `kat` | Georgian | Georgian |
| `amh` | Amharic | Ethiopic |
| `sin` | Sinhala | Sinhala |
| `bod` | Tibetan | Tibetan |
| `chr` | Cherokee | Cherokee |
| `nqo` | N'Ko | N'Ko |
| `mon` | Mongolian (traditional script) | Mongolian |
| `vai` | Vai | Vai |
| `ff` | Fulani (Adlam) | Adlam |
| `mww` | Hmong | Pahawh Hmong |
| `bax` | Bamum | Bamum |
| `lep` | Lepcha | Lepcha |
| `lif` | Limbu | Limbu |
| `saz` | Saurashtra | Saurashtra |
| `bug` | Buginese | Buginese |
| `jav` | Javanese (script) | Javanese |
| `cjm` | Cham | Cham |
| `mni` | Meetei (Manipuri) | Meetei Mayek |
| `nod` | Lanna (Northern Thai) | Tai Tham |
| `sat` | Santali | Ol Chiki |
| `khb` | Tai Lue | New Tai Lue |
| `tdd` | Tai Nüa | Tai Le |

Adding more monopoly-script languages is a one-line addition to
`SCRIPT_RULES` in `ricelang/scripts.py` — see
[Hierarchical detector](../architecture/detector.md).

## Languages **not** supported

The following are deliberately omitted because text-only character-n-gram
detection cannot meaningfully distinguish them from a sibling language
already in the set (the text is often *literally identical*):

- **Indonesian (`ind`)** — shares ~80% vocabulary with `msa`. "Terima kasih"
  is grammatical Malay *and* grammatical Indonesian.
- **Rakhine (`rki`)** — uses the same Myanmar script as `mya` and many short
  phrases are interchangeable.
- **Chinese Traditional (`zho_hant`)** — most characters are identical to
  Simplified; the difference only shows up on a small set of specific
  characters.

For these cases, **caller-side metadata** (region, user profile, surrounding
text) is the right disambiguator, not the model.

## Mon detection

`mnw` is sourced from the **Mon Wikipedia dump** (135k paragraphs), not
YouVersion (Mon has no Bible on the platform). All other trained labels
come from YouVersion Bible scrapes.
