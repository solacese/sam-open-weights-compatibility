# Picking a Model for SAM

This is the "which one should I run" guide: the tier shortlist, the hardware each model needs, the recommended GPU per budget, and the single best pick per provider. For the full per-model reasoning see [`shortlist.md`](shortlist.md); for the benchmark evidence behind every grade see [`benchmarks.md`](benchmarks.md).

## The shortlist, by tier

Full table with specs in [`shortlist.md`](shortlist.md); one spec card per model in [`../models/cards/`](../models/cards/).

| Tier | Models | Use for |
|---|---|---|
| **Orchestrator-grade** | Llama 3.3 70B · Qwen2.5 72B/32B · Qwen3 32B · Mistral Large 2 · Llama 3.1 405B/70B · DeepSeek-V3.1 · GLM-4.6 · gpt-oss 120b · Kimi-K2 · Command A | Multi-hop routing, fan-out, synthesis |
| **Domain / leaf agents** | Qwen2.5 14B/7B · Mistral Small 3 · Mixtral 8x22B · Mistral NeMo 12B · Llama 3.1 8B · Qwen2.5-Coder 32B · gpt-oss 20b | One or two tools, high volume, cost-sensitive |
| **Validate before trusting** | DeepSeek-R1 (0528) · Command R+ (legacy) | Native tool calling only under a specific revision / template / serving path - run the harness first |
| **Not recommended** | Gemma 2 27B · Phi-4 · Yi-1.5 34B | No native tool calling (no vLLM parser, no `tool` role) - they fail the first hard gate. See [`benchmarks.md`](benchmarks.md) for why, and the alternative to use. |

## Best pick per provider

If you're committed to a particular model family, this is the single **best SAM-usable** open-weights model each provider ships in this set. "Best" here means best SAM verdict first, BFCL score as the tiebreak - not raw score, because the highest-scoring checkpoint in a family is sometimes the one SAM can't drive natively.

| Provider | Country | Best SAM pick | BFCL score | SAM verdict | Recommended hardware (4-bit) |
|---|---|---|---|---|---|
| Alibaba (Qwen) | China | Qwen2.5 72B Instruct | 61.31 (P, V3) | excellent | 1x 48GB (A6000 / L40S) |
| Meta | USA | Llama 3.1 70B Instruct | 54.19 (P, V3) | excellent | 1x 48GB (A6000 / L40S) |
| Mistral AI | France | Mistral Large 2 (2411) | 38.37 (FC, V4) | excellent | 1x 80GB (A100 / H100) |
| Zhipu AI (Z.ai) | China | GLM-4.6 | 72.38 (FC, V4) | very-good | 4x 80GB (A100 / H100) |
| Moonshot AI | China | Kimi-K2 Instruct | 59.06 (FC, V4) | very-good | 8x 80GB (1x H100 node) |
| DeepSeek | China | DeepSeek-V3.1 | 57.23 (FC, V3) | very-good | 8x 80GB (1x H100 node) |
| Cohere | Canada | Command A (03-2025) | 46.49 (FC, V4) | very-good | 1x 80GB (A100 / H100) |
| OpenAI | USA | gpt-oss 120b | n/a | very-good | 1x 80GB (A100 / H100) |

> **Google, Microsoft, and 01.AI are absent by design.** Their only open-weights models in this set (Gemma 2 27B, Phi-4, Yi-1.5 34B) are `unsupported` - none can emit the native tool calls SAM requires - so there is no SAM-usable pick to list. Use another provider's model instead.

## Who makes these models

Open-weights models come from labs across the US, China, Europe, and Canada. Country of origin can matter for procurement, data-residency, or export-control policy, so it is called out per model in each [spec card](../models/cards/) and in [`../models/index.csv`](../models/index.csv). Summary:

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

## Next steps

- Confirm the score/verdict behind any pick: [`benchmarks.md`](benchmarks.md).
- Serve your chosen model: [`serving.md`](serving.md).
- Prove it works with SAM: [`validation.md`](validation.md).
