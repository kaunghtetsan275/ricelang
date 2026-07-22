"""Regression tests for demo UI metadata."""

from __future__ import annotations

import importlib.util


def test_demo_labels_do_not_collapse_mongolian_and_mon() -> None:
    """The detector label "mon" and tokenizer language "mon" need distinct names."""
    if importlib.util.find_spec("fastapi") is None:
        return

    from demo.server import lang_name

    assert lang_name("mon", context="detect") == "Mongolian (script)"
    assert lang_name("mon", context="syllable") == "Mon"

