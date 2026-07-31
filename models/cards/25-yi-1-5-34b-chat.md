# 25. Yi-1.5 34B Chat

> **Not recommended for SAM.** This model lacks native OpenAI-schema tool calling, which SAM requires. See the note below for the recommended alternative.

| Field | Value |
|---|---|
| HF repo | `01-ai/Yi-1.5-34B-Chat` |
| Params (active) | 34B (34B) |
| Context window | 32,000 tokens |
| Native tool calling | **no** |
| Tool-calling grade | **unsupported** |
| Benchmark | No confirmed native FC (not in vLLM parser list or BFCL FC tier) |
| License | Apache-2.0 |
| Best SAM role | not-recommended |
| vLLM tool parser | `none` |

## SAM fit

No native tool calling. NOT recommended for SAM. Listed here so you know why, and what to use instead.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** expected FAIL - no native tool calling.
- **Context (S2):** 32,000 tokens - adequate for leaf agents; tight for deep multi-hop.
- **Role:** not a SAM agent model - use the alternative in the notes.
- **Notes:** NOT recommended for SAM: no confirmed native tool calling. Prefer a Qwen2.5/Qwen3 model at similar size.

## Serve it (vLLM)

vLLM has **no tool-call parser** for this model, so SAM tool calling will not work on a stock vLLM serve. Do not use it as a SAM agent model. If you must experiment, see the note above for the supported alternative.

## Validate

```bash
export SAM_TEST_MODEL="openai/01-ai/Yi-1.5-34B-Chat"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
