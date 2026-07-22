# Python API reference

Everything is at the top level — `import ricelang as rl` exposes the full
public surface.

## Detection

### `ricelang.detect`

::: ricelang.detect.detect

### `ricelang.predict`

::: ricelang.detect.predict

## Tokenization

### `ricelang.tokenize`

::: ricelang.tokenize.tokenize

## Encoding conversion

### `ricelang.cvt2zg`

::: ricelang.convert.cvt2zg

### `ricelang.cvt2uni`

::: ricelang.convert.cvt2uni

### `ricelang.cvt2zgi`

Alias for [`cvt2zg`](#ricelangcvt2zg). Preserved for backwards compatibility
with the original pyidaungsu API.

## Module metadata

### `ricelang.__version__`

The installed library version, e.g. `"0.5.0"`.

## Lower-level utilities

For most use cases the top-level functions above are enough. These are
exposed for callers that need finer control:

### `ricelang.scripts.script_detect`

::: ricelang.scripts.script_detect

The Unicode-rule first stage of `detect()`. Returns:

- An ISO 639-3 label if a monopoly-script rule fires
- `"__shared_latin"` or `"__shared_mymr"` if the text is in a shared script
  (caller should run the ML classifier)
- `None` if no supported script dominates the text

You won't normally call this directly — `rl.detect()` handles the dispatch.
