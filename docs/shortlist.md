# October 2026 model candidates

Snapshot: **15 October 2026**. Listing order groups evaluation candidates; it is not a benchmark ranking. Every entry is **publisher-documented / SAM not run**. No live GPU or SAM validation results are claimed.

Context below is the reference config/card limit, not a tested service capacity. Publisher extensions and special memory components are noted on each card. See [selection](pick-a-model.md), [capacity](capacity-planning.md), and [license review](licensing.md).

| Candidate | Total / active parameters | Reference context | License | Suggested evaluation role |
|---|---|---|---|---|
| [Qwen3.8 27B](../models/cards/qwen-qwen3-8-27b.md) | 27B / 27B | 262,144 | apache-2.0 | domain-or-orchestrator |
| [Qwen3.6 35B A3B](../models/cards/qwen-qwen3-6-35b-a3b.md) | 35B / 3B | 262,144 | apache-2.0 | domain-or-orchestrator |
| [Qwen3.5 9B](../models/cards/qwen-qwen3-5-9b.md) | 9B / 9B | 262,144 | apache-2.0 | leaf |
| [Qwen3.8 Flash Next](../models/cards/qwen-qwen3-8-flash-next.md) | 125B backbone + 51B n-gram + 4B MTP / 6B backbone active | 262,144 | qwen-community-1.0 | orchestrator |
| [Qwen3.8 2.4T A95B](../models/cards/qwen-qwen3-8-2-4t-a95b.md) | 2.4T / 95B | 262,144 | qwen3.8-max | frontier |
| [Gemma 4 31B IT](../models/cards/google-gemma-4-31b-it.md) | 30.7B text + vision / 30.7B text | 262,144 | apache-2.0 | domain-or-orchestrator |
| [Gemma 4 26B A4B IT](../models/cards/google-gemma-4-26b-a4b-it.md) | 25.2B text + vision / 3.8B text | 262,144 | apache-2.0 | domain |
| [Gemma 4 12B IT](../models/cards/google-gemma-4-12b-it.md) | 11.95B / 11.95B | 262,144 | apache-2.0 | leaf |
| [Ministral 3 14B Instruct](../models/cards/mistralai-ministral-3-14b-instruct-2512.md) | 14B / 14B | 262,144 | apache-2.0 | leaf |
| [Devstral Small 2 24B](../models/cards/mistralai-devstral-small-2-24b-instruct-2512.md) | 24B / 24B | 393,216 | apache-2.0 | coding |
| [Mistral Small 4 119B](../models/cards/mistralai-mistral-small-4-119b-2603.md) | 119B / 6.5B | 1,048,576 | apache-2.0 | orchestrator |
| [Mistral Medium 3.5 128B](../models/cards/mistralai-mistral-medium-3-5-128b.md) | 128B / 128B | 262,144 | Modified MIT (revenue restriction) | orchestrator |
| [Mistral Large 3 675B](../models/cards/mistralai-mistral-large-3-675b-instruct-2512.md) | 675B / 41B | 294,912 | apache-2.0 | frontier |
| [gpt-oss 20b](../models/cards/openai-gpt-oss-20b.md) | 21B / 3.6B | 131,072 | apache-2.0 | leaf |
| [gpt-oss 120b](../models/cards/openai-gpt-oss-120b.md) | 117B / 5.1B | 131,072 | apache-2.0 | orchestrator |
| [GLM 5.3 Flash](../models/cards/zai-org-glm-5-3-flash.md) | 320B / 18B | 1,048,576 | mit | orchestrator |
| [GLM 5.3](../models/cards/zai-org-glm-5-3.md) | 753B / see report | 1,048,576 | glm-5.3 | frontier |
| [DeepSeek V4.1 Flash](../models/cards/deepseek-ai-deepseek-v4-1-flash.md) | 552B backbone + 196B Engram / 8B prefill / 16B decode | 1,048,576 | mit | frontier |
| [DeepSeek V4 Pro 0813](../models/cards/deepseek-ai-deepseek-v4-pro-0813.md) | 1.6T backbone / 49B | 1,048,576 | mit | frontier |
| [Kimi K2.7 Code](../models/cards/moonshotai-kimi-k2-7-code.md) | 1T + vision / 32B | 262,144 | modified-mit | coding |
| [Kimi K3](../models/cards/moonshotai-kimi-k3.md) | 2.8T + vision / 104B | 1,048,576 | kimi-k3 | frontier |
| [Nemotron 3 Super 120B BF16](../models/cards/nvidia-nvidia-nemotron-3-super-120b-a12b-bf16.md) | 120B / 12B | 262,144 | nvidia-nemotron-open-model-license | orchestrator |
| [Nemotron 3 Ultra 550B NVFP4](../models/cards/nvidia-nvidia-nemotron-3-ultra-550b-a55b-nvfp4.md) | 550B / 55B | 262,144 | openmdw-1.1 | frontier |
| [Nemotron 3.5 Lightning 30B NVFP4](../models/cards/nvidia-nvidia-nemotron-3-5-lightning-30b-a3b-nvfp4.md) | 30B / 3B | 1,048,576 | openmdw-1.1 | leaf-or-domain |
| [Nemotron 3.5 Super VL 120B BF16](../models/cards/nvidia-nvidia-nemotron-3-5-super-vl-120b-a12b-bf16.md) | 120B / 12B | 1,048,576 | openmdw-1.1 | multimodal-orchestrator |

## Announcements and exclusions

- **Mistral Large 4:** API preview announced 6 October; publisher schedules weights for month end. Excluded from downloadable candidates as of this snapshot. [Announcement](https://mistral.ai/news/mistral-large-4/).
- **Reflection Beam:** announced 501B / 23B active. Track checkpoint, license and supported serving evidence before qualification. [Publisher announcement](https://reflection.ai/blog/introducing-beam). No SAM verdict recorded here.
- Hosted aliases and benchmarks do not establish that matching downloadable weights have the same features.
- Draft models, base checkpoints, guard classifiers, embeddings and rerankers are not interchangeable with agent models.

## Historical coverage

The original 25 rows remain in [legacy-2025.csv](../models/legacy-2025.csv) for migration reference. Their grades, parser hints, hardware estimates and BFCL figures are historical, unverified claims, not current recommendations. Existing qualified Llama 3, Qwen 2.5 or other deployments can remain useful; requalify before changing them.
