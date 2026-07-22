# Language detection

```python
import ricelang as rl

rl.detect("ထမင်းစားပြီးပြီလား")   # 'mya'
rl.detect("안녕하세요")            # 'kor'   (via script-rule, no ML)
rl.detect("Pathian nih van")     # 'cnh'
rl.detect("🎉")                  #  None    (out of scope)
```

## `rl.detect(text, fallback=None)`

Returns an ISO 639-3 label, or `fallback` if no rule fires and the text isn't
in a supported shared script.

```python
rl.detect("hello")                        # Latin-script ML fires; short text may be ambiguous
rl.detect("🎉🎉🎉")                       # None
rl.detect("🎉🎉🎉", fallback="unknown")   # 'unknown'
```

The function consults the [hierarchical detector](../architecture/detector.md):

1. **Unicode-script rule** runs first. For monopoly scripts (Hangul, Hiragana,
   Greek, Hebrew, Thai, Tamil, Devanagari, …), the rule alone returns the
   label — no ML invoked.
2. **Trained classifier** runs only when text is in a shared script
   (Latin or the Myanmar block).
3. **`fallback`** is returned when no rule matches and the text isn't in a
   supported shared script.

## `rl.predict(text, k=1, threshold=0.0)`

Returns the raw fastText top-k as `(labels_tuple, probs_array)`. Unlike
`detect()`, this always calls the ML model — no script-rule shortcut.

```python
labels, probs = rl.predict("Pathian nih van", k=5)
# labels = ('__label__cnh', '__label__cfm', '__label__ctd', '__label__ksw', '__label__eng')
# probs  = array([1.0000, 0.0000, 0.0000, 0.0000, 0.0000])

# Strip the __label__ prefix
clean = [(l[9:], float(p)) for l, p in zip(labels, probs)]
```

Use `predict()` when you need:

- Top-k candidates with probabilities
- A confidence score to decide whether to trust the answer
- Batch prediction (`text` can be a list of strings)

## Output reliability tips

### Short text

Short strings (under ~10 characters in Latin or Myanmar block) are inherently
ambiguous because they may not contain discriminating n-grams. The model still
returns a label, but check the top-1 probability before trusting it on short
input.

```python
labels, probs = rl.predict("Ka dam", k=2)
# probably ('cnh', 'cfm') with probs (0.6, 0.4) — genuine ambiguity
```

### Mixed-script input

ricelang routes by the **dominant** script. Mixed-language strings ("Hello
[Burmese text]") will pick whichever script makes up >30% of the text.

```python
rl.detect("Hello, my name is...")              # 'eng'
rl.detect("hello မင်္ဂလာပါ")                    # 'mya' if mostly Burmese
```

If you have mixed-language documents, split into sentences first (sentence
segmentation is on the roadmap).

### Out-of-scope text

For text in scripts ricelang doesn't support (Cyrillic, Arabic, etc.) or
non-textual input (emoji, garbage), `detect()` returns `None`. This is
intentional — silent wrong predictions break downstream pipelines worse than
explicit "I don't know."

```python
rl.detect("Привет")        # None  (no Cyrillic rule)
rl.detect("مرحبا")         # None  (no Arabic rule)
rl.detect("😀😀")           # None
```

If you need worldwide language coverage, run [fasttext's `lid.176`](https://fasttext.cc/docs/en/language-identification.html)
as an upstream router and only call ricelang for SE/South Asian text.

## Performance

- **Cold start**: ~80ms (fastText model + a few BPE tokenizers lazy-load on
  first call)
- **Per-call**: ~0.1ms for script-rule paths, ~1ms for ML paths
- **Batched** (via `predict()` with a list): much higher throughput
- **No GPU, no network, no shared state** — safe in worker pools

## Sibling-language ambiguity (not supported)

A few languages are deliberately *not* in ricelang because text-only detection
can't disambiguate them from a sibling already in the set:

- Indonesian (`ind`) collides with Malay (`msa`) — `"Terima kasih"` is both
- Rakhine (`rki`) collides with Burmese (`mya`) on short phrases
- Chinese Traditional (`zho_hant`) collides with Simplified (`zho`)

See [Supported languages](languages.md) for the rationale.
