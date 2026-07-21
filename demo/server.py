"""Minimal FastAPI demo for ricelang.

Exposes every public function in the library as an HTTP endpoint plus a
single-page form-based UI at ``/``. Interactive API docs at ``/docs``.

Run:

    uv run --group demo uvicorn demo.server:app --reload --port 8000
"""

from __future__ import annotations

import random

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

import ricelang as rl

app = FastAPI(
    title="ricelang demo",
    version=rl.__version__,
    description="Try every function in the ricelang library.",
)

SYLLABLE_LANGS = ["mm", "karen", "mon", "shan"]
BPE_LANGS = [
    "multi",
    # SE Asian minority
    "mya", "ksw", "pwo", "kvq", "cnh", "cfm", "ctd", "eky", "shn",
    # broader SE / South Asian
    "eng", "hin", "khm", "lao", "msa", "tam", "tgl", "tha", "vie", "zho",
    # regional / script variants
    "ban", "hnn", "kac", "mnw", "sun",
]
DETECT_LABELS = [
    # SE Asian minority
    "mya", "zgi", "ksw", "pwo", "kvq", "cnh", "cfm", "ctd", "eky", "shn",
    # broader SE / South Asian
    "eng", "hin", "khm", "lao", "msa", "tam", "tgl", "tha", "vie", "zho",
    # regional / script variants
    "ban", "hnn", "kac", "mnw", "sun",
    # script-monopoly freebies (Unicode-range detection, no ML)
    "kor", "jpn", "ell", "heb", "hye", "kat", "amh", "sin", "bod",
    "chr", "nqo", "mon", "vai", "ful", "mww", "bax", "lep", "lif",
    "saz", "bug", "jav", "cjm", "mni", "nod", "sat", "khb", "tdd",
]

LANG_NAMES: dict[str, str] = {
    # SE Asian minority
    "mya": "Burmese (Unicode)",
    "zgi": "Burmese (Zawgyi)",
    "ksw": "S'gaw Karen",
    "pwo": "Pwo Karen",
    "kvq": "Geba Karen",
    "cnh": "Hakha Chin",
    "cfm": "Falam Chin",
    "ctd": "Tedim Chin",
    "eky": "Eastern Kayah",
    "shn": "Shan (Tai Yai)",
    # broader SE / South Asian
    "eng": "English",
    "hin": "Hindi",
    "khm": "Khmer",
    "lao": "Lao",
    "msa": "Malay",
    "tam": "Tamil",
    "tgl": "Tagalog",
    "tha": "Thai",
    "vie": "Vietnamese",
    "zho": "Chinese",
    # regional / script variants
    "ban": "Balinese",
    "hnn": "Hanunoo",
    "kac": "Jingphaw (Kachin)",
    "mnw": "Mon",
    "sun": "Sundanese",
    # script-monopoly free labels (no training data needed; Unicode-rule)
    "kor": "Korean",
    "jpn": "Japanese",
    "ell": "Greek",
    "heb": "Hebrew",
    "hye": "Armenian",
    "kat": "Georgian",
    "amh": "Amharic",
    "sin": "Sinhala",
    "bod": "Tibetan",
    "chr": "Cherokee",
    "nqo": "N'Ko",
    "mon": "Mongolian (script)",
    "vai": "Vai",
    "ful": "Fulani (Adlam)",
    "mww": "Hmong (Pahawh)",
    "bax": "Bamum",
    "lep": "Lepcha",
    "lif": "Limbu",
    "saz": "Saurashtra",
    "bug": "Buginese",
    "jav": "Javanese (script)",
    "cjm": "Cham",
    "mni": "Meetei (Manipuri)",
    "nod": "Lanna (Tai Tham)",
    "sat": "Santali (Ol Chiki)",
    "khb": "Tai Lue",
    "tdd": "Tai Nüa",
    # special BPE code
    "multi": "Multilingual",
}

SYLLABLE_LANG_NAMES: dict[str, str] = {
    "mm": "Burmese",
    "karen": "Karen",
    "mon": "Mon",
    "shan": "Shan",
}


def lang_name(code: str, context: str = "detect") -> str:
    if context == "syllable":
        return SYLLABLE_LANG_NAMES.get(code, code)
    return LANG_NAMES.get(code, code)

