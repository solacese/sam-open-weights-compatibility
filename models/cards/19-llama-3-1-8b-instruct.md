# Llama 3.1 8B Instruct

*BFCL-score rank #19 of 25 · SAM-fit rank #20 (see [shortlist](../../docs/shortlist.md))*

| Field | Value |
|---|---|
| HF repo | `meta-llama/Llama-3.1-8B-Instruct` |
| Organization | Meta |
| Country of origin | USA |
| Params (active) | 8B (8B) |
| Context window | 128,000 tokens |
| Native tool calling | **yes** |
| Tool-calling grade | **good** |
| BFCL overall acc | 25.83 (P, V4) |
| Benchmark | BFCL Function-Calling tier (self-hosted) |
| License | Llama 3.1 Community |
| Best SAM role | leaf-agent |
| vLLM tool parser | `llama3_json` |
| VRAM (FP16 / 4-bit) | 18 GB / 5 GB |
| Recommended GPU (4-bit) | 1x 16-24GB (RTX 4090 / L4) |

## SAM fit

Works; occasional JSON-argument quirks. Validate S3 on your quant.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** works but validate JSON-arg fidelity.
- **Context (S2):** 128,000 tokens - ample for orchestrator + multi-hop.
- **Role:** suited to domain/leaf agents (one or two tools, cost-sensitive, high volume).
- **Notes:** Ubiquitous small model; in SAM modelinfo. No parallel tool calls (Llama 3).

## SAM `model:` block

```yaml
model:
  model: openai/meta-llama/Llama-3.1-8B-Instruct
  api_base: ${LLM_API_BASE}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${LLM_API_KEY, sk-noop}
  parallel_tool_calls: false
  temperature: 0.2
  max_tokens: 4096
```
## Serve it (vLLM)

```bash
vllm serve meta-llama/Llama-3.1-8B-Instruct \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser llama3_json \
  --max-model-len 128000
```

## Validate

```bash
export SAM_TEST_MODEL="openai/meta-llama/Llama-3.1-8B-Instruct"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
