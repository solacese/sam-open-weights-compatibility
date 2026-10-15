# Mistral Small 4 119B

**Checked 2026-10-15 · publisher-documented · SAM validation: not-run**

| Field | Value |
|---|---|
| Checkpoint | `mistralai/Mistral-Small-4-119B-2603` |
| Publisher | Mistral AI |
| Availability | downloadable |
| Revision | `a11f36bebf709121056b1dbcc943d1c6afbe494d` |
| Total / active parameters | 119B / 6.5B |
| Reference context limit | 1,048,576 tokens (config.json) |
| Weight license | [apache-2.0](https://huggingface.co/mistralai/Mistral-Small-4-119B-2603/blob/a11f36bebf709121056b1dbcc943d1c6afbe494d/README.md) |
| Candidate role | orchestrator |
| vLLM tool parser hint | `mistral` |

Small is a family name: all 119B parameters matter for memory; reasoning parser is mistral.

[Publisher card at checked revision](https://huggingface.co/mistralai/Mistral-Small-4-119B-2603/blob/a11f36bebf709121056b1dbcc943d1c6afbe494d/README.md) · [Serving recipe entry point](https://huggingface.co/mistralai/Mistral-Small-4-119B-2603/blob/a11f36bebf709121056b1dbcc943d1c6afbe494d/README.md)

A parser hint is not a complete launch command. `see-recipe` means this catalog does not assert a parser name.
Select the runtime image, tokenizer, reasoning parser, chat template, quantization and hardware together.
Use the publisher's recipe, then pin and qualify that combination. [Serving guide](../../docs/serving.md).

## SAM model fragment

```yaml
model:
  model: openai/mistralai/Mistral-Small-4-119B-2603
  api_base: ${LLM_API_BASE}
  api_key: ${LLM_API_KEY}
  max_tokens: 4096
```

This fragment assumes the endpoint exposes the checkpoint ID. Replace it with your approved gateway alias when applicable.
The outer `openai/` selects a protocol; the remainder is the endpoint model ID. Configure output/reasoning budgets for your workload;
4096 is only a smoke-test budget. Parallel calls, forced tools and streaming need explicit validation for your SAM runtime.

## Qualify

```bash
export SAM_TEST_MODEL='openai/mistralai/Mistral-Small-4-119B-2603'
export SAM_TEST_API_BASE='http://127.0.0.1:8000/v1'
./scripts/probe.sh --report probe-result.json
```

Credentials come from `SAM_TEST_API_KEY`. A probe pass is endpoint evidence only.
Run real SAM traces, workload evaluation and operational gates before promotion: [validation](../../docs/validation.md).
