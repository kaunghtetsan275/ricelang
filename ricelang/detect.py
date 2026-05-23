"""Language detection backed by a fastText model."""

from __future__ import annotations

from functools import lru_cache
from importlib.resources import files
from typing import Sequence

import fasttext

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
    """Return raw fastText predictions for `text` (string or list of strings)."""
    return _model().predict(text, k, threshold, on_unicode_error)


def detect(text: str) -> str:
    """Return a short language code for `text`, e.g. ``"mm_uni"``, ``"karen"``."""
    labels, _probs = predict(text)
    label = labels[0]
    if label.startswith(_LABEL_PREFIX):
        return label[len(_LABEL_PREFIX):]
    return label
