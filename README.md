# SAM Open-Weights Model Compatibility

Which open-weights LLMs work with **Solace Agent Mesh (SAM)**, why, and how to prove it for yourself.

This repo is the reference for anyone asking *"can I run SAM on an open model instead of a frontier API?"* It contains:

- The **requirements whitelist** - the exact capabilities a model must have, derived from the SAM codebase (not guessed).
- A **verified shortlist** of 25 open-weights models ranked by fit, with per-model specs. Every grade is cross-checked against the vLLM tool-parser matrix, the Berkeley Function-Calling Leaderboard, and each model's Hugging Face chat template - not guessed.
- **Benchmark evidence** ([`docs/benchmarks.md`](docs/benchmarks.md)) showing which models are in the native function-calling tier and which only pretend.
- A **validation harness** - drop-in SAM configs + a two-tool scenario that proves the hard requirements against *any* OpenAI-compatible endpoint (vLLM, Ollama, SGLang, TGI, LiteLLM proxy).
- **Serving recipes** for the common inference servers.

> **TL;DR** - SAM reaches models through Bifrost/LiteLLM. Any OpenAI-compatible endpoint works via the `openai/` prefix + an `api_base`. So compatibility is gated by the **model's capabilities**, not by SAM's provider list. The one filter that matters: **reliable, streaming, OpenAI-schema tool calling.**

---

## Start here

| If you want to… | Read |
|---|---|
| Understand *why* a model qualifies or not | [`docs/requirements.md`](docs/requirements.md) |
| Pick a model | [`docs/shortlist.md`](docs/shortlist.md) + [`models/`](models/) |
| See the benchmark evidence behind each grade | [`docs/benchmarks.md`](docs/benchmarks.md) |
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

Everything else - context size, parallel calls, reasoning tokens, vision, prompt caching - is a quality or cost lever, not a gate. Full detail in [`docs/requirements.md`](docs/requirements.md).

## The shortlist (summary)

Full table with specs in [`docs/shortlist.md`](docs/shortlist.md); one spec card per model in [`models/cards/`](models/cards/).

| Tier | Models | Use for |
|---|---|---|
| **Orchestrator-grade** | Llama 3.3 70B · Qwen2.5 72B/32B · Qwen3 32B · Mistral Large 2 · Llama 3.1 405B/70B · DeepSeek-V3.1 · GLM-4.6 · gpt-oss 120b · Kimi-K2 · Command A | Multi-hop routing, fan-out, synthesis |
| **Domain / leaf agents** | Qwen2.5 14B/7B · Mistral Small 3 · Mixtral 8x22B · Mistral NeMo 12B · Llama 3.1 8B · Qwen2.5-Coder 32B · gpt-oss 20b | One or two tools, high volume, cost-sensitive |
| **Validate before trusting** | DeepSeek-R1 (0528) · Command R+ (legacy) | Native tool calling only under a specific revision / template / serving path - run the harness first |
| **Not recommended** | Gemma 2 27B · Phi-4 · Yi-1.5 34B | No native tool calling (no vLLM parser, no `tool` role) - they fail the first hard gate. See [`docs/benchmarks.md`](docs/benchmarks.md) for why, and the alternative to use. |

## Self-host a model and connect SAM in 5 minutes

You need two things: an OpenAI-compatible endpoint serving the model, and a SAM `model:` block pointing at it. Here is the shortest path with the two most common servers. Full recipes (SGLang, TGI, LiteLLM, air-gapped, TLS) are in [`docs/serving.md`](docs/serving.md).

### Option A - Ollama (easiest, laptop-friendly)

```bash
# 1. Install Ollama (https://ollama.com), then pull a tool-capable model
ollama pull qwen2.5:32b

# 2. Start the server (OpenAI-compatible API on :11434)
ollama serve
```

Point SAM at it. Ollama is a first-class SAM provider prefix:

```yaml
model:
  model: ollama/qwen2.5:32b
  api_base: http://localhost:11434
```

### Option B - vLLM (production, GPU)

```bash
pip install vllm

# The two tool-calling flags are REQUIRED - without them SAM cannot call tools.
vllm serve Qwen/Qwen2.5-32B-Instruct \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser hermes \
  --max-model-len 32768
```

Point SAM at it (`openai/` selects the API protocol, not a hosted model):

```yaml
model:
  model: openai/Qwen/Qwen2.5-32B-Instruct
  api_base: http://localhost:8000/v1
  api_key: sk-noop            # vLLM ignores this unless you set --api-key
  parallel_tool_calls: true
  temperature: 0.2
  max_tokens: 4096
```

### Then confirm it actually works

```bash
export SAM_TEST_MODEL="openai/Qwen/Qwen2.5-32B-Instruct"   # or ollama/qwen2.5:32b
export SAM_TEST_API_BASE="http://localhost:8000/v1"        # or http://localhost:11434/v1
./scripts/probe.sh
```

Each model's card in [`models/cards/`](models/cards/) has the exact `--tool-call-parser`, serve command, and copy-paste `model:` block for that model.

## Validate any model in 3 commands

```bash
# 1. Point at your endpoint (any OpenAI-compatible server)
export SAM_TEST_MODEL="openai/Qwen/Qwen2.5-32B-Instruct"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
export SAM_TEST_API_KEY="sk-noop"        # many local servers ignore this

# 2. Run the capability probe (no SAM required - pure OpenAI-compat check)
./scripts/probe.sh

# 3. Run the full SAM two-tool agent scenario (requires SAM installed)
./scripts/run-sam-scenario.sh
```

`probe.sh` checks the three hard gates directly against the endpoint. `run-sam-scenario.sh` runs a real SAM agent that must call tool A, then call tool B *using A's output* - the exact loop that separates real tool-callers from pretenders. See [`docs/validation.md`](docs/validation.md).

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
  shortlist.md      - 25 models ranked, with the reasoning
  benchmarks.md     - BFCL / vLLM-parser / HF-template evidence behind each grade
  validation.md     - how to prove a model works
  serving.md        - vLLM / Ollama / SGLang / TGI / LiteLLM recipes
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