# Curated short samples — one ~hello/short phrase + one longer sentence per
# language. The /sample/{lang} endpoint picks one at random.
SAMPLES: dict[str, list[str]] = {
    "mya": [
        "မင်္ဂလာပါ",
        "ထမင်းစားပြီးပြီလား",
        "ဖေဖေနဲ့မေမေ၏ကျေးဇူးတရားမှာကြီးမားလှပေသည်",
        "ဒီနေ့မိုးရွာနေတယ်",
    ],
    "zgi": [
        "မဂၤလာပါ",
        "ထမင္းစားၿပီးၿပီလား",
        "ေက်းဇူးတင္ပါတယ္",
    ],
    "ksw": [
        "မ်ဟၤလူၤ",
        "တၢ်ဘျုးလီၤ",
        "လူၤစံယၤ အခီၣ်စ့ၣ်တကပၤ တဂ့ၤလၢၤဘၣ်",
        "ပှၤကီၢ်ယူဒၤဖိတဖၣ်စးထီၣ်ပူာ်ထီၣ်လီၤ",
    ],
    "pwo": [
        "ထါးသၬလၩ",
        "ယီၩမူၭခိၪအဘၩ့အမံ့ၬနီၪဖၩၭဆၧ်ပဍၧၩ်ဍၧၩ်လီၫ",
    ],
    "kvq": [
        "ယ့ၣ်​ရှူး​ခ​ရၱာ်, စီၤ​ဒၤ​ဝံး​အ​ဖဳး, စီၤ​အၤ​ဘြၤ​ဟၣ်​အ​ဖဳး​အ​တဲၤ​အီၣ်​လၤ",
    ],
    "cnh": [
        "Hawi le hna Bible background tihi zeitindah kan let hnga?",
        "Financial abuse hi zeitin dah holh leh ah a tthat bik hnga pls?",
        "Tukum kha minung soktu tlawmtuk ruangah kai a silo.",
        "Hi kong ah cathluan chuahpitu ding minung 10 lengkai an si cang, Kanmah Chin miphun chung in ramleng ah Master le Ph D \"kai liomi siseh, ramleng mi in si hna seh, NGOs riantuanmi tbk. in an si lai.",
        "Hihi tlamtlin khawhnak ah, Sena Galazzi Lian he kan tawlrel cuahmahmi a si.",
    ],
    "cfm": [
        "Dothleng nak ah kan Lung rual lo ruangah Hiram kaipawl dung a sip sung nak si.",
        "CHIN AI & Transalate App cu Android & ISO Phone hmangtu hrang aw download dan ding a DOTDOT a um mi siar hmaisa ta in hmang nuam aw.",
        "Laitlang thlatang khawsik",
        "kan zuk tlang mi a hlon maw si",
        "PATHIAN lam hruainak in Chin kumthar kan thleng leh sal ih kan zaten dam le cak in kan um cio maw?",
    ],
    "ctd": [
        "Pasian",
        "A kipat cil-in Pasian in vantung le leitung a piangsak hi.",
    ],
    "eky": [
        "ꤞꤤ꤭",
        "ꤜꤤ꤬ꤣꤧ꤭ꤗꤢ꤬ ꤢ꤬ ꤚꤢ꤭ꤗꤢꤚꤢ꤭ꤒꤢꤩ꤭ ꤛꤢꤩ꤬ꤏꤛꤢꤨꤋꤚꤤ",
    ],
    "shn": [
        "မႂ်ႇသုင်",
        "ၶွပ်ႈၸႂ်",
        "ၼႂ်းဢိူင်ႇမိူင်းၽူင်း ၸႄႈဝဵင်းတႃႈၶီႈလဵၵ်း ၾႆးမႆႈႁိူၼ်း",
    ],
    "eng": [
        "Hello, how are you?",
        "In the beginning God created the heavens and the earth.",
        "For God so loved the world that he gave his one and only Son.",
    ],
    "hin": [
        "नमस्ते",
        "धन्यवाद",
        "आदि में परमेश्वर ने आकाश और पृथ्वी की सृष्टि की।",
    ],
    "khm": [
        "សួស្ដី",
        "អរគុណច្រើន",
        "នៅដើមដំបូង​បង្អស់ ព្រះ​បាន​បង្កើត​ផ្ទៃ​មេឃ និង​ផែនដី។",
    ],
    "lao": [
        "ສະບາຍດີ",
        "ຂອບໃຈຫຼາຍໆ",
        "ໃນປະຖົມການ ພຣະເຈົ້າຊົງສ້າງສະຫວັນແລະແຜ່ນດິນໂລກ.",
    ],
    "msa": [
        "Selamat petang",
        "Terima kasih",
        "Pada mulanya Allah menciptakan langit dan bumi.",
    ],
    "tam": [
        "வணக்கம்",
        "நன்றி",
        "ஆதியிலே தேவன் வானத்தையும் பூமியையும் சிருஷ்டித்தார்.",
    ],
    "tgl": [
        "Magandang umaga",
        "Salamat po",
        "Nang pasimula ay nilikha ng Diyos ang langit at ang lupa.",
    ],
    "tha": [
        "สวัสดีครับ",
        "ขอบคุณมากครับ",
        "ในปฐมกาล พระเจ้าทรงเนรมิตสร้างฟ้าและแผ่นดิน",
    ],
    "vie": [
        "Xin chào",
        "Cảm ơn rất nhiều",
        "Ban đầu Đức Chúa Trời dựng nên trời đất.",
    ],
    "zho": [
        "你好",
        "谢谢",
        "起初，神创造天地。",
    ],
    "mnw": [
        "နူ ဝဳကဳပဳဒဳယာဏအ် ဒုင်တၠုင်ဏာရအဴ။",
        "ပြကိုဟ်ဗိသ္တာ မသက္ကုင္ၚုဟ်မး ဝွံ ညးလဵုဟွံဟီု လုပ်ပလေဝ်ဒါန် ချူမာန်ရ။",
        "ပရူပရာ သီုဖအိုတ် ဂှ် နဘာသာမန် ဗှ်လ္ၚတ်ကေတ်မာန်ရ။",
    ],
    "ban": [
        "Sanun ceninge idup, tan urungan cening lakar negen karma palan raos ceninge.",
        "Duking purwakala Ida Sang Hyang Widi Wasa ngwentenang akasa miwah pretiwine.",
    ],
    "hnn": [
        "Sa kabag-u linalang Diyus ti langit hanggan ti kalibutan.",
        "Dahil alam nida tanan ti Panginuun ti nagbuwat inda.",
    ],
    "kac": [
        "Shawng ningpawt e, Karai Kasang gaw ninggawn tawa shingra hpe hpan da ai.",
        "Dai Madu Israela a Karai Kasang gaw",
    ],
    "sun": [
        "Nalika Allah nyiptakeun jagat raya,",
        "Sagala rupa di Israil anu geus dibaktikeun ka Kami tanpa sarat, eta oge keur maneh.",
    ],
    # Script-monopoly freebies (greetings; Unicode-rule detection makes
    # the model never look at the trained classifier for these).
    "kor": ["안녕하세요 반갑습니다", "감사합니다", "한국어를 할 수 있습니다"],
    "jpn": ["こんにちは、ありがとうございます", "日本語ができますか", "おはようございます"],
    "ell": ["Γεια σας, τι κάνετε;", "Καλημέρα", "Ευχαριστώ πολύ"],
    "heb": ["שלום עולם", "תודה רבה", "בוקר טוב"],
    "hye": ["Բարեւ ձեզ", "Շնորհակալություն", "Բարի լույս"],
    "kat": ["გამარჯობა", "მადლობა", "დილა მშვიდობისა"],
    "amh": ["ሰላም እንዴት ነህ", "አመሰግናለሁ", "እንኳን ደህና መጣህ"],
    "sin": ["ආයුබෝවන්", "ස්තූතියි", "සුභ උදෑසනක්"],
    "bod": ["བཀྲ་ཤིས་བདེ་ལེགས།", "ཐུགས་རྗེ་ཆེ།", "ཞོགས་པ་བདེ་ལེགས།"],
    "chr": ["ᎣᏏᏲ", "ᏩᏙ"],
    "nqo": ["ߊߟߏ߫"],
    "mon": ["ᠰᠠᠶᠢᠨ ᠪᠠᠶᠢᠨ᠎ᠠ"],
    "jav": ["ꦱꦸꦒꦼꦁ ꦫꦮꦸꦃ"],
    "cjm": ["ꨧꨤꨩꨠ"],
    "mni": ["ꯈꯨꯔꯨꯝꯖꯔꯤ"],
    "nod": ["ᨪᩣ᩠ᨿᨡᩬᩁ"],
    "sat": ["ᱡᱚᱦᱟᱨ"],
    "khb": ["ᦌᦱᧈᦟᦴᧉᧁᦱᧈ"],
    "tdd": ["ᥑᥩᥒᥱᥖᥬᥱ"],
    "vai": ["ꕒꕎ"],
    "ful": ["𞤧𞤢𞤤𞤢𞥄𞤥"],
    "mww": ["𖬓𖬰𖬪𖬰𖬢"],
    "bax": ["ꚠꚡ"],
    "lep": ["ᰀᰕᰒ"],
    "lif": ["ᤛᤣᤘᤠ"],
    "saz": ["ꢂꢫꢼꢰ"],
    "bug": ["ᨔᨙᨒᨆᨙ"],
}


