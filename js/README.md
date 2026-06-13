# ricelang

Regex-based **syllable tokenization** for Burmese and Myanmar-script ethnic
languages — **Karen, Mon, Shan**. A faithful JS/TS port of the syllable
tokenizer in the [`ricelang`](https://pypi.org/project/ricelang/) Python package.

Zero dependencies. Output matches the Python package token-for-token.

```bash
npm install ricelang
```

```ts
import { tokenize, syllables, hasMyanmar } from "ricelang"

tokenize("မလုပ်တတ်ဘူး")            // ["မ", "လုပ်", "တတ်", "ဘူး"]
tokenize("Khatta မလုပ်တတ်ဘူး")     // ["Khatta", "မ", "လုပ်", "တတ်", "ဘူး"]
tokenize("တၢ်မ့ၢ်တၢ်တီ", "karen")  // ["တၢ်", "မ့ၢ်", "တၢ်", "တီ"]
tokenize("မႂ်ႇသုင်ၶႃႈ", "shan")    // ["မႂ်ႇ", "သုင်", "ၶႃႈ"]

hasMyanmar("Khatta မလုပ်")          // true
```

## API

### `tokenize(text, lang?)` → `string[]`
Split into syllables. `lang` is one of `"mm"` (Burmese, default), `"karen"`,
`"mon"`, `"shan"`. Latin runs, digits and punctuation are kept as their own
tokens. `syllables` is an alias.

### `hasMyanmar(text)` → `boolean`
True if the text contains any Myanmar-family script character (main block +
Extended-A/B).

## Scope

Only the **regex syllable tokenizer** is ported. The Python package's CRF word
segmentation, BPE subwords, and fastText language detection rely on bundled
models and are not included here.

## License

MIT
