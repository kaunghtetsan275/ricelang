# ricelang demo server

Minimal FastAPI server that exposes every public function in the
library as an HTTP endpoint, plus a single-page form UI for trying
them in a browser.

## Run

```sh
uv run --group demo python demo/server.py
```

Then open <http://127.0.0.1:8000/> for the form UI, or
<http://127.0.0.1:8000/docs> for the auto-generated Swagger API explorer.

## Endpoints

| Method | Path           | Body                                          | Wraps                       |
| ------ | -------------- | --------------------------------------------- | --------------------------- |
| GET    | `/`            | —                                             | HTML form UI                |
| GET    | `/info`        | —                                             | version + supported codes   |
| POST   | `/detect`      | `{text}`                                      | `ricelang.detect`           |
| POST   | `/predict`     | `{text, k}`                                   | `ricelang.predict` (top-k)  |
| POST   | `/convert/zg`  | `{text}`                                      | `ricelang.cvt2zg`           |
| POST   | `/convert/uni` | `{text}`                                      | `ricelang.cvt2uni`          |
| POST   | `/tokenize`    | `{text, lang, form}` (form: syllable\|word\|bpe) | `ricelang.tokenize`     |
