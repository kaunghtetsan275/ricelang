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
BPE_LANGS = ["multi", "mya", "ksw", "pwo", "kvq", "cnh", "cfm", "ctd", "eky", "shn"]
DETECT_LABELS = ["mya", "zgi", "ksw", "pwo", "kvq", "cnh", "cfm", "ctd", "eky", "shn"]

LANG_NAMES: dict[str, str] = {
    # detector / sample / BPE labels (ISO 639-3 codes)
    "mya": "Burmese (Unicode)",
    "zgi": "Burmese (Zawgyi)",
    "ksw": "S'gaw Karen",
    "pwo": "Pwo Karen",
    "kvq": "Geba Karen",
    "cnh": "Hakha Chin",
    "cfm": "Falam Chin",
    "ctd": "Tedim Chin",
    "eky": "Eastern Kayah",
    "shn": "Shan",
    # special BPE code
    "multi": "Multilingual",
    # legacy syllable-tokenizer lang codes
    "mm": "Burmese",
    "karen": "Karen",
    "mon": "Mon",
    "shan": "Shan",
}

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
        {"label": l[len("__label__"):], "prob": float(p)}
        for l, p in zip(labels, probs)
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
<meta charset="utf-8"><title>ricelang demo</title>
<style>
  body{font:14px/1.5 system-ui,sans-serif;max-width:760px;margin:2rem auto;padding:0 1rem;color:#222}
  h1{margin-bottom:.3rem} h2{margin-top:2rem;border-bottom:1px solid #ddd;padding-bottom:.3rem}
  section{margin-top:1rem}
  textarea{width:100%;min-height:60px;font-family:inherit;font-size:14px;padding:.5rem;border:1px solid #bbb;border-radius:4px}
  label{display:inline-block;margin-right:.5rem}
  select,button{padding:.3rem .6rem;border:1px solid #888;border-radius:4px;background:#fff;cursor:pointer}
  button{background:#1d4ed8;color:#fff;border-color:#1d4ed8;margin-top:.5rem}
  .samples{display:flex;flex-wrap:wrap;gap:.3rem;margin-bottom:.4rem}
  .samples button{margin:0;padding:.15rem .55rem;font-size:12px;background:#f1f5f9;color:#334155;
                  border:1px solid #cbd5e1}
  .samples button:hover{background:#e0e7ff;border-color:#1d4ed8;color:#1e3a8a}
  .samples .label{font-size:12px;color:#666;align-self:center;margin-right:.2rem}
  small{color:#666} a{color:#1d4ed8}

  /* result containers */
  .out{margin-top:.6rem;min-height:1.5rem;display:flex;flex-wrap:wrap;gap:.35rem;align-items:center}
  .out.text{display:block;background:#f4f4f4;padding:.6rem;border-radius:4px;font-size:15px;word-break:break-word}
  .err{color:#b91c1c;font-family:ui-monospace,monospace;font-size:13px}

  /* pills */
  .pill{display:inline-flex;align-items:center;gap:.3rem;padding:.18rem .55rem;border-radius:999px;
        background:#e0e7ff;color:#1e3a8a;font-size:13px;line-height:1.4;border:1px solid #c7d2fe}
  .pill .label{font-weight:600;letter-spacing:.02em}
  .pill .code{font-variant-numeric:tabular-nums;color:#64748b;font-size:11px;
              font-family:ui-monospace,SFMono-Regular,monospace;text-transform:lowercase}
  .pill .prob{font-variant-numeric:tabular-nums;color:#475569;font-size:12px}
  .pill.token{background:#f1f5f9;color:#0f172a;border-color:#e2e8f0;font-family:ui-monospace,SFMono-Regular,monospace}
  .pill.top{background:#1d4ed8;color:#fff;border-color:#1d4ed8}
  .pill.top .prob{color:#dbeafe}
  .pill.top .code{color:#dbeafe}
  .count{color:#666;font-size:12px;margin-left:.4rem}
</style></head><body>
<h1>ricelang demo <small>v__VERSION__</small></h1>
<p><small>Interactive API docs at <a href="/docs">/docs</a>. Library docs in <a href="https://github.com/kaunghtetsan275/ricelang">README</a>.</small></p>

<h2>detect</h2>
<section>
  <div class="samples" id="d_samples"><span class="label">sample:</span></div>
  <textarea id="d_in">ထမင်းစားပြီးပြီလား</textarea>
  <button onclick="doDetect()">detect</button>
  <button onclick="doPredict()">predict (top 5)</button>
  <div id="d_out" class="out"></div>
</section>

<h2>convert (Burmese encoding)</h2>
<section>
  <div class="samples" id="c_samples"><span class="label">sample:</span></div>
  <textarea id="c_in">ထမင်းစားပြီးပြီလား</textarea>
  <button onclick="doConvert('zg')">→ Zawgyi</button>
  <button onclick="doConvert('uni')">→ Unicode</button>
  <div id="c_out" class="out text"></div>
</section>

<h2>tokenize</h2>
<section>
  <div class="samples" id="t_samples"><span class="label">sample:</span></div>
  <textarea id="t_in">ဖေဖေနဲ့မေမေ၏ကျေးဇူးတရားမှာကြီးမားလှပေသည်</textarea>
  <div style="margin-top:.5rem">
    <label>form:
      <select id="t_form">
        <option value="syllable">syllable</option>
        <option value="word">word</option>
        <option value="bpe">bpe</option>
      </select></label>
    <label>lang:
      <select id="t_lang">
        <optgroup label="syllable">__SYL_OPTS__</optgroup>
        <optgroup label="bpe">__BPE_OPTS__</optgroup>
      </select></label>
    <button onclick="doTokenize()">tokenize</button>
  </div>
  <div id="t_out" class="out"></div>
</section>

<script>
const $ = id => document.getElementById(id);
const val = id => $(id).value;
const sel = id => $(id).value;

const ALL_LANGS = __ALL_LANGS_JSON__;
const LANG_NAMES = __LANG_NAMES_JSON__;
const CONVERT_LANGS = ["mya", "zgi"];

function buildSamples(rowId, inputId, langs) {
  const row = $(rowId);
  langs.forEach(lang => {
    const btn = document.createElement("button");
    btn.textContent = LANG_NAMES[lang] || lang;
    btn.title = `random ${lang} sample`;
    btn.onclick = async () => {
      const r = await fetch(`/sample/${lang}`);
      if (!r.ok) return;
      const {text} = await r.json();
      $(inputId).value = text;
    };
    row.appendChild(btn);
  });
}
buildSamples("d_samples", "d_in", ALL_LANGS);
buildSamples("c_samples", "c_in", CONVERT_LANGS);
buildSamples("t_samples", "t_in", ALL_LANGS);
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
    def opt(code: str) -> str:
        name = LANG_NAMES.get(code, code)
        # "Name (code)" so users see both the human name and the API value
        return f'<option value="{code}">{name} ({code})</option>'
    page = (INDEX_HTML
            .replace("__VERSION__", rl.__version__)
            .replace("__SYL_OPTS__", "".join(opt(l) for l in SYLLABLE_LANGS))
            .replace("__BPE_OPTS__", "".join(opt(l) for l in BPE_LANGS))
            .replace("__ALL_LANGS_JSON__", json.dumps(sorted(SAMPLES)))
            .replace("__LANG_NAMES_JSON__", json.dumps(LANG_NAMES)))
    return page


if __name__ == "__main__":
    # The canonical way to run this is via `uvicorn` CLI with --reload
    # (see the docstring). This fallback is a no-reload convenience for
    # `python demo/server.py`.
    import uvicorn
    uvicorn.run("demo.server:app", host="127.0.0.1", port=8000, reload=True)
