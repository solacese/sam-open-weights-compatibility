# Qwen3.5 9B

**Checked 2026-10-15 · publisher-documented · SAM validation: not-run**

| Field | Value |
|---|---|
| Checkpoint | `Qwen/Qwen3.5-9B` |
| Publisher | Alibaba Qwen |
| Availability | downloadable |
| Revision | `c202236235762e1c871ad0ccb60c8ee5ba337b9a` |
| Total / active parameters | 9B / 9B |
| Reference context limit | 262,144 tokens (config.json) |
| Weight license | [apache-2.0](https://huggingface.co/Qwen/Qwen3.5-9B/blob/c202236235762e1c871ad0ccb60c8ee5ba337b9a/LICENSE) |
| Candidate role | leaf |
| vLLM tool parser hint | `qwen3_coder` |

Small multimodal candidate; assess argument fidelity and long-context quality.

[Publisher card at checked revision](https://huggingface.co/Qwen/Qwen3.5-9B/blob/c202236235762e1c871ad0ccb60c8ee5ba337b9a/README.md) · [Serving recipe entry point](https://huggingface.co/Qwen/Qwen3.5-9B/blob/c202236235762e1c871ad0ccb60c8ee5ba337b9a/README.md)

A parser hint is not a complete launch command. `see-recipe` means this catalog does not assert a parser name.
Select the runtime image, tokenizer, reasoning parser, chat template, quantization and hardware together.
Use the publisher's recipe, then pin and qualify that combination. [Serving guide](../../docs/serving.md).

## SAM model fragment

```yaml
model:
  model: openai/Qwen/Qwen3.5-9B
  api_base: ${LLM_API_BASE}
  api_key: ${LLM_API_KEY}
  max_tokens: 4096
```

This fragment assumes the endpoint exposes the checkpoint ID. Replace it with your approved gateway alias when applicable.
The outer `openai/` selects a protocol; the remainder is the endpoint model ID. Configure output/reasoning budgets for your workload;
4096 is only a smoke-test budget. Parallel calls, forced tools and streaming need explicit validation for your SAM runtime.

## Qualify

```bash
export SAM_TEST_MODEL='openai/Qwen/Qwen3.5-9B'
export SAM_TEST_API_BASE='http://127.0.0.1:8000/v1'
./scripts/probe.sh --report probe-result.json
```

Credentials come from `SAM_TEST_API_KEY`. A probe pass is endpoint evidence only.
Run real SAM traces, workload evaluation and operational gates before promotion: [validation](../../docs/validation.md).
