# 20. Yi-1.5 34B Chat

| Field | Value |
|---|---|
| HF repo | `01-ai/Yi-1.5-34B-Chat` |
| Params (active) | 34B (34B) |
| Context window | 32,000 tokens |
| Tool-calling grade | **fair** |
| License | Apache-2.0 |
| Best SAM role | validate-first |
| vLLM tool parser | `hermes` |

## SAM fit

Tool calling is template-dependent. MUST pass the harness (H1-H3) before production.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** REQUIRES harness validation — do not assume.
- **Context (S2):** 32,000 tokens — adequate for leaf agents; tight for deep multi-hop.
- **Role:** suited to domain/leaf agents (one or two tools, cost-sensitive, high volume).
- **Notes:** Templated tool calling; validate H1-H3.

## SAM `model:` block

```yaml
model:
  model: openai/01-ai/Yi-1.5-34B-Chat
  api_base: ${LLM_API_BASE}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${LLM_API_KEY, sk-noop}
  parallel_tool_calls: true
  temperature: 0.2
  max_tokens: 4096
```

## Serve it (vLLM)

```bash
vllm serve 01-ai/Yi-1.5-34B-Chat \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser hermes \
  --max-model-len 32000
```

## Validate

```bash
export SAM_TEST_MODEL="openai/01-ai/Yi-1.5-34B-Chat"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
