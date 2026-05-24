"""ricelang — NLP helpers for Southeast Asian languages.

Language detection (Burmese Unicode/Zawgyi, S'gaw/Pwo/Geba Karen,
Hakha/Falam/Tedim Chin, Eastern Kayah, Shan), Burmese tokenization
(syllable/word/BPE), and Zawgyi <-> Unicode conversion.
"""

from .convert import cvt2uni, cvt2zg, cvt2zgi
from .detect import detect, predict
from .tokenize import Tokenize, tokenize

__version__ = "0.3.1"

__all__ = [
    "cvt2uni",
    "cvt2zg",
    "cvt2zgi",
    "detect",
    "predict",
    "tokenize",
    "Tokenize",
    "__version__",
]
