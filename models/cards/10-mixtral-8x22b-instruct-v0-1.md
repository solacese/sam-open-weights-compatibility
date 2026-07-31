# 10. Mixtral 8x22B Instruct

| Field | Value |
|---|---|
| HF repo | `mistralai/Mixtral-8x22B-Instruct-v0.1` |
| Params (active) | 141B (39B) |
| Context window | 64,000 tokens |
| Tool-calling grade | **very-good** |
| License | Apache-2.0 |
| Best SAM role | orchestrator |
| vLLM tool parser | `mistral` |

## SAM fit

Reliable tool calling. Good for orchestrator or domain agents.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** expected PASS — verify on your stack.
- **Context (S2):** 64,000 tokens — adequate for leaf agents; tight for deep multi-hop.
- **Role:** suited to orchestration (routing, fan-out, synthesis).
- **Notes:** Efficient MoE; smaller context.

## SAM `model:` block

```yaml
model:
  model: openai/mistralai/Mixtral-8x22B-Instruct-v0.1
  api_base: ${LLM_API_BASE}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${LLM_API_KEY, sk-noop}
  parallel_tool_calls: true
  temperature: 0.2
  max_tokens: 4096
```

## Serve it (vLLM)

```bash
vllm serve mistralai/Mixtral-8x22B-Instruct-v0.1 \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser mistral \
  --max-model-len 64000
```

## Validate

```bash
export SAM_TEST_MODEL="openai/mistralai/Mixtral-8x22B-Instruct-v0.1"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
