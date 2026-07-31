# 10. gpt-oss 120b

| Field | Value |
|---|---|
| HF repo | `openai/gpt-oss-120b` |
| Params (active) | 117B (5.1B) |
| Context window | 128,000 tokens |
| Native tool calling | **yes** |
| Tool-calling grade | **very-good** |
| Benchmark | Agentic-first; near o4-mini reasoning (vendor) |
| License | Apache-2.0 |
| Best SAM role | orchestrator |
| vLLM tool parser | `openai` |

## SAM fit

Reliable tool calling. Good for orchestrator or domain agents.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** expected PASS - verify on your stack.
- **Context (S2):** 128,000 tokens - ample for orchestrator + multi-hop.
- **Role:** suited to orchestration (routing, fan-out, synthesis).
- **Notes:** OpenAI open-weight; harmony format required; dedicated vLLM openai parser.

## SAM `model:` block

```yaml
model:
  model: openai/openai/gpt-oss-120b
  api_base: ${LLM_API_BASE}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${LLM_API_KEY, sk-noop}
  parallel_tool_calls: true
  temperature: 0.2
  max_tokens: 4096
```
## Serve it (vLLM)

```bash
vllm serve openai/gpt-oss-120b \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser openai \
  --max-model-len 128000
```

## Validate

```bash
export SAM_TEST_MODEL="openai/openai/gpt-oss-120b"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
