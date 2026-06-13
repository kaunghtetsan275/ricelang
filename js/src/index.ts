/**
 * ricelang — syllable tokenization for Burmese and Myanmar-script ethnic
 * languages (Karen, Mon, Shan). A faithful port of the regex-based syllable
 * tokenizer from the `ricelang` Python package (https://pypi.org/project/ricelang/).
 *
 * Only the regex syllable tokenizer is ported. The Python package's CRF word
 * segmentation, BPE, and fastText language detection require bundled models and
 * are out of scope here.
 */

export type Lang = "mm" | "karen" | "mon" | "shan"

// Consonant sets per language (verbatim from ricelang/tokenize.py).
const KAREN_CONSONANT = "ကခဂဃငစဆၡညတထဒနပဖဘမယရလဝသဟအဧၦ"
const SHAN_CONSONANT = "ၵၶငၸသၹၺတထၼပၽၾမယလဝရႁဢၷႀၻၿ"
const MON_CONSONANT = "ကခဂဃၚစဆဇၛညဋဌဍဎဏတထဒဓနပဖဗဘမယရလဝသဟဠၜအၝ"
const BURMESE_CONSONANT = "က-အ"
const OTHERS = "၀-၉၊။!-/:-@[-`{-~\\s."
const BURMESE_OTHERS = "ဣဤဥဦဧဩဪဿ၌၍၏၀-၉၊။!-/:-@[-`{-~\\s.,"

const VIRAMA = "္" // ္  (Myanmar sign virama / "stacker")
const ASAT = "်" // ်  (Myanmar sign asat)

// (?<![VIRAMA])([consonant])(?![ASAT VIRAMA])  |  ([others])
const BURMESE_SYLLABLE_RE = new RegExp(
  `(?<![${VIRAMA}])([${BURMESE_CONSONANT}])(?![${ASAT}${VIRAMA}])|([${BURMESE_OTHERS}])`,
  "gu",
)
const KAREN_SYLLABLE_RE = new RegExp(`([${KAREN_CONSONANT}])|([${OTHERS}])`, "gu")
const SHAN_SYLLABLE_RE = new RegExp(
  `([${SHAN_CONSONANT}])(?![${ASAT}${VIRAMA}])|([${OTHERS}])`,
  "gu",
)
const MON_SYLLABLE_RE = new RegExp(
  `(?<![${VIRAMA}])([${MON_CONSONANT}])(?![${ASAT}${VIRAMA}])|([${OTHERS}])`,
  "gu",
)

const LATIN_AFTER_BURMESE_RE = /(?<=[က-ၴ])([a-zA-Z0-9])/gu
const DIGIT_RUN_RE = /([0-9၀-၉])\s+([0-9၀-၉])\s*/gu
const DIGIT_PLUS_RE = /([0-9၀-၉])\s+(\+)/gu

const LANG_TO_RE: Record<Lang, RegExp> = {
  mm: BURMESE_SYLLABLE_RE,
  karen: KAREN_SYLLABLE_RE,
  shan: SHAN_SYLLABLE_RE,
  mon: MON_SYLLABLE_RE,
}

/** Any Myanmar-script codepoint (main block + extended-A/B). */
const MYANMAR_RE = /[က-႟ꧠ-꧿ꩠ-ꩿ]/u

/** True if the text contains any Myanmar-family script character. */
export function hasMyanmar(text: string): boolean {
  return MYANMAR_RE.test(text)
}

/**
 * Split `text` into syllables for a Myanmar-family language.
 * Latin runs and punctuation are kept as their own tokens (not split).
 */
export function tokenize(text: string, lang: Lang = "mm"): string[] {
  const pattern = LANG_TO_RE[lang]
  if (!pattern) throw new Error(`unsupported lang: ${lang}`)
  let line = text.replace(pattern, " $1$2").trim()
  line = line.replace(LATIN_AFTER_BURMESE_RE, " $1")
  line = line.replace(DIGIT_RUN_RE, "$1$2 ")
  line = line.replace(DIGIT_PLUS_RE, "$1 $2 ")
  return line.split(/\s+/).filter(Boolean)
}

/** Alias of {@link tokenize}. */
export const syllables = tokenize
