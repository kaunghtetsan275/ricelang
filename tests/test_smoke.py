"""Smoke tests mirroring the examples from the README."""

import pyidaungsu as pds


def test_detect_unicode_burmese():
    assert pds.detect("ထမင်းစားပြီးပြီလား") == "mya"


def test_detect_zawgyi_burmese():
    assert pds.detect("ထမင္းစားၿပီးၿပီလား") == "zgi"


def test_detect_karen():
    # ISO 639-3 label for S'gaw Karen (was "karen" in the pre-0.2.0 model)
    assert pds.detect("တၢ်သိၣ်လိတၢ်ဖးလံာ် ကွဲးလံာ်အိၣ်လၢ မ့ရ့ၣ်အစုပူၤလီၤ.") == "ksw"


def test_detect_eastern_kayah():
    assert pds.detect("ꤜꤤ꤬ꤣꤧ꤭ꤗꤢ꤬ ꤢ꤬ ꤚꤢ꤭ꤗꤢꤚꤢ꤭ꤒꤢꤩ꤭ ꤛꤢꤩ꤬ꤏꤛꤢꤨꤋꤚꤤ") == "eky"


def test_detect_shan():
    assert pds.detect("ၼႂ်းဢိူင်ႇမိူင်းၽူင်း ၸႄႈဝဵင်းတႃႈၶီႈလဵၵ်း ၾႆးမႆႈႁိူၼ်း") == "shn"


def test_zawgyi_roundtrip_to_unicode():
    assert pds.cvt2uni("ထမင္းစားၿပီးၿပီလား") == "ထမင်းစားပြီးပြီလား"


def test_unicode_to_zawgyi():
    assert pds.cvt2zg("ထမင်းစားပြီးပြီလား") == "ထမင္းစားၿပီးၿပီလား"


def test_cvt2zgi_alias_matches_readme():
    assert pds.cvt2zgi("ထမင်းစားပြီးပြီလား") == pds.cvt2zg("ထမင်းစားပြီးပြီလား")


def test_tokenize_syllable_burmese():
    out = pds.tokenize(
        "Alan TuringကိုArtificial Intelligenceနဲ့Computerတွေရဲ့ဖခင်ဆိုပြီးလူသိများပါတယ်"
    )
    assert out == [
        "Alan", "Turing", "ကို", "Artificial", "Intelligence",
        "နဲ့", "Computer", "တွေ", "ရဲ့", "ဖ", "ခင်", "ဆို",
        "ပြီး", "လူ", "သိ", "များ", "ပါ", "တယ်",
    ]


def test_tokenize_bpe_burmese():
    out = pds.tokenize("ဖေဖေနဲ့မေမေ၏ကျေးဇူးတရားမှာကြီးမားလှပေသည်", form="bpe")
    # Just sanity-check: BPE should split this into a handful of subwords,
    # each containing only Burmese characters, and round-tripping by
    # concatenation should reconstruct the input.
    assert 5 <= len(out) <= 20
    assert "".join(out) == "ဖေဖေနဲ့မေမေ၏ကျေးဇူးတရားမှာကြီးမားလှပေသည်"


def test_tokenize_word_burmese():
    out = pds.tokenize("ဖေဖေနဲ့မေမေ၏ကျေးဇူးတရားမှာကြီးမားလှပေသည်", form="word")
    assert out == [
        "ဖေဖေ", "နဲ့", "မေမေ", "၏", "ကျေးဇူးတရား",
        "မှာ", "ကြီးမား", "လှ", "ပေ", "သည်",
    ]
