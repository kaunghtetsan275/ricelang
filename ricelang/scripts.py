"""Unicode-script rules for language detection.

For scripts that are used by exactly one language ("monopoly" scripts),
detection is a pure character-range check — no ML needed. This module
catches those cases before the trained classifier runs, both saving work
and giving correct answers for languages the classifier was never
trained on.

The dispatch table:
    ``script_detect(text)`` returns an ISO-639-3 label if a monopoly
    script dominates the text, ``"__shared_latin"`` / ``"__shared_mymr"``
    if the text is in a shared script that requires ML, or ``None`` if no
    supported script is found (out-of-scope text like garbage, emoji,
    pure punctuation).
"""

from __future__ import annotations

from typing import Optional

# A "monopoly" script rule. The detector returns ``label`` when the text
# meets ``predicate``. Order matters: rules are checked in declaration
# order, so put more specific rules first (e.g. Japanese before CJK).
#
# Each predicate gets a dict ``counts`` mapping range-id to char count,
# plus the original text length, and returns True/False.


def _block(lo: int, hi: int):
    """Return a predicate matching characters in [lo, hi]."""
    return lambda c: lo <= ord(c) <= hi


def _any_of(*ranges):
    """Predicate matching characters in any of the given ranges."""
    return lambda c: any(lo <= ord(c) <= hi for lo, hi in ranges)


# Each rule is (label, blocks, min_fraction, extra_condition).
#  - label:          ISO 639-3 code, or "__shared_..." for ML-needed
#  - blocks:         list of (lo, hi) inclusive Unicode codepoint ranges
#  - min_fraction:   fraction of non-ASCII-non-space chars that must be
#                    in `blocks` for the rule to fire
#  - extra_condition: optional callable(counts_dict, text) -> bool; used
#                    for tie-breakers (Japanese needs kana presence,
#                    Korean needs Hangul presence, etc.)


