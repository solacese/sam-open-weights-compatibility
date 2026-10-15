# Gemma 4 26B A4B IT

**Checked 2026-10-15 · publisher-documented · SAM validation: not-run**

| Field | Value |
|---|---|
| Checkpoint | `google/gemma-4-26B-A4B-it` |
| Publisher | Google DeepMind |
| Availability | downloadable |
| Revision | `4d7ae4984b7db7de8f8457170b3f1a419ee76d52` |
| Total / active parameters | 25.2B text + vision / 3.8B text |
| Reference context limit | 262,144 tokens (config.json) |
| Weight license | [apache-2.0](https://ai.google.dev/gemma/docs/gemma_4_license) |
| Candidate role | domain |
| vLLM tool parser hint | `see-recipe` |

MoE alternative; include vision encoder in physical sizing.

[Publisher card at checked revision](https://huggingface.co/google/gemma-4-26B-A4B-it/blob/4d7ae4984b7db7de8f8457170b3f1a419ee76d52/README.md) · [Serving recipe entry point](https://huggingface.co/google/gemma-4-26B-A4B-it/blob/4d7ae4984b7db7de8f8457170b3f1a419ee76d52/README.md)

A parser hint is not a complete launch command. `see-recipe` means this catalog does not assert a parser name.
Select the runtime image, tokenizer, reasoning parser, chat template, quantization and hardware together.
Use the publisher's recipe, then pin and qualify that combination. [Serving guide](../../docs/serving.md).

## SAM model fragment

```yaml
model:
  model: openai/google/gemma-4-26B-A4B-it
  api_base: ${LLM_API_BASE}
  api_key: ${LLM_API_KEY}
  max_tokens: 4096
```

This fragment assumes the endpoint exposes the checkpoint ID. Replace it with your approved gateway alias when applicable.
The outer `openai/` selects a protocol; the remainder is the endpoint model ID. Configure output/reasoning budgets for your workload;
4096 is only a smoke-test budget. Parallel calls, forced tools and streaming need explicit validation for your SAM runtime.

## Qualify

```bash
export SAM_TEST_MODEL='openai/google/gemma-4-26B-A4B-it'
export SAM_TEST_API_BASE='http://127.0.0.1:8000/v1'
./scripts/probe.sh --report probe-result.json
```

Credentials come from `SAM_TEST_API_KEY`. A probe pass is endpoint evidence only.
Run real SAM traces, workload evaluation and operational gates before promotion: [validation](../../docs/validation.md).
