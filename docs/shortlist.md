# Top-20 Open-Weights Models for SAM

Ranked by fit against the [requirements whitelist](requirements.md), weighted toward the hard gates — **reliable, streaming, OpenAI-schema tool calling** — then by practical hosting cost and context.

All are servable behind an OpenAI-compatible API (`openai/` prefix + `api_base`) via vLLM, SGLang, TGI, Ollama, or a LiteLLM proxy. Context figures are the commonly-served values; some models support larger with RoPE scaling. **Grades are starting points — [validate on your stack](validation.md).**

Tool-calling grade legend: **Excellent** = production-proven native tool calling with a mature server-side parser; **Very good** = reliable, widely used; **Good** = works, occasional arg-format quirks; **Fair** = template-dependent, validate carefully.

| # | Model | Params (active) | Context | Tool calling | License | Best role | Notes |
|---|---|---|---|---|---|---|---|
| 1 | **Llama 3.3 70B Instruct** | 70B | 128K | Excellent | Llama 3.3 Community | Orchestrator | Best all-round open tool caller; mature vLLM/SGLang tool parser. In SAM `modelinfo`. |
| 2 | **Qwen2.5 72B Instruct** | 72B | 128K | Excellent | Qwen | Orchestrator | Strong multi-tool + parallel calls; excellent instruction following. |
| 3 | **Qwen2.5 32B Instruct** | 32B | 128K | Excellent | Apache-2.0 | Orchestrator (budget) | Best "fits one GPU" orchestrator; Apache-2.0 is a licensing win. |
| 4 | **Mistral Large 2 (2411)** | 123B | 128K | Excellent | MRL (research/non-prod free) | Orchestrator | Function calling designed-in. In SAM `modelinfo` (`mistral-large`). Check license for commercial. |
| 5 | **Llama 3.1 405B Instruct** | 405B | 128K | Excellent | Llama 3.1 Community | Orchestrator (ceiling) | Highest reasoning ceiling; heavy to host (multi-GPU/quant). In SAM `modelinfo`. |
| 6 | **Llama 3.1 70B Instruct** | 70B | 128K | Excellent | Llama 3.1 Community | Orchestrator | Ubiquitous, proven, safe default. In SAM `modelinfo`. |
| 7 | **DeepSeek-V3** | 671B MoE (37B) | 128K | Very good | DeepSeek (MIT-style) | Orchestrator | MoE keeps active params low; strong tool + reasoning. Needs big host or provider. |
| 8 | **Command R+** | 104B | 128K | Excellent | CC-BY-NC 4.0 | Orchestrator / RAG | Purpose-built for tool use + RAG. `cohere` prefix or OpenAI-compat. Non-commercial license. |
| 9 | **Qwen2.5 14B Instruct** | 14B | 128K | Very good | Apache-2.0 | Domain agent | Excellent quality/size for leaf agents; Apache-2.0. |
| 10 | **Mixtral 8x22B Instruct** | 141B MoE (39B) | 64K | Very good | Apache-2.0 | Orchestrator (efficient) | Efficient MoE; solid function calling. Smaller context than the leaders. |
| 11 | **Mistral Small 3 (24B)** | 24B | 32K | Very good | Apache-2.0 | Domain agent | Fast, native tool calling. In SAM `modelinfo` (`mistral-small`). |
| 12 | **Qwen2.5 7B Instruct** | 7B | 128K | Good | Apache-2.0 | Leaf agent (volume) | Cheapest reliable tool caller; great for high-QPS leaf agents. |
| 13 | **Command R (35B)** | 35B | 128K | Very good | CC-BY-NC 4.0 | Compliance / RAG | RAG + tool tuned; strong grounded answers. Non-commercial license. |
| 14 | **Qwen2.5-Coder 32B** | 32B | 128K | Very good | Apache-2.0 | Structured-arg tools | Best when tool args are code/structured/JSON-heavy. |
| 15 | **Mistral NeMo 12B** | 12B | 128K | Good | Apache-2.0 | Leaf agent | Long context at small size; decent function calling. |
| 16 | **Llama 3.1 8B Instruct** | 8B | 128K | Good | Llama 3.1 Community | Leaf agent | Ubiquitous small model; fine for single-tool agents. In SAM `modelinfo`. |
| 17 | **Gemma 2 27B Instruct** | 27B | 8K | Fair ⚠ | Gemma | Validate first | Strong general model but tool calling is template-driven; **8K context is limiting**. Confirm H1–H3. |
| 18 | **DeepSeek-R1** | 671B MoE (37B) | 128K | Good ⚠ | DeepSeek (MIT-style) | Reasoning beat | Excellent reasoning; tool calling less battle-tested than V3. Pair with `thinking:` budget. |
| 19 | **Phi-4 (14B)** | 14B | 16K | Good ⚠ | MIT | Leaf agent | Efficient, MIT-licensed; modest context, validate tool-call reliability. |
| 20 | **Yi-1.5 34B Chat** | 34B | 32K | Fair ⚠ | Apache-2.0 | Validate first | Capable general model; tool calling weaker/templated — exercise H1–H3 before trusting. |

