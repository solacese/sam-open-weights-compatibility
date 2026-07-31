# 13. Command R 35B

| Field | Value |
|---|---|
| HF repo | `CohereForAI/c4ai-command-r-v01` |
| Params (active) | 35B (35B) |
| Context window | 128,000 tokens |
| Tool-calling grade | **very-good** |
| License | CC-BY-NC-4.0 |
| Best SAM role | compliance-rag |
| vLLM tool parser | `hermes` |

## SAM fit

Reliable tool calling. Good for orchestrator or domain agents.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** expected PASS — verify on your stack.
- **Context (S2):** 128,000 tokens — ample for orchestrator + multi-hop.
- **Role:** suited to orchestration (routing, fan-out, synthesis).
- **Notes:** RAG+tool tuned; non-commercial license.

## SAM `model:` block

```yaml
model:
  model: cohere/c4ai-command-r-v01
  api_base: ${LLM_API_BASE}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${LLM_API_KEY, sk-noop}
  parallel_tool_calls: true
  temperature: 0.2
  max_tokens: 4096
```

## Serve it (vLLM)

```bash
vllm serve CohereForAI/c4ai-command-r-v01 \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser hermes \
  --max-model-len 128000
```

## Validate

```bash
export SAM_TEST_MODEL="cohere/c4ai-command-r-v01"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
