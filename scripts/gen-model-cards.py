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
}


def slug(repo: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", repo.lower()).strip("-")


def card(row: dict) -> str:
    grade = row["tool_calling_grade"]
    prefix = row["provider_prefix"]
    repo = row["hf_repo"]
    model_str = f"{prefix}/{repo}" if prefix != "cohere" else f"cohere/{repo.split('/')[-1]}"
    ctx = int(row["context_tokens"])
    role = row["best_role"]
    orchestrator = role in ("orchestrator", "reasoning", "compliance-rag")
    return f"""# {row['rank']}. {row['model']}

| Field | Value |
|---|---|
| HF repo | `{repo}` |
| Params (active) | {row['params']} ({row['active_params']}) |
| Context window | {ctx:,} tokens |
| Tool-calling grade | **{grade}** |
| License | {row['license']} |
| Best SAM role | {role} |
| vLLM tool parser | `{row['vllm_tool_parser']}` |

## SAM fit

{GATE_NOTE[grade]}

- **Hard gates (H1 tool calls / H2 streaming / H3 tool-result turns):** {"expected PASS — verify on your stack" if grade in ("excellent", "very-good") else "REQUIRES harness validation — do not assume"}.
- **Context (S2):** {ctx:,} tokens — {"ample for orchestrator + multi-hop" if ctx >= 128000 else ("adequate for leaf agents; tight for deep multi-hop" if ctx >= 32000 else "LIMITING — short for orchestration, watch overflow")}.
- **Role:** {"suited to orchestration (routing, fan-out, synthesis)." if orchestrator else "suited to domain/leaf agents (one or two tools, cost-sensitive, high volume)."}
- **Notes:** {row['notes']}.

## SAM `model:` block

```yaml
model:
  model: {model_str}
  api_base: ${{LLM_API_BASE}}         # your OpenAI-compatible endpoint, e.g. http://localhost:8000/v1
  api_key: ${{LLM_API_KEY, sk-noop}}
  parallel_tool_calls: true
  temperature: 0.2
  max_tokens: 4096
```

## Serve it (vLLM)

```bash
vllm serve {repo} \\
  --host 0.0.0.0 --port 8000 \\
  --enable-auto-tool-choice \\
  --tool-call-parser {row['vllm_tool_parser']} \\
  --max-model-len {min(ctx, 131072)}
```

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
    with CSV.open() as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        name = f"{int(row['rank']):02d}-{slug(row['hf_repo'].split('/')[-1])}.md"
        (OUT / name).write_text(card(row))
    print(f"Generated {len(rows)} model cards in {OUT}")


if __name__ == "__main__":
    main()
