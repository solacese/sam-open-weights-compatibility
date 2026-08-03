# 23. Gemma 2 27B Instruct

> **Not recommended for SAM.** This model lacks native OpenAI-schema tool calling, which SAM requires. See the note below for the recommended alternative.

| Field | Value |
|---|---|
| HF repo | `google/gemma-2-27b-it` |
| Organization | Google |
| Country of origin | USA |
| Params (active) | 27B (27B) |
| Context window | 8,000 tokens |
| Native tool calling | **no** |
| Tool-calling grade | **unsupported** |
| Benchmark | No native FC (vLLM has no parser; HF card has no tool role; BFCL prompt-only) |
| License | Gemma |
| Best SAM role | not-recommended |
| vLLM tool parser | `none` |

## SAM fit

No native tool calling. NOT recommended for SAM. Listed here so you know why, and what to use instead.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** expected FAIL - no native tool calling.
- **Context (S2):** 8,000 tokens - LIMITING - short for orchestration, watch overflow.
- **Role:** not a SAM agent model - use the alternative in the notes.
- **Notes:** NOT recommended for SAM: no native tool calling. Only google/functiongemma-270m-it has FC. 8K context also limiting.

## Serve it (vLLM)

vLLM has **no tool-call parser** for this model, so SAM tool calling will not work on a stock vLLM serve. Do not use it as a SAM agent model. If you must experiment, see the note above for the supported alternative.

## Validate

```bash
export SAM_TEST_MODEL="openai/google/gemma-2-27b-it"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
