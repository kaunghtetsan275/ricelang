"""Behavior covered by CLI documentation examples."""

from __future__ import annotations

import ricelang as rl


def test_latin_short_text_routes_to_classifier() -> None:
    assert rl.detect("hello") is not None

