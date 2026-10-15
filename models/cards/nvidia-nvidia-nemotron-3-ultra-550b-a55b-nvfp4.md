# Nemotron 3 Ultra 550B NVFP4

**Checked 2026-10-15 · publisher-documented · SAM validation: not-run**

| Field | Value |
|---|---|
| Checkpoint | `nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-NVFP4` |
| Publisher | NVIDIA |
| Availability | downloadable |
| Revision | `02462641f13d3af838b904f48195b9bb8a1e4ebc` |
| Total / active parameters | 550B / 55B |
| Reference context limit | 262,144 tokens (config.json) |
| Weight license | [openmdw-1.1](https://openmdw.ai/license/1-1/) |
| Candidate role | frontier |
| vLLM tool parser hint | `see-recipe` |

OpenMDW 1.1; native NVFP4 kernel support required; config is 256K with vendor 1M extension.

[Publisher card at checked revision](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-NVFP4/blob/02462641f13d3af838b904f48195b9bb8a1e4ebc/README.md) · [Serving recipe entry point](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-NVFP4/blob/02462641f13d3af838b904f48195b9bb8a1e4ebc/README.md)

A parser hint is not a complete launch command. `see-recipe` means this catalog does not assert a parser name.
Select the runtime image, tokenizer, reasoning parser, chat template, quantization and hardware together.
Use the publisher's recipe, then pin and qualify that combination. [Serving guide](../../docs/serving.md).

## SAM model fragment

```yaml
model:
  model: openai/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-NVFP4
  api_base: ${LLM_API_BASE}
  api_key: ${LLM_API_KEY}
  max_tokens: 4096
```

This fragment assumes the endpoint exposes the checkpoint ID. Replace it with your approved gateway alias when applicable.
The outer `openai/` selects a protocol; the remainder is the endpoint model ID. Configure output/reasoning budgets for your workload;
4096 is only a smoke-test budget. Parallel calls, forced tools and streaming need explicit validation for your SAM runtime.

## Qualify

```bash
export SAM_TEST_MODEL='openai/nvidia/NVIDIA-Nemotron-3-Ultra-550B-A55B-NVFP4'
export SAM_TEST_API_BASE='http://127.0.0.1:8000/v1'
./scripts/probe.sh --report probe-result.json
```

Credentials come from `SAM_TEST_API_KEY`. A probe pass is endpoint evidence only.
Run real SAM traces, workload evaluation and operational gates before promotion: [validation](../../docs/validation.md).
