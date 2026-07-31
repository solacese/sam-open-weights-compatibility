# Open-Weights Models for SAM: the verified shortlist

25 models, ranked by fit against the [requirements whitelist](requirements.md), weighted toward the hard gates - **reliable, streaming, OpenAI-schema tool calling** - then by practical hosting cost and context.

Every "grade" here is grounded in three primary sources, not a guess: the [vLLM tool-call parser matrix](https://docs.vllm.ai/en/latest/features/tool_calling.html) (does a working server-side parser exist?), the [Berkeley Function-Calling Leaderboard](https://gorilla.cs.berkeley.edu/leaderboard.html) (is the model in the native Function-Calling tier or only the Prompt tier?), and each model's Hugging Face card (does the chat template define a `tool` role?). See [benchmarks.md](benchmarks.md) for the per-model evidence, and **[validate on your stack](validation.md)** before production - the grade tells you where to start, the harness gives the yes/no on your infrastructure.

All models marked `yes`/`partial` are servable behind an OpenAI-compatible API (`openai/` prefix + `api_base`) via vLLM, SGLang, TGI, Ollama, or a LiteLLM proxy. Context figures are the commonly-served values; some support larger with RoPE scaling.

Grade legend: **excellent** = native tool calling with a mature vLLM parser, in the BFCL Function-Calling tier or SAM `modelinfo`; **very-good** = native tool calling with a working parser, widely used; **good** = native tool calling, occasional JSON-arg quirks - validate S3; **validate-first** = tool calling is conditional (specific revision, template, or serving path) - must pass the harness; **unsupported** = no native tool calling, not recommended for SAM.

## Recommended (native tool calling, ready to validate)

| # | Model | Params (active) | Context | Grade | vLLM parser | License | Best role |
|---|---|---|---|---|---|---|---|
| 1 | **Llama 3.3 70B Instruct** | 70B | 128K | excellent | `llama3_json` | Llama 3.3 Community | Orchestrator |
| 2 | **Qwen2.5 72B Instruct** | 72B | 128K | excellent | `hermes` | Qwen | Orchestrator |
| 3 | **Qwen2.5 32B Instruct** | 32B | 128K | excellent | `hermes` | Apache-2.0 | Orchestrator (budget) |
| 4 | **Qwen3 32B** | 32B | 128K | excellent | `hermes` | Apache-2.0 | Orchestrator |
| 5 | **Mistral Large 2 (2411)** | 123B | 128K | excellent | `mistral` | MRL (non-prod free) | Orchestrator |
| 6 | **Llama 3.1 405B Instruct** | 405B | 128K | excellent | `llama3_json` | Llama 3.1 Community | Orchestrator (ceiling) |
| 7 | **Llama 3.1 70B Instruct** | 70B | 128K | excellent | `llama3_json` | Llama 3.1 Community | Orchestrator |
| 8 | **DeepSeek-V3.1** | 671B MoE (37B) | 128K | very-good | `deepseek_v31` | DeepSeek (MIT-style) | Orchestrator |
| 9 | **GLM-4.6** | 355B MoE (32B) | 128K | very-good | `glm45` | MIT | Orchestrator |
| 10 | **gpt-oss 120b** | 117B MoE (5.1B) | 128K | very-good | `openai` | Apache-2.0 | Orchestrator |
| 11 | **Kimi-K2 Instruct** | 1T MoE (32B) | 128K | very-good | `kimi_k2` | Modified MIT | Orchestrator |
| 12 | **Command A (03-2025)** | 111B | 256K | very-good | `cohere_command3` | CC-BY-NC-4.0 | Compliance / RAG |
| 13 | **Qwen2.5 14B Instruct** | 14B | 128K | very-good | `hermes` | Apache-2.0 | Domain agent |
| 14 | **Mixtral 8x22B Instruct** | 141B MoE (39B) | 64K | good | `mistral` | Apache-2.0 | Orchestrator (efficient) |
| 15 | **Mistral Small 3 (24B)** | 24B | 32K | very-good | `mistral` | Apache-2.0 | Domain agent |
| 16 | **Qwen2.5 7B Instruct** | 7B | 128K | good | `hermes` | Apache-2.0 | Leaf agent (volume) |
| 17 | **Qwen2.5-Coder 32B** | 32B | 128K | very-good | `hermes` | Apache-2.0 | Structured-arg tools |
| 18 | **gpt-oss 20b** | 21B MoE (3.6B) | 128K | good | `openai` | Apache-2.0 | Leaf agent |
| 19 | **Mistral NeMo 12B** | 12B | 128K | good | `mistral` | Apache-2.0 | Leaf agent |
| 20 | **Llama 3.1 8B Instruct** | 8B | 128K | good | `llama3_json` | Llama 3.1 Community | Leaf agent |

## Validate first (conditional tool calling)

These have partial or revision-specific tool calling. They can work, but do not assume it - run the [harness](validation.md) (H1-H3) before any use.

| # | Model | Params (active) | Context | Grade | vLLM parser | License | Why conditional |
|---|---|---|---|---|---|---|---|
| 21 | **DeepSeek-R1 (0528)** | 671B MoE (37B) | 128K | validate-first | `deepseek_v3` | MIT | Use the **0528** revision + R1 chat template; base R1 is BFCL Prompt-tier only. |
| 22 | **Command R+ (legacy)** | 104B | 128K | validate-first | none | CC-BY-NC-4.0 | Superseded by Command A; no current vLLM parser. Prefer #12. |

## Not recommended (no native tool calling)

Listed so you know why, and what to use instead. These lack native OpenAI-schema tool calling, so they fail H1 regardless of prompt engineering.

| # | Model | Context | License | Why not | Use instead |
|---|---|---|---|---|---|
| 23 | **Gemma 2 27B Instruct** | 8K | Gemma | No parser in vLLM; HF template has no `tool` role; only `google/functiongemma-270m-it` has FC. 8K context also limiting. | Qwen2.5 32B (#3) |
| 24 | **Phi-4 (14B)** | 16K | MIT | No vLLM parser; HF template is system/user/assistant only; BFCL Prompt-tier only. | Qwen2.5 14B (#13) |
| 25 | **Yi-1.5 34B Chat** | 32K | Apache-2.0 | Not in the vLLM parser list or the BFCL Function-Calling tier; no confirmed native FC. | Mistral Small 3 24B (#15) |

---

## How to choose

### By role

- **Orchestrator** (multi-hop routing, fan-out, synthesis, forced tools): **#1-12, #14, #17**. This is where tool-calling reliability and context matter most. Llama 3.3 70B, Qwen2.5 72B/32B, and Qwen3 32B are the safe picks.
- **Domain / leaf agent** (one or two tools, high volume): **#13, #15, #16, #18, #19, #20**. Optimize for cost and latency; you don't need 70B to call one tool.
- **Compliance / RAG-heavy agent**: **#12** (Command A) or **#2/#3** (Qwen) - strong grounded, citation-friendly answers.
- **Reasoning-forward agent**: **#8** (DeepSeek-V3.1) or **#10** (gpt-oss 120b, agentic-first) for reasoning + reliable tools; **#21** (DeepSeek-R1 0528) with a `thinking:` budget only after the harness passes.

### By constraint

| Constraint | Recommendation |
|---|---|
| **Apache-2.0 / commercial-clean** | Qwen2.5 (any size), Qwen3 32B, Mixtral 8x22B, Mistral Small 3, Mistral NeMo, gpt-oss 20b/120b. |
| **MIT-licensed** | GLM-4.6, DeepSeek-R1 0528. |
| **Single 80GB GPU (quantized)** | Qwen2.5 32B, Qwen3 32B, Mistral Small 3 24B, Qwen2.5-Coder 32B, gpt-oss 20b. |
| **Single consumer GPU (24GB, quantized)** | Qwen2.5 7B/14B, Llama 3.1 8B, Mistral NeMo 12B, gpt-oss 20b (~16GB). |
| **Maximum capability, host is not a constraint** | Llama 3.1 405B, Kimi-K2, DeepSeek-V3.1, Qwen2.5 72B. |
| **Long documents in context** | Command A (256K), or any 128K: Llama 3.x, Qwen2.5/Qwen3, Mistral NeMo/Large, DeepSeek, GLM, gpt-oss. Avoid Gemma 2 (8K), Phi-4 (16K). |

## What we deliberately excluded

- **Base / non-instruct models** - no chat template, no tool calling. Instruct/chat variants only.
- **Models with no native OpenAI tool-call support** - Gemma 2, Phi-4, Yi-1.5 (see the not-recommended table). They fail H1.
- **Sub-7B models** - tool-calling reliability drops off sharply; the agent loop stalls or loops. Use only for trivial single-tool agents after passing the harness.
- **Embedding / reranker models** - not chat/agent models.

## A note on grades vs. reality

Tool-calling reliability for a given model depends heavily on:

1. **The serving stack's tool parser** - vLLM `--tool-call-parser`, SGLang's, or Ollama's template. A wrong or missing parser turns "excellent" into "broken." A model with parser `none` will not do SAM tool calling on a stock serve at all.
2. **Quant level** - aggressive quantization (e.g. 3-bit) degrades JSON-argument fidelity (S3) before it degrades chat quality.
3. **Chat template** - the model's tokenizer template must include the tool-calling sections. Mismatches cause H3 failures.

This is exactly why the [validation harness](validation.md) exists. Treat this table as *where to start*, then let the harness give you the *yes/no on your infrastructure*.
