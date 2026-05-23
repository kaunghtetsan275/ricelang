"""Minimal FastAPI demo for ricelang.

Exposes every public function in the library as an HTTP endpoint plus a
single-page form-based UI at ``/``. Interactive API docs at ``/docs``.

Run:

    uv run --group demo python demo/server.py
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
  pre{background:#f4f4f4;padding:.6rem;border-radius:4px;overflow-x:auto;white-space:pre-wrap;word-break:break-word;font-size:13px}
  small{color:#666}
  a{color:#1d4ed8}
</style></head><body>
<h1>ricelang demo <small>v__VERSION__</small></h1>
<p><small>Interactive API docs at <a href="/docs">/docs</a>. Library docs in <a href="https://github.com/kaunghtetsan275/ricelang">README</a>.</small></p>

<h2>detect</h2>
<section>
  <textarea id="d_in">ထမင်းစားပြီးပြီလား</textarea>
  <button onclick="call('/detect',{text:val('d_in')},'d_out')">detect</button>
  <button onclick="call('/predict',{text:val('d_in'),k:5},'d_out')">predict (top 5)</button>
  <pre id="d_out"></pre>
</section>

<h2>convert (Burmese encoding)</h2>
<section>
  <textarea id="c_in">ထမင်းစားပြီးပြီလား</textarea>
  <button onclick="call('/convert/zg',{text:val('c_in')},'c_out')">→ Zawgyi</button>
  <button onclick="call('/convert/uni',{text:val('c_in')},'c_out')">→ Unicode</button>
  <pre id="c_out"></pre>
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
    <button onclick="call('/tokenize',{text:val('t_in'),form:sel('t_form'),lang:sel('t_lang')},'t_out')">tokenize</button>
  </div>
  <pre id="t_out"></pre>
</section>

<script>
const val = id => document.getElementById(id).value;
const sel = id => document.getElementById(id).value;
async function call(url, body, outId) {
  const out = document.getElementById(outId);
  out.textContent = "...";
  const r = await fetch(url, {method:"POST", headers:{"Content-Type":"application/json"}, body:JSON.stringify(body)});
  out.textContent = JSON.stringify(await r.json(), null, 2);
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
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
