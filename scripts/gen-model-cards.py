#!/usr/bin/env python3
"""Generate one SAM-ready model spec card (Markdown) per row in models/index.csv.

Idempotent: re-run after editing the CSV to regenerate all cards.
Each card documents the model's SAM fit and ships a copy-paste `model:` block.
"""
import csv
import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
CSV = ROOT / "models" / "index.csv"
OUT = ROOT / "models" / "cards"

GATE_NOTE = {
    "excellent": "Production-proven tool calling. Safe for orchestrator roles.",
    "very-good": "Reliable tool calling. Good for orchestrator or domain agents.",
    "good": "Works; occasional JSON-argument quirks. Validate S3 on your quant.",
    "fair": "Tool calling is template-dependent. MUST pass the harness (H1-H3) before production.",
    "validate-first": "Tool calling is conditional (specific revision, template, or serving path). MUST pass the harness (H1-H3) before any use.",
    "unsupported": "No native tool calling. NOT recommended for SAM. Listed here so you know why, and what to use instead.",
}

# Llama 3 does not support parallel tool calls (only Llama 4). Mixtral/Mistral 7B are unreliable at it.
NO_PARALLEL = ("Llama-3.1", "Llama-3.3", "Mixtral")


def slug(repo: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", repo.lower()).strip("-")


def card(row: dict) -> str:
    grade = row["tool_calling_grade"]
    prefix = row["provider_prefix"]
    repo = row["hf_repo"]
    model_str = f"{prefix}/{repo}" if prefix != "cohere" else f"cohere/{repo.split('/')[-1]}"
    ctx = int(row["context_tokens"])
    role = row["best_role"]
    parser = row["vllm_tool_parser"]
    native = row.get("native_tool_calling", "yes")
    bench = row.get("benchmark_note", "").strip()
    orchestrator = role in ("orchestrator", "reasoning", "compliance-rag")
    supported = grade not in ("unsupported",)
    parallel = "true" if not any(k in repo for k in NO_PARALLEL) and supported else "false"

    header = f"# {row['rank']}. {row['model']}\n"
    if grade == "unsupported":
        header += "\n> **Not recommended for SAM.** This model lacks native OpenAI-schema tool calling, which SAM requires. See the note below for the recommended alternative.\n"
    elif grade == "validate-first":
        header += "\n> **Validate before trusting.** Tool calling works only under specific conditions (revision / template / serving path). Run the harness first.\n"

    fit_gate = (
        "expected PASS - verify on your stack"
        if grade in ("excellent", "very-good")
        else ("works but validate JSON-arg fidelity" if grade == "good"
              else ("expected FAIL - no native tool calling" if grade == "unsupported"
                    else "REQUIRES harness validation - do not assume"))
    )
    role_line = (
        "not a SAM agent model - use the alternative in the notes."
        if grade == "unsupported"
        else ("suited to orchestration (routing, fan-out, synthesis)." if orchestrator
              else "suited to domain/leaf agents (one or two tools, cost-sensitive, high volume).")
    )
    ctx_note = (
        "ample for orchestrator + multi-hop" if ctx >= 128000
        else ("adequate for leaf agents; tight for deep multi-hop" if ctx >= 32000
              else "LIMITING - short for orchestration, watch overflow")
    )

    # Serve + config blocks only make sense for models with a real parser.
    if parser and parser != "none":
        serve_block = f"""## Serve it (vLLM)

```bash
vllm serve {repo} \\
  --host 0.0.0.0 --port 8000 \\
  --enable-auto-tool-choice \\
  --tool-call-parser {parser} \\
  --max-model-len {min(ctx, 131072)}
```
"""
        model_block = f"""## SAM `model:` block

```yaml
model:
  model: {model_str}
  api_base: ${{LLM_API_BASE}}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${{LLM_API_KEY, sk-noop}}
  parallel_tool_calls: {parallel}
  temperature: 0.2
  max_tokens: 4096
```
"""
    else:
        serve_block = f"""## Serve it (vLLM)

vLLM has **no tool-call parser** for this model, so SAM tool calling will not work on a stock vLLM serve. Do not use it as a SAM agent model. If you must experiment, see the note above for the supported alternative.
"""
        model_block = ""

    return f"""{header}
| Field | Value |
|---|---|
| HF repo | `{repo}` |
| Params (active) | {row['params']} ({row['active_params']}) |
| Context window | {ctx:,} tokens |
| Native tool calling | **{native}** |
| Tool-calling grade | **{grade}** |
| Benchmark | {bench or 'n/a'} |
| License | {row['license']} |
| Best SAM role | {role} |
| vLLM tool parser | `{parser}` |

## SAM fit

{GATE_NOTE[grade]}

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** {fit_gate}.
- **Context (S2):** {ctx:,} tokens - {ctx_note}.
- **Role:** {role_line}
- **Notes:** {row['notes']}.

{model_block}{serve_block}
## Validate

```bash
export SAM_TEST_MODEL="{model_str}"
export SAM_TEST_API_BASE="http://localhost:8000/v1"
./scripts/probe.sh && ./scripts/run-sam-scenario.sh two-tool-dependency
```

See [`../../docs/validation.md`](../../docs/validation.md) for interpreting results.
"""


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    # Clear stale cards so renamed/removed rows do not linger.
    for old in OUT.glob("*.md"):
        old.unlink()
    with CSV.open() as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        name = f"{int(row['rank']):02d}-{slug(row['hf_repo'].split('/')[-1])}.md"
        (OUT / name).write_text(card(row))
    print(f"Generated {len(rows)} model cards in {OUT}")


if __name__ == "__main__":
    main()