SCRIPT_RULES: list[tuple] = [
    # ----- highest priority: scripts that contain or co-exist with CJK -----
    # Japanese: kana is the disambiguator vs Chinese-only text
    (
        "jpn",
        # Hiragana, Katakana, Katakana Phonetic Extensions, half-width katakana,
        # plus CJK (kanji) -- but the rule fires only if kana is actually present
        [
            (0x3040, 0x309F),   # Hiragana
            (0x30A0, 0x30FF),   # Katakana
            (0x31F0, 0x31FF),   # Katakana Phonetic Extensions
            (0xFF65, 0xFF9F),   # Halfwidth Katakana
            (0x3400, 0x4DBF),   # CJK Unified Ext-A (Kanji)
            (0x4E00, 0x9FFF),   # CJK Unified Ideographs (Kanji)
            (0x20000, 0x2A6DF), # CJK Ext-B
        ],
        0.30,
        # Require at least one kana char so Chinese-only text doesn't trigger jpn.
        lambda counts, text: any(
            0x3040 <= ord(c) <= 0x30FF or 0x31F0 <= ord(c) <= 0x31FF or 0xFF65 <= ord(c) <= 0xFF9F
            for c in text
        ),
    ),

    # Korean: Hangul presence
    (
        "kor",
        [
            (0xAC00, 0xD7AF),   # Hangul Syllables
            (0x1100, 0x11FF),   # Hangul Jamo
            (0x3130, 0x318F),   # Hangul Compatibility Jamo
            (0xA960, 0xA97F),   # Hangul Jamo Extended-A
            (0xD7B0, 0xD7FF),   # Hangul Jamo Extended-B
            (0x3400, 0x4DBF),   # CJK (Hanja)
            (0x4E00, 0x9FFF),   # CJK
        ],
        0.30,
        # Require at least one actual Hangul codepoint
        lambda counts, text: any(
            (0xAC00 <= ord(c) <= 0xD7AF) or (0x1100 <= ord(c) <= 0x11FF)
            or (0x3130 <= ord(c) <= 0x318F) or (0xA960 <= ord(c) <= 0xA97F)
            or (0xD7B0 <= ord(c) <= 0xD7FF)
            for c in text
        ),
    ),

    # ----- single-language scripts (clean monopolies) -----
    ("ell", [(0x0370, 0x03FF), (0x1F00, 0x1FFF)], 0.30, None),   # Greek
    ("heb", [(0x0590, 0x05FF), (0xFB1D, 0xFB4F)], 0.30, None),   # Hebrew
    ("hye", [(0x0530, 0x058F), (0xFB13, 0xFB17)], 0.30, None),   # Armenian
    ("kat", [(0x10A0, 0x10FF), (0x2D00, 0x2D2F), (0x1C90, 0x1CBF)], 0.30, None),  # Georgian
    ("amh", [(0x1200, 0x137F), (0x1380, 0x139F), (0x2D80, 0x2DDF), (0xAB00, 0xAB2F)], 0.30, None),  # Ethiopic
    ("sin", [(0x0D80, 0x0DFF), (0x111E0, 0x111FF)], 0.30, None),  # Sinhala
    ("bod", [(0x0F00, 0x0FFF)], 0.30, None),                      # Tibetan
    ("chr", [(0x13A0, 0x13FF), (0xAB70, 0xABBF)], 0.30, None),    # Cherokee
    ("nqo", [(0x07C0, 0x07FF)], 0.30, None),                      # N'Ko (Mande)
    ("mon", [(0x1800, 0x18AF)], 0.30, None),                      # Mongolian (traditional)
    ("vai", [(0xA500, 0xA63F)], 0.30, None),                      # Vai
    ("ff",  [(0x1E900, 0x1E95F)], 0.30, None),                    # Adlam (Fulani)
    ("mww", [(0x16B00, 0x16B8F)], 0.30, None),                    # Pahawh Hmong
    ("bax", [(0xA6A0, 0xA6FF)], 0.30, None),                      # Bamum
    ("lep", [(0x1C00, 0x1C4F)], 0.30, None),                      # Lepcha
    ("lif", [(0x1900, 0x194F)], 0.30, None),                      # Limbu
    ("saz", [(0xA880, 0xA8DF)], 0.30, None),                      # Saurashtra
    ("bug", [(0x1A00, 0x1A1F)], 0.30, None),                      # Buginese

    # ----- SE Asia-specific monopolies -----
    ("jav", [(0xA980, 0xA9DF)], 0.30, None),                      # Javanese script
    ("cjm", [(0xAA00, 0xAA5F)], 0.30, None),                      # Cham
    ("mni", [(0xABC0, 0xABFF), (0xAAE0, 0xAAFF)], 0.30, None),    # Meetei Mayek
    ("nod", [(0x1A20, 0x1AAF)], 0.30, None),                      # Tai Tham / Lanna
    ("sat", [(0x1C50, 0x1C7F)], 0.30, None),                      # Ol Chiki (Santali)
    ("khb", [(0x1980, 0x19DF)], 0.30, None),                      # New Tai Lue (Sipsong Panna)
    ("tdd", [(0x1950, 0x197F)], 0.30, None),                      # Tai Le

    # ----- already-supported labels that are also script-monopoly -----
    # These would otherwise go to the ML model; handling them here is faster
    # and gives correct answers even on text the model hasn't seen.
    ("hin", [(0x0900, 0x097F), (0xA8E0, 0xA8FF)], 0.30, None),    # Devanagari -> Hindi
    ("tam", [(0x0B80, 0x0BFF), (0x11FC0, 0x11FFF)], 0.30, None),  # Tamil
    ("tha", [(0x0E00, 0x0E7F)], 0.30, None),                      # Thai
    ("lao", [(0x0E80, 0x0EFF)], 0.30, None),                      # Lao
    ("khm", [(0x1780, 0x17FF), (0x19E0, 0x19FF)], 0.30, None),    # Khmer
    ("eky", [(0xA900, 0xA92F)], 0.30, None),                      # Kayah Li
    # CJK without Hiragana/Hangul -> Chinese (already filtered for Japanese/Korean above)
    ("zho", [(0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0x20000, 0x2A6DF)], 0.30, None),

    # ----- shared scripts: hand off to ML -----
    # Myanmar block (Burmese, Shan, Mon, Karen variants, Kachin, Rakhine...)
    (
        "__shared_mymr",
        [
            (0x1000, 0x109F),   # Myanmar
            (0xAA60, 0xAA7F),   # Myanmar Extended-A
            (0xA9E0, 0xA9FF),   # Myanmar Extended-B
        ],
        0.30,
        None,
    ),
    # Latin (and ASCII): hand off to ML if dominant
    (
        "__shared_latin",
        [
            (0x0041, 0x005A),   # A-Z
            (0x0061, 0x007A),   # a-z
            (0x00C0, 0x024F),   # Latin-1 supplement + Latin Extended-A/B
            (0x1E00, 0x1EFF),   # Latin Extended Additional
            (0x2C60, 0x2C7F),   # Latin Extended-C
            (0xA720, 0xA7FF),   # Latin Extended-D
        ],
        0.30,
        None,
    ),
]


def _count_chars_in(text: str, blocks: list[tuple[int, int]]) -> int:
    n = 0
    for c in text:
        o = ord(c)
        for lo, hi in blocks:
            if lo <= o <= hi:
                n += 1
                break
    return n


def script_detect(text: str) -> Optional[str]:
    """Return a label, ``"__shared_latin"``, ``"__shared_mymr"``, or ``None``.

    - **Concrete ISO label** (e.g. ``"kor"``, ``"hin"``): the text is in a
      script used by only one language we care about. No ML needed.
    - **``"__shared_latin"`` / ``"__shared_mymr"``**: the text is dominantly
      in a shared script and needs the ML classifier to disambiguate.
    - **``None``**: no supported script dominates (e.g. emoji-only, pure
      punctuation, or text in some other script not in our table).
    """
    if not text:
        return None

    # Denominator: count only "scriptful" characters -- exclude whitespace,
    # control chars, and ASCII punctuation/digits. This lets short text
    # like "안녕" classify correctly even with trailing whitespace.
    scriptful = sum(
        1 for c in text
        if not c.isspace() and not (0x0020 <= ord(c) <= 0x002F)
        and not (0x003A <= ord(c) <= 0x0040)
        and not (0x005B <= ord(c) <= 0x0060)
        and not (0x007B <= ord(c) <= 0x007E)
        and ord(c) >= 0x0021
    )
    if scriptful == 0:
        return None

    for label, blocks, min_fraction, extra in SCRIPT_RULES:
        n = _count_chars_in(text, blocks)
        if n / scriptful < min_fraction:
            continue
        if extra is not None and not extra({}, text):
            continue
        return label
    return None


__all__ = ["script_detect", "SCRIPT_RULES"]
