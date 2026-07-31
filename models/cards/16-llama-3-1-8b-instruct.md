# 16. Llama 3.1 8B Instruct

| Field | Value |
|---|---|
| HF repo | `meta-llama/Llama-3.1-8B-Instruct` |
| Params (active) | 8B (8B) |
| Context window | 128,000 tokens |
| Tool-calling grade | **good** |
| License | Llama 3.1 Community |
| Best SAM role | leaf-agent |
| vLLM tool parser | `llama3_json` |

## SAM fit

Works; occasional JSON-argument quirks. Validate S3 on your quant.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** REQUIRES harness validation — do not assume.
- **Context (S2):** 128,000 tokens — ample for orchestrator + multi-hop.
- **Role:** suited to domain/leaf agents (one or two tools, cost-sensitive, high volume).
- **Notes:** Ubiquitous small model; in SAM modelinfo.

## SAM `model:` block

```yaml
model:
  model: openai/meta-llama/Llama-3.1-8B-Instruct
  api_base: ${LLM_API_BASE}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${LLM_API_KEY, sk-noop}
  parallel_tool_calls: true
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
