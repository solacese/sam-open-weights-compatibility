# 17. Qwen2.5-Coder 32B

| Field | Value |
|---|---|
| HF repo | `Qwen/Qwen2.5-Coder-32B-Instruct` |
| Params (active) | 32B (32B) |
| Context window | 128,000 tokens |
| Native tool calling | **yes** |
| Tool-calling grade | **very-good** |
| Benchmark | Native Hermes-style FC (vLLM) |
| License | Apache-2.0 |
| Best SAM role | structured-tools |
| vLLM tool parser | `hermes` |

## SAM fit

Reliable tool calling. Good for orchestrator or domain agents.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** expected PASS - verify on your stack.
- **Context (S2):** 128,000 tokens - ample for orchestrator + multi-hop.
- **Role:** suited to domain/leaf agents (one or two tools, cost-sensitive, high volume).
- **Notes:** Best for code/structured tool args.

## SAM `model:` block

```yaml
model:
  model: openai/Qwen/Qwen2.5-Coder-32B-Instruct
  api_base: ${LLM_API_BASE}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${LLM_API_KEY, sk-noop}
  parallel_tool_calls: true
  temperature: 0.2
  max_tokens: 4096
```
## Serve it (vLLM)

```bash
vllm serve Qwen/Qwen2.5-Coder-32B-Instruct \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser hermes \
  --max-model-len 128000
```

## Validate

```bash
export SAM_TEST_MODEL="openai/Qwen/Qwen2.5-Coder-32B-Instruct"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
