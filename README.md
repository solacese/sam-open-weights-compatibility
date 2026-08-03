# SAM Open-Weights Model Compatibility

Which open-weights LLMs work with **Solace Agent Mesh (SAM)**, why, and how to prove it for yourself.

This repo is the reference for anyone asking *"can I run SAM on an open model instead of a frontier API?"* It contains a requirements whitelist derived from the SAM codebase, a verified shortlist of 25 open-weights models with per-model spec cards, the benchmark evidence behind every grade, serving recipes for the common inference servers, and a validation harness that proves the hard requirements against *any* OpenAI-compatible endpoint.

> **TL;DR** - SAM reaches models through Bifrost/LiteLLM. Any OpenAI-compatible endpoint works via the `openai/` prefix + an `api_base`. So compatibility is gated by the **model's capabilities**, not by SAM's provider list. The one filter that matters: **reliable, streaming, OpenAI-schema tool calling.**

---

## The 30-second version

```
                 ┌──────────── SAM Agent Loop ────────────┐
   YAML agent ──▶│  llm.Client  →  Bifrost  →  LiteLLM     │──▶  any OpenAI-compatible
   (model: ...)  │  tools, streaming tool-call deltas,     │      endpoint (vLLM, Ollama,
                 │  multi-turn tool results, tool_choice   │      SGLang, TGI, LiteLLM)
                 └─────────────────────────────────────────┘
```

A model is usable with SAM if and only if, served behind an OpenAI-compatible API, it can:

1. Emit **native tool calls** in the OpenAI `tools` schema.
2. Do so **while streaming** (incremental tool-call deltas).
3. Correctly consume a **`tool` role result** and continue the conversation (multi-turn tool use).

Everything else - context size, parallel calls, reasoning tokens, vision, prompt caching - is a quality or cost lever, not a gate. Full detail in [`docs/requirements.md`](docs/requirements.md).

## How-to guides

Each task has a dedicated guide. Start with the row that matches what you're doing.

| I want to… | Go to |
|---|---|
| Understand *why* a model qualifies or not | [`docs/requirements.md`](docs/requirements.md) |
| **Pick a model** - tiers, hardware/VRAM, GPU budget, best per provider | [`docs/pick-a-model.md`](docs/pick-a-model.md) |
| See the **benchmark evidence** behind each grade | [`docs/benchmarks.md`](docs/benchmarks.md) |
| **Serve** an open model for SAM (vLLM, Ollama, SGLang, TGI, LiteLLM) | [`docs/serving.md`](docs/serving.md) |
| **Check a model works in SAM** - validate your stack | [`docs/validation.md`](docs/validation.md) |
| Read the full ranked shortlist with reasoning | [`docs/shortlist.md`](docs/shortlist.md) |
| Browse per-model spec cards (SAM-ready config block) | [`models/cards/`](models/cards/) |
| See how the conclusions were derived from SAM source | [`docs/methodology.md`](docs/methodology.md) |

## Kept up to date

Open-weights models move fast. This repo is a living reference: the current list already tracks the recent wave (Qwen3, DeepSeek-V3.1, GLM-4.6, gpt-oss 20b/120b, Kimi-K2, Command A), and we will keep adding newer models as they land and prove out (Llama 4 and its `llama4_pythonic` parser, Qwen3-Coder, GLM-4.7, and others), refresh the benchmark and tool-calling-leaderboard numbers, and re-grade anything whose serving story changes. The workflow to add a model is deliberately simple:

1. Add a row to [`models/index.csv`](models/index.csv).
2. Run `python3 scripts/gen-model-cards.py` to regenerate the per-model cards.
3. Validate it with `./scripts/probe.sh` and `./scripts/run-sam-scenario.sh`, then record the stack and date in the CSV.

Spotted a model we should include, or numbers that drifted? Open an issue or PR.

## Scope & honesty

- Context windows and tool-calling grades are the **commonly-served** figures and reflect community + vendor reports as of mid-2026. They are starting points - **the harness is the source of truth for your stack.** A quant level, a serving flag, or a chat-template mismatch can turn a "yes" into a "no."
- "Open-weights" here means weights you can download and self-host. Licenses vary (Apache-2.0, Llama Community, Qwen, MIT, Gemma) - see each model card; check the license against your use before shipping.
- This is a field/SE reference, not an official support matrix. SAM officially *supports the provider integration*; individual open models are your call to validate.

## Layout

```
docs/
  requirements.md   - the whitelist, each requirement traced to SAM source
  pick-a-model.md   - tier shortlist, hardware/VRAM, GPU budget, best per provider
  shortlist.md      - 25 models ranked, with the reasoning
  benchmarks.md     - BFCL / vLLM-parser / HF-template evidence behind each grade
  serving.md        - 5-minute quickstart + vLLM / Ollama / SGLang / TGI / LiteLLM recipes
  validation.md     - how to prove a model works
  methodology.md    - exactly what in the SAM codebase drives each requirement
models/
  index.csv         - machine-readable summary of all 25
  cards/*.md        - one spec card per model (SAM-ready config block)
tests/
  configs/          - SAM model + agent configs templated on env vars
  scenarios/        - declarative two-tool + parallel-tool validation scenarios
scripts/
  probe.sh          - endpoint-only hard-gate probe (curl + jq)
  run-sam-scenario.sh - full SAM agent validation run
```
