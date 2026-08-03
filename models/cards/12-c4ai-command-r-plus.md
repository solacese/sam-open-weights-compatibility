# Command R+ (legacy)

*BFCL-score rank #12 of 25 · SAM-fit rank #22 (see [shortlist](../../docs/shortlist.md))*

> **Validate before trusting.** Tool calling works only under specific conditions (revision / template / serving path). Run the harness first.

| Field | Value |
|---|---|
| HF repo | `CohereForAI/c4ai-command-r-plus` |
| Organization | Cohere |
| Country of origin | Canada |
| Params (active) | 104B (104B) |
| Context window | 128,000 tokens |
| Native tool calling | **partial** |
| Tool-calling grade | **validate-first** |
| BFCL overall acc | 49.35 (FC, V3) |
| Benchmark | Superseded by Command A; not in current vLLM parser list |
| License | CC-BY-NC-4.0 |
| Best SAM role | compliance-rag |
| vLLM tool parser | `none` |
| VRAM (FP16 / 4-bit) | 239 GB / 66 GB |
| Recommended GPU (4-bit) | 1x 80GB (A100 / H100) |

## SAM fit

Tool calling is conditional (specific revision, template, or serving path). MUST pass the harness (H1-H3) before any use.

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** REQUIRES harness validation - do not assume.
- **Context (S2):** 128,000 tokens - ample for orchestrator + multi-hop.
- **Role:** suited to orchestration (routing, fan-out, synthesis).
- **Notes:** Older Cohere tool+RAG model; prefer Command A. No current vLLM parser; validate serving path.

## Serve it (vLLM)

vLLM has **no tool-call parser** for this model, so SAM tool calling will not work on a stock vLLM serve. Do not use it as a SAM agent model. If you must experiment, see the note above for the supported alternative.

## Validate

```bash
export SAM_TEST_MODEL="cohere/c4ai-command-r-plus"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
