# 18. gpt-oss 20b

| Field | Value |
|---|---|
| HF repo | `openai/gpt-oss-20b` |
| Organization | OpenAI |
| Country of origin | USA |
| Params (active) | 21B (3.6B) |
| Context window | 128,000 tokens |
| Native tool calling | **yes** |
| Tool-calling grade | **good** |
| BFCL V4 overall acc | n/a |
| Benchmark | Agentic-first; ~o3-mini class (vendor); runs in ~16GB |
| License | Apache-2.0 |
| Best SAM role | leaf-agent |
| vLLM tool parser | `openai` |
| VRAM (FP16 / 4-bit) | n/a (MXFP4) / ~16 (MXFP4) |
| Recommended GPU (4-bit) | 1x 16-24GB (RTX 4090 / L4) |

## SAM fit

Works; occasional JSON-argument quirks. Validate S3 on your quant.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** works but validate JSON-arg fidelity.
- **Context (S2):** 128,000 tokens - ample for orchestrator + multi-hop.
- **Role:** suited to domain/leaf agents (one or two tools, cost-sensitive, high volume).
- **Notes:** OpenAI open-weight small; harmony format required; vLLM openai parser.

## SAM `model:` block

```yaml
model:
  model: openai/openai/gpt-oss-20b
  api_base: ${LLM_API_BASE}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${LLM_API_KEY, sk-noop}
  parallel_tool_calls: true
  temperature: 0.2
  max_tokens: 4096
```
## Serve it (vLLM)

```bash
vllm serve openai/gpt-oss-20b \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser openai \
  --max-model-len 128000
```

## Validate

```bash
export SAM_TEST_MODEL="openai/openai/gpt-oss-20b"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
