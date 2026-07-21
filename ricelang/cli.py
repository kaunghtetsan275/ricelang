"""ricelang CLI.

Subcommands map 1:1 onto the public library functions:

    ricelang detect "ထမင်းစားပြီးပြီလား"
    ricelang predict "Pathian nih van" -k 5
    ricelang convert --to zg "ထမင်းစားပြီးပြီလား"
    ricelang convert --to uni "ထမင္းစားၿပီးၿပီလား"
    ricelang tokenize "ဖေဖေနဲ့မေမေ"                         # syllable, lang=mm
    ricelang tokenize --form word "ဖေဖေနဲ့မေမေ"
    ricelang tokenize --form bpe "Pathian nih van"          # multilingual BPE
    ricelang tokenize --form bpe --lang mya "ဖေဖေနဲ့မေမေ"   # per-language BPE
    ricelang version

All commands also accept ``--text -`` to read from stdin instead of a
positional argument, which makes shell piping work::

    cat file.txt | ricelang detect -
    cat file.txt | ricelang tokenize --form bpe -

Add ``--json`` to any command for machine-parseable output.
"""

from __future__ import annotations

import argparse
import json as _json
import sys

import ricelang as rl


def _read(text_arg: str) -> str:
    """Resolve ``-`` to stdin, else return the literal argument."""
    if text_arg == "-":
        return sys.stdin.read()
    return text_arg


def _emit(obj, as_json: bool):
    if as_json:
        print(_json.dumps(obj, ensure_ascii=False, separators=(",", ":")))
    else:
        if isinstance(obj, dict):
            for k, v in obj.items():
                print(f"{k}\t{v}")
        elif isinstance(obj, list):
            for line in obj:
                print(line)
        else:
            print(obj)


def _cmd_detect(args):
    text = _read(args.text)
    label = rl.detect(text)
    _emit({"label": label} if args.json else label, args.json)


def _cmd_predict(args):
    text = _read(args.text)
    labels, probs = rl.predict(text, k=args.k)
    preds = [
        {"label": label[len("__label__"):], "prob": float(prob)}
        for label, prob in zip(labels, probs)
    ]
    if args.json:
        _emit({"predictions": preds}, True)
    else:
        for p in preds:
            print(f"{p['label']}\t{p['prob']:.4f}")


def _cmd_convert(args):
    text = _read(args.text)
    if args.to == "zg":
        out = rl.cvt2zg(text)
    else:
        out = rl.cvt2uni(text)
    _emit({"text": out} if args.json else out, args.json)


def _cmd_tokenize(args):
    text = _read(args.text)
    tokens = rl.tokenize(text, lang=args.lang, form=args.form)
    if args.json:
        _emit({"tokens": tokens, "count": len(tokens)}, True)
    else:
        for t in tokens:
            print(t)


def _cmd_version(_args):
    print(rl.__version__)


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="ricelang",
        description=("Language identification and tokenization for SE/South Asian languages. "
                     "Pass '-' as the text argument to read from stdin."),
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--json", action="store_true",
                   help="emit JSON instead of plain text (works on every subcommand)")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("detect", help="predict one language label for `text`")
    d.add_argument("text", help='text to classify, or "-" for stdin')
    d.set_defaults(func=_cmd_detect)

    pr = sub.add_parser("predict", help="top-k label probabilities for `text`")
    pr.add_argument("text", help='text to classify, or "-" for stdin')
    pr.add_argument("-k", type=int, default=3, help="number of predictions (default 3)")
    pr.set_defaults(func=_cmd_predict)

    c = sub.add_parser("convert", help="Burmese encoding conversion (Zawgyi <-> Unicode)")
    c.add_argument("text", help='text to convert, or "-" for stdin')
    c.add_argument("--to", choices=("zg", "uni"), required=True,
                   help="target encoding: zg (Zawgyi) or uni (Unicode)")
    c.set_defaults(func=_cmd_convert)

    t = sub.add_parser("tokenize", help="tokenize `text` (syllable / word / BPE)")
    t.add_argument("text", help='text to tokenize, or "-" for stdin')
    t.add_argument("--form", default="syllable", choices=("syllable", "word", "bpe"),
                   help="tokenization style (default: syllable)")
    t.add_argument("--lang", default="mm",
                   help="for syllable: mm|karen|mon|shan. "
                        "for bpe: multi (default) or an ISO 639-3 code with a bundled model")
    t.set_defaults(func=_cmd_tokenize)

    v = sub.add_parser("version", help="print ricelang version")
    v.set_defaults(func=_cmd_version)

    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    args.func(args)
    return 0


if __name__ == "__main__":
    sys.exit(main())
