# 19. Mistral NeMo 12B

| Field | Value |
|---|---|
| HF repo | `mistralai/Mistral-Nemo-Instruct-2407` |
| Organization | Mistral AI + NVIDIA |
| Country of origin | France |
| Params (active) | 12B (12B) |
| Context window | 128,000 tokens |
| Native tool calling | **yes** |
| Tool-calling grade | **good** |
| BFCL V4 overall acc | 27.63 (FC) |
| Benchmark | BFCL Function-Calling tier (open-mistral-nemo-2407-FC) |
| License | Apache-2.0 |
| Best SAM role | leaf-agent |
| vLLM tool parser | `mistral` |
| VRAM (FP16 / 4-bit) | 28 GB / 8 GB |
| Recommended GPU (4-bit) | 1x 16-24GB (RTX 4090 / L4) |

## SAM fit

Works; occasional JSON-argument quirks. Validate S3 on your quant.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** works but validate JSON-arg fidelity.
- **Context (S2):** 128,000 tokens - ample for orchestrator + multi-hop.
- **Role:** suited to domain/leaf agents (one or two tools, cost-sensitive, high volume).
- **Notes:** Long context at small size.

## SAM `model:` block

```yaml
model:
  model: openai/mistralai/Mistral-Nemo-Instruct-2407
  api_base: ${LLM_API_BASE}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${LLM_API_KEY, sk-noop}
  parallel_tool_calls: true
  temperature: 0.2
  max_tokens: 4096
```
## Serve it (vLLM)

```bash
vllm serve mistralai/Mistral-Nemo-Instruct-2407 \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser mistral \
  --max-model-len 128000
```

## Validate

```bash
export SAM_TEST_MODEL="openai/mistralai/Mistral-Nemo-Instruct-2407"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
