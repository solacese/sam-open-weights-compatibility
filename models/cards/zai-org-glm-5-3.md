# GLM 5.3

**Checked 2026-10-15 · publisher-documented · SAM validation: not-run**

| Field | Value |
|---|---|
| Checkpoint | `zai-org/GLM-5.3` |
| Publisher | Z.ai |
| Availability | downloadable |
| Revision | `ba32f8c19c8738e2c57c71798c601d477a7bf844` |
| Total / active parameters | 753B / see report |
| Reference context limit | 1,048,576 tokens (config.json) |
| Weight license | [glm-5.3](https://huggingface.co/zai-org/GLM-5.3/blob/ba32f8c19c8738e2c57c71798c601d477a7bf844/LICENSE) |
| Candidate role | frontier |
| vLLM tool parser hint | `see-recipe` |

Custom GLM 5.3 license; vendor recipe and reasoning-history behavior require review.

[Publisher card at checked revision](https://huggingface.co/zai-org/GLM-5.3/blob/ba32f8c19c8738e2c57c71798c601d477a7bf844/README.md) · [Serving recipe entry point](https://huggingface.co/zai-org/GLM-5.3/blob/ba32f8c19c8738e2c57c71798c601d477a7bf844/README.md)

A parser hint is not a complete launch command. `see-recipe` means this catalog does not assert a parser name.
Select the runtime image, tokenizer, reasoning parser, chat template, quantization and hardware together.
Use the publisher's recipe, then pin and qualify that combination. [Serving guide](../../docs/serving.md).

## SAM model fragment

```yaml
model:
  model: openai/zai-org/GLM-5.3
  api_base: ${LLM_API_BASE}
  api_key: ${LLM_API_KEY}
  max_tokens: 4096
```

This fragment assumes the endpoint exposes the checkpoint ID. Replace it with your approved gateway alias when applicable.
The outer `openai/` selects a protocol; the remainder is the endpoint model ID. Configure output/reasoning budgets for your workload;
4096 is only a smoke-test budget. Parallel calls, forced tools and streaming need explicit validation for your SAM runtime.

## Qualify

```bash
export SAM_TEST_MODEL='openai/zai-org/GLM-5.3'
export SAM_TEST_API_BASE='http://127.0.0.1:8000/v1'
./scripts/probe.sh --report probe-result.json
```

Credentials come from `SAM_TEST_API_KEY`. A probe pass is endpoint evidence only.
Run real SAM traces, workload evaluation and operational gates before promotion: [validation](../../docs/validation.md).
