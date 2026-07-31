# 12. Command A

| Field | Value |
|---|---|
| HF repo | `CohereForAI/c4ai-command-a-03-2025` |
| Params (active) | 111B (111B) |
| Context window | 256,000 tokens |
| Native tool calling | **yes** |
| Tool-calling grade | **very-good** |
| Benchmark | BFCL Function-Calling tier (command-a-03-2025-FC) |
| License | CC-BY-NC-4.0 |
| Best SAM role | compliance-rag |
| vLLM tool parser | `cohere_command3` |

## SAM fit

Reliable tool calling. Good for orchestrator or domain agents.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** expected PASS - verify on your stack.
- **Context (S2):** 256,000 tokens - ample for orchestrator + multi-hop.
- **Role:** suited to orchestration (routing, fan-out, synthesis).
- **Notes:** Cohere current-gen tool+RAG; non-commercial license; needs cohere_melody pkg.

## SAM `model:` block

```yaml
model:
  model: cohere/c4ai-command-a-03-2025
  api_base: ${LLM_API_BASE}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${LLM_API_KEY, sk-noop}
  parallel_tool_calls: true
  temperature: 0.2
  max_tokens: 4096
```
## Serve it (vLLM)

```bash
vllm serve CohereForAI/c4ai-command-a-03-2025 \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser cohere_command3 \
  --max-model-len 131072
```

## Validate

```bash
export SAM_TEST_MODEL="cohere/c4ai-command-a-03-2025"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
