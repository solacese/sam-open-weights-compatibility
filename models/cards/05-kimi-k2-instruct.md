# Kimi-K2 Instruct

*BFCL-score rank #5 of 25 · SAM-fit rank #11 (see [shortlist](../../docs/shortlist.md))*

| Field | Value |
|---|---|
| HF repo | `moonshotai/Kimi-K2-Instruct` |
| Organization | Moonshot AI |
| Country of origin | China |
| Params (active) | 1000B (32B) |
| Context window | 128,000 tokens |
| Native tool calling | **yes** |
| Tool-calling grade | **very-good** |
| BFCL overall acc | 59.06 (FC, V4) |
| Benchmark | BFCL Function-Calling tier (kimi-k2-FC) |
| License | Modified MIT |
| Best SAM role | orchestrator |
| vLLM tool parser | `kimi_k2` |
| VRAM (FP16 / 4-bit) | 2300 GB / 632 GB |
| Recommended GPU (4-bit) | 8x 80GB (1x H100 node) |

## SAM fit

Reliable tool calling. Good for orchestrator or domain agents.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** expected PASS - verify on your stack.
- **Context (S2):** 128,000 tokens - ample for orchestrator + multi-hop.
- **Role:** suited to orchestration (routing, fan-out, synthesis).
- **Notes:** Very large MoE; strong agentic tool use.

## SAM `model:` block

```yaml
model:
  model: openai/moonshotai/Kimi-K2-Instruct
  api_base: ${LLM_API_BASE}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${LLM_API_KEY, sk-noop}
  parallel_tool_calls: true
  temperature: 0.2
  max_tokens: 4096
```
## Serve it (vLLM)

```bash
vllm serve moonshotai/Kimi-K2-Instruct \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser kimi_k2 \
  --max-model-len 128000
```

## Validate

```bash
export SAM_TEST_MODEL="openai/moonshotai/Kimi-K2-Instruct"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
