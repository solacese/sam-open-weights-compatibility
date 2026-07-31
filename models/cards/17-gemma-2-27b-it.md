# 17. Gemma 2 27B Instruct

| Field | Value |
|---|---|
| HF repo | `google/gemma-2-27b-it` |
| Params (active) | 27B (27B) |
| Context window | 8,000 tokens |
| Tool-calling grade | **fair** |
| License | Gemma |
| Best SAM role | validate-first |
| vLLM tool parser | `hermes` |

## SAM fit

Tool calling is template-dependent. MUST pass the harness (H1-H3) before production.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** REQUIRES harness validation — do not assume.
- **Context (S2):** 8,000 tokens — LIMITING — short for orchestration, watch overflow.
- **Role:** suited to domain/leaf agents (one or two tools, cost-sensitive, high volume).
- **Notes:** Templated tool calling; 8K context limiting.

## SAM `model:` block

```yaml
model:
  model: openai/google/gemma-2-27b-it
  api_base: ${LLM_API_BASE}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${LLM_API_KEY, sk-noop}
  parallel_tool_calls: true
  temperature: 0.2
  max_tokens: 4096
```

## Serve it (vLLM)

```bash
vllm serve google/gemma-2-27b-it \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser hermes \
  --max-model-len 8000
```

## Validate

```bash
export SAM_TEST_MODEL="openai/google/gemma-2-27b-it"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