class TextIn(BaseModel):
    text: str


class TokenizeIn(BaseModel):
    text: str
    lang: str = "mm"
    form: str = "syllable"  # "syllable" | "word" | "bpe"


class PredictIn(BaseModel):
    text: str
    k: int = 3


@app.get("/info")
def info():
    return {
        "version": rl.__version__,
        "detect_labels": DETECT_LABELS,
        "syllable_langs": SYLLABLE_LANGS,
        "bpe_langs": BPE_LANGS,
        "sample_langs": sorted(SAMPLES),
    }


@app.get("/sample/{lang}")
def sample(lang: str):
    if lang not in SAMPLES:
        raise HTTPException(404, f"no samples for lang={lang!r}")
    return {"lang": lang, "text": random.choice(SAMPLES[lang])}


@app.post("/detect")
def detect(body: TextIn):
    return {"label": rl.detect(body.text)}


@app.post("/predict")
def predict(body: PredictIn):
    labels, probs = rl.predict(body.text, k=body.k)
    out = [
        {"label": label[len("__label__"):], "prob": float(prob)}
        for label, prob in zip(labels, probs)
    ]
    return {"predictions": out}


@app.post("/convert/zg")
def to_zawgyi(body: TextIn):
    return {"zawgyi": rl.cvt2zg(body.text)}


