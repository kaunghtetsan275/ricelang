# Zawgyi ↔ Unicode

Burmese has two competing encodings in the wild:

- **Unicode** (`mya`) — the international standard. Compliant with Unicode
  Myanmar block (U+1000–U+109F). Renders correctly on all modern devices.
- **Zawgyi** (`zgi`) — a legacy non-standard encoding that re-uses Unicode
  codepoints for visually-similar but semantically-different characters.
  Common on older devices and content from before ~2019. Not a separate
  language — same Burmese, different bytes.

ricelang provides round-trip conversion between them.

## Convert to Zawgyi

```python
import ricelang as rl

rl.cvt2zg("ထမင်းစားပြီးပြီလား")
# 'ထမင္းစားၿပီးၿပီလား'

# Alias for backwards compatibility with pyidaungsu:
rl.cvt2zgi("ထမင်းစားပြီးပြီလား")
# (same)
```

## Convert to Unicode

```python
rl.cvt2uni("ထမင္းစားၿပီးၿပီလား")
# 'ထမင်းစားပြီးပြီလား'
```

## When to convert

**Always normalize to Unicode before downstream NLP.** Tokenizers,
embeddings, search indexes, and LLMs are all trained on Unicode and will
treat Zawgyi text as garbage or a different language entirely.

Recommended pipeline for Burmese-bearing text:

```python
def normalize_burmese(text: str) -> str:
    if rl.detect(text) == "zgi":
        return rl.cvt2uni(text)
    return text
```

## From the CLI

```sh
ricelang convert --to uni "ထမင္းစားၿပီးၿပီလား"   # Zawgyi → Unicode
ricelang convert --to zg  "ထမင်းစားပြီးပြီလား"   # Unicode → Zawgyi
```

## Background

The Zawgyi font was developed in the 2000s before Burmese Unicode was widely
implemented. Because it stored characters in different positions than the
Unicode standard prescribes, the same byte sequences render differently
depending on which font interprets them. For ~15 years most Burmese text
online was Zawgyi-encoded. Myanmar mostly migrated to proper Unicode after
2019 (the "Migration Day" initiative), but legacy content and some user
inputs are still Zawgyi.

ricelang's conversion routines are direct adaptations of the original
pyidaungsu rule tables, regenerated programmatically so they're byte-perfect
with the upstream pyidaungsu 0.1.4 behavior.