⚠ = meets the soft bar but **must pass the [harness](validation.md)** before production; tool calling is templated or less consistent than the tiers above.

---

## How to choose

### By role

- **Orchestrator** (multi-hop routing, fan-out, synthesis, forced tools): pick from **#1–8, #10**. This is where tool-calling reliability and context size matter most. Llama 3.3 70B and Qwen2.5 72B/32B are the safe picks.
- **Domain / leaf agent** (one or two tools, high volume): **#9, #11, #12, #14, #15, #16**. Optimize for cost and latency; you don't need 70B to call one tool.
- **Compliance / RAG-heavy agent**: **#8, #13** (Command family) or **#2/#3** (Qwen) — strong grounded, citation-friendly answers.
- **Reasoning-forward agent**: **#18** (DeepSeek-R1) with a `thinking:` budget, or **#7** (DeepSeek-V3) for reasoning + reliable tools.

### By constraint

| Constraint | Recommendation |
|---|---|
| **Apache-2.0 / commercial-clean** | Qwen2.5 (any size), Mixtral 8x22B, Mistral Small 3, Mistral NeMo, Yi-1.5. Phi-4 is MIT. |
| **Single 80GB GPU (quantized)** | Qwen2.5 32B, Mistral Small 3 24B, Gemma 2 27B, Command R 35B, Qwen2.5-Coder 32B. |
| **Single consumer GPU (24GB, quantized)** | Qwen2.5 7B/14B, Llama 3.1 8B, Mistral NeMo 12B, Phi-4. |
| **Maximum capability, host is not a constraint** | Llama 3.1 405B, DeepSeek-V3, Qwen2.5 72B. |
| **Long documents in context** | Anything 128K: Llama 3.x, Qwen2.5, Mistral NeMo/Large, DeepSeek. Avoid Gemma 2 (8K), Phi-4 (16K). |

## What we deliberately excluded

- **Base / non-instruct models** — no chat template, no tool calling. Instruct/chat variants only.
- **Models with no OpenAI tool-call support** — e.g. pure text models you can only prompt into pseudo-JSON. They fail H1.
- **Sub-7B models** — tool-calling reliability drops off sharply; the agent loop stalls or loops. Use them only for trivial single-tool agents after passing the harness.
- **Embedding / reranker models** — not chat/agent models.

## A note on grades vs. reality

Tool-calling reliability for a given model depends heavily on:

1. **The serving stack's tool parser** — vLLM `--tool-call-parser`, SGLang's, or Ollama's template. A wrong or missing parser turns "Excellent" into "broken."
2. **Quant level** — aggressive quantization (e.g. 3-bit) degrades JSON-argument fidelity (S3) before it degrades chat quality.
3. **Chat template** — the model's tokenizer template must include the tool-calling sections. Mismatches cause H3 failures.

This is exactly why the [validation harness](validation.md) exists. Treat this table as *where to start*, then let the harness give you the *yes/no on your infrastructure*.
