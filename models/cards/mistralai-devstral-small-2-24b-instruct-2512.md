# Devstral Small 2 24B

**Checked 2026-10-15 · publisher-documented · SAM validation: not-run**

| Field | Value |
|---|---|
| Checkpoint | `mistralai/Devstral-Small-2-24B-Instruct-2512` |
| Publisher | Mistral AI |
| Availability | downloadable |
| Revision | `55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128` |
| Total / active parameters | 24B / 24B |
| Reference context limit | 393,216 tokens (config.json) |
| Weight license | [apache-2.0](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512/blob/55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128/README.md) |
| Candidate role | coding |
| vLLM tool parser hint | `mistral` |

Coding tool specialist; assess general routing separately.

[Publisher card at checked revision](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512/blob/55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128/README.md) · [Serving recipe entry point](https://huggingface.co/mistralai/Devstral-Small-2-24B-Instruct-2512/blob/55c5b41e98c2dbd21b0c8afffc540dcfc9eb5128/README.md)

A parser hint is not a complete launch command. `see-recipe` means this catalog does not assert a parser name.
Select the runtime image, tokenizer, reasoning parser, chat template, quantization and hardware together.
Use the publisher's recipe, then pin and qualify that combination. [Serving guide](../../docs/serving.md).

## SAM model fragment

```yaml
model:
  model: openai/mistralai/Devstral-Small-2-24B-Instruct-2512
  api_base: ${LLM_API_BASE}
  api_key: ${LLM_API_KEY}
  max_tokens: 4096
```

This fragment assumes the endpoint exposes the checkpoint ID. Replace it with your approved gateway alias when applicable.
The outer `openai/` selects a protocol; the remainder is the endpoint model ID. Configure output/reasoning budgets for your workload;
4096 is only a smoke-test budget. Parallel calls, forced tools and streaming need explicit validation for your SAM runtime.

## Qualify

```bash
export SAM_TEST_MODEL='openai/mistralai/Devstral-Small-2-24B-Instruct-2512'
export SAM_TEST_API_BASE='http://127.0.0.1:8000/v1'
./scripts/probe.sh --report probe-result.json
```

Credentials come from `SAM_TEST_API_KEY`. A probe pass is endpoint evidence only.
Run real SAM traces, workload evaluation and operational gates before promotion: [validation](../../docs/validation.md).
