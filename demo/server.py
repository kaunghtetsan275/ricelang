"""Minimal FastAPI demo for ricelang.

Exposes every public function in the library as an HTTP endpoint plus a
single-page form-based UI at ``/``. Interactive API docs at ``/docs``.

Run:

    uv run --group demo uvicorn demo.server:app --reload --port 8000
"""

from __future__ import annotations

from fastapi import FastAPI
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
    }


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
  small{color:#666} a{color:#1d4ed8}

  /* result containers */
  .out{margin-top:.6rem;min-height:1.5rem;display:flex;flex-wrap:wrap;gap:.35rem;align-items:center}
  .out.text{display:block;background:#f4f4f4;padding:.6rem;border-radius:4px;font-size:15px;word-break:break-word}
  .err{color:#b91c1c;font-family:ui-monospace,monospace;font-size:13px}

  /* pills */
  .pill{display:inline-flex;align-items:center;gap:.3rem;padding:.18rem .55rem;border-radius:999px;
        background:#e0e7ff;color:#1e3a8a;font-size:13px;line-height:1.4;border:1px solid #c7d2fe}
  .pill .label{font-weight:600;letter-spacing:.02em;text-transform:lowercase}
  .pill .prob{font-variant-numeric:tabular-nums;color:#475569;font-size:12px}
  .pill.token{background:#f1f5f9;color:#0f172a;border-color:#e2e8f0;font-family:ui-monospace,SFMono-Regular,monospace}
  .pill.top{background:#1d4ed8;color:#fff;border-color:#1d4ed8}
  .pill.top .prob{color:#dbeafe}
  .count{color:#666;font-size:12px;margin-left:.4rem}
</style></head><body>
<h1>ricelang demo <small>v__VERSION__</small></h1>
<p><small>Interactive API docs at <a href="/docs">/docs</a>. Library docs in <a href="https://github.com/kaunghtetsan275/ricelang">README</a>.</small></p>

<h2>detect</h2>
<section>
  <textarea id="d_in">ထမင်းစားပြီးပြီလား</textarea>
  <button onclick="doDetect()">detect</button>
  <button onclick="doPredict()">predict (top 5)</button>
  <div id="d_out" class="out"></div>
</section>

<h2>convert (Burmese encoding)</h2>
<section>
  <textarea id="c_in">ထမင်းစားပြီးပြီလား</textarea>
  <button onclick="doConvert('zg')">→ Zawgyi</button>
  <button onclick="doConvert('uni')">→ Unicode</button>
  <div id="c_out" class="out text"></div>
</section>

<h2>tokenize</h2>
<section>
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
const escape = s => s.replace(/[&<>"']/g, c => ({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"}[c]));

async function post(url, body) {
  const r = await fetch(url, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)});
  if (!r.ok) throw new Error((await r.json()).detail || r.statusText);
  return await r.json();
}

function show(outId, html) { $(outId).innerHTML = html; }
function err(outId, e) { $(outId).innerHTML = `<div class="err">${escape(e.message)}</div>`; }

async function doDetect() {
  try { const {label} = await post("/detect", {text: val("d_in")});
        show("d_out", `<span class="pill top"><span class="label">${escape(label)}</span></span>`); }
  catch(e) { err("d_out", e); }
}

async function doPredict() {
  try {
    const {predictions} = await post("/predict", {text: val("d_in"), k: 5});
    const pills = predictions.map((p, i) =>
      `<span class="pill${i===0?' top':''}"><span class="label">${escape(p.label)}</span>` +
      `<span class="prob">${(p.prob*100).toFixed(1)}%</span></span>`
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

async function doTokenize() {
  try {
    const {tokens, count} = await post("/tokenize",
      {text: val("t_in"), form: sel("t_form"), lang: sel("t_lang")});
    const pills = tokens.map(t => `<span class="pill token">${escape(t)}</span>`).join("");
    show("t_out", pills + `<span class="count">${count} tokens</span>`);
  } catch(e) { err("t_out", e); }
}
</script>
</body></html>"""


@app.get("/", response_class=HTMLResponse)
def index():
    page = (INDEX_HTML
            .replace("__VERSION__", rl.__version__)
            .replace("__SYL_OPTS__", "".join(f"<option>{l}</option>" for l in SYLLABLE_LANGS))
            .replace("__BPE_OPTS__", "".join(f"<option>{l}</option>" for l in BPE_LANGS)))
    return page


if __name__ == "__main__":
    # The canonical way to run this is via `uvicorn` CLI with --reload
    # (see the docstring). This fallback is a no-reload convenience for
    # `python demo/server.py`.
    import uvicorn
    uvicorn.run("demo.server:app", host="127.0.0.1", port=8000, reload=True)
