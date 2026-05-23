"""Smoke tests mirroring the examples from the README."""

import ricelang as pds


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


def test_detect_hakha_chin():
    # Lai (Hakha) Common Language Bible, Gen 1:1
    assert pds.detect("A hramthawk ah, Pathian nih van le vawlei a ser hna tikah,") == "cnh"


def test_detect_tedim_chin():
    # Tedim Bible Revision 2017, Gen 1:1
    assert pds.detect("A kipat cil-in Pasian in vantung le leitung a piangsak hi.") == "ctd"


def test_detect_falam_chin():
    # Falam Common Language Bible, Gen 1:1
    assert pds.detect("A hmaisabik ah Pathian in lei le van tla a seemsuah.") == "cfm"


def test_detect_pwo_karen():
    # Pwo Kayin Bible, Gen 1:1
    assert pds.detect("ယီၩမူၭခိၪအဘၩ့အမံ့ၬနီၪဖၩၭဆၧ်ပဍၧၩ်ဍၧၩ်လီၫ") == "pwo"


def test_detect_geba_karen():
    # Geba Non-Roman NT (kvq), Matt 1:1
    assert pds.detect("ယ့ၣ်​ရှူး​ခ​ရၱာ်, စီၤ​ဒၤ​ဝံး​အ​ဖဳး, စီၤ​အၤ​ဘြၤ​ဟၣ်​အ​ဖဳး​အ​တဲၤ​အီၣ်​လၤ") == "kvq"


def test_detect_broader_languages():
    # Sanity checks for the languages added in v0.3.x. Each is a Gen 1:1
    # opener from the bundled corpus.
    cases = [
        ("eng", "In the beginning God created the heavens and the earth."),
        ("hin", "आदि में परमेश्वर ने आकाश और पृथ्वी की सृष्टि की।"),
        ("khm", "នៅដើមដំបូងបង្អស់ ព្រះបានបង្កើតផ្ទៃមេឃ និងផែនដី។"),
        ("lao", "ໃນປະຖົມການ ພຣະເຈົ້າຊົງສ້າງສະຫວັນແລະແຜ່ນດິນໂລກ."),
        ("tam", "ஆதியிலே தேவன் வானத்தையும் பூமியையும் சிருஷ்டித்தார்."),
        ("tha", "ในปฐมกาล พระเจ้าทรงเนรมิตสร้างฟ้าและแผ่นดิน"),
        ("vie", "Ban đầu Đức Chúa Trời dựng nên trời đất."),
        ("zho", "起初，神创造天地。"),
        ("tgl", "Nang pasimula ay nilikha ng Diyos ang langit at ang lupa."),
    ]
    for expected, text in cases:
        assert pds.detect(text) == expected, f"{expected!r} text predicted {pds.detect(text)!r}"


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
    out = pds.tokenize("ဖေဖေနဲ့မေမေ၏ကျေးဇူးတရားမှာကြီးမားလှပေသည်", lang="mya", form="bpe")
    assert 5 <= len(out) <= 20
    assert "".join(out) == "ဖေဖေနဲ့မေမေ၏ကျေးဇူးတရားမှာကြီးမားလှပေသည်"


def test_tokenize_bpe_multilingual():
    # Multilingual BPE handles every supported script in one tokenizer.
    out = pds.tokenize("Pathian nih van le vawlei a ser hna tikah", form="bpe")
    assert "Pathian" in out


def test_tokenize_bpe_per_language():
    # Per-language BPEs exist for each ISO 639-3 code we have data for.
    for lang in ("mya", "ksw", "pwo", "kvq", "cnh", "cfm", "ctd", "eky", "shn"):
        out = pds.tokenize("test", lang=lang, form="bpe")
        assert isinstance(out, list) and len(out) > 0


def test_tokenize_bpe_unknown_lang_falls_back_to_multi():
    # Unknown lang should fall back to the multilingual BPE rather than raise.
    out = pds.tokenize("hello world", lang="not_a_lang", form="bpe")
    assert out == pds.tokenize("hello world", lang="multi", form="bpe")


def test_tokenize_word_burmese():
    out = pds.tokenize("ဖေဖေနဲ့မေမေ၏ကျေးဇူးတရားမှာကြီးမားလှပေသည်", form="word")
    assert out == [
        "ဖေဖေ", "နဲ့", "မေမေ", "၏", "ကျေးဇူးတရား",
        "မှာ", "ကြီးမား", "လှ", "ပေ", "သည်",
    ]
