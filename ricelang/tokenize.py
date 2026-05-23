"""Tokenization for Burmese, Karen, Mon, and Shan."""

from __future__ import annotations

import re
from functools import lru_cache
from importlib.resources import files
from typing import Literal

import pycrfsuite

Lang = Literal["mm", "karen", "mon", "shan"]
Form = Literal["syllable", "word", "bpe"]

_KAREN_CONSONANT = "ကခဂဃငစဆၡညတထဒနပဖဘမယရလဝသဟအဧၦ"
_SHAN_CONSONANT = "ၵၶငၸသၹၺတထၼပၽၾမယလဝရႁဢၷႀၻၿ"
_MON_CONSONANT = "ကခဂဃၚစဆဇၛညဋဌဍဎဏတထဒဓနပဖဗဘမယရလဝသဟဠၜအၝ"
_BURMESE_CONSONANT = "က-အ"
_OTHERS = r"၀-၉၊။!-/:-@[-`{-~\s."
_BURMESE_OTHERS = r"ဣဤဥဦဧဩဪဿ၌၍၏၀-၉၊။!-/:-@[-`{-~\s.,"

_BURMESE_SYLLABLE_RE = re.compile(
    f"(?<![္])([{_BURMESE_CONSONANT}])(?![်္])|([{_BURMESE_OTHERS}])"
)
_KAREN_SYLLABLE_RE = re.compile(f"([{_KAREN_CONSONANT}])|([{_OTHERS}])")
_SHAN_SYLLABLE_RE = re.compile(f"([{_SHAN_CONSONANT}])(?![်္])|([{_OTHERS}])")
_MON_SYLLABLE_RE = re.compile(
    f"(?<![္])([{_MON_CONSONANT}])(?![်္])|([{_OTHERS}])"
)

_LATIN_AFTER_BURMESE_RE = re.compile(r"(?<=[က-ၴ])([a-zA-Z0-9])")
_DIGIT_RUN_RE = re.compile(r"([0-9၀-၉])\s+([0-9၀-၉])\s*")
_DIGIT_PLUS_RE = re.compile(r"([0-9၀-၉])\s+(\+)")

_LANG_TO_RE = {
    "mm": _BURMESE_SYLLABLE_RE,
    "karen": _KAREN_SYLLABLE_RE,
    "shan": _SHAN_SYLLABLE_RE,
    "mon": _MON_SYLLABLE_RE,
}


@lru_cache(maxsize=1)
def _word_tagger() -> pycrfsuite.Tagger:
    tagger = pycrfsuite.Tagger()
    model_path = files("ricelang").joinpath("model/tokenizer.crfsuite")
    tagger.open(str(model_path))
    return tagger


@lru_cache(maxsize=None)
def _bpe_tokenizer(lang: str):
    """Lazy-load a bundled BPE tokenizer.

    ``lang="multi"`` loads the multilingual BPE; otherwise pass an ISO
    639-3 code that has a bundled ``bpe_<lang>.json`` (e.g. ``mya``,
    ``ksw``, ``cnh``).
    """
    from tokenizers import Tokenizer
    model_path = files("ricelang").joinpath(f"model/bpe_{lang}.json")
    if not model_path.is_file():
        raise ValueError(
            f"no bundled BPE tokenizer for lang={lang!r}; "
            f"expected ricelang/model/bpe_{lang}.json"
        )
    return Tokenizer.from_file(str(model_path))


def _char_features(sentence: str, i: int) -> list[str]:
    features = ["bias", f"char={sentence[i]}"]
    if i >= 1:
        features += [
            f"char-1={sentence[i-1]}",
            f"char-1:0={sentence[i-1]}{sentence[i]}",
        ]
    else:
        features.append("BOS")
    if i >= 2:
        features += [
            f"char-2={sentence[i-2]}",
            f"char-2:0={sentence[i-2]}{sentence[i-1]}{sentence[i]}",
            f"char-2:-1={sentence[i-2]}{sentence[i-1]}",
        ]
    if i >= 3:
        features += [
            f"char-3:0={sentence[i-3]}{sentence[i-2]}{sentence[i-1]}{sentence[i]}",
            f"char-3:-1={sentence[i-3]}{sentence[i-2]}{sentence[i-1]}",
        ]
    n = len(sentence)
    if i + 1 < n:
        features += [
            f"char+1={sentence[i+1]}",
            f"char:+1={sentence[i]}{sentence[i+1]}",
        ]
    else:
        features.append("EOS")
    if i + 2 < n:
        features += [
            f"char+2={sentence[i+2]}",
            f"char:+2={sentence[i]}{sentence[i+1]}{sentence[i+2]}",
            f"char+1:+2={sentence[i+1]}{sentence[i+2]}",
        ]
    if i + 3 < n:
        features += [
            f"char:+3={sentence[i]}{sentence[i+1]}{sentence[i+2]}{sentence[i+3]}",
            f"char+1:+3={sentence[i+1]}{sentence[i+2]}{sentence[i+3]}",
        ]
    return features


def _segment_word(sentence: str) -> str:
    sent = sentence.replace(" ", "")
    features = [_char_features(sent, i) for i in range(len(sent))]
    prediction = _word_tagger().tag(features)
    out = []
    for i, p in enumerate(prediction):
        if p == "1":
            out.append(" ")
        out.append(sent[i])
    return "".join(out)


def tokenize(text: str, lang: str = "mm", form: Form = "syllable") -> list[str]:
    """Tokenize `text` into syllables (default), words, or BPE subwords.

    - ``form="syllable"`` — regex-based syllable split. ``lang`` must be one
      of ``"mm"``, ``"karen"``, ``"mon"``, ``"shan"``.
    - ``form="word"`` — CRF-based word segmentation (Burmese only).
    - ``form="bpe"`` — Byte-Pair Encoding subwords. ``lang`` selects the
      bundled tokenizer: ``"multi"`` (default for BPE) uses the multilingual
      BPE; otherwise pass an ISO 639-3 code with a bundled model
      (``mya``, ``ksw``, ``pwo``, ``kvq``, ``cnh``, ``cfm``, ``ctd``,
      ``eky``, ``shn``).
    """
    if form == "word":
        return _segment_word(text).strip().split()
    if form == "bpe":
        bpe_lang = lang if lang in {"multi", "mya", "ksw", "pwo", "kvq",
                                    "cnh", "cfm", "ctd", "eky", "shn"} else "multi"
        return _bpe_tokenizer(bpe_lang).encode(text).tokens

    pattern = _LANG_TO_RE.get(lang)
    if pattern is None:
        raise ValueError(f"unsupported lang: {lang!r}")
    line = pattern.sub(r" \1\2", text).strip()
    line = _LATIN_AFTER_BURMESE_RE.sub(r" \1", line)
    line = _DIGIT_RUN_RE.sub(r"\1\2 ", line)
    line = _DIGIT_PLUS_RE.sub(r"\1 \2 ", line)
    return line.split()


# Back-compat: original API exposed a `Tokenize` class.
class Tokenize:  # pragma: no cover - thin shim
    def tokenize(self, line: str, lang: Lang = "mm", form: Form = "syllable") -> list[str]:
        return tokenize(line, lang, form)
