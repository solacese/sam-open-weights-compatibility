# 6. Llama 3.1 405B Instruct

| Field | Value |
|---|---|
| HF repo | `meta-llama/Llama-3.1-405B-Instruct` |
| Organization | Meta |
| Country of origin | USA |
| Params (active) | 405B (405B) |
| Context window | 128,000 tokens |
| Native tool calling | **yes** |
| Tool-calling grade | **excellent** |
| BFCL V4 overall acc | n/a |
| Benchmark | BFCL Function-Calling tier (self-hosted) |
| License | Llama 3.1 Community |
| Best SAM role | orchestrator |
| vLLM tool parser | `llama3_json` |
| VRAM (FP16 / 4-bit) | 931 GB / 256 GB |
| Recommended GPU (4-bit) | 4x 80GB (A100 / H100) |

## SAM fit

Production-proven tool calling. Safe for orchestrator roles.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** expected PASS - verify on your stack.
- **Context (S2):** 128,000 tokens - ample for orchestrator + multi-hop.
- **Role:** suited to orchestration (routing, fan-out, synthesis).
- **Notes:** Highest ceiling; heavy host; in SAM modelinfo. No parallel tool calls (Llama 3).

## SAM `model:` block

```yaml
model:
  model: openai/meta-llama/Llama-3.1-405B-Instruct
  api_base: ${LLM_API_BASE}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${LLM_API_KEY, sk-noop}
  parallel_tool_calls: false
  temperature: 0.2
  max_tokens: 4096
```
## Serve it (vLLM)

```bash
vllm serve meta-llama/Llama-3.1-405B-Instruct \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser llama3_json \
  --max-model-len 128000
```

## Validate

```bash
export SAM_TEST_MODEL="openai/meta-llama/Llama-3.1-405B-Instruct"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
