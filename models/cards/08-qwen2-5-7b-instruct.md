# Qwen2.5 7B Instruct

*BFCL-score rank #8 of 25 · SAM-fit rank #16 (see [shortlist](../../docs/shortlist.md))*

| Field | Value |
|---|---|
| HF repo | `Qwen/Qwen2.5-7B-Instruct` |
| Organization | Alibaba (Qwen team) |
| Country of origin | China |
| Params (active) | 7B (7B) |
| Context window | 128,000 tokens |
| Native tool calling | **yes** |
| Tool-calling grade | **good** |
| BFCL overall acc | 56.70 (FC, V3) |
| Benchmark | Native Hermes-style FC (vLLM) |
| License | Apache-2.0 |
| Best SAM role | leaf-agent |
| vLLM tool parser | `hermes` |
| VRAM (FP16 / 4-bit) | 16 GB / 4 GB |
| Recommended GPU (4-bit) | 1x 16-24GB (RTX 4090 / L4) |

## SAM fit

Works; occasional JSON-argument quirks. Validate S3 on your quant.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** works but validate JSON-arg fidelity.
- **Context (S2):** 128,000 tokens - ample for orchestrator + multi-hop.
- **Role:** suited to domain/leaf agents (one or two tools, cost-sensitive, high volume).
- **Notes:** Cheapest reliable tool caller.

## SAM `model:` block

```yaml
model:
  model: openai/Qwen/Qwen2.5-7B-Instruct
  api_base: ${LLM_API_BASE}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${LLM_API_KEY, sk-noop}
  parallel_tool_calls: true
  temperature: 0.2
  max_tokens: 4096
```
## Serve it (vLLM)

```bash
vllm serve Qwen/Qwen2.5-7B-Instruct \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser hermes \
  --max-model-len 128000
```

## Validate

```bash
export SAM_TEST_MODEL="openai/Qwen/Qwen2.5-7B-Instruct"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
