# Mistral Small 3 24B

*BFCL-score rank #22 of 25 · SAM-fit rank #15 (see [shortlist](../../docs/shortlist.md))*

| Field | Value |
|---|---|
| HF repo | `mistralai/Mistral-Small-24B-Instruct-2501` |
| Organization | Mistral AI |
| Country of origin | France |
| Params (active) | 24B (24B) |
| Context window | 32,000 tokens |
| Native tool calling | **yes** |
| Tool-calling grade | **very-good** |
| BFCL overall acc | n/a |
| Benchmark | Mistral Small line on BFCL Function-Calling tier |
| License | Apache-2.0 |
| Best SAM role | domain-agent |
| vLLM tool parser | `mistral` |
| VRAM (FP16 / 4-bit) | 55 GB / 15 GB |
| Recommended GPU (4-bit) | 1x 16-24GB (RTX 4090 / L4) |

## SAM fit

Reliable tool calling. Good for orchestrator or domain agents.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** expected PASS - verify on your stack.
- **Context (S2):** 32,000 tokens - adequate for leaf agents; tight for deep multi-hop.
- **Role:** suited to domain/leaf agents (one or two tools, cost-sensitive, high volume).
- **Notes:** Fast native tool calling; in SAM modelinfo.

## SAM `model:` block

```yaml
model:
  model: openai/mistralai/Mistral-Small-24B-Instruct-2501
  api_base: ${LLM_API_BASE}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${LLM_API_KEY, sk-noop}
  parallel_tool_calls: true
  temperature: 0.2
  max_tokens: 4096
```
## Serve it (vLLM)

```bash
vllm serve mistralai/Mistral-Small-24B-Instruct-2501 \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser mistral \
  --max-model-len 32000
```

## Validate

```bash
export SAM_TEST_MODEL="openai/mistralai/Mistral-Small-24B-Instruct-2501"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
