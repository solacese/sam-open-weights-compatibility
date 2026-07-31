# SAM Open-Weights Model Compatibility

Which open-weights LLMs work with **Solace Agent Mesh (SAM)**, why, and how to prove it for yourself.

This repo is the reference for anyone asking *"can I run SAM on an open model instead of a frontier API?"* It contains:

- The **requirements whitelist** — the exact capabilities a model must have, derived from the SAM codebase (not guessed).
- A **top-20 shortlist** of open-weights models ranked by fit, with per-model specs.
- A **validation harness** — drop-in SAM configs + a two-tool scenario that proves the hard requirements against *any* OpenAI-compatible endpoint (vLLM, Ollama, SGLang, TGI, LiteLLM proxy).
- **Serving recipes** for the common inference servers.

> **TL;DR** — SAM reaches models through Bifrost/LiteLLM. Any OpenAI-compatible endpoint works via the `openai/` prefix + an `api_base`. So compatibility is gated by the **model's capabilities**, not by SAM's provider list. The one filter that matters: **reliable, streaming, OpenAI-schema tool calling.**

---

## Start here

| If you want to… | Read |
|---|---|
| Understand *why* a model qualifies or not | [`docs/requirements.md`](docs/requirements.md) |
| Pick a model | [`docs/shortlist.md`](docs/shortlist.md) + [`models/`](models/) |
| Prove a model works | [`docs/validation.md`](docs/validation.md) + [`tests/`](tests/) |
| Serve an open model for SAM | [`docs/serving.md`](docs/serving.md) |
| See the raw findings from the SAM source | [`docs/methodology.md`](docs/methodology.md) |

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

Everything else — context size, parallel calls, reasoning tokens, vision, prompt caching — is a quality or cost lever, not a gate. Full detail in [`docs/requirements.md`](docs/requirements.md).

## The shortlist (summary)

Full table with specs in [`docs/shortlist.md`](docs/shortlist.md); one spec card per model in [`models/cards/`](models/cards/).

| Tier | Models | Use for |
|---|---|---|
| **Orchestrator-grade** | Llama 3.3 70B · Qwen2.5 72B/32B · Mistral Large 2 · Llama 3.1 405B/70B · DeepSeek-V3 · Command R+ | Multi-hop routing, fan-out, synthesis |
| **Domain / leaf agents** | Qwen2.5 14B/7B · Mistral Small 3 · Command R · Mistral NeMo 12B · Llama 3.1 8B · Qwen2.5-Coder 32B | One or two tools, high volume, cost-sensitive |
| **Validate before trusting** | Gemma 2 27B · DeepSeek-R1 · Phi-4 · Yi-1.5 34B | Capable, but tool-calling is templated / less battle-tested — run the harness first |

## Validate any model in 3 commands

```bash
# 1. Point at your endpoint (any OpenAI-compatible server)
export SAM_TEST_MODEL="openai/Qwen/Qwen2.5-32B-Instruct"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
export SAM_TEST_API_KEY="sk-noop"        # many local servers ignore this

# 2. Run the capability probe (no SAM required — pure OpenAI-compat check)
./scripts/probe.sh

# 3. Run the full SAM two-tool agent scenario (requires SAM installed)
./scripts/run-sam-scenario.sh
```

`probe.sh` checks the three hard gates directly against the endpoint. `run-sam-scenario.sh` runs a real SAM agent that must call tool A, then call tool B *using A's output* — the exact loop that separates real tool-callers from pretenders. See [`docs/validation.md`](docs/validation.md).

## Scope & honesty

- Context windows and tool-calling grades are the **commonly-served** figures and reflect community + vendor reports as of mid-2026. They are starting points — **the harness is the source of truth for your stack.** A quant level, a serving flag, or a chat-template mismatch can turn a "yes" into a "no."
- "Open-weights" here means weights you can download and self-host. Licenses vary (Apache-2.0, Llama Community, Qwen, MIT, Gemma) — see each model card; check the license against your use before shipping.
- This is a field/SE reference, not an official support matrix. SAM officially *supports the provider integration*; individual open models are your call to validate.

## Layout

```
docs/
  requirements.md   — the whitelist, each requirement traced to SAM source
  shortlist.md      — top-20 ranked, with the reasoning
  validation.md     — how to prove a model works
  serving.md        — vLLM / Ollama / SGLang / TGI / LiteLLM recipes
  methodology.md    — exactly what in the SAM codebase drives each requirement
models/
  index.csv         — machine-readable summary of all 20
  cards/*.md        — one spec card per shortlisted model (SAM-ready config block)
tests/
  configs/          — SAM model + agent configs templated on env vars
  scenarios/        — declarative two-tool + parallel-tool validation scenarios
scripts/
  probe.sh          — endpoint-only hard-gate probe (curl + jq)
  run-sam-scenario.sh — full SAM agent validation run
```
