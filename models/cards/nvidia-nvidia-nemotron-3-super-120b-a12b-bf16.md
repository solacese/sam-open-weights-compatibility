# Nemotron 3 Super 120B BF16

**Checked 2026-10-15 · publisher-documented · SAM validation: not-run**

| Field | Value |
|---|---|
| Checkpoint | `nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16` |
| Publisher | NVIDIA |
| Availability | downloadable |
| Revision | `2dc98e2afe4face0e4ce40972a915c45368bd34a` |
| Total / active parameters | 120B / 12B |
| Reference context limit | 262,144 tokens (config.json) |
| Weight license | [nvidia-nemotron-open-model-license](https://www.nvidia.com/en-us/agreements/enterprise-software/nvidia-nemotron-open-model-license/) |
| Candidate role | orchestrator |
| vLLM tool parser hint | `qwen3_coder` |

Custom Nemotron license; config is 256K, card advertises extension to 1M; hybrid state is not ordinary KV.

[Publisher card at checked revision](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16/blob/2dc98e2afe4face0e4ce40972a915c45368bd34a/README.md) · [Serving recipe entry point](https://huggingface.co/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16/blob/2dc98e2afe4face0e4ce40972a915c45368bd34a/README.md)

A parser hint is not a complete launch command. `see-recipe` means this catalog does not assert a parser name.
Select the runtime image, tokenizer, reasoning parser, chat template, quantization and hardware together.
Use the publisher's recipe, then pin and qualify that combination. [Serving guide](../../docs/serving.md).

## SAM model fragment

```yaml
model:
  model: openai/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16
  api_base: ${LLM_API_BASE}
  api_key: ${LLM_API_KEY}
  max_tokens: 4096
```

This fragment assumes the endpoint exposes the checkpoint ID. Replace it with your approved gateway alias when applicable.
The outer `openai/` selects a protocol; the remainder is the endpoint model ID. Configure output/reasoning budgets for your workload;
4096 is only a smoke-test budget. Parallel calls, forced tools and streaming need explicit validation for your SAM runtime.

## Qualify

```bash
export SAM_TEST_MODEL='openai/nvidia/NVIDIA-Nemotron-3-Super-120B-A12B-BF16'
export SAM_TEST_API_BASE='http://127.0.0.1:8000/v1'
./scripts/probe.sh --report probe-result.json
```

Credentials come from `SAM_TEST_API_KEY`. A probe pass is endpoint evidence only.
Run real SAM traces, workload evaluation and operational gates before promotion: [validation](../../docs/validation.md).