@app.post("/convert/uni")
def to_unicode(body: TextIn):
    return {"unicode": rl.cvt2uni(body.text)}


@app.post("/tokenize")
def tokenize(body: TokenizeIn):
    tokens = rl.tokenize(body.text, lang=body.lang, form=body.form)
    return {"tokens": tokens, "count": len(tokens)}


# ---------------------------------------------------------------------------
# Single-page form UI
# ---------------------------------------------------------------------------

INDEX_HTML = """<!doctype html>
<html lang="en"><head>
<meta charset="utf-8">
<title>ricelang</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
  :root{
    --bg:#fafafa;
    --fg:#111;
    --muted:#666;
    --soft:#999;
    --line:#e5e5e5;
    --accent:#0a7;
    --mono:"JetBrains Mono",ui-monospace,SFMono-Regular,Menlo,monospace;
  }
  *{box-sizing:border-box}
  html,body{margin:0;padding:0}
  body{
    background:var(--bg);
    color:var(--fg);
    font:13px/1.5 var(--mono);
    min-height:100vh;
  }
  main{max-width:780px;margin:0 auto;padding:2.5rem 1.5rem 4rem}
  a{color:var(--accent);text-decoration:none}
  a:hover{text-decoration:underline}

  header{
    display:flex;align-items:baseline;justify-content:space-between;gap:1rem;
    padding-bottom:1rem;margin-bottom:2.5rem;border-bottom:1px solid var(--line);
  }
  h1{
    font:500 1.2rem/1 var(--mono);
    margin:0;letter-spacing:-0.01em;
  }
  h1 .v{color:var(--soft);font-weight:400;margin-left:.5rem}
  header nav{font-size:12px;color:var(--muted)}
  header nav a{color:var(--muted);margin-left:1rem}

  section{margin-bottom:3rem}
  h2{
    font:500 13px/1 var(--mono);
    text-transform:uppercase;letter-spacing:.1em;color:var(--muted);
    margin:0 0 .75rem;
  }
  h2::before{content:"# ";color:var(--soft)}

  .card{
    background:#fff;border:1px solid var(--line);border-radius:3px;overflow:hidden;
  }
  textarea{
    display:block;width:100%;min-height:4rem;padding:.75rem .9rem;
    border:none;background:transparent;color:var(--fg);
    font:13px/1.55 var(--mono);resize:vertical;outline:none;
  }
  textarea:focus{background:#fcfcfc}

  .controls{
    display:flex;flex-wrap:wrap;align-items:center;gap:.5rem;
    padding:.5rem .75rem;border-top:1px solid var(--line);background:#fafafa;
    font-size:12px;
  }
  .controls .grow{flex:1}
  .control-group{display:inline-flex;align-items:center;gap:.4rem;color:var(--muted)}
  select{
    font:12px/1 var(--mono);background:#fff;border:1px solid var(--line);
    color:var(--fg);padding:.2rem .4rem;border-radius:2px;cursor:pointer;
  }
  select:focus{outline:1px solid var(--accent);outline-offset:0}

  button.primary{
    font:500 12px/1 var(--mono);letter-spacing:.02em;
    background:var(--fg);color:var(--bg);border:1px solid var(--fg);
    padding:.35rem .8rem;border-radius:2px;cursor:pointer;
  }
  button.primary:hover{background:var(--accent);border-color:var(--accent)}
  button.primary.ghost{background:transparent;color:var(--fg)}
  button.primary.ghost:hover{background:var(--fg);color:var(--bg)}

  /* sample picker = a single <select> at the top of the input card */
  .picker{
    display:flex;align-items:center;gap:.4rem;
    padding:.4rem .75rem;border-bottom:1px solid var(--line);
    background:#fafafa;
    font-size:12px;color:var(--muted);
  }
  .picker select{
    flex:1;font:12px/1.3 var(--mono);
    background:#fff;border:1px solid var(--line);color:var(--fg);
    padding:.2rem .4rem;border-radius:2px;cursor:pointer;
  }
  .picker .label{color:var(--soft);font-size:11px}

  /* output */
  .out{margin-top:.85rem;min-height:0}
  .out:empty{display:none}
  .out.text{
    font:13px/1.55 var(--mono);padding:.7rem .9rem;
    background:#fff;border:1px solid var(--line);border-radius:3px;word-break:break-word;
  }
  .out.pills{display:flex;flex-wrap:wrap;gap:.4rem;align-items:stretch}
  .err{color:#c00;font-size:12px;padding:.4rem 0}

  /* pills - flat, mono, no rounded corners */
  .pill{
    display:inline-flex;flex-direction:column;align-items:flex-start;gap:.1rem;
    padding:.4rem .6rem;
    background:#fff;border:1px solid var(--line);border-radius:2px;
    font-size:12px;
  }
  .pill .label{font-weight:500;color:var(--fg);white-space:nowrap}
  .pill .code{color:var(--soft);font-size:10.5px}
  .pill .prob{color:var(--muted);font-size:11px;font-variant-numeric:tabular-nums;margin-top:.1rem}
  .pill.top{background:var(--fg);border-color:var(--fg);padding:.55rem .8rem}
  .pill.top .label{color:var(--bg);font-size:14px}
  .pill.top .code{color:var(--accent)}
  .pill.top .prob{color:#bbb}

  /* token pills - JS sets bg/color inline */
  .pill.token{
    flex-direction:row;align-items:center;
    padding:.2rem .45rem;gap:0;
    font-size:12px;line-height:1.3;
    border-radius:2px;border:1px solid transparent;
  }
  .count{color:var(--soft);font-size:11px;margin-left:.5rem;align-self:center}

  @media (max-width:560px){
    main{padding:1.5rem 1rem 3rem}
    .samples .group-label{flex:1 1 100%}
  }
</style></head><body>
<main>
  <header>
    <h1>ricelang<span class="v">v__VERSION__</span></h1>
    <nav>
      <a href="/docs">/docs</a>
      <a href="https://github.com/kaunghtetsan275/ricelang">github</a>
      <a href="https://pypi.org/project/ricelang/">pypi</a>
    </nav>
  </header>

  <section>
    <h2>detect</h2>
    <div class="card">
      <div class="picker">
        <span class="label">try</span>
        <select id="d_pick" data-input="d_in" data-action="auto"></select>
      </div>
      <textarea id="d_in">ထမင်းစားပြီးပြီလား</textarea>
      <div class="controls">
        <span class="grow"></span>
        <button class="primary ghost" onclick="doDetect()">detect</button>
        <button class="primary" onclick="doPredict()">predict · top 5</button>
      </div>
    </div>
    <div id="d_out" class="out pills"></div>
  </section>

  <section>
    <h2>convert · zawgyi ↔ unicode</h2>
    <div class="card">
      <div class="picker">
        <span class="label">try</span>
        <select id="c_pick" data-input="c_in" data-action="convert"></select>
      </div>
      <textarea id="c_in">ထမင်းစားပြီးပြီလား</textarea>
      <div class="controls">
        <span class="grow"></span>
        <button class="primary ghost" onclick="doConvert('zg')">→ zawgyi</button>
        <button class="primary" onclick="doConvert('uni')">→ unicode</button>
      </div>
    </div>
    <div id="c_out" class="out text"></div>
  </section>

  <section>
    <h2>tokenize</h2>
    <div class="card">
      <div class="picker">
        <span class="label">try</span>
        <select id="t_pick" data-input="t_in" data-action="tokenize"></select>
      </div>
      <textarea id="t_in">ဖေဖေနဲ့မေမေ၏ကျေးဇူးတရားမှာကြီးမားလှပေသည်</textarea>
      <div class="controls">
        <span class="control-group">form
          <select id="t_form">
            <option value="syllable">syllable</option>
            <option value="word">word</option>
            <option value="bpe">bpe</option>
          </select>
        </span>
        <span class="control-group">lang
          <select id="t_lang">
            <optgroup label="syllable">__SYL_OPTS__</optgroup>
            <optgroup label="bpe">__BPE_OPTS__</optgroup>
          </select>
        </span>
        <span class="grow"></span>
        <button class="primary" onclick="doTokenize()">tokenize</button>
      </div>
    </div>
    <div id="t_out" class="out pills"></div>
  </section>
</main>

<script>
const $ = id => document.getElementById(id);
const val = id => $(id).value;
const sel = id => $(id).value;

const LANG_NAMES = __LANG_NAMES_JSON__;
const GROUPS = __GROUPS_JSON__;          // [{label, langs}, ...]
const CONVERT_LANGS = ["mya", "zgi"];

// Map a group's `action` (or "auto" = use group's own) to a handler.
// Handlers read input directly from their textarea.
const ACTIONS = {
  detect:   () => doDetect(),
  predict:  () => doPredict(),
  convert:  () => doConvert("zg"),
  tokenize: () => doTokenize(),
};

// Populate a <select> with optgroup'd options from GROUPS, then run
// the action whenever the user picks a language.
function wirePicker(selectId, groups) {
  const sel = $(selectId);
  const inputId = sel.dataset.input;
  const dataAction = sel.dataset.action;  // "auto" or a specific action

  // placeholder option
  const ph = document.createElement("option");
  ph.value = ""; ph.textContent = "load a sample…";
  ph.disabled = true; ph.selected = true;
  sel.appendChild(ph);

  groups.forEach(g => {
    const og = g.label
      ? document.createElement("optgroup")
      : sel;
    if (g.label) { og.label = g.label; sel.appendChild(og); }
    g.langs.forEach(lang => {
      const opt = document.createElement("option");
      opt.value = lang;
      opt.dataset.action = g.action || "";
      opt.textContent = LANG_NAMES[lang] || lang;
      og.appendChild(opt);
    });
  });

  sel.addEventListener("change", async () => {
    const lang = sel.value;
    if (!lang) return;
    const action = dataAction === "auto"
      ? (sel.options[sel.selectedIndex].dataset.action || "detect")
      : dataAction;
    const r = await fetch(`/sample/${lang}`);
    if (!r.ok) return;
    const {text} = await r.json();
    $(inputId).value = text;
    if (ACTIONS[action]) ACTIONS[action]();
    sel.selectedIndex = 0;  // reset to placeholder
  });
}
wirePicker("d_pick", GROUPS);
wirePicker("c_pick", [{label: null, action: "convert", langs: CONVERT_LANGS}]);
wirePicker("t_pick", GROUPS);
const escape = s => s.replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

async function post(url, body) {
  const r = await fetch(url, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)});
  if (!r.ok) throw new Error((await r.json()).detail || r.statusText);
  return await r.json();
}

function show(outId, html) { $(outId).innerHTML = html; }
function err(outId, e) { $(outId).innerHTML = `<div class="err">${escape(e.message)}</div>`; }

function langPill(code, {top = false, prob = null} = {}) {
  const name = LANG_NAMES[code] || code;
  const probHtml = prob == null ? "" : `<span class="prob">${(prob*100).toFixed(1)}%</span>`;
  return `<span class="pill${top?' top':''}">` +
         `<span class="label">${escape(name)}</span>` +
         `<span class="code">${escape(code)}</span>` +
         probHtml + `</span>`;
}

async function doDetect() {
  try { const {label} = await post("/detect", {text: val("d_in")});
        show("d_out", langPill(label, {top: true})); }
  catch(e) { err("d_out", e); }
}

async function doPredict() {
  try {
    const {predictions} = await post("/predict", {text: val("d_in"), k: 5});
    const pills = predictions.map((p, i) =>
      langPill(p.label, {top: i===0, prob: p.prob})
    ).join("");
    show("d_out", pills);
  } catch(e) { err("d_out", e); }
}

async function doConvert(kind) {
  try {
    const data = await post(`/convert/${kind}`, {text: val("c_in")});
    const text = data.zawgyi ?? data.unicode ?? "";
    show("c_out", escape(text));
  } catch(e) { err("c_out", e); }
}

// Stable hash so identical tokens get identical colors across the row.
function tokenColor(t) {
  let h = 0;
  for (const c of t) h = ((h * 31 + c.charCodeAt(0)) >>> 0) % 360;
  return {bg: `hsl(${h}, 65%, 90%)`, fg: `hsl(${h}, 55%, 25%)`, br: `hsl(${h}, 45%, 72%)`};
}

async function doTokenize() {
  try {
    const {tokens, count} = await post("/tokenize",
      {text: val("t_in"), form: sel("t_form"), lang: sel("t_lang")});
    const pills = tokens.map(t => {
      const c = tokenColor(t);
      return `<span class="pill token" style="background:${c.bg};color:${c.fg};border-color:${c.br}">${escape(t)}</span>`;
    }).join("");
    show("t_out", pills + `<span class="count">${count} tokens</span>`);
  } catch(e) { err("t_out", e); }
}
</script>
</body></html>"""


