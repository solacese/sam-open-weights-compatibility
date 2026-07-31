# 4. Mistral Large 2 2411

| Field | Value |
|---|---|
| HF repo | `mistralai/Mistral-Large-Instruct-2411` |
| Params (active) | 123B (123B) |
| Context window | 128,000 tokens |
| Tool-calling grade | **excellent** |
| License | MRL non-prod |
| Best SAM role | orchestrator |
| vLLM tool parser | `mistral` |

## SAM fit

Production-proven tool calling. Safe for orchestrator roles.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** expected PASS — verify on your stack.
- **Context (S2):** 128,000 tokens — ample for orchestrator + multi-hop.
- **Role:** suited to orchestration (routing, fan-out, synthesis).
- **Notes:** Function calling designed-in; in SAM modelinfo.

## SAM `model:` block

```yaml
model:
  model: openai/mistralai/Mistral-Large-Instruct-2411
  api_base: ${LLM_API_BASE}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${LLM_API_KEY, sk-noop}
  parallel_tool_calls: true
  temperature: 0.2
  max_tokens: 4096
```

## Serve it (vLLM)

```bash
vllm serve mistralai/Mistral-Large-Instruct-2411 \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser mistral \
  --max-model-len 128000
```

## Validate

```bash
export SAM_TEST_MODEL="openai/mistralai/Mistral-Large-Instruct-2411"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
