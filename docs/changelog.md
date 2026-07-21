# Changelog

GitHub releases mirror this changelog and link to the diffs:
<https://github.com/kaunghtetsan275/ricelang/releases>.

## 0.4.3 — Documentation site

- New mkdocs-material documentation site at
  <https://kaunghtetsan275.github.io/ricelang/>.
- Source under `docs/`. Deployed via GitHub Actions on push to master.
- No code or behavior changes.

## 0.4.2 — Drop Python 3.9

- Bumped `requires-python` from `>=3.9` to `>=3.10`.
- This clears 6 Dependabot alerts (2 high, 4 medium) on urllib3, pytest,
  requests, filelock that were pinned to vulnerable versions specifically
  for Python 3.9 (no patched versions backport to 3.9).
- Python 3.9 has been EOL since October 2025.

## 0.4.1 — Shan script-rule + demo redesign + CLI docs

- **Shan (`shn`) detected by Unicode-rule** instead of ML for short text.
  Density-based check on U+1075–U+108A plus three Shan-only codepoints
  (U+1022, U+1079, U+1084) that Zawgyi never uses.
- **Demo UI redesign**: minimal monospace (JetBrains Mono only). Sample
  picker collapsed from chip walls to a single optgroup'd `<select>` per
  section.
- **README**: added top-level CLI section that was missing since 0.3.1.

## 0.4.0 — Unicode-script-rule detector

- **Hierarchical detector**: Unicode-block rule runs first; the trained
  fastText classifier only fires for shared scripts (Latin + Myanmar block).
- **27 new monopoly-script labels** added with no training data: `kor`,
  `jpn`, `ell`, `heb`, `hye`, `kat`, `amh`, `sin`, `bod`, `chr`, `nqo`,
  `mon`, `vai`, `ful`, `mww`, `bax`, `lep`, `lif`, `saz`, `bug`, `jav`,
  `cjm`, `mni`, `nod`, `sat`, `khb`, `tdd`.
- **Out-of-scope text returns `None`** instead of a confidently-wrong label.
- 50+ supported labels total.

## 0.3.1 — CLI

- New `ricelang` console command. Thin argparse wrapper over the public
  Python API. See [CLI reference](cli.md).
- Supports stdin via `-` and `--json` output for all subcommands.

## 0.3.0 — Per-language BPE tokenizers

- 24 per-language BPE tokenizers + 1 multilingual (`multi`, 32k vocab)
  bundled.
- `tokenize(text, form="bpe", lang="<iso>")` selects the per-language
  model; `lang="multi"` (default) uses the multilingual one.
- Lazy-loaded — only the tokenizers you use hit memory.

## 0.2.x — Revamp from `pyidaungsu`

- Renamed from `pyidaungsu` → `ricelang` (PyPI + GitHub + import path).
- 25 trained labels (was 3): added 22 SE/South Asian languages with full
  ISO 639-3 codes throughout.
- Retrained detector on a 787k-example corpus (YouVersion Bible scrapes +
  Mon Wikipedia). 99.85% P@1.
- `uv`-native packaging via `pyproject.toml`. No more `setup.py`.
- FastAPI demo server under `demo/`.

See [Migrating from pyidaungsu](migration.md) for upgrade details.
