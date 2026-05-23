"""Zawgyi <-> Unicode conversion for Burmese text."""

from __future__ import annotations

from ._zawgyi_rules import UNI_TO_ZG, ZG_TO_UNI


def cvt2zg(text: str) -> str:
    """Convert Unicode Burmese to Zawgyi."""
    for pattern, repl in UNI_TO_ZG:
        text = pattern.sub(repl, text)
    return text


def cvt2uni(text: str) -> str:
    """Convert Zawgyi Burmese to Unicode."""
    for pattern, repl in ZG_TO_UNI:
        text = pattern.sub(repl, text)
    return text


# README documents `cvt2zgi`; keep as alias for backwards compatibility.
cvt2zgi = cvt2zg
