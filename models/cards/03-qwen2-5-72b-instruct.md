# Qwen2.5 72B Instruct

*BFCL-score rank #3 of 25 · SAM-fit rank #2 (see [shortlist](../../docs/shortlist.md))*

| Field | Value |
|---|---|
| HF repo | `Qwen/Qwen2.5-72B-Instruct` |
| Organization | Alibaba (Qwen team) |
| Country of origin | China |
| Params (active) | 72B (72B) |
| Context window | 128,000 tokens |
| Native tool calling | **yes** |
| Tool-calling grade | **excellent** |
| BFCL overall acc | 61.31 (P, V3) |
| Benchmark | Native Hermes-style FC (vLLM); superseded on BFCL by Qwen3 |
| License | Qwen |
| Best SAM role | orchestrator |
| vLLM tool parser | `hermes` |
| VRAM (FP16 / 4-bit) | 166 GB / 46 GB |
| Recommended GPU (4-bit) | 1x 48GB (A6000 / L40S) |

## SAM fit

Production-proven tool calling. Safe for orchestrator roles.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** expected PASS - verify on your stack.
- **Context (S2):** 128,000 tokens - ample for orchestrator + multi-hop.
- **Role:** suited to orchestration (routing, fan-out, synthesis).
- **Notes:** Strong multi-tool and parallel calls.

## SAM `model:` block

```yaml
model:
  model: openai/Qwen/Qwen2.5-72B-Instruct
  api_base: ${LLM_API_BASE}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${LLM_API_KEY, sk-noop}
  parallel_tool_calls: true
  temperature: 0.2
  max_tokens: 4096
```
## Serve it (vLLM)

```bash
vllm serve Qwen/Qwen2.5-72B-Instruct \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser hermes \
  --max-model-len 128000
```

## Validate

```bash
export SAM_TEST_MODEL="openai/Qwen/Qwen2.5-72B-Instruct"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
