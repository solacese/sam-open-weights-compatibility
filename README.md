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
| Know the VRAM and GPU each model needs | [Hardware to self-host](#hardware-to-self-host) + [Recommended GPUs](#recommended-gpus) |
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

## Who makes these models

Open-weights models come from labs across the US, China, Europe, and Canada. Country of origin can matter for procurement, data-residency, or export-control policy, so it is called out per model in each [spec card](models/cards/) and in [`models/index.csv`](models/index.csv). Summary:

| Organization | Country | Models here |
|---|---|---|
| Meta | USA | Llama 3.3 70B, Llama 3.1 405B/70B/8B |
| OpenAI | USA | gpt-oss 120b, gpt-oss 20b |
| Google | USA | Gemma 2 27B (not recommended) |
| Microsoft | USA | Phi-4 (not recommended) |
| Mistral AI | France | Mistral Large 2, Mixtral 8x22B, Mistral Small 3, Mistral NeMo (with NVIDIA) |
| Cohere | Canada | Command A, Command R+ (legacy) |
| Alibaba (Qwen team) | China | Qwen2.5 72B/32B/14B/7B, Qwen3 32B, Qwen2.5-Coder 32B |
| DeepSeek | China | DeepSeek-V3.1, DeepSeek-R1 (0528) |
| Zhipu AI (Z.ai) | China | GLM-4.6 |
| Moonshot AI | China | Kimi-K2 |
| 01.AI | China | Yi-1.5 34B (not recommended) |

## Hardware to self-host

The table below is the VRAM each model needs and the smallest GPU setup that runs it. Two numbers per model: **FP16** (full precision, what you need for a lossless deploy) and **4-bit** (AWQ / GPTQ / MXFP4, the practical self-host path most people take). Both include roughly 15% headroom for the KV cache and activations at a working context length; a very long context or high concurrency pushes the real number up, so size with margin.

Sizing rules used here:

- **FP16 is about 2 GB per billion total parameters; 4-bit is about 0.55 GB per billion.** Add ~15% for KV cache and activation overhead.
- **Mixture-of-Experts (MoE) models must fit *all* parameters in VRAM, not just the active ones.** DeepSeek-V3.1 activates 37B per token but you still have to hold all 671B in memory. Size by total params, always.
- **gpt-oss ships natively in MXFP4** (~4.25-bit), so there is no separate FP16 weight download; the 4-bit column is the real footprint.

| Model | Params (active) | VRAM FP16 | VRAM 4-bit | Recommended GPU (4-bit) |
|---|---|---|---|---|
| Llama 3.3 70B Instruct | 70B | 161 GB | 44 GB | 1x 48GB (A6000 / L40S) |
| Qwen2.5 72B Instruct | 72B | 166 GB | 46 GB | 1x 48GB (A6000 / L40S) |
| Qwen2.5 32B Instruct | 32B | 74 GB | 20 GB | 1x 24GB (RTX 4090 / A10) |
| Qwen3 32B | 32B | 74 GB | 20 GB | 1x 24GB (RTX 4090 / A10) |
| Mistral Large 2 (2411) | 123B | 283 GB | 78 GB | 1x 80GB (A100 / H100) |
| Llama 3.1 405B Instruct | 405B | 931 GB | 256 GB | 4x 80GB (A100 / H100) |
| Llama 3.1 70B Instruct | 70B | 161 GB | 44 GB | 1x 48GB (A6000 / L40S) |
| DeepSeek-V3.1 | 671B (37B) | 1543 GB | 424 GB | 8x 80GB (1x H100 node) |
| GLM-4.6 | 355B (32B) | 816 GB | 225 GB | 4x 80GB (A100 / H100) |
| gpt-oss 120b | 117B (5.1B) | n/a (MXFP4) | ~65 GB (MXFP4) | 1x 80GB (A100 / H100) |
| Kimi-K2 Instruct | 1000B (32B) | 2300 GB | 632 GB | 8x 80GB (1x H100 node) |
| Command A (03-2025) | 111B | 255 GB | 70 GB | 1x 80GB (A100 / H100) |
| Qwen2.5 14B Instruct | 14B | 32 GB | 9 GB | 1x 16-24GB (RTX 4090 / L4) |
| Mixtral 8x22B Instruct | 141B (39B) | 324 GB | 89 GB | 2x 80GB (A100 / H100) |
| Mistral Small 3 (24B) | 24B | 55 GB | 15 GB | 1x 16-24GB (RTX 4090 / L4) |
| Qwen2.5 7B Instruct | 7B | 16 GB | 4 GB | 1x 16-24GB (RTX 4090 / L4) |
| Qwen2.5-Coder 32B | 32B | 74 GB | 20 GB | 1x 24GB (RTX 4090 / A10) |
| gpt-oss 20b | 21B (3.6B) | n/a (MXFP4) | ~16 GB (MXFP4) | 1x 16-24GB (RTX 4090 / L4) |
| Mistral NeMo 12B | 12B | 28 GB | 8 GB | 1x 16-24GB (RTX 4090 / L4) |
| Llama 3.1 8B Instruct | 8B | 18 GB | 5 GB | 1x 16-24GB (RTX 4090 / L4) |
| DeepSeek-R1 (0528) | 671B (37B) | 1543 GB | 424 GB | 8x 80GB (1x H100 node) |
| Command R+ (legacy) | 104B | 239 GB | 66 GB | 1x 80GB (A100 / H100) |
| Gemma 2 27B Instruct | 27B | 62 GB | 17 GB | 1x 24GB (RTX 4090 / A10) |
| Phi-4 (14B) | 14B | 32 GB | 9 GB | 1x 16-24GB (RTX 4090 / L4) |
| Yi-1.5 34B Chat | 34B | 78 GB | 22 GB | 1x 24GB (RTX 4090 / A10) |

## Recommended GPUs

Pick the smallest tier that fits your target model at 4-bit with room for context. Going one tier up buys you longer context and higher concurrency before you have to shard across cards.

| GPU tier | VRAM | Runs (4-bit) | Notes |
|---|---|---|---|
| **Consumer** (RTX 4090 / RTX 3090) | 24 GB | Everything up to ~32B dense (Qwen2.5/Qwen3 32B, Gemma 2 27B, Yi 34B) and all the 7-14B models | The cheapest real self-host path. A single 4090 comfortably orchestrates SAM with a 32B model at 4-bit. |
| **Workstation** (L4 / A10) | 16-24 GB | 7-14B models, gpt-oss 20b, Mistral Small 3 | Data-center cards for always-on inference; lower power draw than a 4090, easy to rack. |
| **Single big-card** (A6000 / L40S) | 48 GB | 70-72B dense (Llama 3.3 70B, Qwen2.5 72B) | The sweet spot for a strong single-GPU orchestrator without an 80GB card. |
| **Data-center** (A100 / H100) | 80 GB | 100-123B dense (Command A, Mistral Large), gpt-oss 120b, and MoE models whose *total* size fits | One card covers most heavyweight single-node deploys. |
| **Multi-GPU node** (4-8x A100/H100) | 320-640 GB | Frontier MoE (DeepSeek-V3.1/R1, GLM-4.6, Kimi-K2) and Llama 3.1 405B | Needed because MoE holds all experts in memory. Kimi-K2 and DeepSeek want a full 8x80GB node even at 4-bit. |

**Buyer's guidance:**

- **Just want SAM to work well on one machine?** A single 24GB card (RTX 4090) running a 32B model at 4-bit (Qwen3 32B or Qwen2.5 32B) is the best price/capability point for a self-hosted orchestrator.
- **Need the strongest single-card orchestrator?** A 48GB A6000/L40S runs Llama 3.3 70B at 4-bit, the top-ranked model here.
- **Going frontier (GLM-4.6, DeepSeek, Kimi-K2)?** Budget for a multi-GPU 80GB node and remember to size by *total* MoE params, not active.

## Benchmark results

The one capability SAM depends on is reliable tool calling, so the ranking below is grounded in the **Berkeley Function-Calling Leaderboard (BFCL)** rather than general benchmarks (MMLU, etc.). A model that scores high on MMLU but sits in BFCL's *Prompt-only* tier is a poor SAM fit, because it cannot emit native tool calls.

Each verdict is cross-checked against three primary sources: the BFCL tier (native **Function-Calling** vs **Prompt-only**), the **vLLM `--tool-call-parser`** (or `none` if vLLM ships no parser for it), and the model's **Hugging Face chat template** (does it define the `tool` role SAM needs for multi-turn tool results?). Full reasoning in [`docs/benchmarks.md`](docs/benchmarks.md).

The table below is **sorted by BFCL overall accuracy, highest first**. `(FC)` = function-calling variant, `(P)` = prompt variant (highest-scoring variant shown). `(V4)` = the live [BFCL V4 board](https://gorilla.cs.berkeley.edu/leaderboard.html) (observed 2026-07-31); `(V3)` = the archived V3 `data_overall.csv` snapshot (2025-03), used for the checkpoints V4 pruned. `n/a` means the model was **never submitted to BFCL** in any board version, not that it is bad at tool calling. Scores are absolute (BFCL is deliberately hard: a 30-40% here is a capable tool caller, not a failing grade).

> **Read this before trusting the order.** A raw score sort is *not* a SAM-fitness ranking, for two reasons. (1) **V3 and V4 scores are not directly comparable**: BFCL re-scores between versions (DeepSeek-R1-0528 moved from 63.79 to 48.97 between two 2025 snapshots alone), so a V3 61 and a V4 48 are not a clean 13-point gap. (2) **A high score does not mean SAM can use the model.** Gemma 2 27B scores 52.21 but only in BFCL's *prompt* mode; it has no vLLM tool parser and no `tool` role, so it fails SAM's first hard gate regardless of the number. The **SAM verdict** column, not the score, is what governs whether SAM can drive the model. For the SAM-fitness ranking, use [the shortlist](docs/shortlist.md); this table is the raw benchmark evidence behind it.

| Model | BFCL score | BFCL tier | vLLM parser | HF `tool` role | SAM verdict |
|---|---|---|---|---|---|
| GLM-4.6 | 72.38 (FC, V4) | Function Calling | `glm45` | yes | very-good |
| DeepSeek-R1 (0528) | 63.79 (FC, V4) | Prompt (base R1) | `deepseek_v3` | conditional | validate-first |
| Qwen2.5 72B Instruct | 61.31 (P, V3) | Function Calling | `hermes` | yes | excellent |
| Qwen2.5 32B Instruct | 59.67 (P, V3) | Function Calling | `hermes` | yes | excellent |
| Kimi-K2 Instruct | 59.06 (FC, V4) | Function Calling | `kimi_k2` | yes | very-good |
| Qwen2.5 14B Instruct | 57.68 (P, V3) | Function Calling | `hermes` | yes | very-good |
| DeepSeek-V3.1 | 57.23 (FC, V3) | Function Calling | `deepseek_v31` | yes | very-good |
| Qwen2.5 7B Instruct | 56.70 (FC, V3) | Function Calling | `hermes` | yes | good |
| Llama 3.1 70B Instruct | 54.19 (P, V3) | Function Calling | `llama3_json` | yes | excellent |
| Gemma 2 27B Instruct | 52.21 (P, V3) | Prompt only | none | no | unsupported |
| Mixtral 8x22B Instruct | 50.36 (P, V3) | not listed | `mistral` | yes | good |
| Command R+ (legacy) | 49.35 (FC, V3) | Function Calling | none | yes | validate-first |
| Qwen3 32B | 48.71 (FC, V4) | Function Calling | `hermes` | yes | excellent |
| Command A (03-2025) | 46.49 (FC, V4) | Function Calling | `cohere_command3` | yes | very-good |
| Mistral Large 2 (2411) | 38.37 (FC, V4) | Function Calling | `mistral` | yes | excellent |
| Llama 3.3 70B Instruct | 31.9 (FC, V4) | Function Calling | `llama3_json` | yes | excellent |
| Phi-4 (14B) | 28.79 (P, V4) | Prompt only | none | no | unsupported |
| Mistral NeMo 12B | 27.63 (FC, V4) | Function Calling | `mistral` | yes | good |
| Llama 3.1 8B Instruct | 25.83 (P, V4) | Function Calling | `llama3_json` | yes | good |
| Llama 3.1 405B Instruct | n/a | Function Calling | `llama3_json` | yes | excellent |
| gpt-oss 120b | n/a | Function Calling | `openai` | yes (harmony) | very-good |
| Mistral Small 3 (24B) | n/a | Function Calling | `mistral` | yes | very-good |
| Qwen2.5-Coder 32B | n/a | Function Calling | `hermes` | yes | very-good |
| gpt-oss 20b | n/a | Function Calling | `openai` | yes (harmony) | good |
| Yi-1.5 34B Chat | n/a | not in FC tier | none | no | unsupported |

Notes on specific rows:

- **DeepSeek-V3.1** carries the score for the original **DeepSeek-V3** (57.23, V3); BFCL never listed a distinct V3.1 checkpoint, so treat it as an indicative prior for the family.
- **DeepSeek-R1 (0528)** tops the numeric list at 63.79 but is still `validate-first`: on stock vLLM it serves through the base-R1 prompt path (`deepseek_v3` parser, conditional `tool` role), so native tool calling is not guaranteed without validating your serve.
- **Gemma 2, Phi-4, Yi-1.5** appear mid-table on score but are `unsupported`: no vLLM tool parser and no `tool` role means they fail SAM's first hard gate. Phi-4's and Gemma's numbers are *prompt-mode* pseudo-JSON, not the native `tool_calls` SAM's loop consumes.
- The six **n/a** models (Llama 3.1 405B, both gpt-oss, Mistral Small 3, Qwen2.5-Coder 32B, and Yi-1.5) were never submitted to BFCL; their SAM verdict rests on the parser + `tool` role columns, verified per [`docs/benchmarks.md`](docs/benchmarks.md).

> Leaderboards move and these are documentation-backed priors, not per-stack measurements. The [validation harness](docs/validation.md) is the source of truth for your quant and serving path.
