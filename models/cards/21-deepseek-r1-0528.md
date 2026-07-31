# 21. DeepSeek-R1 (0528)

> **Validate before trusting.** Tool calling works only under specific conditions (revision / template / serving path). Run the harness first.

| Field | Value |
|---|---|
| HF repo | `deepseek-ai/DeepSeek-R1-0528` |
| Params (active) | 671B (37B) |
| Context window | 128,000 tokens |
| Native tool calling | **partial** |
| Tool-calling grade | **validate-first** |
| Benchmark | BFCL Prompt tier only (base R1 has no native FC) |
| License | MIT |
| Best SAM role | reasoning |
| vLLM tool parser | `deepseek_v3` |

## SAM fit

Tool calling is conditional (specific revision, template, or serving path). MUST pass the harness (H1-H3) before any use.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** REQUIRES harness validation - do not assume.
- **Context (S2):** 128,000 tokens - ample for orchestrator + multi-hop.
- **Role:** suited to orchestration (routing, fan-out, synthesis).
- **Notes:** Use the 0528 revision + deepseek R1 chat template; base DeepSeek-R1 is prompt-only. Validate H1-H3.

## SAM `model:` block

```yaml
model:
  model: openai/deepseek-ai/DeepSeek-R1-0528
  api_base: ${LLM_API_BASE}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${LLM_API_KEY, sk-noop}
  parallel_tool_calls: true
  temperature: 0.2
  max_tokens: 4096
```
## Serve it (vLLM)

```bash
vllm serve deepseek-ai/DeepSeek-R1-0528 \
  --host 0.0.0.0 --port 8000 \
  --enable-auto-tool-choice \
  --tool-call-parser deepseek_v3 \
  --max-model-len 128000
```

## Validate

```bash
export SAM_TEST_MODEL="openai/deepseek-ai/DeepSeek-R1-0528"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
