# Why not just use an LLM?

Modern LLMs (Gemini, Claude, GPT-4o) handle Burmese, Karen, Chin, Mon and
many SE Asian languages quite well. So why a specialised library?

**Because language identification is a classification task that doesn't need
an LLM's reasoning capacity.** Calling an LLM to ask "what language is this?"
is like calling a chess engine to do arithmetic — it works, but it's the
wrong shape of tool.

## Comparison

|  | ricelang | LLM API call |
|---|---|---|
| Per-call latency | ~1–10 ms | 200 ms – 2 s |
| Per-call cost | $0 | per-token billing |
| Footprint | 1.8 MB model, no GPU | gigabytes, or external API |
| Determinism | same input → same output | sampling can give different answers |
| Privacy / offline | local, on-device | text goes to a vendor's API |
| Out-of-scope handling | returns `None` explicitly | confidently picks a plausible-sounding answer |
| Hosting | ships inside your Docker image | external dependency, rate limits |
| Specialisation | trained on SE/South Asian text | trained on internet-at-large |

## Use ricelang for

- **Volume / scale routing** — millions of messages per day, classify before
  expensive downstream calls
- **Embedded / edge / on-device** — no GPU, no network
- **Deterministic analytics** — pipeline cells that must give the same answer
  every run
- **Sensitive content** — text that legally can't leave the machine
- **Specialised SE Asian work** — Zawgyi/Unicode normalization, Burmese
  word/syllable segmentation, BPE for under-served scripts

## Use an LLM for

- **Translation, summarization, structured extraction** — the things that
  actually need reasoning
- **Free-form QA over the text**
- **Multi-turn dialog**
- **Generation, not classification**

## The right architecture

For most pipelines that touch multilingual text:

```
incoming text
     │
     ▼
  ricelang.detect()      ← fast filter / router
     │
     ▼
  (per-language path)
     │
     ├─ Burmese → tokenize → normalize → ...
     ├─ Thai    → segment  → ...
     └─ ...
     │
     ▼
  LLM call (only for the messages that need it)
```

ricelang isn't a replacement for an LLM; it's the thing you put **in front
of** the LLM so you only spend tokens on work that actually needs them.
