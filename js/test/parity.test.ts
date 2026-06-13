// Parity check: JS tokenizer output must match the Python ricelang package.
// Expected values are produced by ricelang (python) and pasted here.
import { tokenize } from "../src/index.ts"
import assert from "node:assert"

const CASES: [string, "mm" | "karen" | "mon" | "shan", string[]][] = [
  ["မလုပ်တတ်ဘူး", "mm", ["မ", "လုပ်", "တတ်", "ဘူး"]],
  [" မင်္ဂလာပါ", "mm", ["မင်္ဂ", "လာ", "ပါ"]],
  ["Khatta မလုပ်တတ်ဘူး", "mm", ["Khatta", "မ", "လုပ်", "တတ်", "ဘူး"]],
  ["ကမ္ဘာ", "mm", ["ကမ္ဘာ"]],
  ["တၢ်မ့ၢ်တၢ်တီ", "karen", ["တၢ်", "မ့ၢ်", "တၢ်", "တီ"]],
  ["ဘာသာမန်", "mon", ["ဘာ", "သာ", "မန်"]],
  ["မႂ်ႇသုင်ၶႃႈ", "shan", ["မႂ်ႇ", "သုင်", "ၶႃႈ"]],
]

let pass = 0
for (const [text, lang, expected] of CASES) {
  const got = tokenize(text, lang)
  assert.deepStrictEqual(got, expected, `tokenize(${JSON.stringify(text)}, ${lang})`)
  pass++
}
console.log(`parity ok: ${pass}/${CASES.length} cases match Python ricelang`)
