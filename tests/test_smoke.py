"""Smoke tests mirroring the examples from the README."""

import pyidaungsu as pds


def test_detect_unicode_burmese():
    # Note: the bundled model emits "uni"/"zg" labels, not "mm_uni"/"mm_zg"
    # as the README claims. Matches behavior of original 0.1.4.
    assert pds.detect("ထမင်းစားပြီးပြီလား") == "uni"


def test_detect_zawgyi_burmese():
    assert pds.detect("ထမင္းစားၿပီးၿပီလား") == "zg"


def test_detect_karen():
    assert pds.detect("တၢ်သိၣ်လိတၢ်ဖးလံာ် ကွဲးလံာ်အိၣ်လၢ မ့ရ့ၣ်အစုပူၤလီၤ.") == "karen"


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


def test_tokenize_word_burmese():
    out = pds.tokenize("ဖေဖေနဲ့မေမေ၏ကျေးဇူးတရားမှာကြီးမားလှပေသည်", form="word")
    assert out == [
        "ဖေဖေ", "နဲ့", "မေမေ", "၏", "ကျေးဇူးတရား",
        "မှာ", "ကြီးမား", "လှ", "ပေ", "သည်",
    ]