@app.get("/", response_class=HTMLResponse)
def index():
    import json

    def opt(code: str, context: str = "detect") -> str:
        name = lang_name(code, context=context)
        # "Name (code)" so users see both the human name and the API value
        return f'<option value="{code}">{name} ({code})</option>'

    page = (INDEX_HTML
            .replace("__VERSION__", rl.__version__)
            .replace("__SYL_OPTS__", "".join(opt(code, "syllable") for code in SYLLABLE_LANGS))
            .replace("__BPE_OPTS__", "".join(opt(code, "bpe") for code in BPE_LANGS))
            .replace("__LANG_NAMES_JSON__", json.dumps(LANG_NAMES))
            .replace("__GROUPS_JSON__", json.dumps([
                # Grouped by the script family the detector handles. Each
                # group carries an `action`: clicking a sample button fills
                # the textarea AND auto-runs that action. ML-classifier
                # buttons show top-5 predictions (interesting because
                # there's actually a competition among labels); script-rule
                # buttons show the single deterministic label.
                {"label": "Latin · ML",
                 "action": "predict",
                 "langs": ["eng", "cnh", "cfm", "ctd", "msa", "tgl", "vie",
                           "ban", "sun", "hnn", "kac"]},
                {"label": "Myanmar block · ML",
                 "action": "predict",
                 "langs": ["mya", "zgi", "ksw", "pwo", "kvq", "mnw"]},
                {"label": "Myanmar block · No ML",
                 "action": "detect",
                 "langs": ["shn"]},
                {"label": "Single script · No ML",
                 "action": "detect",
                 "langs": [
                     "hin", "tam", "tha", "lao", "khm", "eky", "zho",
                     "kor", "jpn", "ell", "heb", "hye", "kat", "amh",
                     "sin", "bod", "jav", "cjm", "mni", "nod", "sat",
                     "khb", "tdd", "mon", "chr", "vai", "nqo", "ful",
                 ]},
            ])))
    return page


if __name__ == "__main__":
    # The canonical way to run this is via `uvicorn` CLI with --reload
    # (see the docstring). This fallback is a no-reload convenience for
    # `python demo/server.py`.
    import uvicorn
    uvicorn.run("demo.server:app", host="127.0.0.1", port=8000, reload=True)
