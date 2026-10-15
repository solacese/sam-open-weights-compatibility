# Research ledger — 15 October 2026

This ledger identifies the primary evidence behind the October refresh. “Checked” means metadata/documentation inspected, not weight inference reproduced. Model revisions and immutable card URLs and license links are in [models/index.csv](../models/index.csv). Each generated card exposes those same sources.

## Model publishers

| Publisher | Evidence inspected | What it establishes |
|---|---|---|
| Alibaba Qwen | [Official model organization](https://huggingface.co/Qwen/models); pinned Qwen3.8, Qwen3.6 and Qwen3.5 cards/configs/licenses in the catalog | Downloadable IDs, architecture components, reference context, sampling/serving entry points and differing terms |
| Google DeepMind | [Gemma 4 official page](https://deepmind.google/models/gemma/gemma-4/); pinned 31B, 26B A4B and 12B cards/configs | Current family supports native function calling; older Gemma 2 restrictions are not transferable |
| Mistral AI | [Official model organization](https://huggingface.co/mistralai/models); pinned Small 4, Medium 3.5, Large 3, Ministral and Devstral cards/licenses | Downloadable candidates and their distinct licenses; “Small” does not mean a small total parameter count |
| Mistral AI | [Large 4 announcement, 6 October 2026](https://mistral.ai/news/mistral-large-4/) | API public preview and weights planned for month end; no downloadable-candidate verdict at this cutoff |
| DeepSeek | [V4.1 Flash announcement](https://www.deepseek.com/en/news/deepseek-v4-1-flash/); pinned V4.1 Flash and V4 Pro 0813 cards/configs | Released weight artifacts, specialized architecture and deployment requirements |
| Z.ai | [Official model organization](https://huggingface.co/zai-org/models); pinned GLM 5.3 / Flash cards/licenses | Current candidates; Flash and flagship do not share the same weight license |
| Moonshot AI | [Official model organization](https://huggingface.co/moonshotai/models); pinned Kimi K3 / K2.7 Code cards/configs/licenses | Current multimodal/coding candidates and custom-license distinctions |
| NVIDIA | [Nemotron 3 Super](https://research.nvidia.com/labs/nemotron/Nemotron-3-Super/); pinned 3.5 Lightning / Super VL, Super BF16 and Ultra NVFP4 cards/configs | Hybrid architecture, supported deployment entry points, format and license differences |
| OpenAI | [Verifying gpt-oss implementations](https://developers.openai.com/cookbook/articles/gpt-oss/verifying-implementations); retained official hub metadata | Harmony/template implementation must be correct; baseline cards remain candidates, not new release claims |
| Reflection | [Beam announcement](https://reflection.ai/blog/introducing-beam) | Announced 501B / 23B active model; artifact/license/serving qualification tracked on watchlist |

Some published values use different definitions. The catalog preserves backbone versus auxiliary parameters, reference config versus extended context, and exact checkpoint versus hosted alias distinctions. No headline parameter figure is used as a complete physical memory budget.

## Serving, security and platform evidence

| Primary source | Use in this reference |
|---|---|
| [vLLM tool calling](https://docs.vllm.ai/en/latest/features/tool_calling/) | Parser availability is a serving capability, not SAM validation |
| [vLLM security](https://docs.vllm.ai/en/latest/usage/security/) | Private worker network, endpoint exposure, resource and cache isolation considerations |
| [vLLM tuning](https://docs.vllm.ai/en/latest/configuration/optimization/) · [metrics](https://docs.vllm.ai/en/latest/usage/metrics/) | Measure memory/latency envelope and service saturation |
| [SGLang documentation](https://docs.sglang.io/) | Alternative engine with checkpoint-specific recipes |
| [NVIDIA NIM](https://docs.nvidia.com/nim/large-language-models/latest/) · [Dynamo](https://docs.nvidia.com/dynamo/latest/) | Supported inference profiles and distributed serving platform options |
| [KServe](https://kserve.github.io/website/) | Kubernetes lifecycle/orchestration layer around inference engines |
| [Kubernetes multi-tenancy](https://kubernetes.io/docs/concepts/security/multi-tenancy/) | Isolation layers, ownership and resource controls |
| [Hugging Face TGI](https://huggingface.co/docs/text-generation-inference/en/index) | Maintenance status changes the recommendation for new platform work |
| [BFCL](https://gorilla.cs.berkeley.edu/leaderboard.html) | Benchmark methodology discovery; no numeric snapshot/ranking reproduced in this update |

SAM source revisions, paths and inspected behavior are in [methodology.md](methodology.md). Enterprise architecture, selection priorities and rollout gates are engineering recommendations informed by these sources, not vendor certifications.

## Known evidence limits

- No GPU inference, live model endpoint, deployed gateway, live SAM scenario, load test or failover drill was executed for this refresh.
- The offline tests exercise synthetic protocol responses and trace fixtures. Their success validates repository tooling only.
- No universal runtime launch bundle or live trace normalizer is supplied. The serving command and SAM config fragments are clearly identified as starting examples.
- Full model weights and all serving dependencies were not downloaded or audited. Artifact provenance, availability in a restricted environment, full license review and production support remain deployment qualification tasks.
- Search snippets and hosted benchmark aliases are not accepted as model compatibility evidence. Unverified parser names are left `see-recipe`.

## Refresh procedure

On a new release or planned upgrade, recheck the official checkpoint, exact license, config and authored deployment recipe. Add the immutable revision and research date, regenerate cards, run integrity checks, then qualify the actual bundle. Keep announcements on the watchlist until the required artifacts are available. Maintain validation results in a separate access-controlled evidence store and link only sanitized references here.
