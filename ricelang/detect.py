"""Language detection.

Two-stage hierarchy:

1. **Unicode-script rule** (``ricelang.scripts.script_detect``) first.
   For monopoly scripts (Hangul -> kor, Hiragana -> jpn, Greek -> ell,
   Thai -> tha, Tamil -> tam, Devanagari -> hin, Kayah Li -> eky, ...)
   the script alone identifies the language -- no ML needed and no
   training data required.
2. **Trained fastText classifier** is only consulted when the text is
   in a shared script (Latin or Myanmar block), where multiple
   supported languages overlap and ML is actually necessary.

Text in a script not in the supported set (e.g. emoji, pure punctuation,
or scripts with no rule) returns ``None`` from ``detect`` when called
with ``fallback=None`` (the default), or whatever ``fallback`` value
the caller passes.
"""

from __future__ import annotations

from functools import lru_cache
from importlib.resources import files
from typing import Optional, Sequence

import fasttext

from .scripts import script_detect

_LABEL_PREFIX = "__label__"


@lru_cache(maxsize=1)
def _model() -> fasttext.FastText._FastText:
    fasttext.FastText.eprint = lambda x: None
    model_path = files("ricelang").joinpath("model/pdsdetect.ftz")
    return fasttext.load_model(str(model_path))


def predict(
    text: str | Sequence[str],
    k: int = 1,
    threshold: float = 0.0,
    on_unicode_error: str = "strict",
):
    """Return raw fastText predictions for `text` (string or list of strings).

    This always calls the ML classifier. For script-aware dispatch (which
    catches Korean / Japanese / Greek / etc. without the model), use
    :func:`detect`.
    """
    return _model().predict(text, k, threshold, on_unicode_error)


def _ml_label(text: str) -> str:
    labels, _probs = _model().predict(text)
    label = labels[0]
    return label[len(_LABEL_PREFIX):] if label.startswith(_LABEL_PREFIX) else label


def detect(text: str, fallback: Optional[str] = None) -> Optional[str]:
    """Return an ISO 639-3 language label for ``text``.

    Strategy:
      - If a monopoly Unicode-script rule fires (Korean, Japanese, Greek,
        Hebrew, Thai, Tamil, Hindi, ..., or any of the SE-Asia-specific
        scripts like Javanese, Cham, Meetei), return that label directly.
      - If the text is in Latin or the Myanmar block (shared scripts
        used by multiple supported languages), defer to the trained
        fastText classifier.
      - If neither — text contains no characters in any supported script
        — return ``fallback`` (default ``None``). Examples: emoji-only,
        garbage like "lkj qwerty 123", text in a script with no rule.

    A few labels also marked as "trained" are intentionally captured by
    the script rule first because their script is monopolistic in our
    label set (e.g. ``hin`` for Devanagari, ``zho`` for CJK without
    kana/Hangul, ``tha`` for Thai block, ``eky`` for Kayah Li). This
    means the classifier never runs for those, which is faster and more
    robust on very short input.
    """
    result = script_detect(text)
    if result is None:
        return fallback
    if result.startswith("__shared_"):
        return _ml_label(text)
    return result
